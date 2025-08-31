import gc
import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QStackedLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.draw_PAOH import draw_paoh_from_data
from hypergraphx.viz.draw_projections import _draw_extra_node_on_ax, _draw_bipartite_on_ax, _draw_clique_on_ax
from hypergraphx.viz.draw_radial import _draw_radial_elements
from hypergraphx.viz.draw_sets import _draw_set_elements
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.controller import HypergraphType
from hypergraphx.viz.interactive_view.custom_widgets.loading_screen import LoadingScreen
from hypergraphx.viz.interactive_view.custom_widgets.slider_dock_widget import SliderDockWidget
from hypergraphx.viz.interactive_view.drawing_view.drawing_options_dockedwidget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.drawing_view.drawing_thread import PlotWorker


class HypergraphDrawingWidget(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.controller.updated_hypergraph.connect(self.update_hypergraph)
        self.controller.finished_drawing.connect(self.drawn)
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
        self.figure = Figure()
        self.drawing_options = None
        self.last_pos = dict()
        self.loading = False
        self.slider_value = (2, self.controller.get_hypergraph().max_size())
        # Defines Canvas and Options Toolbar
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.community_model = None
        # Sliders Management
        # Create layout and add everything
        self.loading_container = LoadingScreen()
        self.canvas = FigureCanvas(self.figure)
        self.setCentralWidget(self.canvas)
        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.canvas)
        self.stacked.addWidget(self.loading_container)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.stacked)
        self.setCentralWidget(self.central_widget)

        self.aggregation_options = {
            "use_simplification": False,
            "aggregation_threshold": 0.85,
            "use_polygonal_simplification": False
        }

        self.toolbar = NavigationToolbar(parent=self, canvas=self.canvas)
        home_icon = QIcon("icons/home.svg")
        self.toolbar._actions['home'].setIcon(home_icon)
        back_icon = QIcon("icons/left.svg")
        self.toolbar._actions['back'].setIcon(back_icon)
        forward_icon = QIcon("icons/right.svg")
        self.toolbar._actions['forward'].setIcon(forward_icon)
        pan_icon = QIcon("icons/move.svg")
        self.toolbar._actions['pan'].setIcon(pan_icon)
        zoom_icon = QIcon("icons/zoom.svg")
        self.toolbar._actions['zoom'].setIcon(zoom_icon)
        configure_subplots_icon = QIcon("icons/options.svg")
        self.toolbar._actions['configure_subplots'].setIcon(configure_subplots_icon)
        edit_parameters_icon = QIcon("icons/settings.svg")
        self.toolbar._actions['edit_parameters'].setIcon(edit_parameters_icon)
        save_icon = QIcon("icons/save.svg")
        self.toolbar._actions['save_figure'].setIcon(save_icon)

        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.slider = SliderDockWidget(self.controller.get_hypergraph().max_size(), parent=self)
        self.slider.setTitleBarWidget(QWidget())
        self.slider.setFixedHeight(self.slider.sizeHint().height())
        self.slider.update_value.connect(self.new_slider_value)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.slider)

        hypergraph_type = "normal"
        match self.controller.hypergraph_type:
            case HypergraphType.NORMAL:
                hypergraph_type = "normal"
            case HypergraphType.DIRECTED:
                hypergraph_type = "directed"
            case HypergraphType.TEMPORAL:
                hypergraph_type = "temporal"
        self.drawing_options_widget = DrawingOptionsDockWidget(weighted= self.controller.get_hypergraph().is_weighted(), hypergraph_type=hypergraph_type,n_nodes=self.controller.get_hypergraph().num_nodes(),
                                                               parent=self)
        self.drawing_options_widget.setTitleBarWidget(QWidget())
        suggested_width = self.drawing_options_widget.sizeHint().width()
        self.drawing_options_widget.setFixedWidth(int(suggested_width * 1.45))
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
        self.use_default()

    def update_hypergraph(self):
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
        self.slider_value = (2, self.controller.get_hypergraph().max_size())
        match self.controller.hypergraph_type:
            case HypergraphType.NORMAL:
                self.drawing_options_widget.update_hypergraph(hypergraph_type = "normal", n_nodes = self.controller.get_hypergraph().num_nodes(), weighted = self.controller.get_hypergraph().is_weighted())
            case HypergraphType.DIRECTED:
                self.drawing_options_widget.update_hypergraph(hypergraph_type = "directed", n_nodes = self.controller.get_hypergraph().num_nodes(), weighted = self.controller.get_hypergraph().is_weighted())
            case HypergraphType.TEMPORAL:
                self.drawing_options_widget.update_hypergraph(hypergraph_type = "temporal", n_nodes = self.controller.get_hypergraph().num_nodes(), weighted = self.controller.get_hypergraph().is_weighted())

        self.slider.update_max(self.controller.get_hypergraph().max_size())
        self.use_default()

    def plot(self):
        """
        Handles the logic to start a new drawing.
        If a drawing is already in progress, cancels it before starting a new one.
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
        input_values = dict()
        input_values["dictionary"] = dictionary
        input_values["curr_function"] = self.current_function
        input_values["community_model"] = self.community_model
        input_values["community_algorithm"] = self.community_algorithm
        input_values["community_options_dict"] = self.community_options_dict
        input_values["aggregation_options"] = self.aggregation_options
        input_values["use_last"] = self.use_last

        self.controller.plot_graph(input_values)

        self.use_last = False

    def drawn(self):
        data = self.controller.drawing_result[0]
        n_times = self.controller.drawing_result[2]
        self.graphic_options.add_centrality_factor_dict(self.controller.drawing_result[1])
        self.figure.clf()
        gc.collect()
        if self.current_function == "PAOH":
            ax = self.figure.add_subplot(111)
            draw_paoh_from_data(
                ax=ax,
                data=data[0],
                graphicOptions=self.graphic_options.copy(),
                axis_labels_size=self.extra_attributes["axis_labels_size"],
                nodes_name_size=self.extra_attributes["nodes_name_size"]
            )
        else:
            axs_flat = []
            if n_times != 1:
                n_rows = math.ceil(math.sqrt(n_times))
                n_cols = math.ceil(n_times / n_rows)
                for i in range(n_times):
                    axs_flat.append(self.figure.add_subplot(n_rows, n_cols, i + 1))
            else:
                axs_flat.append(self.figure.add_subplot(111))

            for i, (time, timed_data) in enumerate(data.items()):
                if self.current_function == "Sets":
                    _draw_set_elements(
                        ax=axs_flat[i],
                        data=timed_data,
                        draw_labels=self.algorithm_options_dict["draw_labels"],
                        graphicOptions=self.graphic_options.copy()
                    )
                elif self.current_function == "PAOH":
                    draw_paoh_from_data(
                        ax=axs_flat[i],
                        data=timed_data,
                        graphicOptions=self.graphic_options.copy(),
                        axis_labels_size=self.extra_attributes["axis_labels_size"],
                        nodes_name_size=self.extra_attributes["nodes_name_size"]
                    )
                elif self.current_function == "Radial":
                    _draw_radial_elements(
                        ax=axs_flat[i],
                        data=timed_data,
                        draw_labels=self.algorithm_options_dict["draw_labels"],
                        font_spacing_factor=self.extra_attributes["font_spacing_factor"],
                        graphicOptions=self.graphic_options.copy()
                    )
                elif self.current_function == "Extra-Node":
                    _draw_extra_node_on_ax(
                        ax=axs_flat[i],
                        data=timed_data,
                        u=self.community_model,
                        show_edge_nodes=self.algorithm_options_dict["show_edge_nodes"],
                        draw_labels=self.algorithm_options_dict["draw_labels"],
                        graphicOptions=self.graphic_options.copy()
                    )
                elif self.current_function == "Bipartite":
                    _draw_bipartite_on_ax(
                        ax=axs_flat[i],
                        data=timed_data,
                        u=self.community_model,
                        draw_labels=self.algorithm_options_dict["draw_labels"],
                        align=self.algorithm_options_dict["align"],
                        graphicOptions=self.graphic_options.copy()
                    )
                elif self.current_function == "Clique":
                    _draw_clique_on_ax(
                        ax=axs_flat[i],
                        data=timed_data,
                        u=self.community_model,
                        draw_labels=self.algorithm_options_dict["draw_labels"],
                        graphicOptions=self.graphic_options.copy()
                    )
                if n_times != 1:
                    axs_flat[i].set_title(f"Hypergraph at time {time}")

            if n_times != 1:
                for ax in axs_flat[n_times:]:
                    ax.set_visible(False)
        if self.current_function != "PAOH" and n_times == 1:
            self.figure.gca().axis('off')
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
        self.aggregation_options = input_dictionary["aggregation_options"]
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
        match self.controller.hypergraph_type:
            case HypergraphType.TEMPORAL:
                self.current_function = "PAOH"
            case HypergraphType.DIRECTED:
                self.current_function = "Extra-Node"
            case HypergraphType.NORMAL:
                self.current_function = "Sets"
            case _:
                self.current_function = "PAOH"
        self.plot()