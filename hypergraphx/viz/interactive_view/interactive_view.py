import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QSlider, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QRadioButton, QSpacerItem, QLayout, QCheckBox
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


# noinspection PyUnresolvedReferences
class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")
        #Set Default Values
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
        self.radius_scale_factor = 1.0
        self.ignore_binary_relations = True
        self.show_edge_nodes = True
        self.strong_gravity = True
        self.iterations = 1000
        self.alignment = "vertical"
        self.figure = plt.figure()
        self.max_edge = 0
        for edge in h.get_edges():
            if len(edge) > self.max_edge:
                self.max_edge = len(edge)
        #Defines Canvas and Options Toolbar
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        options_button = self.add_options_button()
        self.toolbar.insertWidget(self.toolbar.actions()[-1],options_button)
        self.canvas_hbox.addWidget(self.canvas)

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
        button = QPushButton("Options")
        def open_options():
            if self.option_menu is None:
                self.option_menu = MenuWindow(self.graphic_options)
                self.option_menu.modified_options.connect(self.get_new_option)
                self.option_menu.show()
            else:
                self.option_menu = None

        button.clicked.connect(open_options)
        return button
    def plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.current_function(self.hypergraph, cardinality= self.slider_value, x_heaviest = float(self.spin_box.value()/100), ax=ax,
                              draw_labels=self.active_labels, space_optimization = self.space_optimization, radius_scale_factor = self.radius_scale_factor,
                              ignore_binary_relations = self.ignore_binary_relations, show_edge_nodes = self.show_edge_nodes, strong_gravity = self.strong_gravity,
                              iterations = int(self.iterations), align = self.alignment,
                              graphicOptions=copy.deepcopy(self.graphic_options))
        self.canvas.draw()
    def get_new_option(self, graphic_options):
        self.graphic_options = graphic_options
        self.plot()
    def heaviest_edges(self):
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.plot()
    def assign_radial(self):
        self.current_function = draw_radial_layout
        self.graphic_options = GraphicOptions(is_PAOH=True)
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_radial_option = QVBoxLayout()
        labels_button = QCheckBox("Show Labels")
        labels_button.setChecked(True)
        labels_button.toggled.connect(self.activate_labels)
        def radial_scale_factor_modifier():
            self.radius_scale_factor = radial_scale_factor_selector.value()
            self.plot()

        radial_scale_factor_selector = QDoubleSpinBox()
        radial_scale_factor_selector.setDecimals(2)
        radial_scale_factor_selector.setRange(0, 10)
        radial_scale_factor_selector.setValue(1.0)
        radial_scale_factor_selector.setSingleStep(0.1)
        radial_scale_factor_selector.valueChanged.connect(radial_scale_factor_modifier)

        radial_scale_factor_selector_label = QLabel()
        radial_scale_factor_selector_label.setText("Radius Scale Factor:")
        radial_scale_factor_selector_label.setAlignment(Qt.AlignTop)
        radial_scale_factor_selector_label.setAlignment(Qt.AlignTop)

        vbox_radial_option.addWidget(labels_button)
        vbox_radial_option.addWidget(radial_scale_factor_selector_label)
        vbox_radial_option.addWidget(radial_scale_factor_selector)
        self.vbox.addLayout(vbox_radial_option)
        self.vbox.addStretch()
        self.plot()
    def assign_PAOH(self):
        self.current_function = draw_PAOH
        self.graphic_options = GraphicOptions(is_PAOH=True)
        if self.option_menu is not None:
            self.option_menu = None
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_PAOH_option = QVBoxLayout()
        space_optimization_option_btn = QCheckBox("Optimize Space Usage")
        space_optimization_option_btn.setChecked(True)

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
    def assign_metroset(self):
        self.current_function = draw_metroset
        self.graphic_options = GraphicOptions(is_PAOH=False)
        self.iterations = 10
        remove_last_x_elements_from_layout(self.vbox, 2)
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
    def assign_clique_projection(self):
        self.current_function = draw_clique
        self.graphic_options = GraphicOptions(is_PAOH=False)
        self.iterations = 1000
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_clique_expasion_option = QVBoxLayout()
        strong_gravity_btn = QCheckBox("Use Strong Gravity")
        strong_gravity_btn.setChecked(True)
        strong_gravity_btn.toggled.connect(self.activate_strong_gravity)
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
        vbox_clique_expasion_option.addWidget(strong_gravity_btn)
        vbox_clique_expasion_option.addWidget(labels_btn)
        vbox_clique_expasion_option.addWidget(iterations_selector_label)
        vbox_clique_expasion_option.addWidget(iterations_selector)
        self.vbox.addLayout(vbox_clique_expasion_option)
        self.vbox.addStretch()
        self.plot()
    def assign_extra_node(self):
        self.current_function = draw_extra_node
        self.graphic_options = GraphicOptions(is_PAOH=False)
        self.iterations = 1000
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_extra_node_option = QVBoxLayout()
        edge_nodes_btn = QCheckBox("Show Edge Nodes")
        edge_nodes_btn.setChecked(True)

        def activate_edge_nodes():
            if self.show_edge_nodes:
                self.show_edge_nodes = False
            else:
                self.show_edge_nodes = True
            self.plot()

        edge_nodes_btn.toggled.connect(activate_edge_nodes)
        ignore_binary_relations_btn = QCheckBox("Ignore Binary Relations")
        ignore_binary_relations_btn.setChecked(True)

        def ignore_binary_relations_funz():
            if self.ignore_binary_relations:
                self.ignore_binary_relations = False
            else:
                self.ignore_binary_relations = True

            self.plot()

        ignore_binary_relations_btn.toggled.connect(ignore_binary_relations_funz)
        strong_gravity_btn = QCheckBox("Use Strong Gravity")
        strong_gravity_btn.setChecked(True)
        strong_gravity_btn.toggled.connect(self.activate_strong_gravity)
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
        vbox_extra_node_option.addWidget(strong_gravity_btn)
        vbox_extra_node_option.addWidget(labels_btn)
        vbox_extra_node_option.addWidget(iterations_selector_label)
        vbox_extra_node_option.addWidget(iterations_selector)
        self.vbox.addLayout(vbox_extra_node_option)
        self.vbox.addStretch()
        self.plot()
    def assign_bipartite(self):
        self.current_function = draw_bipartite
        self.graphic_options = GraphicOptions(is_PAOH=False)
        remove_last_x_elements_from_layout(self.vbox, 2)
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
    def assign_sets(self):
        self.current_function = draw_sets
        self.graphic_options = GraphicOptions(is_PAOH=False)
        self.iterations = 100
        remove_last_x_elements_from_layout(self.vbox, 2)
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
        self.vbox.addLayout(vbox_set_option)
        self.vbox.addStretch()
        self.plot()
    def option_vbox(self):
        self.vbox = QVBoxLayout()
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
        radio_btn_list = self.add_radio_option()
        for btn in radio_btn_list:
            self.vbox.addWidget(btn)
        self.vbox.addStretch()
        self.vbox.addStretch()
        radio_btn_list[0].setChecked(True)
        self.canvas_hbox.addLayout(self.vbox)
    def add_radio_option(self):
        button_list = []
        if isinstance(self.hypergraph, TemporalHypergraph):
            options_dict = { "PAOH": self.assign_PAOH}
        elif isinstance(self.hypergraph, DirectedHypergraph):
            options_dict = { "PAOH": self.assign_PAOH, "Extra-Node": self.assign_extra_node}
        else:
            options_dict = { "Radial": self.assign_radial, "PAOH": self.assign_PAOH, "Clique Expansion": self.assign_clique_projection,
                         "Extra-Node": self.assign_extra_node, "Bipartite": self.assign_bipartite, "Sets": self.assign_sets}

        for val, fun in options_dict.items():
            button = QRadioButton(val)
            button.toggled.connect(fun)
            button_list.append(button)
        if not self.hypergraph.is_weighted():
            radio_button_metroset = QRadioButton("MetroSet")
            radio_button_metroset.toggled.connect(self.assign_metroset)
            button_list.append(radio_button_metroset)
        return button_list
    def activate_labels(self):
        if self.active_labels:
            self.active_labels = False
            self.plot()
        else:
            self.active_labels = True
            self.plot()
    def activate_strong_gravity(self):
        if self.strong_gravity:
            self.strong_gravity = False
            self.plot()
        else:
            self.strong_gravity = True
            self.plot()

def clear_layout(layout: QLayout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

def remove_last_x_elements_from_layout(layout, x=1):
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

def start_interactive_view(h: Hypergraph):
    app = QApplication(sys.argv)
    main = Window(hypergraph=h)
    main.show()
    sys.exit(app.exec_())

h = Hypergraph(weighted=True)
h.add_edge((1, 2), 5)
h.add_edge((42, 3, 4), 1)
h.add_edge((1, 2, 3, 4, 5), 3)
h._weighted = True
start_interactive_view(h)