import gc
import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QStackedLayout
import pyqtgraph as pg

from hypergraphx.viz.interactive_view.pyqtgraph_functions.draw_projections_pyqtgraph import _draw_bipartite_pyqtgraph, \
    _draw_clique_pyqtgraph, _draw_extra_node_pyqtgraph
from hypergraphx.viz.interactive_view.pyqtgraph_functions.radial_pyqtgraph import _draw_radial_elements_pyqt
from hypergraphx.viz.interactive_view.pyqtgraph_functions.set_pyqtgraph import _draw_set_pyqtgraph

pg.setConfigOption('background', 'w')  # 'w' = white

# Imposta il colore degli assi e della griglia
pg.setConfigOptions(antialias=True)

# Configura lo stile predefinito degli assi
axis_pen = pg.mkPen(color='k', width=1)
grid_pen = pg.mkPen(color='k', width=0.5, style=pg.QtCore.Qt.DashLine)

# Monkey patch per impostare i colori di default
original_setStyle = pg.AxisItem.setStyle

def new_setStyle(self, **kwds):
    original_setStyle(self, **kwds)
    self.setPen(axis_pen)
    self.setTextPen('k')
    self.setZValue(-1000)

pg.AxisItem.setStyle = new_setStyle
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsDict
from hypergraphx.viz.interactive_view.controller import HypergraphType
from hypergraphx.viz.interactive_view.custom_widgets.loading_screen import LoadingScreen
from hypergraphx.viz.interactive_view.custom_widgets.slider_dock_widget import SliderDockWidget
from hypergraphx.viz.interactive_view.drawing_view.drawing_options_dockedwidget import DrawingOptionsDockWidget
from hypergraphx.viz.interactive_view.pyqtgraph_functions.PAOH_pyqtgraph import draw_paoh_pyqtgraph


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
            "axis_labels_size": 16,
            "nodes_name_size": 12
        }
        self.graphic_options = GraphicOptions()
        self.slider = None
        self.community_option_menu = None
        self.option_menu = None
        self.pyqtgraph_widget = None
        self.drawing_options = None
        self.last_pos = dict()
        self.loading = False
        self.slider_value = (2, self.controller.get_hypergraph().max_size())
        # Defines Canvas and Options Toolbar
        self.setContextMenuPolicy(Qt.NoContextMenu)

        self.community_model = None

        # Container per il plot PyQtGraph
        self.plot_container = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_container)
        self.plot_layout.setContentsMargins(0, 0, 0, 0)

        # Create layout and add everything
        self.loading_container = LoadingScreen()

        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.plot_container)
        self.stacked.addWidget(self.loading_container)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.stacked)
        self.setCentralWidget(self.central_widget)

        self.aggregation_options = {
            "use_simplification": False,
            "aggregation_threshold": 0.85,
            "use_polygonal_simplification": False
        }

        # Rimuovi la toolbar di matplotlib (opzionale, puoi tenerla se serve)
        # Se vuoi una toolbar personalizzata per PyQtGraph, puoi aggiungerla qui

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
        self.drawing_options_widget = DrawingOptionsDockWidget(
            weighted=self.controller.get_hypergraph().is_weighted(),
            hypergraph_type=hypergraph_type,
            n_nodes=self.controller.get_hypergraph().num_nodes(),
            parent=self
        )
        self.drawing_options_widget.setTitleBarWidget(QWidget())
        suggested_width = self.drawing_options_widget.sizeHint().width()
        self.drawing_options_widget.setFixedWidth(int(suggested_width * 1.45))
        self.drawing_options_widget.update_value.connect(self.get_new_drawing_options)
        self.addDockWidget(Qt.RightDockWidgetArea, self.drawing_options_widget)
        self.use_default()

    def _clear_plot_container(self):
        """Pulisce il container del plot rimuovendo tutti i widget"""
        while self.plot_layout.count():
            item = self.plot_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.pyqtgraph_widget = None
        gc.collect()

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
                self.drawing_options_widget.update_hypergraph(
                    hypergraph_type="normal",
                    n_nodes=self.controller.get_hypergraph().num_nodes(),
                    weighted=self.controller.get_hypergraph().is_weighted()
                )
            case HypergraphType.DIRECTED:
                self.drawing_options_widget.update_hypergraph(
                    hypergraph_type="directed",
                    n_nodes=self.controller.get_hypergraph().num_nodes(),
                    weighted=self.controller.get_hypergraph().is_weighted()
                )
            case HypergraphType.TEMPORAL:
                self.drawing_options_widget.update_hypergraph(
                    hypergraph_type="temporal",
                    n_nodes=self.controller.get_hypergraph().num_nodes(),
                    weighted=self.controller.get_hypergraph().is_weighted()
                )

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
        """
        Disegna il grafico usando PyQtGraph dopo che i dati sono pronti
        """
        data = self.controller.drawing_result[0]
        n_times = self.controller.drawing_result[2]
        self.graphic_options.add_centrality_factor_dict(self.controller.drawing_result[1])

        self._clear_plot_container()
        gc.collect()

        if n_times == 1:
            if self.current_function == "PAOH":
                self.pyqtgraph_widget = draw_paoh_pyqtgraph(
                    data=data[0],
                    widget=None,
                    graphicOptions=self.graphic_options.copy(),
                    axis_labels_size=self.extra_attributes["axis_labels_size"],
                    nodes_name_size=self.extra_attributes["nodes_name_size"]

                )
            elif self.current_function == "Radial":
                self.pyqtgraph_widget = _draw_radial_elements_pyqt(
                    data=data[0],
                    widget=None,
                    graphicOptions=self.graphic_options.copy(),
                    draw_labels=self.algorithm_options_dict["draw_labels"],
                    font_spacing_factor=self.extra_attributes["font_spacing_factor"],
                )
            elif self.current_function == "Bipartite":
                self.pyqtgraph_widget = _draw_bipartite_pyqtgraph(
                    data=data[0],
                    widget=None,
                    graphicOptions=self.graphic_options.copy(),
                    draw_labels=self.algorithm_options_dict["draw_labels"],
                    align=self.algorithm_options_dict["align"],
                    u=self.community_model,
                )
            elif self.current_function == "Clique":
                self.pyqtgraph_widget = _draw_clique_pyqtgraph(
                    data=data[0],
                    widget=None,
                    graphicOptions=self.graphic_options.copy(),
                    draw_labels=self.algorithm_options_dict["draw_labels"],
                    u=self.community_model,
                )
            elif self.current_function == "Extra-Node":
                self.pyqtgraph_widget = _draw_extra_node_pyqtgraph(
                    data=data[0],
                    widget=None,
                    u=self.community_model,
                    show_edge_nodes=self.algorithm_options_dict["show_edge_nodes"],
                    draw_labels=self.algorithm_options_dict["draw_labels"],
                    graphicOptions=self.graphic_options.copy()
                )
            elif self.current_function == "Sets":
                self.pyqtgraph_widget = _draw_set_pyqtgraph(
                    data=data[0],
                    widget=None,
                    draw_labels=self.algorithm_options_dict["draw_labels"],
                    graphicOptions=self.graphic_options.copy()
                )
            self.plot_layout.addWidget(self.pyqtgraph_widget)
        else:
            from PyQt5.QtWidgets import QGridLayout

            grid_widget = QWidget()
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(5)

            n_rows = math.ceil(math.sqrt(n_times))
            n_cols = math.ceil(n_times / n_rows)

            for i, (time, timed_data) in enumerate(data.items()):
                row = i // n_cols
                col = i % n_cols

                widget = _draw_radial_elements_pyqt(
                    data=timed_data,
                    widget=None,
                    graphicOptions=self.graphic_options.copy(),
                    draw_labels=self.algorithm_options_dict["draw_labels"],
                    font_spacing_factor=self.extra_attributes["font_spacing_factor"],
                )

                # Aggiungi titolo per timestamp multipli
                from PyQt5.QtWidgets import QLabel, QVBoxLayout
                timestamp_container = QWidget()
                timestamp_layout = QVBoxLayout(timestamp_container)
                timestamp_layout.setContentsMargins(0, 0, 0, 0)

                title_label = QLabel(f"Hypergraph at time {time}")
                title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
                title_label.setAlignment(Qt.AlignCenter)

                timestamp_layout.addWidget(title_label)
                timestamp_layout.addWidget(widget)

                grid_layout.addWidget(timestamp_container, row, col)

            self.plot_layout.addWidget(grid_widget)

        # Cambia focus e pulisce
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
            A dictionary containing configurations and options for updating drawing parameters.
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
        Determina e imposta la funzione di disegno appropriata.
        Ora forza sempre PAOH indipendentemente dal tipo di ipergrafo.
        """
        # Forza sempre PAOH
        self.current_function = "PAOH"
        self.plot()