import gc
import multiprocessing

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QSizePolicy, QTabWidget, \
    QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from qtpy import QtCore

from hypergraphx import Hypergraph, TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness, s_closeness, s_betweenness_nodes, s_closeness_nodes, \
    s_betweenness_nodes_averaged, s_closenness_nodes_averaged, s_betweenness_averaged, s_closeness_averaged
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.interactive_view.custom_widgets import LoadingScreen
from hypergraphx.viz.plot_motifs import plot_motifs


# Motifs
def motifs_calculations(hypergraph):
    motifs_3 = compute_motifs(hypergraph, order=3)
    motifs3_profile = [i[1] for i in motifs_3['norm_delta']]
    return motifs3_profile


def draw_adjacency(axes, values_list, **kwargs):
    draw_bar(axes[0], values_list[0], "Nodes", "Adjacency Factor (t=0)")
    draw_bar(axes[1], values_list[1], "Nodes", "Adjacency Factor (t=1)")

#Adjacency
def adjacency_calculations_pool(hypergraph):
    results = []
    for t in [0,1]:
        adj_factor = hypergraph.adjacency_factor(t)
        adj_factor_keys_label, adj_factor_label = generate_key(adj_factor)
        results.append([adj_factor, adj_factor_keys_label, adj_factor_label])
    return results

#Centrality
def calculate_centrality_pool(hypergraph):
    functions = [
        s_betweenness_averaged if isinstance(hypergraph, TemporalHypergraph) else s_betweenness,
        s_closeness_averaged if isinstance(hypergraph, TemporalHypergraph) else s_closeness,
        s_betweenness_nodes_averaged if isinstance(hypergraph, TemporalHypergraph) else s_betweenness_nodes,
        s_closenness_nodes_averaged if isinstance(hypergraph, TemporalHypergraph) else s_closeness_nodes,
    ]
    results = []
    for func in functions:
        result = func(hypergraph)
        keys_label, keys = generate_key(result)
        results.append((result, keys_label, keys))
    return results

def draw_centrality(axes, values_list, **kwargs):
    draw_bar(axes[0, 0], values_list[0], 'Edges', 'Edges Betweenness Centrality')
    draw_bar(axes[0, 1], values_list[1], 'Edges', 'Edges Closeness Centrality')
    draw_bar(axes[1, 0], values_list[2], 'Nodes', 'Nodes Betweenness Centrality')
    draw_bar(axes[1, 1], values_list[3], 'Nodes', 'Nodes Closeness Centrality')

# Degree
def degree_calculations(hypergraph):
    degree_distribution = hypergraph.degree_distribution()
    sizes = dict()
    for edge in hypergraph.get_edges():
        if len(edge) not in sizes.keys():
            sizes[len(edge)] = 0
        sizes[len(edge)] += 1
    return [degree_distribution, sizes]

def draw_degree(axes, value_list, **kwargs):
    draw_bar(axes[0], value_list[0], "Degrees", "Degree Distribution")
    draw_bar(axes[1], value_list[1], "Sizes", "Size Distribution")

# Weight
def calculate_weight_distribution(hypergraph):
    weight_distribution = {}
    value_list = []
    for weight in hypergraph.get_weights():
        if weight not in weight_distribution:
            weight_distribution[weight] = 0
            value_list.append(len(value_list))
        weight_distribution[weight] += 1
    return [weight_distribution, value_list]

def draw_weight(axes, value_list, **kwargs):
    weights = value_list[0]
    positions = value_list[1]
    axes.bar(positions, weights.values())
    axes.set_xlabel('Weights')
    axes.set_title('Weights Distribution')
    axes.set_xticks(positions, list(weights.keys()))
    axes.set_ylim(0, max(weights.values()) + 1)
    axes.set_yticks(range(1, max(weights.values()) + 1))

