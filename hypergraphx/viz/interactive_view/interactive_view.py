import ctypes
import faulthandler
import multiprocessing
import os
import sys
import tracemalloc
import copy
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, \
    QDoubleSpinBox, QTabWidget, QMainWindow, QStackedLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from memory_profiler import profile

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.communities.hy_mmsbm.model import HyMMSBM
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.communities.hypergraph_mt.model import HypergraphMT
from hypergraphx.measures.degree import degree_sequence
from hypergraphx.measures.s_centralities import s_betweenness_nodes, s_betweenness_nodes_averaged
from hypergraphx.utils import normalize_array
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.draw_PAOH import draw_PAOH, calculate_paoh_layout, draw_paoh_from_data
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique, \
    _compute_bipartite_drawing_data, _compute_clique_drawing_data, _compute_extra_node_drawing_data, \
    _draw_bipartite_on_ax, _draw_clique_on_ax, _draw_extra_node_on_ax
from hypergraphx.viz.draw_radial import draw_radial_layout, _compute_radial_layout, _draw_radial_elements
from hypergraphx.viz.draw_sets import draw_sets, _compute_set_layout, _draw_set_elements
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.custom_widgets import SliderDockWidget, LoadingScreen
from hypergraphx.viz.interactive_view.drawing_options_widget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.hypergraph_editing_view import ModifyHypergraphMenu
from hypergraphx.viz.interactive_view.stats_view import HypergraphStatsWidget

