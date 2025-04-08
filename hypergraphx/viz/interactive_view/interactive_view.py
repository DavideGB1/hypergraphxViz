import copy
import ctypes
import faulthandler
import multiprocessing
import os
import sys
from copy import deepcopy

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QTabWidget, QMainWindow, QStackedLayout
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.communities.hy_mmsbm.model import HyMMSBM
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.communities.hypergraph_mt.model import HypergraphMT
from hypergraphx.measures.degree import degree_sequence
from hypergraphx.measures.s_centralities import s_betweenness_nodes, s_betweenness_nodes_averaged
from hypergraphx.utils import normalize_array
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.draw_sets import draw_sets
from hypergraphx.viz.interactive_view.__graphic_option_menu import GraphicOptionsWidget
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.custom_widgets import SliderDockWidget, LoadingScreen
from hypergraphx.viz.interactive_view.drawing_options_widget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.hypergraph_editing_view import ModifyHypergraphMenu
from hypergraphx.viz.interactive_view.pool_singleton import PoolSingleton
from hypergraphx.viz.interactive_view.stats_view import HypergraphStatsWidget

class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")
        #Used in order to avoid copying useless data when creating childrens
        pool = PoolSingleton()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(script_dir + os.path.sep+ 'logo_cropped.png'))
        if "win" in sys.platform:
            myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.community_algorithm = "None"
        self.heaviest_edges_value = 1.0
        self.thread_community = None
        #Set Default Values
        self.thread = None
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
        self.current_function = "PAOH"
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
        self.slider_value = (2, self.hypergraph.max_size())
        #Defines Canvas and Options Toolbar
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.canvas_hbox.addWidget(self.canvas, 80)
        self.community_model = None
        # Sliders Management
        # Create layout and add everything
        self.main_layout = QMainWindow()
        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.main_layout.setCentralWidget(self.canvas)
        self.slider = SliderDockWidget(self.hypergraph.max_size())
        self.slider.update_value.connect(self.new_slider_value)
        self.main_layout.addDockWidget(Qt.BottomDockWidgetArea, self.slider)


        # setting layout to the main window

        self.central_tab = QTabWidget()
        self.stacked.addWidget(self.main_layout)
        drawing_tab = QWidget()
        drawing_tab.setLayout(self.stacked)
        self.central_tab.addTab(drawing_tab, "Drawing Area")
        self.stats_tab = HypergraphStatsWidget(self.hypergraph)
        self.central_tab.addTab(self.stats_tab, "Statistics")
        modify_hypergraph_tab = ModifyHypergraphMenu(hypergraph)
        modify_hypergraph_tab.updated_hypergraph.connect(self.update_hypergraph)
        self.central_tab.addTab(modify_hypergraph_tab, "Edit Hypergraph")


        azdd = QVBoxLayout()
        azdd.addWidget(self.central_tab)
        self.setLayout(azdd)
        self.stacked.addWidget(LoadingScreen())
        self.drawing_options_widget = DrawingOptionsDockWidget(n_nodes = self.hypergraph.num_nodes())
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
        self.use_default()

    #Drawing
    def plot(self):
        """
        Plot the hypergraph on screen using the assigner draw function.
        """
        #Clears the plot
        dictionary = dict()
        dictionary["slider_value"] = self.slider_value
        dictionary["centrality"] = self.centrality
        dictionary["algorithm_options_dict"] = self.algorithm_options_dict
        dictionary["heaviest_edges_value"] = self.heaviest_edges_value
        dictionary["community_options_dict"] = self.community_options_dict
        dictionary["weight_positioning"] = self.weight_positioning
        dictionary["extra_attributes"] = self.extra_attributes
        if self.use_last:
            dictionary["last_pos"] = self.last_pos
        else:
            dictionary["last_pos"] = None
        dictionary["community_model"] = self.community_model
        dictionary["algorithm_options_dict"] = self.algorithm_options_dict
        dictionary["graphic_options"] = self.graphic_options
        if self.thread is None:
            self.change_focus()
            pool = PoolSingleton()
            self.thread = PlotWorker(self.current_function, self.hypergraph, dictionary, pool.get_pool(), self.community_model, self.community_algorithm, self.community_options_dict, self.use_last)
            self.thread.progress.connect(self.drawn)
            self.thread.start()
        self.use_last = False

    def drawn(self, value_list):
        self.last_pos = value_list[0]
        self.figure = value_list[1]
        self.community_model = value_list[2]
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.removeToolBar(self.toolbar)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.main_layout.setCentralWidget(self.canvas)
        self.canvas.draw()
        self.change_focus()
        self.thread = None

    def change_focus(self):
        """
        Changes the focus of the stacked widget.

        The method toggles the current index of the `stacked` widget
        between 0 and 1. If the current index is 0, it changes to 1;
        otherwise, it changes to 0. After changing the index, the
        `repaint()` method is called to refresh the widget.
        """
        if self.stacked.currentIndex() == 0:
            self.stacked.setCurrentIndex(1)
        else:
            self.stacked.setCurrentIndex(0)
        self.repaint()

    #Get Update Data
    def update_hypergraph(self, example = None, hypergraph = None):
        """
        Updates the hypergraph instance with new data and corresponding UI components.

        Parameters
        ----------
        example : dict, optional
            Dictionary containing a key "hypergraph" which holds the new hypergraph data.
        hypergraph : Hypergraph, DirectedHypergraph, or TemporalHypergraph, optional
            A new hypergraph instance to update the current hypergraph.
        """
        self.community_model = None
        self.main_layout.removeDockWidget(self.drawing_options_widget)
        self.drawing_options_widget.deleteLater()
        self.drawing_options_widget = None
        if example is not None:
            self.hypergraph = example["hypergraph"]
        if hypergraph is not None:
            self.hypergraph = hypergraph
        self.slider_value = (2, self.hypergraph.max_size())
        if isinstance(self.hypergraph, Hypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="normal",n_nodes=self.hypergraph.num_nodes())
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="directed",n_nodes=self.hypergraph.num_nodes())
        elif isinstance(self.hypergraph, TemporalHypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="temporal",n_nodes=len(self.hypergraph.get_nodes()))
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
        self.drawing_options_widget.update()
        self.slider.update_max(self.hypergraph.max_size())
        self.use_default()
        self.stats_tab.update_hypergraph(self.hypergraph)

    def get_new_drawing_options(self, input_dictionary):
        """
        Parameters
        ----------
        input_dictionary : dict
            A dictionary containing configurations and options for updating drawing parameters. Expected keys include:
            - "%_heaviest_edges" : Sets the value for `heaviest_edges_value`.
            - "drawing_options" : Specifies the drawing function to assign to `current_function`, options include "Sets", "PAOH", "Radial", "Extra-Node", "Bipartite", "Clique".
            - "centrality" : Specifies the type of centrality to use, options include "No Centrality", "Degree Centrality", "Betweenness Centrality", "Adjacency Factor (t=1)", and "Adjacency Factor (t=2)".
            - "community_options" : Updates the `community_options_dict` with existing options in the input.
            - "use_last" : Boolean flag denoting whether to reuse the last community configuration.
            - "community_detection_algorithm" : Specifies the community detection algorithm to be used when `use_last` is False. Options include "None", "Hypergraph Spectral Clustering", "Hypergraph-MT", and "Hy-MMSBM".
            - "weight_influence" : Specifies the relationship for weight positioning, options include "No Relationship", "Directly Proportional", and "Inversely Proportional".
            - "algorithm_options" : Specifies additional algorithm-related options to configure.
            - "graphic_options" : Specifies graphic-related options for plotting.
            - "extra_attributes" : Additional attributes for the plot.

        Notes
        -----
        Certain keys in the input dictionary trigger specific functions or calculations based on their values.
        The function ties together drawing settings, centrality calculations, community detection algorithms, and plotting configurations.
        This function involves normalization of centrality measures in applicable cases.
        The function updates graphical rendering and custom attributes before finalizing with `plot()`.
        """
        self.heaviest_edges_value = input_dictionary["%_heaviest_edges"]
        self.current_function = input_dictionary["drawing_options"]
        match input_dictionary["centrality"]:
            case "No Centrality":
                self.centrality = None
            case "Degree Centrality":
                self.centrality = degree_sequence(self.hypergraph)
                self.normalize_centrality()
            case "Betweenness Centrality":
                if isinstance(self.hypergraph, TemporalHypergraph):
                    self.centrality = s_betweenness_nodes_averaged(self.hypergraph)
                else:
                    self.centrality = s_betweenness_nodes(self.hypergraph)
                for k in self.centrality.keys():
                    self.centrality[k] *= 2
                    self.centrality[k] += 0.5
                self.normalize_centrality()
            case "Adjacency Factor (t=1)":
                self.centrality = self.hypergraph.adjacency_factor( t= 1)
                self.normalize_centrality()
            case "Adjacency Factor (t=2)":
                self.centrality = self.hypergraph.adjacency_factor( t= 2)
                self.normalize_centrality()
        self.community_options_dict.update(input_dictionary["community_options"])
        self.use_last = input_dictionary["use_last"]
        self.community_algorithm = input_dictionary["community_detection_algorithm"]
        match input_dictionary["weight_influence"]:
            case "No Relationship":
                self.weight_positioning = 0
            case "Directly Proportional":
                self.weight_positioning = 1
            case "Inversely Proportional":
                self.weight_positioning = 2
        self.algorithm_options_dict = input_dictionary["algorithm_options"]
        self.graphic_options = input_dictionary["graphic_options"]
        self.extra_attributes = input_dictionary["extra_attributes"]
        self.plot()

    def new_slider_value(self, value):
        """
        gets the new slider value and refreshes the plot.

        Parameters
        ----------
        value : numeric
            The new value to update the slider with.
        """
        self.slider_value = value
        self.plot()

    # Support
    def normalize_centrality(self):
        """
        Normalizes the centrality scores stored in the `self.centrality` dictionary
        by dividing each centrality value by the mean centrality value. This ensures
        that the centrality values are relative to the mean and scaled proportionally.

        Returns
        -------
        None
            The method updates the `self.centrality` dictionary in place.
        """
        mean = sum(self.centrality.values()) / len(self.centrality)
        for k, v in self.centrality.items():
            self.centrality[k] = v / mean

    def use_default(self):
        """
        Determines and sets the appropriate drawing function based on the type of the hypergraph attribute and then executes the plotting operation.

        Notes
        -----
        - If `hypergraph` is an instance of `TemporalHypergraph`, the drawing function is set to `draw_PAOH`.
        - If `hypergraph` is an instance of `DirectedHypergraph`, the drawing function is set to `draw_extra_node`.
        - For other types of `hypergraph`, the drawing function defaults to `draw_sets`.
        """
        if isinstance(self.hypergraph, TemporalHypergraph):
            self.current_function = "PAOH"
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.current_function = "Extra-Node"
        else:
            self.current_function = "Sets"
        self.plot()

