import gc

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QTabWidget

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.measures.node_similarity import jaccard_similarity_matrix
from hypergraphx.viz.interactive_view.stats_view.stats_calculations import calculate_weight_distribution, draw_weight, \
    adjacency_calculations_pool, draw_adjacency, degree_calculations, calculate_centrality_pool, draw_centrality, \
    draw_degree, draw_similarity
from hypergraphx.viz.interactive_view.stats_view.stats_widgets import GenericGraphWidget, MotifsWidget, CentralityWidget


class HypergraphStatsWidget(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(HypergraphStatsWidget, self).__init__(parent)
        self.controller = controller
        self.controller.updated_hypergraph.connect(self.update_hypergraph)
        self.centrality_tab = None
        self.degree_tab = None
        self.motifs_tab = None
        self.adj_tab = None
        self.weight_tab = None
        self.vertical_tab = QTabWidget(parent=self)
        self.vertical_tab.setTabPosition(QTabWidget.West)
        self.vertical_tab.setObjectName("StatsTab")

        self.vertical_tab.clear()
        self.centrality_tab = CentralityWidget(
            hypergraph=self.controller.get_hypergraph(),
            parent=self.vertical_tab
        )
        self.degree_tab = GenericGraphWidget(
            hypergraph=self.controller.get_hypergraph(),
            drawing_function=draw_degree,
            drawing_params={'axes': (1, 2), 'calculation_function': degree_calculations},
            title="Degree",
            parent=self.vertical_tab
        )
        self.node_similarity_tab = GenericGraphWidget(
            hypergraph=self.controller.get_hypergraph(),
            drawing_function=draw_similarity,
            drawing_params={'axes': 1, 'calculation_function': jaccard_similarity_matrix},
            title="Degree",
            parent=self.vertical_tab
        )
        self.vertical_tab.addTab(self.degree_tab, "Degree")
        self.vertical_tab.addTab(self.centrality_tab, "Centrality")
        self.vertical_tab.addTab(self.node_similarity_tab, "Similarity")
        if isinstance(self.controller.get_hypergraph(), Hypergraph):
            self.motifs_tab = MotifsWidget(self.controller.get_hypergraph(), parent=self.vertical_tab)
            self.vertical_tab.addTab(self.motifs_tab, "Motifs")
        if isinstance(self.controller.get_hypergraph(), Hypergraph):
            self.adj_tab = GenericGraphWidget(
                hypergraph=self.controller.get_hypergraph(),
                drawing_function=draw_adjacency,
                drawing_params={'axes': (2, 2), 'calculation_function': adjacency_calculations_pool, 'layout': '2_plus_1'},
                title="Adjacency",
                parent=self.vertical_tab
            )
            self.vertical_tab.addTab(self.adj_tab, "Adjacency")
        if self.controller.get_hypergraph().is_weighted():
            self.weight_tab = GenericGraphWidget(
                hypergraph=self.controller.get_hypergraph(),
                drawing_function=draw_weight,
                drawing_params={'axes': (1, 1), 'calculation_function': calculate_weight_distribution},
                title="Weight",
                parent=self.vertical_tab
            )
            self.vertical_tab.addTab(self.weight_tab, "Weights")
        gc.collect()
        self.setCentralWidget(self.vertical_tab)
    def update_hypergraph(self):
        if isinstance(self.controller.get_hypergraph(), Hypergraph):
            if self.motifs_tab is None:
                self.motifs_tab = MotifsWidget(self.controller.get_hypergraph(), parent=self.vertical_tab)
                self.vertical_tab.addTab(self.motifs_tab, "Motifs")
            else:
                self.motifs_tab.update_hypergraph(self.controller.get_hypergraph())
        else:
            if self.motifs_tab is not None:
                self.vertical_tab.removeTab(self.vertical_tab.indexOf(self.motifs_tab))
                self.motifs_tab.deleteLater()
                self.motifs_tab = None

        if not isinstance(self.controller.get_hypergraph(), DirectedHypergraph):
            if self.adj_tab is None:
                self.adj_tab = GenericGraphWidget(
                    hypergraph=self.controller.get_hypergraph(),
                    drawing_function=draw_adjacency,
                    drawing_params={'axes': (2, 2), 'calculation_function': adjacency_calculations_pool,
                                    'layout': '2_plus_1'},
                    title="Adjacency",
                    parent=self.vertical_tab
                )
                self.vertical_tab.addTab(self.adj_tab, "Adjacency")
            else:
                self.adj_tab.update_hypergraph(self.controller.get_hypergraph())
        else:
            if self.adj_tab is not None:
                self.vertical_tab.removeTab(self.vertical_tab.indexOf(self.motifs_tab))
                self.adj_tab.deleteLater()
                self.adj_tab = None

        if self.controller.get_hypergraph().is_weighted():
            if self.weight_tab is None:
                self.weight_tab = GenericGraphWidget(
                    hypergraph=self.controller.get_hypergraph(),
                    drawing_function=draw_weight,
                    drawing_params={'axes': (1, 2), 'calculation_function': calculate_weight_distribution},
                    title="Weight",
                    parent=self.vertical_tab
                )
                self.vertical_tab.addTab(self.weight_tab, "Weights")
            else:
                self.weight_tab.update_hypergraph(self.controller.get_hypergraph())
                self.weight_tab.setVisible(True)
                self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.weight_tab), True)
        else:
            if self.weight_tab is not None:
                self.vertical_tab.removeTab(self.vertical_tab.indexOf(self.weight_tab))
                self.weight_tab.deleteLater()
                self.weight_tab = None

        self.centrality_tab.update_hypergraph(self.controller.get_hypergraph())
        self.degree_tab.update_hypergraph(self.controller.get_hypergraph())
        self.node_similarity_tab.update_hypergraph(self.controller.get_hypergraph())
        self.vertical_tab.setCurrentIndex(0)
        gc.collect()