def create_canvas_with_toolbar(figure):
    canvas = FigureCanvas(figure)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    toolbar = NavigationToolbar(canvas)
    home_icon = QIcon("home.svg")
    toolbar._actions['home'].setIcon(home_icon)
    back_icon = QIcon("left.svg")
    toolbar._actions['back'].setIcon(back_icon)
    forward_icon = QIcon("right.svg")
    toolbar._actions['forward'].setIcon(forward_icon)
    pan_icon = QIcon("move.svg")
    toolbar._actions['pan'].setIcon(pan_icon)
    zoom_icon = QIcon("zoom.svg")
    toolbar._actions['zoom'].setIcon(zoom_icon)
    configure_subplots_icon = QIcon("options.svg")
    toolbar._actions['configure_subplots'].setIcon(configure_subplots_icon)
    edit_parameters_icon = QIcon("settings.svg")
    toolbar._actions['edit_parameters'].setIcon(edit_parameters_icon)
    save_icon = QIcon("save.svg")
    toolbar._actions['save_figure'].setIcon(save_icon)
    return canvas, toolbar

#Drawing
def draw_bar(ax, values, label, title, y_ticks_increment=1):
    dict_values = values if isinstance(values, dict) else values[0]
    labels = values[1] if isinstance(values, tuple) else dict_values.keys()

    ax.bar(labels, dict_values.values())
    ax.set_xlabel(label)
    ax.set_ylabel('Values')
    ax.set_title(title)
    try:
        ax.set_xticks(list(dict_values.keys()))
        max_value = max(dict_values.values())
        ax.set_yticks(range(1, max_value + y_ticks_increment))
        ax.set_ylim(0, max_value + y_ticks_increment)

    except Exception:
        pass

#Worker and Widget

