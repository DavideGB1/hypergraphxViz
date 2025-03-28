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
from hypergraphx.viz.interactive_view.custom_widgets import WaitingScreen, SliderDockWidget
from hypergraphx.viz.interactive_view.drawing_options_widget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.hypergraph_editing_view import ModifyHypergraphMenu
from hypergraphx.viz.interactive_view.stats_view import HypergraphStatsWidget


def plot(draw_function, hypergraph, output, dictionary, graphic_options):
    figure = plt.figure()
    figure.clear()
    ax = figure.add_subplot(111)

    extra_attributes = dictionary["extra_attributes"]
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
        graphic_options.add_centrality_factor_dict(dictionary["centrality"])
    else:
        graphic_options.add_centrality_factor_dict(None)
    if dictionary["algorithm_options_dict"] is None:
        dictionary["algorithm_options_dict"] = {}
    # Plot and draw the hypergraph using it's function
    position = draw_function(hypergraph, cardinality=dictionary["slider_value"],
                                          x_heaviest= dictionary["heaviest_edges_value"], ax=ax,
                                          time_font_size=time_font_size,
                                          time_separation_line_color=time_separation_line_color,
                                          k= dictionary["community_options_dict"]["number_communities"],
                                          graphicOptions=copy.deepcopy(graphic_options),
                                          radius_scale_factor=radius_scale_factor,
                                          font_spacing_factor=font_spacing_factor,
                                          time_separation_line_width=time_separation_line_width,
                                          polygon_expansion_factor=polygon_expansion_factor,
                                          weight_positioning= dictionary["weight_positioning"],
                                          rounding_radius_size=rounding_radius_size, hyperedge_alpha=hyperedge_alpha,
                                          pos=dictionary["last_pos"], u= dictionary["community_model"], **dictionary["algorithm_options_dict"])
    output.put([position, deepcopy(figure)])

