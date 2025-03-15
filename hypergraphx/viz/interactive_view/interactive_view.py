import copy
import ctypes
import faulthandler
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QTabWidget, QLayout, QMainWindow, QStackedLayout
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
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.draw_sets import draw_sets
from hypergraphx.viz.interactive_view.__graphic_option_menu import GraphicOptionsWidget
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.custom_widgets import WaitingScreen, SliderDockWidget
from hypergraphx.viz.interactive_view.drawing_options_widget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.hypergraph_editing_view import ModifyHypergraphMenu


class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep+ 'logo_cropped.png'))
        if "win" in sys.platform:
            myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.heaviest_edges_value = 1.0

        #Set Default Values
        self.weight_positioning = 0
        self.community_algorithm_option_gui = None
        self.community_options_dict = CommunityOptionsDict()
        self.algorithm_options_dict = dict()
        self.tab = None
        self.community_options_tab = None
        self.community_options_list = None
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
        self.drawing_options = None
        self.last_pos = dict()
        self.stacked = QStackedLayout()
        self.max_edge = max(h.distribution_sizes().keys())
        self.slider_value = (2, self.max_edge)
        #Defines Canvas and Options Toolbar
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_hbox.addWidget(self.canvas, 80)
        self.community_model = None
        # Sliders Management
        # Create layout and add everything
        self.main_layout = QMainWindow()
        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.main_layout.setCentralWidget(self.canvas)
        self.slider = SliderDockWidget(self.max_edge)
        self.slider.update_value.connect(self.new_slider_value)
        self.main_layout.addDockWidget(Qt.BottomDockWidgetArea, self.slider)


        # setting layout to the main window

        self.central_tab = QTabWidget()
        self.stacked.addWidget(self.main_layout)
        drawing_tab = QWidget()
        drawing_tab.setLayout(self.stacked)
        modify_hypergraph_tab = ModifyHypergraphMenu(hypergraph)
        modify_hypergraph_tab.updated_hypergraph.connect(self.update_hypergraph)
        self.central_tab.addTab(drawing_tab, "Drawing Area")
        self.central_tab.addTab(modify_hypergraph_tab, "Modify Hypergraph")


        azdd = QVBoxLayout()
        azdd.addWidget(self.central_tab)
        self.setLayout(azdd)
        self.use_default()
        self.stacked.addWidget(WaitingScreen())
        self.drawing_options_widget = DrawingOptionsDockWidget(n_nodes = self.hypergraph.num_nodes())
        self.drawing_options_widget.update_value.connect(self.must_change_name)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
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
            self.current_function = draw_PAOH
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.current_function = draw_extra_node
        else:
            self.current_function = draw_sets
        self.plot()
    def must_change_name(self, input):
        self.change_focus()
        self.heaviest_edges_value = input["%_heaviest_edges"]
        if input["drawing_options"] == "Sets":
            self.current_function = draw_sets
        elif input["drawing_options"] == "PAOH":
            self.current_function = draw_PAOH
        elif input["drawing_options"] == "Radial":
            self.current_function = draw_radial_layout
        elif input["drawing_options"] == "Extra-Node":
            self.current_function = draw_extra_node
        elif input["drawing_options"] == "Bipartite":
            self.current_function = draw_bipartite
        elif input["drawing_options"] == "Clique":
            self.current_function = draw_clique
        if input["centrality"] == "No Centrality":
            self.centrality = None
        elif input["centrality"] == "Degree Centrality":
            self.centrality = degree_sequence(self.hypergraph)
            mean = sum(self.centrality.values()) / len(self.centrality)
            for k, v in self.centrality.items():
                self.centrality[k] = v / mean
        self.community_options_dict.update(input["community_options"])
        if input["use_last"]:
            self.use_last = True
        else:
            self.use_last = False
        if not self.use_last:
            if input["community_detection_algorithm"] == "None":
                self.no_community()
            elif input["community_detection_algorithm"] == "Hypergraph Spectral Clustering":
                self.use_spectral_clustering()
            elif input["community_detection_algorithm"] == "Hypergraph-MT":
                self.use_MT()
            elif input["community_detection_algorithm"] == "Hy-MMSBM":
                self.use_MMSBM()
        match input["weight_influence"]:
            case "No Relationship":
                self.weight_positioning = 0
            case "Directly Proportional":
                self.weight_positioning = 1
            case "Inversely Proportional":
                self.weight_positioning = 2
        self.algorithm_options_dict = input["algorithm_options"]
        self.graphic_options = input["graphic_options"]
        self.extra_attributes = input["extra_attributes"]
        self.plot()
        self.change_focus()

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
        if self.algorithm_options_dict is None:
            self.algorithm_options_dict = {}
        #Plot and draw the hypergraph using it's function
        self.last_pos = self.current_function(self.hypergraph, cardinality= self.slider_value, x_heaviest = self.heaviest_edges_value, ax=ax,
                time_font_size = time_font_size, time_separation_line_color = time_separation_line_color,k=self.community_options_dict["number_communities"],
                graphicOptions=copy.deepcopy(self.graphic_options), radius_scale_factor=radius_scale_factor, font_spacing_factor=font_spacing_factor,
                time_separation_line_width = time_separation_line_width, polygon_expansion_factor = polygon_expansion_factor, weight_positioning = self.weight_positioning,
                rounding_radius_size = rounding_radius_size, hyperedge_alpha = hyperedge_alpha,pos = last_pos, u = self.community_model, **self.algorithm_options_dict)
        self.use_last = False
        self.canvas.draw()
        self.change_focus()
    #Get Support for Options
    def update_hypergraph(self, example = None, hypergraph = None):
        self.community_model = None
        self.main_layout.removeDockWidget(self.drawing_options_widget)
        self.drawing_options_widget.deleteLater()
        self.drawing_options_widget = None
        self.change_focus()
        if example is not None:
            self.hypergraph = example["hypergraph"]
        if hypergraph is not None:
            self.hypergraph = hypergraph
        self.max_edge = max(self.hypergraph.get_sizes())
        if isinstance(self.hypergraph, Hypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="normal",n_nodes=self.hypergraph.num_nodes())
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="directed",n_nodes=self.hypergraph.num_nodes())
        elif isinstance(self.hypergraph, TemporalHypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="temporal",n_nodes=len(self.hypergraph.get_nodes()))
        self.drawing_options_widget.update_value.connect(self.must_change_name)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
        self.drawing_options_widget.update()
        self.change_focus()
        self.use_default()
        self.slider.update_max(self.max_edge)

    #Community
    def use_spectral_clustering(self):
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
        self.community_model = None

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