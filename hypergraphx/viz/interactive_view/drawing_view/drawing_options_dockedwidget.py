from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDockWidget, QDoubleSpinBox, QLabel, QTabWidget, QComboBox, \
    QStackedWidget, QWidget, QScrollArea, QVBoxLayout, QPushButton

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.drawing_options.clustering_options import SpectralClusteringOptionsWidget, \
    MTOptionsWidget, MMSBMOptionsWidget
from hypergraphx.viz.interactive_view.drawing_options.drawing_options import SetOptionsWidget, RadialOptionsWidget, \
    PAOHOptionsWidget, ExtraNodeOptionsWidget, BipartiteOptionsWidget, CliqueOptionsWidget
from hypergraphx.viz.interactive_view.drawing_view.aggregation_widget import AggregationWidget
from hypergraphx.viz.interactive_view.graphic_options.derived_graphic_options import create_graphic_options_widget


class DrawingOptionsDockWidget(QDockWidget):
    update_value = pyqtSignal(dict)
    def __init__(self, weighted = False, hypergraph_type = "normal", n_nodes = 0, parent=None):
        super().__init__(parent)
        self.redraw_flag = False
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
        self.drawing_options_widgets = dict()
        self.drawing_options_stack = QStackedWidget(self)

        self.drawing_options_widgets["Sets"] = SetOptionsWidget(self)
        self.drawing_options_widgets["Radial"] = RadialOptionsWidget(self)
        self.drawing_options_widgets["PAOH"] = PAOHOptionsWidget(self)
        self.drawing_options_widgets["Extra-Node"] = ExtraNodeOptionsWidget(self)
        self.drawing_options_widgets["Bipartite"] = BipartiteOptionsWidget(self)
        self.drawing_options_widgets["Clique"] = CliqueOptionsWidget(self)
        for widget in self.drawing_options_widgets.values():
            self.drawing_options_stack.addWidget(widget)
            widget.modified_options.connect(self.__update_drawing_options)

        self.weighted = weighted
        self.vbox = QVBoxLayout()

        self.drawing_vbox = QVBoxLayout()
        self.drawing_label = QLabel("Drawing Algorithm:",parent=self)
        self.drawing_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.drawing_vbox.addWidget(self.drawing_label)
        self.drawing_vbox_widget = QWidget(self)
        self.drawing_vbox_widget.setLayout(self.drawing_vbox)
        self.drawing_vbox_widget.setStyleSheet("border-bottom: 1px solid #dcdcdc;")
        self.vbox.addWidget(self.drawing_vbox_widget)
        self.__create_drawing_combobox()

        if self.hypergraph_type == "normal":
            self.community_vbox= QVBoxLayout()
            self.community_label = QLabel("Community Detection Algorithm:", parent=self)
            self.community_label.setStyleSheet("font-weight: bold; font-size: 12px;")
            self.community_vbox.addWidget(self.community_label)
            self.__create_community_detection_combobox()
            self.community_vbox_widget = QWidget(self)
            self.community_vbox_widget.setLayout(self.community_vbox)
            self.community_vbox_widget.setStyleSheet("border-bottom: 1px solid #dcdcdc;")
            self.vbox.addWidget(self.community_vbox_widget)

        self.centrality_vbox = QVBoxLayout()
        self.centrality_label = QLabel("Centrality Calculation Method:", parent=self)
        self.centrality_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.centrality_vbox.addWidget(self.centrality_label)
        self.centrality_vbox_widget = QWidget(self)
        self.centrality_vbox_widget.setLayout(self.centrality_vbox)
        self.centrality_vbox_widget.setStyleSheet("border-bottom: 1px solid #dcdcdc;")
        self.vbox.addWidget(self.centrality_vbox_widget)
        self.__create_centrality_combobox()
        self.__weighted_options()
        self.change_weighted_options()
        self.redraw_button = QPushButton("Redraw",parent=self)
        self.redraw_button.clicked.connect(self.redraw)
        self.redraw_button.setIcon(QIcon('../interactive_view/icons/draw.svg'))
        self.vbox.addWidget(self.redraw_button, 0, Qt.AlignCenter)

        self.use_last = False

        self.tab = QTabWidget()

        self.tab.addTab(self.drawing_options_stack, "Algorithm")

        self.graphic_options = GraphicOptions()
        self.graphic_options_widgets = dict()
        self.graphic_options_tab = QStackedWidget(self)
        self.graphic_options_tab.setStyleSheet("QStackedWidget { background-color: white; }")
        for widget in self.graphic_options_widgets.values():
            self.graphic_options_tab.addWidget(widget)
            widget.modified_options.connect(self.__update_graphic_options)
        self.__create_graphic_options_widgets()

        self.tab.addTab(self.graphic_options_tab, "Graphic")

        self.community_options_widgets = dict()
        self.community_options_tab = QStackedWidget(self)

        self.community_options_widgets["Hypergraph Spectral Clustering"] = SpectralClusteringOptionsWidget(self)
        self.community_options_widgets["Hypergraph-MT"] = MTOptionsWidget(self)
        self.community_options_widgets["Hy-MMSBM"] = MMSBMOptionsWidget(self)
        for widget in self.community_options_widgets.values():
            widget.set_max_communities(self.n_nodes)
            self.community_options_tab.addWidget(widget)
            widget.modified_options.connect(self.__update_community_options)
        self.tab.addTab(self.community_options_tab, "Community")
        self.tab.setTabEnabled(self.tab.indexOf(self.community_options_tab), False)
        self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), False)
        self.aggregation_options_tab = AggregationWidget(self)
        self.tab.addTab(self.aggregation_options_tab, "Aggregation")
        if self.hypergraph_type != "normal":
            self.tab.setTabEnabled(self.tab.indexOf(self.aggregation_options_tab), False)
            self.tab.setTabVisible(self.tab.indexOf(self.aggregation_options_tab), False)

        self.tab.setObjectName("OptionsTabs")
        self.vbox.addWidget(self.tab)

        self.widget = QWidget(parent=self)
        self.widget.setObjectName("OptionsContainer")
        self.widget.setStyleSheet("""
                    QWidget#OptionsContainer {
                        border-left: 1px solid #dcdcdc;
                        padding: 0px;
                    }
                """)
        self.widget.setLayout(self.vbox)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.widget)
        self.setWidget(scroll_area)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.__changes_drawing_algorithm()

    @staticmethod
    def __extra_options(val, hypergraph_type):
        """
        Generate the extra options list for the visualization functions
        """
        extra_attributes = dict()
        if val == "Radial":
            extra_attributes["radius_scale_factor"] = 1.0
            extra_attributes["font_spacing_factor"] = 1.5
        if val == "PAOH":
            extra_attributes["axis_labels_size"] = 30
            extra_attributes["nodes_name_size"] = 25
        elif val == "Sets":
            extra_attributes["hyperedge_alpha"] = 0.8
            extra_attributes["rounding_radius_factor"] = 0.1
            extra_attributes["polygon_expansion_factor"] = 1.8
        return extra_attributes

    def __create_graphic_options_widgets(self):
        """
        Clears and recreates all graphic options widgets based on the current
        hypergraph type and weighted status.
        """
        # Clear existing widgets
        while self.graphic_options_tab.count() > 0:
            widget = self.graphic_options_tab.widget(0)
            self.graphic_options_tab.removeWidget(widget)
            widget.deleteLater()
        self.graphic_options_widgets.clear()

        # Define layout types
        layout_types = ["Sets", "Radial", "PAOH", "Extra-Node", "Bipartite", "Clique"]

        # Recreate widgets with current properties
        for layout in layout_types:
            widget = create_graphic_options_widget(
                layout_type=layout,
                graphic_options=self.graphic_options,
                extra_attributes=self.__extra_options(layout, self.hypergraph_type),
                weighted=self.weighted,
                hypergraph_type=self.hypergraph_type,
                parent=self
            )
            if widget:
                self.graphic_options_widgets[layout] = widget
                self.graphic_options_tab.addWidget(widget)
                widget.modified_options.connect(self.__update_graphic_options)
            if self.hypergraph_type == "directed":
                self.graphic_options_tab.setCurrentIndex(3)
            elif self.hypergraph_type == "temporal":
                self.graphic_options_tab.setCurrentIndex(2)
            else:
                self.graphic_options_tab.setCurrentIndex(0)

    def __weighted_options(self):
        self.heaviest_weight_vbox = QVBoxLayout()
        self.heaviest_edges_spin_box = QDoubleSpinBox(self)
        self.heaviest_edges_spin_box.setDecimals(0)
        self.heaviest_edges_spin_box.setRange(0, 100)
        self.heaviest_edges_spin_box.setValue(100)
        self.heaviest_edges_spin_box.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #BDBDBD;
                border-top-color: #A0A0A0; 
                border-left-color: #A0A0A0;
                border-radius: 8px;
                padding: 4px;
                font-size: 13px;
                color: #333;
                padding-left: 10px; 
            }
            
            QDoubleSpinBox:hover {
                border-color: #5D9CEC;
            }
            
            QDoubleSpinBox:focus {
                border-color: #4A89DC;
            }
            
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                width: 22px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AACFF, stop:1 #4A89DC);
                border: 1px solid #3A79CB;
                border-bottom: 2px solid #3A79CB; 
                border-radius: 4px;
            }
            
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7BCFFF, stop:1 #5D9CEC);
            }
            
            QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A89DC, stop:1 #3A79CB);
                border-bottom: 1px solid #3A79CB;
            }
            
            QDoubleSpinBox::up-button:pressed {
                padding-top: 1px; /* Sposta la freccia in giù */
            }
            QDoubleSpinBox::down-button:pressed {
                padding-top: 1px; /* Sposta la freccia in giù */
            }
            
            QDoubleSpinBox::up-button {
                subcontrol-position: top right;
                margin: 2px 2px 1px 0px;
            }
            
            QDoubleSpinBox::down-button {
                subcontrol-position: bottom right;
                margin: 1px 2px 2px 0px;
            }
        """)
        self.heaviest_edges_spin_box_label = QLabel(self)
        self.heaviest_edges_spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.heaviest_edges_spin_box.value()))
        self.heaviest_edges_spin_box_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.heaviest_edges_spin_box_label.setAlignment(Qt.AlignTop)
        self.heaviest_edges_spin_box.setAlignment(Qt.AlignTop)
        self.heaviest_edges_spin_box.valueChanged.connect(self.__send_new_heaviest_edges)
        self.heaviest_weight_vbox.addWidget(self.heaviest_edges_spin_box_label)
        self.heaviest_weight_vbox.addWidget(self.heaviest_edges_spin_box)
        self.heaviest_weight_vbox_widget = QWidget(self)
        self.heaviest_weight_vbox_widget.setLayout(self.heaviest_weight_vbox)
        self.heaviest_weight_vbox_widget.setStyleSheet("border-bottom: 1px solid #dcdcdc;")
        self.vbox.addWidget(self.heaviest_weight_vbox_widget)

        self.weight_influence_vbox = QVBoxLayout()
        self.combobox_weight_influence_label = QLabel("Weight-Distance Relation",self)
        self.combobox_weight_influence_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.weight_influence_vbox.addWidget(self.combobox_weight_influence_label)
        self.combobox_weight_influence = QComboBox(self)
        self.combobox_weight_influence.addItems(["No Relationship", "Directly Proportional","Inversely Proportional"])
        self.combobox_weight_influence.currentTextChanged.connect(self.update)
        self.weight_influence_vbox.addWidget(self.combobox_weight_influence)
        self.weight_influence_vbox_widget = QWidget(self)
        self.weight_influence_vbox_widget.setLayout(self.weight_influence_vbox)
        self.weight_influence_vbox_widget.setStyleSheet("border-bottom: 1px solid #dcdcdc;")
        self.vbox.addWidget(self.weight_influence_vbox_widget)

    def change_weighted_options(self):
        if self.weighted and self.drawing_combobox.currentText() != "PAOH":
            self.weight_influence_vbox_widget.setVisible(True)
            self.heaviest_weight_vbox_widget.setVisible(True)
        else:
            self.weight_influence_vbox_widget.setVisible(False)
            self.heaviest_weight_vbox_widget.setVisible(False)

    def __send_new_heaviest_edges(self):
        self.heaviest_edges_spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.heaviest_edges_spin_box.value()))
        self.update()

    def __create_centrality_combobox(self):
        self.centrality_combobox = QComboBox(parent=self)
        if self.hypergraph_type != "directed":
            self.centrality_combobox.addItems(
            ["No Centrality", "Degree Centrality", "Betweenness Centrality",
             "Adjacency Factor (t=1)", "Adjacency Factor (t=2)"])
        else:
            self.centrality_combobox.addItems(
                ["No Centrality", "Degree Centrality", "Betweenness Centrality"])
        self.centrality_combobox.currentTextChanged.connect(self.__update_centrality)
        self.centrality_vbox.addWidget(self.centrality_combobox)

    def __update_hypergraph_centrality_options(self):
        self.centrality_combobox.clear()
        if self.hypergraph_type != "directed":
            self.centrality_combobox.addItems(
            ["No Centrality", "Degree Centrality", "Betweenness Centrality",
             "Adjacency Factor (t=1)", "Adjacency Factor (t=2)"])
        else:
            self.centrality_combobox.addItems(
                ["No Centrality", "Degree Centrality", "Betweenness Centrality"])

    def __update_centrality(self):
        if self.centrality_combobox.currentText() == "No Centrality":
            self.drawing_options_widgets["PAOH"].space_optimization_btn.setEnabled(True)
            self.algorithm_options_dict["sort_nodes_by"] = False
        else:
            self.drawing_options_widgets["PAOH"].space_optimization_btn.setEnabled(False)
            self.algorithm_options_dict["sort_nodes_by"] = True
        self.drawing_options_widgets["PAOH"].space_optimization_btn.setChecked(False)
        self.use_last = True
        self.update()

    def __create_community_detection_combobox(self):
        self.community_combobox = QComboBox(parent=self)
        self.community_combobox.addItems(["None", "Hypergraph Spectral Clustering","Hypergraph-MT", "Hy-MMSBM"])
        self.community_combobox.currentTextChanged.connect(self.__change_community_detection_algorithm)
        self.community_vbox.addWidget(self.community_combobox)

    def __change_community_detection_algorithm(self):
        """
        Changes the community detection algorithm settings based on the user's selection
        from a combobox and dynamically updates the GUI.
        """
        if self.community_combobox.currentText() == "None":
            self.tab.setTabEnabled(self.tab.indexOf(self.community_options_tab), False)
            self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), False)
        else:
            current_algorithm_name = self.community_combobox.currentText()
            if current_algorithm_name in self.community_options_widgets:
                widget_to_show = self.community_options_widgets[current_algorithm_name]
                self.community_options_tab.setCurrentWidget(widget_to_show)

            self.tab.setTabEnabled(self.tab.indexOf(self.community_options_tab), True)
            self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), True)
        self.update()

    def __update_community_options(self, dictionary):
        """
        Updates the community options with the provided dictionary and triggers an update.

        Parameters
        ----------
        dictionary : dict
            A dictionary containing new or updated community options to be merged with the existing options.
        """
        self.community_options_dict.update(dictionary)
        self.update()

    def __create_drawing_combobox(self):
        """
        Creates and initializes a QComboBox widget for selecting drawing algorithms.
        """
        self.drawing_combobox = QComboBox(parent=self)

        self.__update_hypergraph_drawing_options()
        self.drawing_combobox.currentTextChanged.connect(self.__changes_drawing_algorithm)
        self.drawing_vbox.addWidget(self.drawing_combobox)

    def __changes_drawing_algorithm(self):
        """
        Updates the drawing algorithm options and configurations based on the selected parameters.
        This method updates the graphic options and drawing options widgets,
        adds corresponding buttons for updating these options, and adjusts the
        visibility of the weight influence combobox based on the current drawing type.
        It also ensures the overall update of the interface after adjusting options.
        """
        current_algorithm_name = self.drawing_combobox.currentText()

        if current_algorithm_name in self.drawing_options_widgets:
            widget_to_show = self.drawing_options_widgets[current_algorithm_name]
            self.drawing_options_stack.setCurrentWidget(widget_to_show)
            self.algorithm_options_dict = widget_to_show.get_options()

        if current_algorithm_name in self.graphic_options_widgets:
            widget_to_show = self.graphic_options_widgets[current_algorithm_name]
            self.graphic_options_tab.setCurrentWidget(widget_to_show)
            self.graphic_options, self.extra_attributes = widget_to_show.get_data()
        self.change_weighted_options()
        self.update()

    def __update_graphic_options(self, new_options):
        """
        Updates the graphic options for the instance.

        Parameters
        ----------
        new_options : tuple
            A tuple containing new graphic options and additional attributes to be set for the object.
        """
        self.graphic_options, self.extra_attributes = new_options
        self.use_last = True
        self.update()

    def __update_drawing_options(self, dictionary):
        """
        Updates the drawing options with new parameters from the given dictionary.

        Parameters
        ----------
        dictionary : dict
            A dictionary containing drawing options. The dictionary may include
            the key "use_last"""
        self.algorithm_options_dict = dictionary
        try:
            self.use_last = dictionary["use_last"]
        except KeyError:
            self.use_last = True
        self.update()

    def __update_hypergraph_drawing_options(self):
        """
        Updates the options available in the drawing combobox based on the type of hypergraph
        and other associated properties.
        """
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

    def update_hypergraph(self, hypergraph_type, n_nodes, weighted):
        self.hypergraph_type = hypergraph_type
        self.n_nodes = n_nodes
        self.weighted = weighted
        self.community_combobox.setCurrentText("None")
        if not self.hypergraph_type == "normal":
            self.community_label.setVisible(False)
            self.community_combobox.setVisible(False)
        else:
            self.community_label.setVisible(True)
            self.community_combobox.setVisible(True)

        self.centrality_combobox.setCurrentText("No Centrality")
        self.__update_hypergraph_drawing_options()
        self.__update_hypergraph_centrality_options()
        self.__create_graphic_options_widgets()
        if self.hypergraph_type != "normal":
            self.tab.setTabEnabled(self.tab.indexOf(self.aggregation_options_tab), False)
            self.tab.setTabVisible(self.tab.indexOf(self.aggregation_options_tab), False)
        else:
            self.tab.setTabEnabled(self.tab.indexOf(self.aggregation_options_tab), True)
            self.tab.setTabVisible(self.tab.indexOf(self.aggregation_options_tab), True)

        self.change_weighted_options()

    def redraw(self):
        self.redraw_flag = True
        self.update()

    def update(self):
        if self.weighted:
            heaviest_value = self.heaviest_edges_spin_box.value()/100
            weight_influence = self.combobox_weight_influence.currentText()
        else:
            heaviest_value = 1
            weight_influence = "No Relationship"
        try:
            cda = self.community_combobox.currentText()
        except Exception:
            cda = "None"

        if self.centrality_combobox.currentText() == "No Centrality":
            self.algorithm_options_dict["sort_nodes_by"] = False
        else:
            self.algorithm_options_dict["sort_nodes_by"] = True
        update_dict = {
            "%_heaviest_edges": heaviest_value,
            "centrality": self.centrality_combobox.currentText(),
            "community_detection_algorithm": cda,
            "drawing_options":self.drawing_combobox.currentText(),
            "use_last": self.use_last,
            "algorithm_options":self.algorithm_options_dict,
            "graphic_options": self.graphic_options,
            "extra_attributes": self.extra_attributes,
            "community_options": self.community_options_dict,
            "weight_influence": weight_influence,
            "aggregation_options": self.aggregation_options_tab.get_options(),
            "redraw": self.redraw_flag
        }
        self.update_value.emit(update_dict )
        self.redraw_flag = False
        self.use_last = False