class PlotWorker(QThread):
    progress = pyqtSignal(list)

    def __init__(self, draw_function, hypergraph, output_queue, input_dictionary, graphic_options, parent=None):
        super(PlotWorker, self).__init__(parent)
        self.output_queue = output_queue
        self.hypergraph = hypergraph
        self.draw_function = draw_function
        self.input_dictionary = input_dictionary
        self.graphic_options = graphic_options
        self.process = None

    def run(self):
        self.process = multiprocessing.Process(target=plot,
                                               args=(self.draw_function,
                                                   self.hypergraph,
                                                     self.output_queue,
                                                    self.input_dictionary,
                                                     self.graphic_options
                                            ))
        self.process.start()
        self.process.join()
        res = self.output_queue.get()
        self.progress.emit(res)

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
        self.output_queue = multiprocessing.Queue()
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
        self.slider_value = (2, self.hypergraph.max_size())
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
        self.use_default()
        self.stacked.addWidget(WaitingScreen())
        self.drawing_options_widget = DrawingOptionsDockWidget(n_nodes = self.hypergraph.num_nodes())
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)

    #Drawing
    def plot(self):
        """
        Plot the hypergraph on screen using the assigner draw function.
        """
        #Clears the plot
        self.change_focus()
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
        self.thread = PlotWorker(self.current_function, self.hypergraph, self.output_queue, dictionary,copy.deepcopy(self.graphic_options))
        self.thread.progress.connect(self.drawn)
        self.thread.start()
        self.use_last = False
    def drawn(self, value_list):
        print("MAMMATA")
        self.last_pos = value_list[0]
        self.figure = value_list[1]
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.main_layout.setCentralWidget(self.canvas)
        self.canvas.draw()
        self.change_focus()

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
        self.change_focus()
        if example is not None:
            self.hypergraph = example["hypergraph"]
        if hypergraph is not None:
            self.hypergraph = hypergraph
        if isinstance(self.hypergraph, Hypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="normal",n_nodes=self.hypergraph.num_nodes())
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="directed",n_nodes=self.hypergraph.num_nodes())
        elif isinstance(self.hypergraph, TemporalHypergraph):
            self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.hypergraph.is_weighted(),hypergraph_type="temporal",n_nodes=len(self.hypergraph.get_nodes()))
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
        self.drawing_options_widget.update()
        self.change_focus()
        self.use_default()
        self.slider.update_max(self.hypergraph.max_size())
        self.stats_tab.update_hypergraph(self.hypergraph)

    def get_new_drawing_options(self, input):
        """
        Parameters
        ----------
        input : dict
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
            self.normalize_centrality()
        elif input["centrality"] == "Betweenness Centrality":
            if isinstance(self.hypergraph, TemporalHypergraph):
                self.centrality = s_betweenness_nodes_averaged(self.hypergraph)
            else:
                self.centrality = s_betweenness_nodes(self.hypergraph)
            for k in self.centrality.keys():
                self.centrality[k] *= 2
                self.centrality[k] += 0.5
            self.normalize_centrality()
        elif input["centrality"] == "Adjacency Factor (t=1)":
            self.centrality = self.hypergraph.adjacency_factor( t= 1)
            self.normalize_centrality()
        elif input["centrality"] == "Adjacency Factor (t=2)":
            self.centrality = self.hypergraph.adjacency_factor( t= 2)
            self.normalize_centrality()
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

    #Community
    def use_spectral_clustering(self):
        """
        Uses spectral clustering to determine community structure within a hypergraph.

        This method initializes a HySC model with the given configuration, fits the model
        to the provided hypergraph to identify community groupings, and stores the fitted
        model.

        Parameters
        ----------
        self : object
            Instance of the calling object, expected to contain:
            - `hypergraph`: The hypergraph data structure on which community detection will be performed.
            - `community_options_dict`: A dictionary containing options for community detection:
                * `seed`: Integer seed value for reproducibility.
                * `realizations`: Number of realizations to be used in clustering.
                * `number_communities`: Target number of communities for clustering.

        Side Effects
        ------------
        Updates the `community_model` attribute of the instance with the fitted HySC model.

        Raises
        ------
        KeyError
            If required keys are missing in `community_options_dict`.

        TypeError
            If `hypergraph` or `community_options_dict` is of invalid type.

        Notes
        -----
        Spectral clustering is performed by constructing and utilizing a spectral representation of
        the hypergraph's adjacency structure, followed by fitting the HySC model with the specified
        community count and additional parameters.
        """
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
        """
        Use the Hypergraph Model Testing (HypergraphMT) for community detection in hypergraphs.

        This method initializes and fits the HypergraphMT model using the parameters specified
        in the `community_options_dict` for detecting communities in the provided hypergraph.
        It normalizes the resulting community membership matrix and assigns it as the community model.

        Parameters
        ----------
        self : object
            The instance of the class containing this method. It is expected to have `community_options_dict`
            and `hypergraph` as attributes.

        Attributes Updated
        ------------------
        self.community_model : ndarray
            A normalized 2D array representing the community membership matrix generated by HypergraphMT.
        """
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
        """
        Fits a Mixed Membership Stochastic Block Model (MMSBM) to the hypergraph data.

        The method iteratively trains multiple MMSBM models on the hypergraph and
        selects the one that maximizes the log-likelihood. The selected model's
        membership matrix is then normalized for further use.

        Attributes
        ----------
        community_options_dict : dict
            A dictionary containing configuration parameters such as:
            - "realizations": Number of models to train and compare.
            - "number_communities": The number of communities assumed in the MMSBM.
            - "assortative": Whether to enforce assortativity in the model structure.
            - "max_iterations": The maximum number of iterations for MMSBM fitting.
        hypergraph : object
            The hypergraph data structure on which the MMSBM is fitted.
        community_model : ndarray
            The normalized membership matrix resulting from the best MMSBM model.

        Method Workflow
        ---------------
        1. Initializes multiple MMSBM models with the provided configuration.
        2. Fits each model to the hypergraph for a predefined number of iterations.
        3. Evaluates the log-likelihood of each model to select the best one.
        4. Sets the best model's normalized membership matrix as the output.
        """
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

        self.community_model = best_model.u
        self.community_model = normalize_array(self.community_model, axis=1)

    def no_community(self):
        """
        Sets the community model attribute to None.

        This method resets the community model associated with the instance, effectively removing any community model previously assigned.
        """
        self.community_model = None

    # Support
    def normalize_centrality(self):
        """
        Normalizes the centrality scores stored in the `self.centrality` dictionary
        by dividing each centrality value by the mean centrality value. This ensures
        that the centrality values are relative to the mean and scaled proportionally.

        Parameters
        ----------
        None

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

        Attributes
        ----------
        hypergraph : object
            The hypergraph instance whose type is used to determine the drawing function.

        current_function : function
            The function that will be used to draw the hypergraph, based on its type.

        Methods
        -------
        plot()
            Executes the plotting operation using the current_function.

        Notes
        -----
        - If `hypergraph` is an instance of `TemporalHypergraph`, the drawing function is set to `draw_PAOH`.
        - If `hypergraph` is an instance of `DirectedHypergraph`, the drawing function is set to `draw_extra_node`.
        - For other types of `hypergraph`, the drawing function defaults to `draw_sets`.
        """
        if isinstance(self.hypergraph, TemporalHypergraph):
            self.current_function = draw_PAOH
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.current_function = draw_extra_node
        else:
            self.current_function = draw_sets
        self.plot()

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

h = Hypergraph([("A","B","C"),('D','C')])
start_interactive_view(h)