class StatsWorker(QtCore.QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, function, parent=None):
        super(StatsWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.function = function
    def run(self):
        with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
            result = pool.apply(self.function, args=(self.hypergraph, ))
            self.progress.emit(result)

class HypergraphStatsWidget(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, hypergraph, parent=None):
        super(HypergraphStatsWidget, self).__init__(parent)
        self.hypergraph = None
        self.centrality_tab = None
        self.degree_tab = None
        self.motifs_tab = None
        self.adj_tab = None
        self.weight_tab = None
        self.vertical_tab = QTabWidget(parent=self)
        self.vertical_tab.setTabPosition(QTabWidget.West)
        self.vertical_tab.setObjectName("StatsTab")
        self.vertical_tab.setStyleSheet("""
        QTabWidget#MainTab::pane {
    /* Il bordo che verrà sovrascritto dalla linguetta selezionata */
    border: 1px solid #BDBDBD;
    background-color: white;
    
    /* Sposta il pannello a sinistra per allinearsi con il bordo interno delle tab */
    margin-left: -1px;
}

/* La prima tab in alto */
QTabBar::tab:first {
    margin-top: 10px;
}

/* Stile generale per ogni linguetta della barra verticale */
QTabWidget#StatsTab QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F5F5F5, stop: 1 #E0E0E0);
    border: 1px solid #BDBDBD;
        
    /* Arrotondiamo gli angoli a sinistra */
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;

    padding: 5px 8px;
    margin-bottom: 3px; /* Spazio tra le linguette verticali */
    margin-left: 10px;
    color: #444;
    font-weight: bold;
    font-size: 12px;
    
    /* Impostiamo altezza e larghezza. L'altezza è più importante in un layout verticale. */
    width: 30px; 
    height: 75px;
}

/* Linguetta quando il mouse è sopra, ma NON è selezionata */
QTabWidget#StatsTab QTabBar::tab:hover:!selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FFFFFF, stop: 1 #E8E8E8);
}

/* Linguetta SELEZIONATA - la regola più importante */
QTabWidget#StatsTab QTabBar::tab:selected {
    background-color: white; /* Forza lo sfondo bianco per fondersi con il pannello */
    color: #005A9E;
    
    /* Rimuoviamo il bordo destro per la connessione.
       Usiamo un colore trasparente per essere sicuri che sparisca. */
    border-right-color: transparent; 
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    /* Spostiamo la tab a destra per sovrapporla al bordo del pannello */
    margin-right: -1px;
    
    /* Aumentiamo il padding a destra per compensare il margine negativo */
    padding-right: 12px; 
}

/* Assicuriamoci che non cambi colore al hover quando è selezionata */
QTabWidget#StatsTab QTabBar::tab:selected:hover {
    background-color: white;
}
        """)
        self.vertical_tab.clear()
        self.hypergraph = hypergraph
        self.centrality_tab = GenericGraphWidget(
            hypergraph=hypergraph,
            drawing_function=draw_centrality,
            drawing_params={'axes': (2, 2), 'calculation_function': calculate_centrality_pool, 'wspace': 2,
                            'hspace': 2},
            title="Centrality",
            parent=self.vertical_tab
        )
        self.degree_tab = GenericGraphWidget(
            hypergraph=hypergraph,
            drawing_function=draw_degree,
            drawing_params={'axes': (2, 1), 'calculation_function': degree_calculations},
            title="Degree",
            parent=self.vertical_tab
        )

        self.vertical_tab.addTab(self.degree_tab, "Degree")
        self.vertical_tab.addTab(self.centrality_tab, "Centrality")
        if isinstance(hypergraph, Hypergraph):
            self.motifs_tab = MotifsWidget(hypergraph, parent=self.vertical_tab)
            self.vertical_tab.addTab(self.motifs_tab, "Motifs")
        if isinstance(hypergraph, Hypergraph):
            self.adj_tab = GenericGraphWidget(
                hypergraph=hypergraph,
                drawing_function=draw_adjacency,
                drawing_params={'axes': (2, 1), 'calculation_function': adjacency_calculations_pool},
                title="Adjacency",
                parent=self.vertical_tab
            )
            self.vertical_tab.addTab(self.adj_tab, "Adjacency")
        if self.hypergraph.is_weighted():
            self.weight_tab = GenericGraphWidget(
                hypergraph=hypergraph,
                drawing_function=draw_weight,
                drawing_params={'axes': (1, 1), 'calculation_function': calculate_weight_distribution},
                title="Weight",
                parent=self.vertical_tab
            )
            self.vertical_tab.addTab(self.weight_tab, "Weights")
        gc.collect()
        self.setCentralWidget(self.vertical_tab)
    def update_hypergraph(self, hypergraph):
        self.hypergraph = hypergraph
        if isinstance(hypergraph, Hypergraph):
            if self.motifs_tab is None:
                self.motifs_tab = MotifsWidget(hypergraph, parent=self.vertical_tab)
                self.vertical_tab.addTab(self.motifs_tab, "Motifs")
            else:
                if isinstance(hypergraph, Hypergraph):
                    self.motifs_tab.update_hypergraph(self.hypergraph)
                    self.motifs_tab.setVisible(True)
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.motifs_tab), True)
                else:
                    self.motifs_tab.setVisible(False)
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.motifs_tab), False)

        if isinstance(hypergraph, Hypergraph):
            if self.adj_tab is None:
                self.adj_tab = GenericGraphWidget(
                    hypergraph=hypergraph,
                    drawing_function=draw_adjacency,
                    drawing_params={'axes': (2, 1), 'calculation_function': adjacency_calculations_pool},
                    title="Adjacency",
                    parent=self.vertical_tab
                )
                self.vertical_tab.addTab(self.adj_tab, "Adjacency")
            else:
                if isinstance(hypergraph, Hypergraph):
                    self.adj_tab.update_hypergraph(self.hypergraph)
                    self.adj_tab.setVisible(True)
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.adj_tab), True)
                else:
                    self.adj_tab.setVisible(False)
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.motifs_tab), False)

        if hypergraph.is_weighted():
            if self.weight_tab is None:
                self.weight_tab = GenericGraphWidget(
                    hypergraph=hypergraph,
                    drawing_function=draw_weight,
                    drawing_params={'axes': (1, 1), 'calculation_function': calculate_weight_distribution},
                    title="Weight",
                    parent=self.vertical_tab
                )
                self.vertical_tab.addTab(self.weight_tab, "Weights")
            else:
                if self.hypergraph.is_weighted():
                    self.weight_tab.update_hypergraph(self.hypergraph)
                    self.weight_tab.setVisible(True)
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.weight_tab), True)
                else:
                    self.weight_tab.setVisible(False)
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.weight_tab), False)
        self.centrality_tab.update_hypergraph(self.hypergraph)
        self.degree_tab.update_hypergraph(self.hypergraph)
        self.vertical_tab.setCurrentIndex(0)
        gc.collect()

