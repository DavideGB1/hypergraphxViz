import copy
import ctypes
import faulthandler
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QComboBox, QListWidget, \
    QListWidgetItem, QTabWidget, QLayout, QMainWindow, QStackedLayout, QDockWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.communities.hy_mmsbm.model import HyMMSBM
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.communities.hypergraph_mt.model import HypergraphMT
from hypergraphx.measures.degree import degree_sequence
from hypergraphx.utils import normalize_array
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_metroset import draw_metroset
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.draw_sets import draw_sets
from hypergraphx.viz.interactive_view.__drawing_options import PAOHOptionsWidget, RadialOptionsWidget, \
    CliqueOptionsWidget, ExtraNodeOptionsWidget, BipartiteOptionsWidget, SetOptionsWidget
from hypergraphx.viz.interactive_view.__graphic_option_menu import GraphicOptionsWidget, \
    get_PAOH_options, get_Radial_options, get_Clique_options, get_ExtraNode_options, get_Bipartite_options, \
    get_Sets_options
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import SpectralClusteringOptionsWidget, \
    CommunityOptionsDict, MTOptionsWidget, MMSBMOptionsWidget
from hypergraphx.viz.interactive_view.custom_widgets import WaitingScreen, SliderDockWidget
from hypergraphx.viz.interactive_view.table_view import ModifyHypergraphMenu


