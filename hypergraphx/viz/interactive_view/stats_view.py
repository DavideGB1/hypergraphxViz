import multiprocessing
import pickle

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QProgressBar, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pyqt_vertical_tab_widget import VerticalTabWidget
from qtpy import QtCore

from hypergraphx import Hypergraph, TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness, s_closeness, s_betweenness_nodes, s_closeness_nodes, \
    s_betweenness_nodes_averaged, s_closenness_nodes_averaged, s_betweenness_averaged, s_closeness_averaged
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.interactive_view import pool_singleton
from hypergraphx.viz.interactive_view.pool_singleton import PoolSingleton
from hypergraphx.viz.interactive_view.support import clear_layout
from hypergraphx.viz.plot_motifs import plot_motifs


def draw_bar(ax, values, label, title):
    ax.bar(values[2], values[0].values())
    ax.set_xlabel(label)
    ax.set_title(title)
    ax.set_xticks(values[2], values[1])

def generate_key(dictionary):
    keys_label = []
    keys = []
    idx = 1
    for edge in dictionary.keys():
        keys.append(idx)
        idx += 1
        keys_label.append(str(edge))
    return keys_label, keys

class HypergraphStatsWidget(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, hypergraph):
        super(HypergraphStatsWidget, self).__init__()
        self.vertical_tab = VerticalTabWidget()
        self.hypergraph = hypergraph
        self.update_hypergraph(self.hypergraph)

    def update_hypergraph(self, hypergraph):
        self.hypergraph = hypergraph
        self.vertical_tab = VerticalTabWidget()
        self.hypergraph = hypergraph
        degree_tab = DegreeWidget(self.hypergraph)
        centrality_tab = CentralityWidget(self.hypergraph)
        self.vertical_tab.addTab(degree_tab, "Degree")
        self.vertical_tab.addTab(centrality_tab, "Centrality")
        if isinstance(hypergraph, Hypergraph):
            motifs_tab = MotifsWidget(self.hypergraph)
            self.vertical_tab.addTab(motifs_tab, "Motifs")
        if isinstance(hypergraph, Hypergraph):
            adj_factor_widgtet = AdjWidget(self.hypergraph)
            self.vertical_tab.addTab(adj_factor_widgtet, "Adjacency")
        if self.hypergraph.is_weighted():
            weight_tab = WeightWidget(self.hypergraph)
            self.vertical_tab.addTab(weight_tab, "Weights")

        self.setCentralWidget(self.vertical_tab)

# Motifs
def motifs_calculations(hypergraph):
    motifs_3 = compute_motifs(hypergraph, order=3)
    motifs3_profile = [i[1] for i in motifs_3['norm_delta']]
    return motifs3_profile # Restituisce i risultati

