from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QProgressBar, QLabel, QLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pyqt_vertical_tab_widget import VerticalTabWidget
from qtpy import QtCore
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from hypergraphx import Hypergraph, TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness, s_closeness, s_betweenness_nodes, s_closeness_nodes, \
    s_betweenness_nodes_averaged, s_closenness_nodes_averaged, s_betweenness_averaged, s_closeness_averaged
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.interactive_view.support import clear_layout
from hypergraphx.viz.plot_motifs import plot_motifs


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
        degree_tab = self.degree_widget()
        centrality_tab = self.centrality_widget()
        self.vertical_tab.addTab(degree_tab, "Degree")
        self.vertical_tab.addTab(centrality_tab, "Centrality")
        if isinstance(hypergraph, Hypergraph):
            self.motifs_tab = MotifsWidget(self.hypergraph)
            self.vertical_tab.addTab(self.motifs_tab, "Motifs")
        if isinstance(hypergraph, Hypergraph):
            adj_factor_widgtet = self.adjacency_widget()
            self.vertical_tab.addTab(adj_factor_widgtet, "Adjacency")
        if self.hypergraph.is_weighted():
            weight_tab = self.weight_widget()
            self.vertical_tab.addTab(weight_tab, "Weights")

        self.setCentralWidget(self.vertical_tab)

    def __create_widgets(self,figure):
        canvas = FigureCanvas(figure)
        layout = QVBoxLayout()
        toolbar = NavigationToolbar(canvas, self)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def __create_bar_chart(self,ax, data, x_label, y_label, title, y_ticks_increment=1):
        ax.bar(data.keys(), data.values())
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.set_xticks(list(data.keys()))
        max_value = max(data.values())
        ax.set_yticks(range(1, max_value + y_ticks_increment))
        ax.set_ylim(0, max_value + y_ticks_increment)

    def weight_widget(self):
        """
        Generates and displays a weight distribution bar chart widget.

        This function processes the weights of a hypergraph, calculates their distribution,
        and displays the results as a bar chart. The widgets created from this process
        are returned to be incorporated into a graphical user interface.

        Parameters
        ----------
        self : object
            The current instance of the class, which should contain a `hypergraph` attribute with
            a `get_weights()` method to retrieve the list of weights.

        Returns
        -------
        object
            A widget object displaying a bar chart of the weight distribution, generated from the
            processed data.
        """
        def calculate_weight_distribution(weights):
            weight_distribution = {}
            value_list = []
            for weight in weights:
                if weight not in weight_distribution:
                    weight_distribution[weight] = 0
                    value_list.append(len(value_list))
                weight_distribution[weight] += 1
            return weight_distribution, value_list

        # Extracting weights and calculating distribution
        weights = self.hypergraph.get_weights()
        weight_distribution, value_list = calculate_weight_distribution(weights)

        # Creating the plot
        fig = Figure()
        ax = fig.subplots(1)
        ax.bar(value_list, weight_distribution.values())
        ax.set_xlabel('Weights')
        ax.set_title('Weights Distribution')
        ax.set_xticks(value_list, list(weight_distribution.keys()))
        ax.set_ylim(0, max(weight_distribution.values()) + 1)
        ax.set_yticks(range(1, max(weight_distribution.values()) + 1))
        fig.subplots_adjust(wspace=1, hspace=1)

        return self.__create_widgets(fig)

    def degree_widget(self):
        """
        Generates degree and size distribution widgets for the hypergraph.

        This method creates a widget displaying two bar charts:
        1. Degree Distribution: Represents the distribution of degrees in the hypergraph.
        2. Size Distribution: Represents the distribution of edge sizes in the hypergraph.

        The method processes the degree distribution of the hypergraph using the degree_distribution function
        and generates corresponding bar charts. Additionally, it calculates the count of edges based on their
        size and plots this data in a second bar chart.

        Returns
        -------
        Widget
            A widget displaying the generated bar charts.

        """
        figure = Figure()
        axes = figure.subplots(2)
        degree_distribution = self.hypergraph.degree_distribution()
        self.__create_bar_chart(ax=axes[0], data = degree_distribution, x_label="Degrees", y_label = "Values",
                                title = "Degree Distribution", y_ticks_increment=2)
        sizes = dict()
        for edge in self.hypergraph.get_edges():
            if len(edge) not in sizes.keys():
                sizes[len(edge)] = 0
            sizes[len(edge)] += 1

        self.__create_bar_chart(ax=axes[1], data = sizes, x_label="Degrees", y_label = "Values",
                                title = "Size Distribution", y_ticks_increment=2)

        figure.subplots_adjust(wspace=1, hspace=0.5)

        return self.__create_widgets(figure)

    def centrality_widget(self):
        figure = Figure()
        axes = figure.subplots(2,2)
        figure.subplots_adjust(wspace=0.5, hspace=0.5)
        if isinstance(self.hypergraph, TemporalHypergraph):
            edge_s_betweenness = s_betweenness_averaged(self.hypergraph)
        else:
            edge_s_betweenness = s_betweenness(self.hypergraph)

        keys_label = []
        keys = []
        idx = 1
        for edge in edge_s_betweenness.keys():
            keys.append(idx)
            idx += 1
            keys_label.append(str(edge))
        axes[0, 0].bar(keys, edge_s_betweenness.values())
        axes[0, 0].set_xlabel('Edges')
        axes[0, 0].set_title('Edges Betweenness Centrality')
        axes[0, 0].set_xticks(keys, keys_label)


        if isinstance(self.hypergraph, TemporalHypergraph):
            edge_s_closeness = s_closeness_averaged(self.hypergraph)
        else:
            edge_s_closeness = s_closeness(self.hypergraph)
        keys_label = []
        keys = []
        idx = 1
        for edge in edge_s_closeness.keys():
            keys.append(idx)
            idx += 1
            keys_label.append(str(edge))
        axes[0, 1].bar(keys, edge_s_closeness.values())
        axes[0, 1].set_xlabel('Edges')
        axes[0, 1].set_title('Edges Closeness Centrality')
        axes[0, 1].set_xticks(keys, keys_label)

        if isinstance(self.hypergraph, TemporalHypergraph):
            node_s_betweenness = s_betweenness_nodes_averaged(self.hypergraph)
        else:
            node_s_betweenness = s_betweenness_nodes(self.hypergraph)
        keys_label = []
        keys = []
        idx = 1
        for edge in node_s_betweenness.keys():
            keys.append(idx)
            idx += 1
            keys_label.append(str(edge))
        axes[1, 0].bar(keys, node_s_betweenness.values())
        axes[1, 0].set_xlabel('Nodes')
        axes[1, 0].set_title('Nodes Betweenness Centrality')
        axes[1, 0].set_xticks(keys, keys_label)

        if isinstance(self.hypergraph, TemporalHypergraph):
            node_s_closeness = s_closenness_nodes_averaged(self.hypergraph)
        else:
            node_s_closeness = s_closeness_nodes(self.hypergraph)
        keys_label = []
        keys = []
        idx = 1
        for edge in node_s_closeness.keys():
            keys.append(idx)
            idx += 1
            keys_label.append(str(edge))
        axes[1, 1].bar(keys, node_s_closeness.values())
        axes[1, 1].set_xlabel('Nodes')
        axes[1, 1].set_title('Nodes Closeness Centrality')
        axes[1, 1].set_xticks(keys, keys_label)

        return self.__create_widgets(figure)

    def adjacency_widget(self):
        figure = Figure()
        axes = figure.subplots(1,2)
        adj_factor_t0 = self.hypergraph.adjacency_factor(0)
        keys_label = []
        keys = []
        idx = 1
        for edge in adj_factor_t0.keys():
            keys.append(idx)
            idx += 1
            keys_label.append(str(edge))
        axes[0].bar(keys, adj_factor_t0.values())
        axes[0].set_xlabel('Nodes')
        axes[0].set_title('Adjacency Factor (t=0)')
        axes[0].set_xticks(keys, keys_label)

        adj_factor_t1 = self.hypergraph.adjacency_factor(t=1)
        keys_label = []
        keys = []
        idx = 1
        for edge in adj_factor_t1.keys():
            keys.append(idx)
            idx += 1
            keys_label.append(str(edge))
        axes[1].bar(keys, adj_factor_t1.values())
        axes[1].set_xlabel('Nodes')
        axes[1].set_title('Adjacency Factor (t=1)')
        axes[1].set_xticks(keys, keys_label)

        return self.__create_widgets(figure)

class MotifsWorker(QtCore.QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, parent=None):
        super(MotifsWorker, self).__init__(parent)
        self.hypergraph = hypergraph
    def run(self):
        motifs_3 = compute_motifs(self.hypergraph, order = 3)
        motifs3_profile = [i[1] for i in motifs_3['norm_delta']]
        self.progress.emit(motifs3_profile)

class MotifsWidget(QWidget):
    def __init__(self, hypergraph,parent=None):
        super(MotifsWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.update_hypergraph(hypergraph)
    def draw_motifs(self, list):
        clear_layout(self.layout)
        plot_motifs(list,save_name = None,ax = self.ax)
        canvas = FigureCanvas(self.figure)
        self.ax.set_title('Motifs')
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
        self.ax = self.figure.subplots(1,1)
        self.hypergraph = hypergraph
        self.thread = MotifsWorker(self.hypergraph)
        self.thread.progress.connect(self.draw_motifs)
        self.thread.start()