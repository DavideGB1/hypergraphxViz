import sys
from tkinter.ttk import Combobox

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QSlider, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QRadioButton, QSpacerItem, QLayout, QCheckBox, QStackedLayout, QComboBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_sets import draw_sets
from hypergraphx.viz.draw_metroset import draw_metroset
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.interactive_view.__option_menu import MenuWindow
from hypergraphx.viz.__graphic_options import GraphicOptions
import copy
from superqt import QRangeSlider
import ctypes


# noinspection PyUnresolvedReferences
class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")
        self.setWindowIcon(QIcon("logo_cropped.svg"))
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        #Set Default Values
        self.options_dict = dict()
        self.spin_box_label = QLabel()
        self.spin_box = QDoubleSpinBox()
        self.vbox = QVBoxLayout()
        self.current_function = draw_PAOH
        self.slider = None
        self.ranged = True
        self.option_menu = None
        self.graphic_options = GraphicOptions()
        self.active_labels = True
        self.space_optimization = False
        self.slider_value = 2
        self.hypergraph = hypergraph
        self.canvas_hbox = QHBoxLayout()
        self.ignore_binary_relations = False
        self.show_edge_nodes = False
        self.iterations = 1000
        self.alignment = "vertical"
        self.figure = plt.figure()
        self.max_edge = 0
        self.rounded_polygon = True
        self.extra_attributes = dict()
        self.last_pos = dict()
        for edge in h.get_edges():
            if len(edge) > self.max_edge:
                self.max_edge = len(edge)
        #Defines Canvas and Options Toolbar
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_hbox.addWidget(self.canvas, 80)

        # Sliders Management
        slider_hbox = self.add_sliders()
        # Create layout and add everything
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(self.canvas_hbox)
        layout.addLayout(slider_hbox)
        # setting layout to the main window
        self.setLayout(layout)
        self.option_vbox()
        # action called by the push button
    def add_sliders(self):
        slider_label = QLabel()
        slider_label.setAlignment(Qt.AlignLeft)
        slider_label.setText("Edge Cardinality: " + str(self.slider_value))
        def slider_value_changed():
            self.slider_value = self.slider.value()
            slider_label.setText("Edge Cardinality: " + str(self.slider_value))
            self.plot()
        def change_slider_type():
            if self.ranged:
                self.ranged = False
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(2)
                slider.setMaximum(self.max_edge)
            else:
                self.ranged = True
                slider = QRangeSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(2)
                slider.setMaximum(self.max_edge)
                slider.setValue((2, self.max_edge))
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(1)
            slider.setPageStep(0)
            slider.valueChanged.connect(slider_value_changed)
            slider_hbox.replaceWidget(self.slider, slider)
            slider_hbox.removeWidget(self.slider)
            self.slider = slider
            slider_value_changed()
        slider_hbox = QHBoxLayout()
        change_slider_type()
        slider_button = QPushButton("Change Slider Type")
        slider_button.setChecked(True)
        slider_button.toggle()
        slider_button.clicked.connect(change_slider_type)
        slider_hbox.addWidget(slider_label)
        slider_hbox.addWidget(self.slider)
        slider_hbox.addWidget(slider_button)
        return slider_hbox
    def add_options_button(self):
        button = QPushButton("Graphic Options")
        def open_options():
            if self.option_menu is None:
                self.option_menu = MenuWindow(self.graphic_options, self.extra_attributes)
                self.option_menu.modified_options.connect(self.get_new_option)
                self.option_menu.show()
            else:
                self.option_menu = None

        button.clicked.connect(open_options)
        return button
    def plot(self) -> None:
        """
        Plot the hypergraph on screen using the assigner draw function.
        """
        #Clears the plot
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
            self.graphic_options.in_edge_color = self.extra_attributes["in_edge_color"]
        except KeyError:
            pass
        try:
            self.graphic_options.out_edge_color = self.extra_attributes["out_edge_color"]
        except KeyError:
            pass
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
        #Plot and draw the hypergraph using it's function
        self.current_function(self.hypergraph, cardinality= self.slider_value, x_heaviest = float(self.spin_box.value()/100), ax=ax,
                draw_labels=self.active_labels, space_optimization = self.space_optimization, time_font_size = time_font_size,
                ignore_binary_relations = self.ignore_binary_relations, show_edge_nodes = self.show_edge_nodes,
                iterations = int(self.iterations), align = self.alignment, time_separation_line_color = time_separation_line_color,
                graphicOptions=copy.deepcopy(self.graphic_options), radius_scale_factor=radius_scale_factor, font_spacing_factor=font_spacing_factor,
                time_separation_line_width = time_separation_line_width, rounded_polygon = self.rounded_polygon, polygon_expansion_factor = polygon_expansion_factor,
                rounding_radius_size = rounding_radius_size, hyperedge_alpha = hyperedge_alpha,)
        self.canvas.draw()
    def get_new_option(self, new_options: tuple[GraphicOptions,dict]) -> None:
        """
        Update the graphic options with the one sent from the option menu.
        Parameters
        ----------
        new_options: tuple[GraphicOptions, dict]
            The tuple inside the signal received from the option menu.
        """
        self.graphic_options, self.extra_attributes = new_options
        self.plot()
    def heaviest_edges(self) -> None:
        """
        Updates the label showing what % of edges we are considering.
        """
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.plot()
    def assign_radial(self) -> None:
        """
        Assigns draw_radial_layout as plot function.
        """
        self.current_function = draw_radial_layout
        #Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        #Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
        #Create the new custom options for the radial function
        vbox_radial_option = QVBoxLayout()
        labels_button = QCheckBox("Show Labels")
        labels_button.setChecked(True)
        labels_button.toggled.connect(self.activate_labels)

        vbox_radial_option.addWidget(labels_button)
        self.vbox.addLayout(vbox_radial_option)
        self.vbox.addStretch()
        self.plot()
    def assign_PAOH(self) -> None:
        """
        Assigns draw_PAOH as plot function.
        """
        self.current_function = draw_PAOH
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
        #Create the new custom options for the PAOH function
        vbox_PAOH_option = QVBoxLayout()
        space_optimization_option_btn = QCheckBox("Optimize Space Usage")
        space_optimization_option_btn.setChecked(False)

        def optimize_space_usage():
            if self.space_optimization:
                self.space_optimization = False
            else:
                self.space_optimization = True
            self.plot()

        space_optimization_option_btn.toggled.connect(optimize_space_usage)
        vbox_PAOH_option.addWidget(space_optimization_option_btn)
        self.vbox.addLayout(vbox_PAOH_option)
        self.vbox.addStretch()
        self.plot()
    def assign_metroset(self) -> None:
        """
        Assigns draw_metroset as plot function.
        """
        self.current_function = draw_metroset
        self.iterations = 10
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
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
        self.iterations = 1000
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
        # Create the new custom options for the clique function
        vbox_clique_expasion_option = QVBoxLayout()
        labels_btn = QCheckBox("Show Labels")
        labels_btn.setChecked(True)
        labels_btn.toggled.connect(self.activate_labels)
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
        vbox_clique_expasion_option.addWidget(labels_btn)
        vbox_clique_expasion_option.addWidget(iterations_selector_label)
        vbox_clique_expasion_option.addWidget(iterations_selector)
        self.vbox.addLayout(vbox_clique_expasion_option)
        self.vbox.addStretch()
        self.plot()
    def assign_extra_node(self) -> None:
        """
        Assigns draw_extra_node as plot function.
        """
        self.current_function = draw_extra_node
        self.iterations = 1000
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
        # Create the new custom options for the extra-node function
        vbox_extra_node_option = QVBoxLayout()
        edge_nodes_btn = QCheckBox("Show Edge Nodes")

        def activate_edge_nodes():
            if self.show_edge_nodes:
                self.show_edge_nodes = False
            else:
                self.show_edge_nodes = True
            self.plot()

        edge_nodes_btn.toggled.connect(activate_edge_nodes)
        ignore_binary_relations_btn = QCheckBox("Ignore Binary Relations")

        def ignore_binary_relations_funz():
            if self.ignore_binary_relations:
                self.ignore_binary_relations = False
            else:
                self.ignore_binary_relations = True

            self.plot()

        ignore_binary_relations_btn.toggled.connect(ignore_binary_relations_funz)

        labels_btn = QCheckBox("Show Labels")
        labels_btn.setChecked(True)
        labels_btn.toggled.connect(self.activate_labels)
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



        vbox_extra_node_option.addWidget(edge_nodes_btn)
        vbox_extra_node_option.addWidget(ignore_binary_relations_btn)
        vbox_extra_node_option.addWidget(labels_btn)
        vbox_extra_node_option.addWidget(iterations_selector_label)
        vbox_extra_node_option.addWidget(iterations_selector)
        self.vbox.addLayout(vbox_extra_node_option)
        self.vbox.addStretch()
        self.plot()
    def assign_bipartite(self) -> None:
        """
        Assigns draw_bipartite as plot function.
        """
        self.current_function = draw_bipartite
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
        # Create the new custom options for the bipartite function
        vbox_bipartite_option = QVBoxLayout()

        def change_alignment():
            if self.alignment == "vertical":
                self.alignment = "horizontal"
            else:
                self.alignment = "vertical"
            self.plot()

        change_alignment_btn = QPushButton("Change Alignment")
        change_alignment_btn.setChecked(True)
        change_alignment_btn.clicked.connect(change_alignment)
        vbox_bipartite_option.addWidget(change_alignment_btn)
        self.vbox.addLayout(vbox_bipartite_option)
        self.vbox.addStretch()
        self.plot()
    def assign_sets(self) -> None:
        """
        Assigns draw_sets as plot function.
        """
        self.current_function = draw_sets
        self.iterations = 100
        # Close the option menu if open
        if self.option_menu is not None:
            self.option_menu = None
        # Gets new extra options
        self.extra_options()
        remove_last_x_elements_from_layout(self.vbox, 2)
        # Create the new custom options for the bipartite function
        vbox_set_option = QVBoxLayout()
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
        vbox_set_option.addWidget(iterations_selector_label)
        vbox_set_option.addWidget(iterations_selector)
        def activate_rounded_polygons():
            if self.rounded_polygon:
                self.rounded_polygon = False
            else:
                self.rounded_polygon = True
            self.plot()

        rounded_polygons_btn = QCheckBox("Draw Rounded Polygons")
        rounded_polygons_btn.setChecked(True)
        rounded_polygons_btn.toggled.connect(activate_rounded_polygons)
        vbox_set_option.addWidget(rounded_polygons_btn)
        self.vbox.addLayout(vbox_set_option)
        self.vbox.addStretch()
        self.plot()
    def option_vbox(self) -> None:
        """
        Creates the standard options for the visualization functions
        """
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.add_options_button())
        if self.hypergraph.is_weighted():
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setDecimals(0)
            self.spin_box.setRange(0, 100)
            self.spin_box.setValue(100)
            self.spin_box_label = QLabel()
            self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
            self.spin_box_label.setAlignment(Qt.AlignTop)
            self.spin_box.setAlignment(Qt.AlignTop)
            self.vbox.addWidget(self.spin_box_label)
            self.vbox.addWidget(self.spin_box)
            self.spin_box.valueChanged.connect(self.heaviest_edges)

        combobox = self.add_radio_option()
        self.vbox.addWidget(combobox)
        combobox_community = self.add_community_detection_options()
        self.vbox.addWidget(combobox)
        self.vbox.addStretch()
        self.vbox.addStretch()
        self.canvas_hbox.addLayout(self.vbox, 20)
    def add_radio_option(self) -> Combobox:
        """
        Create the selection list for the visualization function
        """
        combobox = QComboBox()
        if isinstance(self.hypergraph, TemporalHypergraph):
            self.options_dict = { "PAOH": self.assign_PAOH}
        elif isinstance(self.hypergraph, DirectedHypergraph):
            self.options_dict = { "PAOH": self.assign_PAOH,"Radial": self.assign_radial, "Extra-Node": self.assign_extra_node}
        else:
            self.options_dict = {"PAOH": self.assign_PAOH,"Radial": self.assign_radial,
                         "Extra-Node": self.assign_extra_node, "Bipartite": self.assign_bipartite, "Sets": self.assign_sets,
                            "MetroSet": self.assign_metroset}
            if not self.hypergraph.is_weighted():
                self.options_dict["Clique"] = self.assign_clique_projection

        combobox.addItems(list(self.options_dict.keys()))
        def activate_function():
            self.options_dict[combobox.currentText()]()
        combobox.currentTextChanged.connect(activate_function)
        return combobox
    def add_community_detection_options(self) -> Combobox:
        """
        Create the selection list for the community detection function
        """

    def activate_labels(self) -> None:
        """
        Manage the draw_labels option button.
        """
        if self.active_labels:
            self.active_labels = False
            self.plot()
        else:
            self.active_labels = True
            self.plot()
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