class MotifsWorker(QtCore.QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, pool, parent=None): # Aggiungi pool
        super(MotifsWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.pool = pool
    def run(self):
        motifs3_profile = self.pool.apply(motifs_calculations, args=(self.hypergraph,)) # Usa apply
        self.progress.emit(motifs3_profile)

class MotifsWidget(QWidget):
    def __init__(self, hypergraph,parent=None):
        super(MotifsWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.figure = None
        self.ax = None
        self.thread = None
        self.update_hypergraph(hypergraph)
        self.pool_singleton = PoolSingleton() # Istanza del singleton

    def draw_motifs(self, list):
        clear_layout(self.layout)
        plot_motifs(list, save_name=None, ax=self.ax)
        canvas = FigureCanvas(self.figure)
        self.ax.set_title('Motifs')
        toolbar = NavigationToolbar(canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(canvas)
        self.setLayout(self.layout)
        self.update()

    def update_hypergraph(self, hypergraph):
        clear_layout(self.layout)
        label = QLabel("Waiting...")
        self.layout.addWidget(label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 10)
        self.layout.addWidget(self.progress_bar)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.figure = Figure()
        self.ax = self.figure.subplots(1, 1)
        self.hypergraph = hypergraph
        pool = PoolSingleton()
        self.thread = MotifsWorker(self.hypergraph, pool.get_pool())
        self.thread.progress.connect(self.draw_motifs)
        self.thread.start()


def adjacency_calculations_part(hypergraph, t):
    adj_factor = hypergraph.adjacency_factor(t)
    adj_factor_keys_label, adj_factor_label = generate_key(adj_factor)
    return adj_factor, adj_factor_keys_label, adj_factor_label

def adjacency_calculations_pool(hypergraph, pool):
    results = pool.starmap(adjacency_calculations_part, [(hypergraph, t) for t in [0, 1]])
    return results

class AdjWorker(QtCore.QThread):
    progress = pyqtSignal(list)

    def __init__(self, hypergraph, pool, parent=None):
        super(AdjWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.pool = pool

    def run(self):
        results = adjacency_calculations_pool(self.hypergraph, self.pool)
        self.progress.emit(results)

class AdjWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(AdjWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.progress_bar = None
        self.figure = None
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.update_hypergraph()

    def draw_adj(self, list):
        clear_layout(self.layout)
        canvas = FigureCanvas(self.figure)

        draw_bar(
            ax=self.axes[0],
            values=list[0],
            label="Nodes",
            title="Adjacency Factor (t=0)"
        )

        draw_bar(
            ax=self.axes[1],
            values=list[1],
            label="Nodes",
            title="Adjacency Factor (t=1)"
        )

        toolbar = NavigationToolbar(canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(canvas)
        self.setLayout(self.layout)
        self.update()

    def update_hypergraph(self):
        clear_layout(self.layout)
        label = QLabel("Waiting...")
        self.layout.addWidget(label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 10)
        self.layout.addWidget(self.progress_bar)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.figure = Figure()
        self.figure.subplots(2, 1)
        self.axes = self.figure.subplots(2, 1)
        pool = PoolSingleton()
        self.thread = AdjWorker(self.hypergraph, pool.get_pool()) # Usa il pool del singleton
        self.thread.progress.connect(self.draw_adj)
        self.thread.start()

def calculate_centrality_part(hypergraph, function):
    result = function(hypergraph)
    keys_label, keys = generate_key(result)
    return result, keys_label, keys

def calculate_centrality_pool(hypergraph, pool):
    functions = [
        s_betweenness_averaged if isinstance(hypergraph, TemporalHypergraph) else s_betweenness,
        s_closeness_averaged if isinstance(hypergraph, TemporalHypergraph) else s_closeness,
        s_betweenness_nodes_averaged if isinstance(hypergraph, TemporalHypergraph) else s_betweenness_nodes,
        s_closenness_nodes_averaged if isinstance(hypergraph, TemporalHypergraph) else s_closeness_nodes,
    ]

    results = pool.starmap(calculate_centrality_part, [(hypergraph, func) for func in functions])
    return results

class CentralityWorkerPool(QtCore.QThread):
    progress = pyqtSignal(list)

    def __init__(self, hypergraph, pool, parent=None):
        super(CentralityWorkerPool, self).__init__(parent)
        self.hypergraph = hypergraph
        self.pool = pool

    def run(self):
        results = calculate_centrality_pool(self.hypergraph, self.pool)
        self.progress.emit(results)

class CentralityWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(CentralityWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.progress_bar = None
        self.figure = None
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.update_hypergraph()

    def draw_adj(self, values_list):
        clear_layout(self.layout)
        self.figure = Figure()
        self.axes = self.figure.subplots(2, 2)
        self.figure.subplots_adjust(wspace=2, hspace=2)
        canvas = FigureCanvas(self.figure)

        draw_bar(
            ax=self.axes[0, 0],
            values=values_list[0],
            label='Edges',
            title='Edges Betweenness Centrality')

        draw_bar(
            ax=self.axes[0, 1],
            values=values_list[1],
            label='Edges',
            title='Edges Closeness Centrality')

        draw_bar(
            ax=self.axes[1, 0],
            values=values_list[2],
            label='Nodes',
            title='Nodes Betweenness Centrality')

        draw_bar(
            ax=self.axes[1, 1],
            values=values_list[3],
            label='Nodes',
            title='Nodes Closeness Centrality')

        toolbar = NavigationToolbar(canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(canvas)
        self.setLayout(self.layout)
        self.update()

    def update_hypergraph(self):
        clear_layout(self.layout)
        label = QLabel("Waiting...")
        self.layout.addWidget(label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 10)
        self.layout.addWidget(self.progress_bar)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.figure = Figure()
        self.figure.subplots_adjust(wspace=0.5, hspace=1)
        self.axes = self.figure.subplots(2, 1)
        pool = PoolSingleton()
        self.thread = CentralityWorkerPool(self.hypergraph, pool.get_pool())
        self.thread.progress.connect(self.draw_adj)
        self.thread.start()

# Degree
def degree_calculations(hypergraph):
    degree_distribution = hypergraph.degree_distribution()
    sizes = dict()
    for edge in hypergraph.get_edges():
        if len(edge) not in sizes.keys():
            sizes[len(edge)] = 0
        sizes[len(edge)] += 1
    return [degree_distribution, sizes] # Restituisce i risultati

class DegreeWorker(QtCore.QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, pool, parent=None): # Aggiungi pool
        super(DegreeWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.pool = pool
    def run(self):
        results = self.pool.apply(degree_calculations, args=(self.hypergraph,)) # Usa apply
        self.progress.emit(results)

class DegreeWidget(QWidget):
    def __init__(self, hypergraph,parent=None):
        super(DegreeWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.progress_bar = None
        self.figure = None
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.update_hypergraph()
        self.pool_singleton = PoolSingleton() # Istanza del singleton

    def draw_adj(self, value_list):
        clear_layout(self.layout)
        self.figure = Figure()
        self.axes = self.figure.subplots(2, 1)
        self.figure.subplots_adjust(wspace=1, hspace=0.5)
        canvas = FigureCanvas(self.figure)

        def __create_bar_chart(ax, data, x_label, y_label, title, y_ticks_increment=1):
            ax.bar(data.keys(), data.values())
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.set_xticks(list(data.keys()))
            max_value = max(data.values())
            ax.set_yticks(range(1, max_value + y_ticks_increment))
            ax.set_ylim(0, max_value + y_ticks_increment)

        __create_bar_chart(ax=self.axes[0], data=value_list[0], x_label="Degrees", y_label = "Values", title="Degree Distribution")
        __create_bar_chart(ax=self.axes[1], data=value_list[1], x_label="Sizes", y_label = "Values", title="Size Distribution")

        toolbar = NavigationToolbar(canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(canvas)
        self.setLayout(self.layout)
        self.update()

    def update_hypergraph(self):
        clear_layout(self.layout)
        label = QLabel("Waiting...")
        self.layout.addWidget(label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 10)
        self.layout.addWidget(self.progress_bar)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.figure = Figure()
        self.figure.subplots_adjust(wspace=0.5, hspace=1)
        self.axes = self.figure.subplots(2,1)
        pool = PoolSingleton()
        self.thread = DegreeWorker(self.hypergraph, pool.get_pool())
        self.thread.progress.connect(self.draw_adj)
        self.thread.start()

# Weight
def calculate_weight_distribution(hypergraph):
    weight_distribution = {}
    value_list = []
    for weight in hypergraph.get_weights():
        if weight not in weight_distribution:
            weight_distribution[weight] = 0
            value_list.append(len(value_list))
        weight_distribution[weight] += 1
    return [weight_distribution, value_list] # Restituisce i risultati

class WeightWorker(QtCore.QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, pool, parent=None): # Aggiungi pool
        super(WeightWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.pool = pool
    def run(self):
        results = self.pool.apply(calculate_weight_distribution, args=(self.hypergraph,)) # Usa apply
        self.progress.emit([results])

class WeightWidget(QWidget):
    def __init__(self, hypergraph,parent=None):
        super(WeightWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.progress_bar = None
        self.figure = None
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.update_hypergraph()
        self.pool_singleton = PoolSingleton() # Istanza del singleton

    def draw_adj(self, value_list):
        clear_layout(self.layout)
        self.figure = Figure()
        self.axes = self.figure.subplots(1, 1)
        self.figure.subplots_adjust(wspace=1, hspace=0.5)
        canvas = FigureCanvas(self.figure)

        self.axes.bar(value_list[0][1], value_list[0][0].values())
        self.axes.set_xlabel('Weights')
        self.axes.set_title('Weights Distribution')
        self.axes.set_xticks(value_list[0][1], list(value_list[0][0].keys()))
        self.axes.set_ylim(0, max(value_list[0][0].values()) + 1)
        self.axes.set_yticks(range(1, max(value_list[0][0].values()) + 1))

        toolbar = NavigationToolbar(canvas, self)
        self.layout.addWidget(toolbar)
        self.layout.addWidget(canvas)
        self.setLayout(self.layout)
        self.update()

    def update_hypergraph(self):
        clear_layout(self.layout)
        label = QLabel("Waiting...")
        self.layout.addWidget(label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 10)
        self.layout.addWidget(self.progress_bar)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        self.figure = Figure()
        self.figure.subplots_adjust(wspace=0.5, hspace=1)
        self.axes = self.figure.subplots(2,1)
        pool = PoolSingleton()
        self.thread = WeightWorker(self.hypergraph, pool.get_pool())
        self.thread.progress.connect(self.draw_adj)
        self.thread.start()
