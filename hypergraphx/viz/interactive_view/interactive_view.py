import ctypes
import gc
import multiprocessing
import os
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, \
    QDoubleSpinBox, QTabWidget, QMainWindow, QStackedLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.communities.hy_mmsbm.model import HyMMSBM
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.communities.hypergraph_mt.model import HypergraphMT
from hypergraphx.measures.degree import degree_sequence
from hypergraphx.measures.s_centralities import s_betweenness_nodes, s_betweenness_nodes_averaged
from hypergraphx.utils import normalize_array
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.draw_PAOH import calculate_paoh_layout, draw_paoh_from_data
from hypergraphx.viz.draw_projections import _compute_bipartite_drawing_data, _compute_clique_drawing_data, \
    _compute_extra_node_drawing_data, \
    _draw_bipartite_on_ax, _draw_clique_on_ax, _draw_extra_node_on_ax
from hypergraphx.viz.draw_radial import _compute_radial_layout, _draw_radial_elements
from hypergraphx.viz.draw_sets import _compute_set_layout, _draw_set_elements
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.custom_widgets import SliderDockWidget, LoadingScreen
from hypergraphx.viz.interactive_view.drawing_options_widget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.hypergraph_editing_view import ModifyHypergraphMenu
from hypergraphx.viz.interactive_view.stats_view import HypergraphStatsWidget