class GenericGraphWidget(QWidget):
    def __init__(self, hypergraph, drawing_function, drawing_params, title, parent=None):
        super(GenericGraphWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.drawing_function = drawing_function
        self.drawing_params = drawing_params
        self.title = title
        self.figure = Figure()
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.canvas, self.toolbar = create_canvas_with_toolbar(self.figure)
        self.toolbar.setParent(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, data):
        self.figure.clf()
        if isinstance(self.drawing_params['axes'], tuple):
            self.axes = self.figure.subplots(*self.drawing_params['axes'])
        else:
            self.axes = self.figure.subplots(1, 1)
        if not self.drawing_function == plot_motifs:
            self.drawing_function(self.axes, data, **self.drawing_params.get('extra_params', {}))
        else:
            plot_motifs(data, None, self.axes)
        self.figure.subplots_adjust(wspace=self.drawing_params.get('wspace', 0.5), hspace=self.drawing_params.get('hspace', 0.5))
        self.canvas.draw()
        self.loading_container.setVisible(False)
        self.canvas.setVisible(True)
        self.toolbar.setVisible(True)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.canvas.setVisible(False)
        self.toolbar.setVisible(False)
        self.loading_container.setVisible(True)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, self.drawing_params['calculation_function'])
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

class MotifsWidget(QWidget):

    def __init__(self, hypergraph, parent=None):
        super().__init__(parent)
        self.hypergraph = hypergraph
        self.button = QPushButton("Calculate Motifs")
        self.button.clicked.connect(self.calculate_motifs)
        self.figure = Figure()
        self.layout = QVBoxLayout()
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.canvas, self.toolbar = create_canvas_with_toolbar(self.figure)
        self.toolbar.setParent(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.toolbar.setVisible(False)
        self.canvas.setVisible(False)
        self.loading_container.setVisible(False)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.drawing_function = plot_motifs
        self.drawing_params = {'axes': (1, 1), 'calculation_function': motifs_calculations}
        self.title = "Motifs"
        self.axes = None
        self.thread = None

    def draw_graph(self, data):
        self.figure.clf()
        if isinstance(self.drawing_params['axes'], tuple):
            self.axes = self.figure.subplots(*self.drawing_params['axes'])
        else:
            self.axes = self.figure.subplots(1, 1)
        if not self.drawing_function == plot_motifs:
            self.drawing_function(self.axes, data, **self.drawing_params.get('extra_params', {}))
        else:
            plot_motifs(data, None, self.axes)
        self.figure.subplots_adjust(wspace=self.drawing_params.get('wspace', 0.5),
                                    hspace=self.drawing_params.get('hspace', 0.5))
        self.canvas.draw()
        self.loading_container.setVisible(False)
        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.setLayout(self.layout)
        self.update()

    def calculate_motifs(self):
        self.button.setVisible(False)
        self.loading_container.setVisible(True)
        self.thread = StatsWorker(self.hypergraph, self.drawing_params['calculation_function'])
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

    def update_hypergraph(self, hypergraph):
        self.loading_container.setVisible(False)
        self.button.setVisible(True)
        self.toolbar.setVisible(False)
        self.canvas.setVisible(False)
        self.hypergraph = hypergraph

#Support
def generate_key(dictionary):
    keys_label = []
    keys = []
    idx = 1
    for edge in dictionary.keys():
        keys.append(idx)
        idx += 1
        keys_label.append(str(edge))
    return keys_label, keys