def create_figure(draw_function, hypergraph, dictionary):
    figure = plt.figure()
    figure.clear()
    ax = figure.add_subplot(111)
    extra_attributes = dictionary["extra_attributes"]
    if draw_function == "Sets":
        function = draw_sets
    elif draw_function == "PAOH":
        function = draw_PAOH
    elif draw_function == "Radial":
        function = draw_radial_layout
    elif draw_function == "Extra-Node":
        function = draw_extra_node
    elif draw_function == "Bipartite":
        function = draw_bipartite
    elif draw_function == "Clique":
        function = draw_clique
    # Try to get the extra attributes
    try:
        radius_scale_factor = extra_attributes["radius_scale_factor"]
    except KeyError:
        radius_scale_factor = 1.0
    try:
        font_spacing_factor = extra_attributes["font_spacing_factor"]
    except KeyError:
        font_spacing_factor = 1.5
    try:
        time_font_size = extra_attributes["time_font_size"]
    except KeyError:
        time_font_size = 18
    try:
        time_separation_line_color = extra_attributes["time_separation_line_color"]
    except KeyError:
        time_separation_line_color = "#000000"
    try:
        time_separation_line_width = extra_attributes["time_separation_line_width"]
    except KeyError:
        time_separation_line_width = 4
    try:
        rounding_radius_size = extra_attributes["rounding_radius_factor"]
    except KeyError:
        rounding_radius_size = 0.1
    try:
        polygon_expansion_factor = extra_attributes["polygon_expansion_factor"]
    except KeyError:
        polygon_expansion_factor = 1.8
    try:
        hyperedge_alpha = extra_attributes["hyperedge_alpha"]
    except KeyError:
        hyperedge_alpha = 0.8

    if dictionary["centrality"] is not None:
        dictionary["graphic_options"].add_centrality_factor_dict(dictionary["centrality"])
    else:
        dictionary["graphic_options"].add_centrality_factor_dict(None)
    if dictionary["algorithm_options_dict"] is None:
        dictionary["algorithm_options_dict"] = {}
    # Plot and draw the hypergraph using it's function
    position = function(hypergraph, cardinality=dictionary["slider_value"],
                                          x_heaviest= dictionary["heaviest_edges_value"], ax=ax,
                                          time_font_size=time_font_size,
                                          time_separation_line_color=time_separation_line_color,
                                          k= dictionary["community_options_dict"]["number_communities"],
                                          graphicOptions=copy.deepcopy(dictionary["graphic_options"]),
                                          radius_scale_factor=radius_scale_factor,
                                          font_spacing_factor=font_spacing_factor,
                                          time_separation_line_width=time_separation_line_width,
                                          polygon_expansion_factor=polygon_expansion_factor,
                                          weight_positioning= dictionary["weight_positioning"],
                                          rounding_radius_size=rounding_radius_size, hyperedge_alpha=hyperedge_alpha,
                                          pos=dictionary["last_pos"], u= dictionary["community_model"], **dictionary["algorithm_options_dict"])
    return [position, deepcopy(figure)]