class Window(QWidget):

    # constructor
    def __init__(self, hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph, parent=None):
        super().__init__(parent)

        self.setWindowTitle("HypergraphX Visualizer")
        # Used in order to avoid copying useless data when creating childrens
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(script_dir + os.path.sep + 'logo_cropped.png'))
        if "win" in sys.platform and "darwin" not in sys.platform:
            myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.community_algorithm = "None"
        self.heaviest_edges_value = 1.0
        self.thread_community = None
        # Set Default Values
        self.thread = None
        self.weight_positioning = 0
        self.community_algorithm_option_gui = None
        self.community_options_dict = CommunityOptionsDict()
        self.algorithm_options_dict = {
            "rounded_polygon": True,
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
            "hyperedge_alpha": 0.8,
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
        # Defines Canvas and Options Toolbar
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.community_model = None
        # Sliders Management
        # Create layout and add everything
        self.main_layout = QMainWindow(parent=self)

        self.canvas = FigureCanvas(self.figure)
        self.main_layout.setCentralWidget(self.canvas)

        self.toolbar = NavigationToolbar(parent=self.main_layout, canvas=self.canvas)
        home_icon = QIcon("home.svg")
        self.toolbar._actions['home'].setIcon(home_icon)
        back_icon = QIcon("left.svg")
        self.toolbar._actions['back'].setIcon(back_icon)
        forward_icon = QIcon("right.svg")
        self.toolbar._actions['forward'].setIcon(forward_icon)
        pan_icon = QIcon("move.svg")
        self.toolbar._actions['pan'].setIcon(pan_icon)
        zoom_icon = QIcon("zoom.svg")
        self.toolbar._actions['zoom'].setIcon(zoom_icon)
        configure_subplots_icon = QIcon("options.svg")
        self.toolbar._actions['configure_subplots'].setIcon(configure_subplots_icon)
        edit_parameters_icon = QIcon("settings.svg")
        self.toolbar._actions['edit_parameters'].setIcon(edit_parameters_icon)
        save_icon = QIcon("save.svg")
        self.toolbar._actions['save_figure'].setIcon(save_icon)

        self.main_layout.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.slider = SliderDockWidget(self.hypergraph.max_size(), parent=self.main_layout)
        self.slider.setTitleBarWidget(QWidget())
        self.slider.setFixedHeight(self.slider.sizeHint().height())
        self.slider.update_value.connect(self.new_slider_value)
        self.main_layout.addDockWidget(Qt.BottomDockWidgetArea, self.slider)

        self.loading = False

        # setting layout to the main window

        self.central_tab = QTabWidget(parent=self)
        self.central_tab.setObjectName("MainTab")
        self.central_tab.setStyleSheet("""
        QTabWidget#OptionsTabs::pane {
}
        QTabBar::tab:first {
        margin-left: 10px; /* Aggiunge un margine solo a sinistra della prima scheda */
    }
/* La barra delle tab */
QTabWidget#MainTab QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F5F5F5, stop: 1 #E0E0E0);
                border: 1px solid #BDBDBD;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 4px 5px;
                margin-right: 2px;
                color: #444;
                font-weight: bold;
                font-size: 12px;
                width: 150px;
}

/* Linguetta quando il mouse è sopra, ma NON è selezionata */
QTabWidget#MainTab QTabBar::tab:hover:!selected {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FFFFFF, stop: 1 #E8E8E8);
}

/* Linguetta SELEZIONATA - la regola più importante */
QTabWidget#MainTab QTabBar::tab:selected {
    background-color: white; /* FORZA lo sfondo bianco */
    color: #005A9E;
    
    /* Rimuoviamo il bordo inferiore per la connessione.
       Usiamo un colore trasparente per essere sicuri che sparisca. */
    border-bottom-color: transparent; 
    
    /* Spostiamo la tab per sovrapporla al bordo del pannello */
    margin-bottom: -1px;
    padding-bottom: 9px; /* Aumenta il padding per compensare il margine */
}

/* Assicuriamoci che non cambi colore al hover quando è selezionata */
QTabWidget#MainTab QTabBar::tab:selected:hover {
    background-color: white;
}
        """)

        self.central_tab.setDocumentMode(True)
        drawing_tab = QWidget(parent=self.central_tab)
        visualization_icon = QIcon("hypergraph.svg")
        self.central_tab.addTab(drawing_tab, visualization_icon, "Visualization")
        self.stats_tab = HypergraphStatsWidget(self.hypergraph, parent=self.central_tab)
        statistics_icon = QIcon("stats.svg")
        self.central_tab.addTab(self.stats_tab, statistics_icon,"Statistics")
        modify_hypergraph_tab = ModifyHypergraphMenu(hypergraph, parent=self.central_tab)
        modify_hypergraph_tab.updated_hypergraph.connect(self.update_hypergraph)
        editing_icon = QIcon("edit.svg")
        self.central_tab.addTab(modify_hypergraph_tab, editing_icon, "Hypergraph Editing")

        self.drawing_options_widget = DrawingOptionsDockWidget(n_nodes=self.hypergraph.num_nodes(),
                                                               parent=self.main_layout)
        self.drawing_options_widget.setTitleBarWidget(QWidget())
        suggested_width = self.drawing_options_widget.sizeHint().width()
        self.drawing_options_widget.setFixedWidth(int(suggested_width * 1.45))
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.main_layout.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)

        self.loading_container = LoadingScreen()
        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.main_layout)
        self.stacked.addWidget(self.loading_container)

        drawing_tab.setLayout(self.stacked)

        azdd = QVBoxLayout()
        azdd.addWidget(self.central_tab)
        self.setLayout(azdd)
        azdd.setContentsMargins(0, 0, 0, 0)

        self.use_default()

    #Drawing
    def plot(self):
        """
        Gestisce la logica per avviare un nuovo disegno.
        Se un disegno è già in corso, lo annulla prima di avviarne uno nuovo.
        """
        if self.thread and self.thread.isRunning():
            self.thread.cancel()
            self.thread.quit()

        if self.stacked.currentIndex() != 1:
            self.change_focus()

        dictionary = {
            "slider_value": self.slider_value,
            "centrality": self.centrality,
            "algorithm_options_dict": self.algorithm_options_dict,
            "heaviest_edges_value": self.heaviest_edges_value,
            "community_options_dict": self.community_options_dict,
            "weight_positioning": self.weight_positioning,
            "extra_attributes": self.extra_attributes,
            "last_pos": self.last_pos if self.use_last else None,
            "community_model": self.community_model,
            "graphic_options": self.graphic_options
        }

        self.thread = PlotWorker(
            self.current_function,
            self.hypergraph,
            dictionary,
            self.community_model,
            self.community_algorithm,
            self.community_options_dict,
            self.use_last
        )

        self.thread.progress.connect(self.drawn)
        self.thread.finished.connect(self.on_worker_finished)
        self.thread.start()

        self.use_last = False

    def drawn(self, value_list):
        if self.sender() is not self.thread:
            return
        self.graphic_options.add_centrality_factor_dict(value_list[1])
        self.figure.clf()
        gc.collect()
        if self.current_function == "Sets":
            _draw_set_elements(
                ax=self.figure.gca(),
                data = value_list[0],
                draw_labels= self.algorithm_options_dict["draw_labels"],
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
        self.figure.tight_layout()
        self.canvas.draw()
        self.change_focus()
        if self.thread:
            self.thread = None
        gc.collect()

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

    def on_worker_finished(self):
        if self.sender() is self.thread:
            self.thread = None
        if self.sender():
            self.sender().deleteLater()

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
        if example is not None:
            self.hypergraph = example["hypergraph"]
        if hypergraph is not None:
            self.hypergraph = hypergraph
        self.slider_value = (2, self.hypergraph.max_size())
        if isinstance(self.hypergraph, Hypergraph):
            self.drawing_options_widget.update_hypergraph(hypergraph_type = "normal", n_nodes = self.hypergraph.num_nodes(), weighted = self.hypergraph.is_weighted())
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.drawing_options_widget.update_hypergraph(hypergraph_type = "directed", n_nodes = self.hypergraph.num_nodes(), weighted = self.hypergraph.is_weighted())
        elif isinstance(self.hypergraph, TemporalHypergraph):
            self.drawing_options_widget.update_hypergraph(hypergraph_type = "temporal", n_nodes = self.hypergraph.num_nodes(), weighted = self.hypergraph.is_weighted())

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
            weight_positioning = dictionary["weight_positioning"],
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
        print(dictionary["extra_attributes"]["radius_scale_factor"])
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
            weight_positioning=dictionary["weight_positioning"],
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
            weight_positioning = dictionary["weight_positioning"],
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
        self._is_cancelled = False

    def run(self):
        try:
            if self._is_cancelled:
                return

            if not self.use_last:
                with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
                    self.model = pool.apply(run_community_detection,
                                            args=(self.hypergraph, self.community_algorithm, self.community_options))

                self.input_dictionary["community_model"] = self.model
            else:
                self.model = self.input_dictionary["community_model"]

            if self._is_cancelled:
                return

            with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
                results = pool.apply(create_figure, args=(self.draw_function, self.hypergraph, self.input_dictionary))

            if self._is_cancelled:
                return

            results.append(self.model)
            self.progress.emit(results)
        except Exception as e:
            print(f"Error in PlotWorker: {e}")

    def cancel(self):
        """Richiede la cancellazione del thread."""
        self._is_cancelled = True

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
        app.setStyleSheet("""
         QComboBox {
        border: 1px solid #BDBDBD;
        border-radius: 5px;
        padding: 2px 4px 2px 4px; /* Padding ridotto per dare spazio al pulsante interno */
        min-width: 6em;
        background: white;
        font-size: 13px;
    }

    /* Stile del campo di testo interno */
    QComboBox QLineEdit {
        background: transparent; /* Sfondo trasparente per ereditare quello della QComboBox */
        border: none;
        padding-left: 8px;
        color: #333;
    }

    QComboBox:hover {
        border-color: #5D9CEC;
    }

    QComboBox:on { /* Quando la lista è aperta */
        border: 1px solid #4A89DC;
    }

    /* Area del pulsante a discesa */
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 35px; /* Larghezza del pulsante */
        border-left-width: 0px;
        border-radius: 4px;
        border-radius: 4px;
    }

    /* Pulsante a discesa come un bottone 3D (quando NON aperto) */
    QComboBox::drop-down:!on {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #5D9CEC, stop: 1 #4A89DC);
        border: 1px solid #3A79CB;
        border-bottom: 3px solid #3A79CB;
        border-radius: 5px;
        margin: 2px;
    }

    QComboBox::drop-down:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #6AACFF, stop: 1 #5D9CEC);
    }

    /* Pulsante quando la lista è aperta (effetto "premuto") */
    QComboBox::drop-down:on {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #4A89DC, stop: 1 #3A79CB);
        border: 1px solid #3A79CB; /* Bordo normale */
        border-bottom: 1px solid #3A79CB; /* Rimuoviamo l'ombra */
        margin: 2px;
        margin-top: 4px; /* Spostiamo il pulsante verso il basso */
    }

    /* Freccia dentro il pulsante */
    QComboBox::down-arrow {
        image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' fill='white'><path d='M7 10l5-5H2z'/></svg>);
        width: 14px;
        height: 14px;
    }
    
    QDoubleSpinBox {
    background-color: white;
    border: 1px solid #BDBDBD;
    border-radius: 5px;
    padding: 4px;
    font-size: 13px;
    color: #333;
    /* Effetto leggermente incavato */
    padding-left: 8px; 
}

QDoubleSpinBox:hover {
    border-color: #5D9CEC;
}

QDoubleSpinBox:focus {
    border-color: #4A89DC; /* Bordo più scuro quando ha il focus */
}

/* Stile per i pulsanti SU e GIÙ */
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; /* Posizionamento relativo al bordo principale */
    width: 20px;
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #F5F5F5, stop: 1 #E0E0E0);
    border: 1px solid #BDBDBD;
}

QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #FFFFFF, stop: 1 #E8E8E8);
}

QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E0E0E0, stop: 1 #D0D0D0);
    /* Spostiamo la freccia per l'effetto pressione */
    padding-top: 2px;
}

/* Stile del pulsante SU */
QDoubleSpinBox::up-button {
    subcontrol-position: top right;
    border-top-right-radius: 4px;
    border-left-width: 1px;
}

/* Stile del pulsante GIÙ */
QDoubleSpinBox::down-button {
    subcontrol-position: bottom right;
    border-bottom-right-radius: 4px;
    border-left-width: 1px;
    margin-top: -1px; /* Evita un doppio bordo tra i due pulsanti */
}

/* Stile della freccia SU */
QDoubleSpinBox::up-arrow {
    image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%23666'><path d='M5 2l4 4H1z'/></svg>);
    width: 10px;
    height: 10px;
}

/* Stile della freccia GIÙ */
QDoubleSpinBox::down-arrow {
    image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%23666'><path d='M5 8L1 4h8z'/></svg>);
    width: 10px;
    height: 10px;
}

QCheckBox {
        spacing: 10px; /* Spazio tra il box e il testo */
        color: #333;
        font-size: 13px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border-radius: 5px; /* Angoli leggermente arrotondati */
    }

    /* Stato normale (non selezionato) */
    QCheckBox::indicator:unchecked {
        background-color: white;
        border: 1px solid #BDBDBD;
        /* Simula un leggero incavo */
        border-top-color: #A0A0A0;
        border-left-color: #A0A0A0;
    }
    
    QCheckBox::indicator:unchecked:hover {
        border-color: #5D9CEC;
    }

    /* Stato selezionato */
    QCheckBox::indicator:checked {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #5D9CEC, stop: 1 #4A89DC);
        border: 1px solid #3A79CB;
        
        /* Icona del segno di spunta (SVG incorporato) */
        image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24'><path fill='white' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>);
    }

    QCheckBox::indicator:checked:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #6AACFF, stop: 1 #5D9CEC);
    }
    
    /* Stato disabilitato */
    QCheckBox::indicator:disabled {
        background-color: #E0E0E0;
        border: 1px solid #C0C0C0;
    }
""")
        main = Window(hypergraph=h)
        main.show()
        sys.exit(app.exec_())

h = Hypergraph([("A", "B", "C"), ('D', 'C')])
start_interactive_view(h)
