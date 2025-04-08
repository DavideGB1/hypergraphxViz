from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QProgressBar, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pyqt_vertical_tab_widget import VerticalTabWidget
from qtpy import QtCore

from hypergraphx import Hypergraph, TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness, s_closeness, s_betweenness_nodes, s_closeness_nodes, \
    s_betweenness_nodes_averaged, s_closenness_nodes_averaged, s_betweenness_averaged, s_closeness_averaged
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.interactive_view.custom_widgets import LoadingScreen
from hypergraphx.viz.interactive_view.pool_singleton import PoolSingleton
from hypergraphx.viz.interactive_view.support import clear_layout
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

class GenericGraphWidget(QWidget):
    def __init__(self, hypergraph, drawing_function, drawing_params, title, parent=None):
        super(GenericGraphWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.drawing_function = drawing_function
        self.drawing_params = drawing_params
        self.title = title
        self.figure = None
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.update_hypergraph()

    def draw_graph(self, data):
        clear_layout(self.layout)
        self.figure = Figure()
        if isinstance(self.drawing_params['axes'], tuple):
            self.axes = self.figure.subplots(*self.drawing_params['axes'])
        else:
            self.axes = self.figure.subplots(1, 1)
        if not self.drawing_function == plot_motifs:
            self.drawing_function(self.axes, data, **self.drawing_params.get('extra_params', {}))
        else:
            plot_motifs(data, None, self.axes)
        self.figure.subplots_adjust(wspace=self.drawing_params.get('wspace', 0.5), hspace=self.drawing_params.get('hspace', 0.5))

        canvas = FigureCanvas(self.figure)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        toolbar = NavigationToolbar(canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(canvas)
        self.setLayout(self.layout)
        self.update()

    def update_hypergraph(self):
        clear_layout(self.layout)
        self.layout.addWidget(LoadingScreen())
        self.setLayout(self.layout)
        self.thread = StatsWorker(self.hypergraph, self.drawing_params['calculation_function'])
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

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
        res = PoolSingleton().get_pool().apply(self.function, args=(self.hypergraph, ))
        self.progress.emit(res)

class HypergraphStatsWidget(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, hypergraph):
        super(HypergraphStatsWidget, self).__init__()
        self.hypergraph = None
        self.vertical_tab = VerticalTabWidget()
        self.update_hypergraph(hypergraph)


    def update_hypergraph(self, hypergraph):
        self.hypergraph = hypergraph
        self.vertical_tab = VerticalTabWidget()
        self.hypergraph = hypergraph

        centrality_tab = GenericGraphWidget(
            hypergraph=hypergraph,
            drawing_function=draw_centrality,
            drawing_params={'axes': (2, 2), 'calculation_function': calculate_centrality_pool, 'wspace': 2,
                            'hspace': 2},
            title="Centrality"
        )

        degree_tab = GenericGraphWidget(
            hypergraph=hypergraph,
            drawing_function=draw_degree,
            drawing_params={'axes': (2, 1), 'calculation_function': degree_calculations},
            title="Degree"
        )


        self.vertical_tab.addTab(degree_tab, "Degree")
        self.vertical_tab.addTab(centrality_tab, "Centrality")
        if isinstance(hypergraph, Hypergraph):
            motifs_tab = GenericGraphWidget(
                hypergraph=hypergraph,
                drawing_function=plot_motifs,
                drawing_params={'axes': (1, 1), 'calculation_function': motifs_calculations},
                title="Motifs"
            )
            self.vertical_tab.addTab(motifs_tab, "Motifs")
        if isinstance(hypergraph, Hypergraph):
            adj_tab = GenericGraphWidget(
                hypergraph=hypergraph,
                drawing_function=draw_adjacency,
                drawing_params={'axes': (2, 1), 'calculation_function': adjacency_calculations_pool},
                title="Adjacency"
            )
            self.vertical_tab.addTab(adj_tab, "Adjacency")
        if self.hypergraph.is_weighted():
            weight_tab = GenericGraphWidget(
                hypergraph=hypergraph,
                drawing_function=draw_weight,
                drawing_params={'axes': (1, 1), 'calculation_function': calculate_weight_distribution},
                title="Weight"
            )
            self.vertical_tab.addTab(weight_tab, "Weights")

        self.setCentralWidget(self.vertical_tab)

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