def run_community_detection(hypergraph, algorithm, community_options):
    """
    Worker function to perform community detection in a separate process.

    Args:
        hypergraph: The Hypergraph object.
        algorithm: The name of the community detection algorithm
                   ('HySC', 'HypergraphMT', 'Hy-MMSBM', or 'None').
        community_options: Dictionary of options for the algorithm.

    Returns:
        The community model (e.g., membership matrix) or None.
    """
    if algorithm == "Hypergraph Spectral Clustering":
        model = HySC(
            seed=community_options["seed"],
            n_realizations=community_options["realizations"]
        )
        community_model = model.fit(
            hypergraph,
            K=community_options["number_communities"],
            weighted_L=False
        )
    elif algorithm == "Hypergraph-MT":
        model = HypergraphMT(
            n_realizations=community_options["realizations"],
            max_iter=community_options["max_iterations"],
            check_convergence_every=community_options["check_convergence_every"],
            verbose=False
        )
        u, _, _ = model.fit(
            hypergraph,
            K=community_options["number_communities"],
            seed=community_options["seed"],
            normalizeU=community_options["normalizeU"],
            baseline_r0=community_options["baseline_r0"],
        )
        community_model = normalize_array(u, axis=1)
    elif algorithm == "Hy-MMSBM":
        best_model = None
        best_loglik = float("-inf")
        for j in range(community_options["realizations"]):
            model = HyMMSBM(
                K=community_options["number_communities"],
                assortative=community_options["assortative"]
            )
            model.fit(
                hypergraph,
                n_iter=community_options["max_iterations"],
            )

            log_lik = model.log_likelihood(hypergraph)
            if log_lik > best_loglik:
                best_model = model
                best_loglik = log_lik

        community_model = normalize_array(best_model.u, axis=1)
    elif algorithm == "None":
        community_model = None
    else:
        raise ValueError(f"Unknown community detection algorithm: {algorithm}")
    return community_model

