import gc

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QTabWidget

from hypergraphx import Hypergraph
from hypergraphx.viz.interactive_view.stats_view.stats_calculations import calculate_weight_distribution, draw_weight, \
    adjacency_calculations_pool, draw_adjacency, degree_calculations, calculate_centrality_pool, draw_centrality, \
    draw_degree
from hypergraphx.viz.interactive_view.stats_view.stats_widgets import GenericGraphWidget, MotifsWidget


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