def remove_last_x_elements_from_layout(layout: QLayout, x: int=1) -> None:
    """
    Function to remove last x elements from a QLayout
    Parameters
    ----------
    layout: QLayout
    x: int
    """
    for x in range(x):
        widget_layout = layout.takeAt(layout.count() - 1)
        layout.removeItem(widget_layout)
        if isinstance(widget_layout, QSpacerItem):
            pass
        elif isinstance(widget_layout, QLayout):
            clear_layout(widget_layout)
        else:
            try:
                widget_layout.deleteLater()
            except AttributeError:
                pass

def start_interactive_view(h: Hypergraph|TemporalHypergraph|DirectedHypergraph) -> None:
    """
    Wrapper function used to start the interactive view.
    Parameters
    ----------
    h: Hypergraph or TemporalHypergraph or DirectedHypergraph
    """
    app = QApplication(sys.argv)
    main = Window(hypergraph=h)
    main.show()
    sys.exit(app.exec_())


#h = Hypergraph([(1,2,3),(4,5,6),(6,7,8,9),(10,11,12,1,4),(4,1),(3,6)])
#h = DirectedHypergraph()
#h.add_edge(((1,2),(3,4)))
h = Hypergraph(weighted=True)
h.add_edge((1,2,3),12)
h.add_edge((4,5,6),3)
h.add_edge((6,7,8,9),1)
h.add_edge((10,11,12,1,4),5)
h.add_edge((4,1),1)
h.add_edge((3,6),7)
start_interactive_view(h)