class Window(QMainWindow):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep+ 'logo_cropped.png'))
        if "win" in sys.platform:
            myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        #Set Default Values
        self.community_algorithm_option_gui = None
        self.community_options_dict = CommunityOptionsDict()
        self.algorithm_options_dict = dict()
        self.tab = None
        self.drawing_options_list = None
        self.use_last = False
        self.centrality = None
        self.options_dict = dict()
        self.spin_box_label = QLabel()
        self.spin_box = QDoubleSpinBox()
        self.vbox = QVBoxLayout()
        self.current_function = draw_PAOH
        self.extra_attributes = dict()
        self.graphic_options = GraphicOptions()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes)
        self.slider = None
        self.community_option_menu = None
        self.option_menu = None
        self.hypergraph = hypergraph
        self.canvas_hbox = QHBoxLayout()
        self.figure = plt.figure()
        self.max_edge = 0
        self.last_pos = dict()
        self.stacked = QStackedLayout()
        for edge in h.get_edges():
            if len(edge) > self.max_edge:
                self.max_edge = len(edge)
        self.slider_value = (2, self.max_edge)
        #Defines Canvas and Options Toolbar
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_hbox.addWidget(self.canvas, 80)
        self.community_model = None
        # Sliders Management
        # Create layout and add everything
        layout = QMainWindow()
        layout.addToolBar(Qt.TopToolBarArea, self.toolbar)
        layout.setCentralWidget(self.canvas)
        self.slider = SliderDockWidget(self.max_edge)
        self.slider.update_value.connect(self.new_slider_value)
        layout.addDockWidget(Qt.BottomDockWidgetArea, self.slider)


        # setting layout to the main window

        self.central_tab = QTabWidget()
        self.stacked.addWidget(layout)
        drawing_tab = QWidget()
        drawing_tab.setLayout(self.stacked)
        modify_hypergraph_tab = ModifyHypergraphMenu(hypergraph)
        modify_hypergraph_tab.updated_hypergraph.connect(self.update_hypergraph)
        self.central_tab.addTab(drawing_tab, "Drawing Area")
        self.central_tab.addTab(modify_hypergraph_tab, "Modify Hypergraph")


        self.setCentralWidget(self.central_tab)
        self.option_vbox()
        self.use_default()
        self.stacked.addWidget(WaitingScreen())

        dummy2 = QWidget()
        dummy2.setLayout(self.vbox)
        tmp2 = QDockWidget()
        tmp2.setWidget(dummy2)
        tmp2.setFeatures(QDockWidget.NoDockWidgetFeatures)
        layout.addDockWidget(Qt.RightDockWidgetArea, tmp2)
    def new_slider_value(self, value):
        self.slider_value = value
        self.plot()
    def change_focus(self):
        if self.stacked.currentIndex() == 0:
            self.stacked.setCurrentIndex(1)
        else:
            self.stacked.setCurrentIndex(0)
        self.repaint()
    def use_default(self):
        if isinstance(self.hypergraph, TemporalHypergraph):
            self.assign_PAOH()
            self.combobox_drawing.setCurrentIndex(0)
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.assign_extra_node()
            self.combobox_drawing.setCurrentIndex(0)
        else:
            self.assign_sets()
            self.combobox_drawing.setCurrentIndex(0)

    #Drawing
    def plot(self) -> None:
        """
        Plot the hypergraph on screen using the assigner draw function.
        """
        #Clears the plot
        self.change_focus()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        #Try to get the extra attributes
        try:
            radius_scale_factor = self.extra_attributes["radius_scale_factor"]
        except KeyError:
            radius_scale_factor = 1.0
        try:
            font_spacing_factor = self.extra_attributes["font_spacing_factor"]
        except KeyError:
            font_spacing_factor = 1.5
        try:
            time_font_size = self.extra_attributes["time_font_size"]
        except KeyError:
            time_font_size = 18
        try:
            time_separation_line_color = self.extra_attributes["time_separation_line_color"]
        except KeyError:
            time_separation_line_color = "#000000"
        try:
            time_separation_line_width = self.extra_attributes["time_separation_line_width"]
        except KeyError:
            time_separation_line_width = 4
        try:
            rounding_radius_size = self.extra_attributes["rounding_radius_factor"]
        except KeyError:
            rounding_radius_size = 0.1
        try:
            polygon_expansion_factor = self.extra_attributes["polygon_expansion_factor"]
        except KeyError:
            polygon_expansion_factor = 1.8
        try:
             hyperedge_alpha = self.extra_attributes["hyperedge_alpha"]
        except KeyError:
            hyperedge_alpha = 0.8
        if self.use_last:
            last_pos = self.last_pos
        else:
            last_pos = None
        if self.centrality is not None:
            self.graphic_options.add_centrality_factor_dict(self.centrality)
        else:
            self.graphic_options.add_centrality_factor_dict(None)
        #Plot and draw the hypergraph using it's function
        self.last_pos = self.current_function(self.hypergraph, cardinality= self.slider_value, x_heaviest = float(self.spin_box.value()/100), ax=ax,
                time_font_size = time_font_size, time_separation_line_color = time_separation_line_color,k=self.community_options_dict["number_communities"],
                graphicOptions=copy.deepcopy(self.graphic_options), radius_scale_factor=radius_scale_factor, font_spacing_factor=font_spacing_factor,
                time_separation_line_width = time_separation_line_width, polygon_expansion_factor = polygon_expansion_factor,
                rounding_radius_size = rounding_radius_size, hyperedge_alpha = hyperedge_alpha,pos = last_pos, u = self.community_model, **self.algorithm_options_dict)
        self.use_last = False
        self.canvas.draw()
        self.change_focus()
    def redraw(self):
        self.use_last = False
        self.plot()
    #Get Support for Options
    def get_drawing_algorithm_options(self, dict):
        self.algorithm_options_dict = dict
        try:
            self.use_last = dict["use_last"]
        except KeyError:
            self.use_last = True
        self.plot()
    def get_new_option(self, new_options: tuple[GraphicOptions,dict]) -> None:
        """
        Update the graphic options with the one sent from the option menu.
        Parameters
        ----------
        new_options: tuple[GraphicOptions, dict]
            The tuple inside the signal received from the option menu.
        """
        self.graphic_options, self.extra_attributes = new_options
        self.use_last = True
        self.plot()
    def update_hypergraph(self, example = None, hypergraph = None):
        self.change_focus()
        if example is not None:
            self.hypergraph = example["hypergraph"]
        if hypergraph is not None:
            self.hypergraph = hypergraph
        self.create_algorithm_options()
        for edge in self.hypergraph.get_edges():
            if len(edge) > self.max_edge:
                self.max_edge = len(edge)
        clear_layout(self.vbox)

        self.slider.update_max(self.max_edge)
        self.option_vbox()
        self.change_focus()
        self.use_default()
    def extra_options(self) -> None:
        """
        Generate the extra options list for the visualization functions
        """
        if self.current_function == draw_radial_layout:
            self.extra_attributes = dict()
            self.extra_attributes["radius_scale_factor"] = 1.0
            self.extra_attributes["font_spacing_factor"] = 1.5
        elif self.current_function == draw_PAOH and isinstance(self.hypergraph, TemporalHypergraph):
            self.extra_attributes = dict()
            self.extra_attributes["time_font_size"] = 18
            self.extra_attributes["time_separation_line_color"] = "#000000"
            self.extra_attributes["time_separation_line_size"] = 4
        elif self.current_function == draw_sets:
            self.extra_attributes = dict()
            self.extra_attributes["hyperedge_alpha"] = 0.8
            self.extra_attributes["rounding_radius_factor"] = 0.1
            self.extra_attributes["polygon_expansion_factor"] = 1.8
        else:
            self.extra_attributes = dict()
        if isinstance(self.hypergraph, DirectedHypergraph):
            self.extra_attributes["in_edge_color"] = "green"
            self.extra_attributes["out_edge_color"] = "red"
    def heaviest_edges(self) -> None:
        """
        Updates the label showing what % of edges we are considering.
        """
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.plot()
    #Assign Drawing Function
    def assign_PAOH(self) -> None:
        """
        Assigns draw_PAOH as plot function.
        """
        self.current_function = draw_PAOH
        # Gets new extra options
        self.extra_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes, get_PAOH_options(self.hypergraph.is_weighted(), isinstance(self.hypergraph, DirectedHypergraph)))
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.get_new_option)
        self.drawing_options = PAOHOptionsWidget()
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.get_drawing_algorithm_options)
        self.plot()
    def assign_radial(self) -> None:
        """
        Assigns draw_radial_layout as plot function.
        """
        self.current_function = draw_radial_layout

        #Gets new extra options
        self.extra_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes,
                                                           get_Radial_options(self.hypergraph.is_weighted(), isinstance(self.hypergraph, DirectedHypergraph)))
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.get_new_option)
        #Create the new custom options for the radial function
        self.drawing_options = RadialOptionsWidget()
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.get_drawing_algorithm_options)
        self.plot()
    def assign_metroset(self) -> None:
        """
        Assigns draw_metroset as plot function.
        """
        self.current_function = draw_metroset
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        # Create the new custom options for the metroset function
        vbox_metroset_option = QVBoxLayout()
        iterations_selector_label = QLabel()
        iterations_selector_label.setText("Number of Iterations:")
        iterations_selector = QDoubleSpinBox()

        def iterations_selector_funz():
            self.iterations = iterations_selector.value()
            self.plot()

        iterations_selector.setDecimals(0)
        iterations_selector.setRange(0, 100000000)
        iterations_selector.setValue(1000)
        iterations_selector.setSingleStep(1)
        iterations_selector.valueChanged.connect(iterations_selector_funz)
        vbox_metroset_option.addWidget(iterations_selector_label)
        vbox_metroset_option.addWidget(iterations_selector)
        self.vbox.addLayout(vbox_metroset_option)
        self.vbox.addStretch()
        self.plot()
    def assign_clique_projection(self) -> None:
        """
        Assigns draw_clique as plot function.
        """
        self.current_function = draw_clique
        # Gets new extra options
        self.extra_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes, get_Clique_options())
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.get_new_option)
        self.drawing_options = CliqueOptionsWidget()
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.get_drawing_algorithm_options)
        self.plot()
    def assign_extra_node(self) -> None:
        """
        Assigns draw_extra_node as plot function.
        """
        self.current_function = draw_extra_node
        # Gets new extra options
        self.extra_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes,
                        get_ExtraNode_options(self.hypergraph.is_weighted(), isinstance(self.hypergraph, DirectedHypergraph)))
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.get_new_option)
        self.drawing_options = ExtraNodeOptionsWidget()
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.get_drawing_algorithm_options)
        self.plot()
    def assign_bipartite(self) -> None:
        """
        Assigns draw_bipartite as plot function.
        """
        self.current_function = draw_bipartite
        # Gets new extra options
        self.extra_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes,
                            get_Bipartite_options(self.hypergraph.is_weighted(), isinstance(self.hypergraph, DirectedHypergraph)))
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.get_new_option)
        self.drawing_options = BipartiteOptionsWidget()
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.get_drawing_algorithm_options)
        self.plot()
    def assign_sets(self) -> None:
        """
        Assigns draw_sets as plot function.
        """
        self.current_function = draw_sets
        # Gets new extra options
        self.extra_options()
        self.graphic_options_widget = GraphicOptionsWidget(self.graphic_options, self.extra_attributes,
                    get_Sets_options(self.hypergraph.is_weighted(), isinstance(self.hypergraph, DirectedHypergraph)))
        self.add_algorithm_options_button(self.graphic_options_widget, self.graphic_options_list,
                                          self.get_new_option)

        self.drawing_options = SetOptionsWidget()
        self.add_algorithm_options_button(self.drawing_options, self.drawing_options_list, self.get_drawing_algorithm_options)
        self.plot()
    #Community
    def use_community_detection_algorithm(self):
        self.change_focus()
        self.options_community[self.community_combobox.currentText()]()
        self.change_focus()
        self.redraw()
    def create_community_detection_options(self) -> QComboBox:
        """
        Create the selection list for the visualization function
        """
        self.community_combobox = QComboBox()
        self.options_community = {"None": self.no_community,
                                  "Hypergraph Spectral Clustering": self.use_spectral_clustering,
                                  "Hypergraph-MT": self.use_MT,
                                  "Hy-MMSBM": self.use_MMSBM}

        self.community_combobox.addItems(list(self.options_community.keys()))
        self.community_combobox.currentTextChanged.connect(self.use_community_detection_algorithm)
        return self.community_combobox
    def use_spectral_clustering(self):
        self.update_community_options_gui(SpectralClusteringOptionsWidget(self.hypergraph.num_nodes()))

        model = HySC(
            seed=self.community_options_dict["seed"],
            n_realizations=self.community_options_dict["realizations"]
        )
        self.community_model = model.fit(
            self.hypergraph,
            K=self.community_options_dict["number_communities"],
            weighted_L=False
        )
    def use_MT(self):
        self.update_community_options_gui(MTOptionsWidget(self.hypergraph.num_nodes()))

        model = HypergraphMT(
            n_realizations=self.community_options_dict["realizations"],
            max_iter=self.community_options_dict["max_iterations"],
            check_convergence_every=self.community_options_dict["check_convergence_every"],
            verbose=False
        )
        u_HypergraphMT, w_HypergraphMT, _ = model.fit(
            self.hypergraph,
            K=self.community_options_dict["number_communities"],
            seed=self.community_options_dict["seed"],
            normalizeU=self.community_options_dict["normalizeU"] ,
            baseline_r0=self.community_options_dict["baseline_r0"],
        )
        u_HypergraphMT = normalize_array(u_HypergraphMT, axis=1)
        self.community_model = u_HypergraphMT
    def use_MMSBM(self):
        self.update_community_options_gui(MMSBMOptionsWidget(self.hypergraph.num_nodes()))

        best_model = None
        best_loglik = float("-inf")
        for j in range(self.community_options_dict["realizations"]):
            model = HyMMSBM(
                K=self.community_options_dict["number_communities"],
                assortative=self.community_options_dict["assortative"]
            )
            model.fit(
                self.hypergraph,
                n_iter=self.community_options_dict["max_iterations"],
            )

            log_lik = model.log_likelihood(self.hypergraph)
            if log_lik > best_loglik:
                best_model = model
                best_loglik = log_lik

        u_HyMMSBM = best_model.u
        u_HyMMSBM = normalize_array(u_HyMMSBM, axis=1)

        self.community_model = u_HyMMSBM
    def no_community(self):
        self.update_community_options_gui(None)
        self.community_model = None
    def update_community_options_gui(self, gui):
        if gui is None:
            self.community_algorithm_option_gui = None
            self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), False)
        elif not isinstance(self.community_algorithm_option_gui, type(gui)):
            self.tab.setTabVisible(self.tab.indexOf(self.community_options_tab), True)
            self.community_options_dict = CommunityOptionsDict()
            self.community_algorithm_option_gui = gui
            self.add_algorithm_options_button(self.community_algorithm_option_gui, self.community_options_list, self.get_community_algorithm_options)
    def get_community_algorithm_options(self, dict):
        self.community_options_dict.update(dict)
        self.use_community_detection_algorithm()
        self.plot()

    #Create GUI Components

    def create_centrality_button(self):
        combobox = QComboBox()
        combobox.addItems(["No Centrality", "Degree Centrality"])
        def calculate_centrality():
            if self.centrality_combobox.currentText() == "No Centrality":
                self.centrality = None
            elif self.centrality_combobox.currentText() == "Degree Centrality":
                self.centrality = degree_sequence(self.hypergraph)
                mean = sum(self.centrality.values()) / len(self.centrality)
                for k, v in self.centrality.items():
                    self.centrality[k] = v / mean
            self.use_last = True
            self.plot()
        combobox.currentTextChanged.connect(calculate_centrality)
        return combobox
    def option_vbox(self) -> None:
        """
        Creates the standard options for the visualization functions
        """
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setDecimals(0)
        self.spin_box.setRange(0, 100)
        self.spin_box.setValue(100)
        self.spin_box_label = QLabel()
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.spin_box_label.setAlignment(Qt.AlignTop)
        self.spin_box.setAlignment(Qt.AlignTop)
        self.spin_box.valueChanged.connect(self.heaviest_edges)
        if not self.hypergraph.is_weighted():
            self.spin_box.setVisible(False)
            self.spin_box_label.setVisible(False)

        self.combobox_drawing = self.create_algorithm_options()
        redraw = QPushButton("Redraw")
        redraw.clicked.connect(self.redraw)

        self.centrality_combobox = self.create_centrality_button()

        def activate_function():
            self.options_dict[self.combobox_drawing.currentText()]()
        combobox_communities = self.create_community_detection_options()
        self.combobox_drawing.currentTextChanged.connect(activate_function)

        drawing_label = QLabel("Drawing Algorithm:")

        self.vbox.addWidget(drawing_label)
        self.vbox.addWidget(self.combobox_drawing)

        community_label = QLabel("Community Detection Algorithm:")
        self.vbox.addWidget(community_label)
        self.vbox.addWidget(combobox_communities)
        centrality_label = QLabel("Centrality Calculation Method:")
        self.vbox.addWidget(centrality_label)
        self.vbox.addWidget(self.centrality_combobox)
        self.vbox.addWidget(self.spin_box_label)
        self.vbox.addWidget(self.spin_box)
        self.vbox.addWidget(redraw)

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

    def create_algorithm_options(self) -> QComboBox:
        """
        Create the selection list for the visualization function
        """
        combobox = QComboBox()
        if isinstance(self.hypergraph, TemporalHypergraph):
            self.options_dict = { "PAOH": self.assign_PAOH}
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.options_dict = { "Extra-Node": self.assign_extra_node, "PAOH": self.assign_PAOH,"Radial": self.assign_radial,
                                  "Bipartite": self.assign_bipartite }
        else:
            self.options_dict = {"Sets": self.assign_sets, "PAOH": self.assign_PAOH,"Radial": self.assign_radial,
                         "Extra-Node": self.assign_extra_node, "Bipartite": self.assign_bipartite}
            if not self.hypergraph.is_weighted():
                self.options_dict["Clique"] = self.assign_clique_projection

        combobox.addItems(list(self.options_dict.keys()))
        def activate_function():
            self.options_dict[combobox.currentText()]()
        combobox.currentTextChanged.connect(activate_function)
        return combobox
    def add_algorithm_options_button(self, widget, list, func):
        list.clear()
        for x in widget.widget_list:
            myQListWidgetItem = QListWidgetItem(list)
            myQListWidgetItem.setSizeHint(x.sizeHint())
            list.addItem(myQListWidgetItem)
            list.setItemWidget(myQListWidgetItem, x)
        widget.modified_options.connect(func)

def clear_layout(layout: QLayout):
    """
    Function to clear a QLayout
    Parameters
    ----------
    layout: QLayout
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

def start_interactive_view(h: Hypergraph|TemporalHypergraph|DirectedHypergraph) -> None:
    """
    Wrapper function used to start the interactive view.
    Parameters
    ----------
    h: Hypergraph or TemporalHypergraph or DirectedHypergraph
    """
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    faulthandler.enable()
    main = Window(hypergraph=h)
    main.show()

    sys.exit(app.exec_())

h = Hypergraph([("A","B","C"),('D','C')])
start_interactive_view(h)