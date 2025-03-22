from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pyqt_vertical_tab_widget import VerticalTabWidget

from hypergraphx.measures.s_centralities import s_betweenness, s_closeness
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.plot_motifs import plot_motifs


class HypergraphStatsWidget(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, hypergraph):
        super(HypergraphStatsWidget, self).__init__()
        self.vertical_tab = VerticalTabWidget()
        self.hypergraph = hypergraph
        degree_tab = self.degree_widget()
        centrality_tab = self.centrality_widget()
        motifs_tab = self.motifs_widget()
        self.vertical_tab.addTab(degree_tab, "Degree")
        self.vertical_tab.addTab(centrality_tab, "Centrality")
        self.vertical_tab.addTab(motifs_tab, "Motifs")
        self.setCentralWidget(self.vertical_tab)
    def update_hypergraph(self, hypergraph):
        self.hypergraph = hypergraph
        self.vertical_tab = VerticalTabWidget()
        self.hypergraph = hypergraph
        degree_tab = self.degree_widget()
        centrality_tab = self.centrality_widget()
        motifs_tab = self.motifs_widget()
        self.vertical_tab.addTab(degree_tab, "Degree")
        self.vertical_tab.addTab(centrality_tab, "Centrality")
        self.vertical_tab.addTab(motifs_tab, "Motifs")
        self.setCentralWidget(self.vertical_tab)
    def __create_widgets(self,figure):
        canvas = FigureCanvas(figure)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def degree_widget(self):
        figure = Figure()
        axes = figure.subplots(2)
        degree_distribution = self.hypergraph.degree_distribution()
        axes[0].bar(degree_distribution.keys(), degree_distribution.values())
        axes[0].set_xlabel('Degrees')
        axes[0].set_ylabel('Values')
        axes[0].set_title('Degree Distribution')
        axes[0].set_xticks(list(degree_distribution.keys()))
        axes[0].set_ylim(0, max(degree_distribution.values()) + 1)
        axes[0].set_yticks(range(1, max(degree_distribution.values()) + 1))

        sizes = dict()
        for edge in self.hypergraph.get_edges():
            if len(edge) not in sizes.keys():
                sizes[len(edge)] = 0
            sizes[len(edge)] += 1
        axes[1].bar(sizes.keys(), sizes.values())
        axes[1].set_xlabel('Degrees')
        axes[1].set_ylabel('Values')
        axes[1].set_title('Size Distribution')
        axes[1].set_xticks(list(sizes.keys()))
        axes[1].set_yticks(range(1, max(sizes.values()) + 1))
        figure.subplots_adjust(wspace=1, hspace=1)

        return self.__create_widgets(figure)

    def centrality_widget(self):
        figure = Figure()
        axes = figure.subplots(2,2)
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

        return self.__create_widgets(figure)

    def motifs_widget(self):
        figure = Figure()
        ax = figure.subplots(1,1)
        motifs_3 = compute_motifs(self.hypergraph, order = 3)
        motifs3_profile = [i[1] for i in motifs_3['norm_delta']]
        plot_motifs(motifs3_profile,save_name = None,ax = ax)

        return self.__create_widgets(figure)

    '''
    Degree:
        !Distribution
        !Size Distribution
    Centrality:
        !Edge Betweenness Centrality
        !Edges Closeness Centrality
        Node Betweenness Centrality
        Node Closeness Centrality
        Adjacency Factor
    Motifs:
        Motif 3
        Motif 4
    '''