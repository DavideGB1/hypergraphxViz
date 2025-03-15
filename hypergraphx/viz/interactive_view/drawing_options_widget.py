from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QDockWidget, QDoubleSpinBox, QLabel, QPushButton, QTabWidget, QWidget, QVBoxLayout, \
    QListWidget, QComboBox, QListWidgetItem

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.__drawing_options import *
from hypergraphx.viz.interactive_view.__graphic_option_menu import GraphicOptionsWidget, get_Sets_options, \
    get_PAOH_options, get_Radial_options, get_ExtraNode_options, get_Bipartite_options, get_Clique_options
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict, \
    SpectralClusteringOptionsWidget, MTOptionsWidget, MMSBMOptionsWidget


class DrawingOptionsDockWidget(QDockWidget):
    update_value = pyqtSignal(dict)
    def __init__(self, weighted = False, hypergraph_type = "normal", n_nodes = 0):
        super().__init__()
        self.combobox_weight_influence = None
        self.spin_box_label = None
        self.n_nodes = n_nodes
        self.community_options_dict = CommunityOptionsDict()
        self.community_algorithm_option_gui = None
        self.graphic_options_widget = None
        self.extra_attributes = None
        self.algorithm_options_dict = None
        self.drawing_options = None
        self.community_combobox = None
        self.drawing_combobox = None
        self.hypergraph_type = hypergraph_type
        self.centrality_combobox = None
        self.heaviest_edges_spin_box = None
        self.heaviest_edges_spin_box_label = None
        self.weighted = weighted
        self.graphic_options = GraphicOptions()
        self.vbox = QVBoxLayout()

        drawing_label = QLabel("Drawing Algorithm:")
        self.vbox.addWidget(drawing_label)
        self.create_drawing_combobox()
        community_label = QLabel("Community Detection Algorithm:")
        self.vbox.addWidget(community_label)
        self.create_community_detection_combobox()
        centrality_label = QLabel("Centrality Calculation Method:")
        self.vbox.addWidget(centrality_label)
        self.create_centrality_combobox()
        if self.weighted:
            self.weighted_options()
        self.redraw_button = QPushButton("Redraw")
        self.redraw_button.clicked.connect(self.update)
        self.vbox.addWidget(self.redraw_button)

        self.use_last = False

        self.tab = QTabWidget()

        drawing_options_tab = QWidget()
        vbox = QVBoxLayout()
        drawing_options_tab.setLayout(vbox)
        self.drawing_options_list = QListWidget()
        vbox.addWidget(self.drawing_options_list)
        self.tab.addTab(drawing_options_tab, "Drawing Options")

        graphic_options_tab = QWidget()
        vbox = QVBoxLayout()
        graphic_options_tab.setLayout(vbox)
        self.graphic_options_list = QListWidget()
        vbox.addWidget(self.graphic_options_list)
        self.tab.addTab(graphic_options_tab, "Graphic Options")

        self.community_options_tab = QWidget()
        vbox = QVBoxLayout()
        self.community_options_tab.setLayout(vbox)
        self.community_options_list = QListWidget()
        vbox.addWidget(self.community_options_list)
        self.tab.addTab(self.community_options_tab, "Community Options")
        self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), False)
        self.vbox.addWidget(self.tab)

        self.widget = QWidget()
        self.widget.setLayout(self.vbox)
        self.setWidget(self.widget)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.changes_drawing_algorithm()
    def extra_options(self) -> None:
        """
        Generate the extra options list for the visualization functions
        """
        if self.drawing_combobox.currentText() == "Radial":
            self.extra_attributes = dict()
            self.extra_attributes["radius_scale_factor"] = 1.0
            self.extra_attributes["font_spacing_factor"] = 1.5
        elif self.drawing_combobox.currentText() == "PAOH" and self.hypergraph_type == "temporal":
            self.extra_attributes = dict()
            self.extra_attributes["time_font_size"] = 18
            self.extra_attributes["time_separation_line_color"] = "#000000"
            self.extra_attributes["time_separation_line_size"] = 4
        elif self.drawing_combobox.currentText() == "Sets":
            self.extra_attributes = dict()
            self.extra_attributes["hyperedge_alpha"] = 0.8
            self.extra_attributes["rounding_radius_factor"] = 0.1
            self.extra_attributes["polygon_expansion_factor"] = 1.8
        else:
            self.extra_attributes = dict()
        if self.hypergraph_type == "directed":
            self.extra_attributes["in_edge_color"] = "green"
            self.extra_attributes["out_edge_color"] = "red"
    #Chiamare da main view
    def weighted_options(self):
        self.heaviest_edges_spin_box = QDoubleSpinBox(self)
        self.heaviest_edges_spin_box.setDecimals(0)
        self.heaviest_edges_spin_box.setRange(0, 100)
        self.heaviest_edges_spin_box.setValue(100)
        self.heaviest_edges_spin_box_label = QLabel(self)
        self.heaviest_edges_spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.heaviest_edges_spin_box.value()))
        self.heaviest_edges_spin_box_label.setAlignment(Qt.AlignTop)
        self.heaviest_edges_spin_box.setAlignment(Qt.AlignTop)
        self.heaviest_edges_spin_box.valueChanged.connect(self.send_new_heaviest_edges)
        self.vbox.addWidget(self.heaviest_edges_spin_box_label)
        self.vbox.addWidget(self.heaviest_edges_spin_box)
        self.combobox_weight_influence_label = QLabel("Weight-Distance Relationship",self)
        self.vbox.addWidget(self.combobox_weight_influence_label)
        self.combobox_weight_influence = QComboBox(self)
        self.combobox_weight_influence.addItems(["No Relationship", "Directly Proportional","Inversely Proportional"])
        self.combobox_weight_influence.currentTextChanged.connect(self.update)
        self.vbox.addWidget(self.combobox_weight_influence)

    def send_new_heaviest_edges(self):
        self.heaviest_edges_spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.heaviest_edges_spin_box.value()))
        self.update()
    @staticmethod
    def add_algorithm_options_button(widget, list, func):
        list.clear()
        for x in widget.widget_list:
            myQListWidgetItem = QListWidgetItem(list)
            myQListWidgetItem.setSizeHint(x.sizeHint())
            list.addItem(myQListWidgetItem)
            list.setItemWidget(myQListWidgetItem, x)
        widget.modified_options.connect(func)
    def create_centrality_combobox(self):
        self.centrality_combobox = QComboBox()
        self.centrality_combobox.addItems(["No Centrality", "Degree Centrality"])
        self.centrality_combobox.currentTextChanged.connect(self.update_centrality)
        self.vbox.addWidget(self.centrality_combobox)
    def update_centrality(self):
        self.use_last = True
        self.update()
    def create_community_detection_combobox(self):
        self.community_combobox = QComboBox()
        self.community_combobox.addItems(["None", "Hypergraph Spectral Clustering","Hypergraph-MT", "Hy-MMSBM"])
        self.community_combobox.currentTextChanged.connect(self.change_community_detection_algorithm)
        self.vbox.addWidget(self.community_combobox)
    def get_community_options(self):
        match self.community_combobox.currentText():
            case "None":
                return None
            case "Hypergraph Spectral Clustering":
                return SpectralClusteringOptionsWidget(self.n_nodes)
            case "Hypergraph-MT":
                return MTOptionsWidget(self.n_nodes)
            case "Hy-MMSBM":
                return MMSBMOptionsWidget(self.n_nodes)
    def change_community_detection_algorithm(self):
        if self.community_combobox.currentText() == "None":
            self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), False)
        else:
            self.community_options_dict = CommunityOptionsDict()
            self.community_algorithm_option_gui = self.get_community_options()
            self.add_algorithm_options_button(self.community_algorithm_option_gui, self.community_options_list,
                                              self.update_community_options)
            self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), True)
        self.update()
    def update_community_options(self, dictionary):
        self.community_options_dict.update(dictionary)
        self.update()
    def create_drawing_combobox(self):
        self.drawing_combobox = QComboBox()
        self.update_hypergraph_drawing_options()
        self.drawing_combobox.currentTextChanged.connect(self.changes_drawing_algorithm)
        self.vbox.addWidget(self.drawing_combobox)
    def changes_drawing_algorithm(self):
        self.get_correct_options()
        self.extra_options()
        graphic_options = self.get_graphic_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes, graphic_options)
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.update_graphic_options)
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.update_drawing_options)
        self.algorithm_options_dict = self.drawing_options.get_options()
        if self.heaviest_edges_spin_box_label is not None:
            if self.drawing_combobox.currentText() in ["Sets", "Extra-Node"]:
                self.combobox_weight_influence.show()
                self.combobox_weight_influence_label.show()
            else:
                self.combobox_weight_influence.hide()
                self.combobox_weight_influence_label.hide()
        self.update()
    def get_graphic_options(self):
        match self.drawing_combobox.currentText():
            case "Sets":
                return get_Sets_options(self.weighted, self.hypergraph_type == "directed")
            case "PAOH":
                return get_PAOH_options(self.weighted, self.hypergraph_type == "directed")
            case "Radial":
                return get_Radial_options(self.weighted, self.hypergraph_type == "directed")
            case "Extra-Node":
                return get_ExtraNode_options(self.weighted, self.hypergraph_type == "directed")
            case "Bipartite":
                return get_Bipartite_options(self.weighted, self.hypergraph_type == "directed")
            case "Clique":
                return get_Clique_options()
    def get_correct_options(self):
        match self.drawing_combobox.currentText():
            case "Sets":
                self.drawing_options = SetOptionsWidget()
            case "PAOH":
                self.drawing_options = PAOHOptionsWidget()
            case "Radial":
                self.drawing_options = RadialOptionsWidget()
            case "Extra-Node":
                self.drawing_options = ExtraNodeOptionsWidget()
            case "Bipartite":
                self.drawing_options = BipartiteOptionsWidget()
            case "Clique":
                self.drawing_options = CliqueOptionsWidget()
    def update_graphic_options(self, new_options):
        self.graphic_options, self.extra_attributes = new_options
        self.use_last = True
        self.update()
    def update_drawing_options(self, dictionary):
        self.algorithm_options_dict = dictionary
        try:
            self.use_last = dictionary["use_last"]
        except KeyError:
            self.use_last = True
        self.update()
    def update_hypergraph_drawing_options(self):
        self.drawing_combobox.clear()
        if self.hypergraph_type == "normal":
            self.drawing_combobox.addItems(["Sets", "PAOH","Radial", "Extra-Node","Bipartite"])
            if not self.weighted:
                self.drawing_combobox.addItem("Clique")
            self.drawing_combobox.setCurrentText("Sets")
        elif self.hypergraph_type == "directed":
            self.drawing_combobox.addItems(["PAOH","Radial", "Extra-Node","Bipartite"])
            self.drawing_combobox.setCurrentText("Extra-Node")
        elif self.hypergraph_type == "temporal":
            self.drawing_combobox.addItems(["PAOH"])
            self.drawing_combobox.setCurrentText("PAOH")

    def update_hypergraph_type(self, hypergraph_type):
        self.hypergraph_type = hypergraph_type
        self.update_hypergraph_drawing_options()
    def update(self):
        if self.heaviest_edges_spin_box_label is not None:
            heaviest_value = self.heaviest_edges_spin_box.value()/100
            weight_influence = self.combobox_weight_influence.currentText()
        else:
            heaviest_value = 1
            weight_influence = "No Relationship"
        self.update_value.emit({"%_heaviest_edges": heaviest_value,"centrality": self.centrality_combobox.currentText(),
                                "community_detection_algorithm": self.community_combobox.currentText(),
                                "drawing_options":self.drawing_combobox.currentText() ,"use_last": self.use_last, "algorithm_options":self.algorithm_options_dict,
                                "graphic_options": self.graphic_options,"extra_attributes": self.extra_attributes,
                                "community_options": self.community_options_dict, "weight_influence": weight_influence})
        self.use_last = False