class PlotWorker(QThread):
    progress = pyqtSignal(list)

    def __init__(self, draw_function, hypergraph, input_dictionary, pool, model, community_algorithm, community_options, use_last, parent=None):
        super(PlotWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.draw_function = draw_function
        self.input_dictionary = input_dictionary
        self.pool = pool
        self.model = model
        self.use_last = use_last
        self.community_algorithm = community_algorithm
        self.community_options = community_options

    def run(self):
        if not self.use_last:
            self.model = self.pool.apply(run_community_detection, args=(self.hypergraph, self.community_algorithm, self.community_options))
            self.input_dictionary["community_model"] = self.model
        else:
            self.model = self.input_dictionary["community_model"]
        results = self.pool.apply(create_figure, args=(self.draw_function, self.hypergraph, self.input_dictionary))
        results.append(self.model)
        self.progress.emit(results)

def start_interactive_view(h: Hypergraph|TemporalHypergraph|DirectedHypergraph) -> None:
    """
    Wrapper function used to start the interactive view.
    Parameters
    ----------
    h: Hypergraph or TemporalHypergraph or DirectedHypergraph
    """
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        app = QApplication(sys.argv)

        faulthandler.enable()
        main = Window(hypergraph=h)
        main.show()
        sys.exit(app.exec_())

h = Hypergraph([("A", "B", "C"), ('D', 'C')])
start_interactive_view(h)