class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")
        #Used in order to avoid copying useless data when creating childrens
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(script_dir + os.path.sep+ 'logo_cropped.png'))
        if "win" in sys.platform and "darwin" not in sys.platform:
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
        self.algorithm_options_dict = {
            "rounded_polygon":True,
            "draw_labels": True,
            "iterations": 1000,
            "scale_factor": 1
        }
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
        self.extra_attributes = {
            "hyperedge_alpha":0.8,
            "rounding_radius_factor": 0.1,
            "polygon_expansion_factor": 1.8,
        }
        self.graphic_options = GraphicOptions()
        self.slider = None
        self.community_option_menu = None
        self.option_menu = None
        self.hypergraph = hypergraph
        self.figure = Figure()
        self.drawing_options = None
        self.last_pos = dict()
        self.slider_value = (2, self.hypergraph.max_size())
        #Defines Canvas and Options Toolbar
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.community_model = None
        # Sliders Management
        # Create layout and add everything
        self.main_layout = QMainWindow(parent=self)

        self.canvas = FigureCanvas(self.figure)
        self.main_layout.setCentralWidget(self.canvas)

        self.toolbar = NavigationToolbar(parent= self.main_layout, canvas = self.canvas)
        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)


        self.slider = SliderDockWidget(self.hypergraph.max_size(),parent=self.main_layout)
        self.slider.update_value.connect(self.new_slider_value)
        self.main_layout.addDockWidget(Qt.BottomDockWidgetArea, self.slider)

        self.loading = False


        # setting layout to the main window

        self.central_tab = QTabWidget(parent=self)
        drawing_tab = QWidget(parent=self.central_tab)
        self.central_tab.addTab(drawing_tab, "Drawing Area")
        self.stats_tab = HypergraphStatsWidget(self.hypergraph, parent=self.central_tab)
        self.central_tab.addTab(self.stats_tab, "Statistics")
        modify_hypergraph_tab = ModifyHypergraphMenu(hypergraph,parent=self.central_tab)
        modify_hypergraph_tab.updated_hypergraph.connect(self.update_hypergraph)
        self.central_tab.addTab(modify_hypergraph_tab, "Edit Hypergraph")


        self.drawing_options_widget = DrawingOptionsDockWidget(n_nodes = self.hypergraph.num_nodes(), parent=self.main_layout)
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)

        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.main_layout)
        self.stacked.addWidget(LoadingScreen())

        drawing_tab.setLayout(self.stacked)

        azdd = QVBoxLayout()
        azdd.addWidget(self.central_tab)
        self.setLayout(azdd)

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
        dictionary["graphic_options"] = self.graphic_options
        if self.thread is not None and not self.thread.isFinished() and self.loading:
            self.thread.terminate()
            self.change_focus()
            self.thread = None

        if self.thread is None:
            self.change_focus()
            self.thread = PlotWorker(self.current_function, self.hypergraph, dictionary,
                                     self.community_model, self.community_algorithm, self.community_options_dict,
                                     self.use_last)
            self.thread.progress.connect(self.drawn)
            self.thread.start()
            self.loading = False
        self.use_last = False

    def drawn(self, value_list):
        self.graphic_options.add_centrality_factor_dict(value_list[1])
        self.figure.clf()
        if self.current_function == "Sets":
            _draw_set_elements(
                ax=self.figure.gca(),
                data = value_list[0],
                draw_labels= True,
                graphicOptions=self.graphic_options.copy()
            )
        elif self.current_function == "PAOH":
            draw_paoh_from_data(ax=self.figure.gca(), data=value_list[0],graphicOptions=self.graphic_options.copy())
        elif self.current_function == "Radial":
            _draw_radial_elements(
                ax=self.figure.gca(),
                data=value_list[0],
                draw_labels=self.algorithm_options_dict["draw_labels"],
                font_spacing_factor = self.extra_attributes["font_spacing_factor"],
                graphicOptions=self.graphic_options.copy()
            )
        elif self.current_function == "Extra-Node":
            _draw_extra_node_on_ax(
                ax=self.figure.gca(),
                data=value_list[0],
                u = self.community_model,
                show_edge_nodes=self.algorithm_options_dict["show_edge_nodes"],
                draw_labels=self.algorithm_options_dict["draw_labels"],
                graphicOptions=self.graphic_options.copy()
            )
        elif self.current_function == "Bipartite":
            _draw_bipartite_on_ax(
                ax=self.figure.gca(),
                data=value_list[0],
                u = self.community_model,
                draw_labels=self.algorithm_options_dict["draw_labels"],
                align= self.algorithm_options_dict["align"],
                graphicOptions=self.graphic_options.copy()
            )
        elif self.current_function == "Clique":
            _draw_clique_on_ax(
                ax=self.figure.gca(),
                data=value_list[0],
                u=self.community_model,
                draw_labels=self.algorithm_options_dict["draw_labels"],
                graphicOptions=self.graphic_options.copy()
            )

        # Update toolbar to point to the new canvas
        self.main_layout.removeToolBar(self.toolbar)
        self.toolbar.deleteLater()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.canvas.draw()
        self.change_focus()
        if self.thread:
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
        self.loading = True
        self.community_model = None
        if self.drawing_options_widget:
            self.main_layout.removeDockWidget(self.drawing_options_widget)
            self.drawing_options_widget.deleteLater()
            del self.drawing_options_widget
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
        self.centrality = input_dictionary["centrality"]
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
        if input_dictionary["redraw"]:
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
    # Support
    def normalize_centrality(centrality):
        """
        Normalizes the centrality scores stored in the `self.centrality` dictionary
        by dividing each centrality value by the mean centrality value. This ensures
        that the centrality values are relative to the mean and scaled proportionally.

        Returns
        -------
        None
            The method updates the `self.centrality` dictionary in place.
        """
        if centrality is None:
            return None
        mean = sum(centrality.values()) / len(centrality)
        for k, v in centrality.items():
            centrality[k] = v / mean
        return centrality

    centrality = None
    match dictionary["centrality"]:
        case "No Centrality":
            centrality = None
        case "Degree Centrality":
            centrality = degree_sequence(hypergraph)
        case "Betweenness Centrality":
            if isinstance(hypergraph, TemporalHypergraph):
                centrality = s_betweenness_nodes_averaged(hypergraph)
            else:
                centrality = s_betweenness_nodes(hypergraph)
            for k in centrality.keys():
                centrality[k] *= 2
                centrality[k] += 0.5
        case "Adjacency Factor (t=1)":
            centrality = hypergraph.adjacency_factor(t=1)
        case "Adjacency Factor (t=2)":
            centrality = hypergraph.adjacency_factor(t=2)
    centrality = normalize_centrality(centrality)
    if draw_function == "Sets":
        result = _compute_set_layout(
            hypergraph= hypergraph,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
            weight_positioning = 0,
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            iterations=dictionary["algorithm_options_dict"]["iterations"],
            pos=None,
            rounded_polygon = dictionary["algorithm_options_dict"]["rounded_polygon"],
            hyperedge_color_by_order = None,
            hyperedge_facecolor_by_order  = None,
            hyperedge_alpha = dictionary["extra_attributes"]["hyperedge_alpha"],
            scale = dictionary["algorithm_options_dict"]["scale_factor"],
            rounding_radius_size = dictionary["extra_attributes"]["rounding_radius_factor"],
            polygon_expansion_factor = dictionary["extra_attributes"]["polygon_expansion_factor"],
            dummy_nodes = [],
        )
    elif draw_function == "PAOH":
        result = calculate_paoh_layout(
            h=hypergraph,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            space_optimization=dictionary["algorithm_options_dict"]["space_optimization"],
        )
    elif draw_function == "Radial":
        result = _compute_radial_layout(
            h=hypergraph,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            radius_scale_factor=dictionary["extra_attributes"]["radius_scale_factor"],
        )
    elif draw_function == "Extra-Node":
        result = _compute_extra_node_drawing_data(
            h=hypergraph,
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            ignore_binary_relations=dictionary["algorithm_options_dict"]["ignore_binary_relations"],
            weight_positioning=0,
            respect_planarity=dictionary["algorithm_options_dict"]["respect_planarity"],
            iterations=dictionary["algorithm_options_dict"]["iterations"],
            pos=None,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
            draw_edge_graph=False
        )
    elif draw_function == "Bipartite":
        result = _compute_bipartite_drawing_data(
            h=hypergraph,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
            pos = None,
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            align=dictionary["algorithm_options_dict"]["align"],
        )
    elif draw_function == "Clique":
        result = _compute_clique_drawing_data(
            h=hypergraph,
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            iterations=dictionary["algorithm_options_dict"]["iterations"],
            pos=None,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
        )
    return [result,centrality]

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

    def __init__(self, draw_function, hypergraph, input_dictionary, model, community_algorithm, community_options, use_last, parent=None):
        super(PlotWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.draw_function = draw_function
        self.input_dictionary = input_dictionary
        self.model = model
        self.use_last = use_last
        self.community_algorithm = community_algorithm
        self.community_options = community_options

    def run(self):
        if not self.use_last:
            with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
                self.model = pool.apply(run_community_detection, args=(self.hypergraph, self.community_algorithm, self.community_options))
                self.input_dictionary["community_model"] = self.model
        else:
            self.model = self.input_dictionary["community_model"]
        with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
            results = pool.apply(create_figure, args=(self.draw_function, self.hypergraph, self.input_dictionary))
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
        tracemalloc.start()

        multiprocessing.freeze_support()
        app = QApplication(sys.argv)

        faulthandler.enable()
        main = Window(hypergraph=h)
        main.show()
        sys.exit(app.exec_())

h = Hypergraph([("A", "B", "C"), ('D', 'C')])
start_interactive_view(h)
