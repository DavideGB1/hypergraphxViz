import inspect
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QSlider, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QRadioButton, QSpacerItem, QLayout, QCheckBox

from hypergraphx import Hypergraph
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from qtrangeslider import QRangeSlider

from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_hypergraph import draw_hypergraph
from hypergraphx.viz.draw_metroset import draw_metroset
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.interactive_view.__option_menu import MenuWindow
from hypergraphx.viz.interactive_view.__options import Options


class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")
        self.option_menu = None
        self.options = Options()
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
        # a figure instance to plot on
        self.figure = plt.figure()
        self.max_edge = 0
        for edge in h.get_edges():
            if len(edge) > self.max_edge:
                self.max_edge = len(edge)

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        button = QPushButton("Options")
        def open_options():
            if self.option_menu is None:
                self.option_menu = MenuWindow(self.options)
                self.option_menu.modified_options.connect(self.get_new_option)
                self.option_menu.show()
            else:
                self.option_menu = None
        button.clicked.connect(open_options)

        self.toolbar.insertWidget(self.toolbar.actions()[-1],
                                  button)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        self.canvas_hbox.addWidget(self.canvas,75)
        layout.addLayout(self.canvas_hbox)
        #Sliders Management



        layout.addLayout(self.slider_creation())
        # setting layout to the main window
        self.setLayout(layout)
        ax = self.figure.add_subplot(111)
        self.option_vbox()
    def slider_creation(self):

        slider_hbox = QHBoxLayout()
        sliders = QWidget()
        slider = QSlider(Qt.Horizontal, sliders)
        slider.setMinimum(2)
        slider.setMaximum(self.max_edge)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(1)
        slider.setPageStep(0)
        slider.valueChanged.connect(self.plot)
        range_slider = QRangeSlider(Qt.Horizontal, self)
        range_slider.setTickPosition(QSlider.TicksBelow)
        range_slider.setTickInterval(1)
        range_slider.setMinimum(1)
        range_slider.setMaximum(self.max_edge + 1)
        range_slider.setPageStep(0)
        range_slider.valueChanged.connect(self.plot)
        range_slider.setVisible(False)
        # adding push button to the layout
        slider_label = QLabel()
        slider_label.setAlignment(Qt.AlignLeft)
        slider_label.setText("Edge Cardinality: " + str(self.slider_value))
        slider_button = QPushButton("Change Slider Type")
        slider_button.setChecked(True)
        slider_button.toggle()

        def change_slider_type():
            if range_slider.isVisible():
                range_slider.setVisible(False)
                slider.setValue(2)
                slider.setVisible(True)
                self.plot()
            else:
                range_slider.setVisible(True)
                range_slider.setValue((2, self.max_edge))
                slider.setVisible(False)
                self.plot()

        slider_button.clicked.connect(change_slider_type)
        slider_hbox.addWidget(slider_label)
        slider_hbox.addWidget(slider)
        slider_hbox.addWidget(range_slider)
        slider_hbox.addWidget(slider_button)


        return slider_hbox
    # action called by the push button
    def plot(self):
        if self.range_slider.isVisible():
            self.slider_value = self.range_slider.value()
        else:
            self.slider_value = self.slider.value()
        self.figure.clear()
        self.slider_label.setText("Edge Cardinality: "+str(self.slider_value))
        # create an axis
        ax = self.figure.add_subplot(111)

        self.current_function(self.hypergraph, cardinality= self.slider_value, x_heaviest = float(self.spin_box.value()/100), ax=ax,
                              draw_labels=self.active_labels, space_optimization = self.space_optimization, radius_scale_factor = self.radius_scale_factor,
                              ignore_binary_relations = self.ignore_binary_relations, show_edge_nodes = self.show_edge_nodes, strong_gravity = self.strong_gravity,
                              iterations = int(self.iterations), align = self.alignment, node_color = self.options.get_node_color(),
                              edge_color = self.options.get_edge_color(), marker_edge_color = self.options.get_marker_edge_color(),
                              time_separation_line_color = self.options.get_time_separation_line_color(), edge_node_color = self.options.get_edge_node_color(),
                              marker_color = self.options.get_marker_color(), node_shape=self.options.get_node_shape(), edge_node_shape=self.options.get_edge_node_shape(),
                              edge_width = self.options.get_edge_width(), marker_edge_width = self.options.get_marker_edge_width(), time_font_size = self.options.get_time_font_size(),
                              time_separation_line_width = self.options.get_time_separation_line_width(), marker_size=self.options.get_marker_size(),
                              font_size = self.options.get_font_size(), edge_lenght = self.options.get_edge_lenght(), node_size=self.options.get_node_size())
        # refresh canvas
        self.canvas.draw()
    def get_new_option(self, option):
        self.options = option
        self.plot()


    def heaviest_edges(self):
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.plot()



    def assign_radial(self):
        self.current_function = draw_radial_layout
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_radial_option = QVBoxLayout()
        labels_button = QCheckBox("Show Labels")
        labels_button.setChecked(True)
        labels_button.toggled.connect(self.activate_labels)
        self.options.set_default_radial()
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
        if self.option_menu is not None:
            self.option_menu = None
        self.options.set_default_PAOH()
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_PAOH_option = QVBoxLayout()
        space_optimization_option_btn = QCheckBox("Optimize Space Usage")
        space_optimization_option_btn.setChecked(True)
        space_optimization_option_btn.toggled.connect(self.optimize_space_usage)
        vbox_PAOH_option.addWidget(space_optimization_option_btn)
        self.vbox.addLayout(vbox_PAOH_option)
        self.vbox.addStretch()
        self.plot()

    def assign_metroset(self):
        self.current_function = draw_metroset
        self.iterations = 10
        self.options.set_default_metroset()
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
        self.iterations = 1000
        self.options.set_default_extra_node_bipartite()
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
        self.iterations = 1000
        self.options.set_default_extra_node()
        remove_last_x_elements_from_layout(self.vbox, 2)
        vbox_extra_node_option = QVBoxLayout()
        edge_nodes_btn = QCheckBox("Show Edge Nodes")
        edge_nodes_btn.setChecked(True)
        edge_nodes_btn.toggled.connect(self.activate_edge_nodes)
        ignore_binary_relations_btn = QCheckBox("Ignore Binary Relations")
        ignore_binary_relations_btn.setChecked(True)
        ignore_binary_relations_btn.toggled.connect(self.ignore_binary_relations_funz)
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
        self.options.set_default_extra_node_bipartite()
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
        self.current_function = draw_hypergraph
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

    def optimize_space_usage(self):
        if self.space_optimization:
            self.space_optimization = False
        else:
            self.space_optimization = True
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
        self.assign_radial()
        self.canvas_hbox.addLayout(self.vbox,25)
    def add_radio_option(self):
        button_list = []
        radio_button_radial = QRadioButton("Radial")
        radio_button_radial.setChecked(True)
        radio_button_radial.toggled.connect(self.assign_radial)
        button_list.append(radio_button_radial)
        radio_button_PAOH = QRadioButton("PAOH")
        radio_button_PAOH.toggled.connect(self.assign_PAOH)
        button_list.append(radio_button_PAOH)
        if not self.hypergraph.is_weighted():
            radio_button_metroset = QRadioButton("MetroSet")
            radio_button_metroset.toggled.connect(self.assign_metroset)
            button_list.append(radio_button_metroset)
        radio_button_clique_expasion = QRadioButton("Clique Expansion")
        radio_button_clique_expasion.toggled.connect(self.assign_clique_projection)
        button_list.append(radio_button_clique_expasion)
        radio_button_extra_node = QRadioButton("Extra-Node")
        radio_button_extra_node.toggled.connect(self.assign_extra_node)
        button_list.append(radio_button_extra_node)
        radio_button_bipartite = QRadioButton("Bipartite")
        radio_button_bipartite.toggled.connect(self.assign_bipartite)
        button_list.append(radio_button_bipartite)
        radio_button_sets = QRadioButton("Sets")
        radio_button_sets.toggled.connect(self.assign_sets)
        button_list.append(radio_button_sets)
        return button_list

    def activate_labels(self):
        if self.active_labels:
            self.active_labels = False
            self.plot()
        else:
            self.active_labels = True
            self.plot()

    def ignore_binary_relations_funz(self):
        if self.ignore_binary_relations:
            self.ignore_binary_relations = False
            self.plot()
        else:
            self.ignore_binary_relations = True
            self.plot()

    def activate_edge_nodes(self):
        if self.show_edge_nodes:
            self.show_edge_nodes = False
            self.plot()
        else:
            self.show_edge_nodes = True
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
            widget_layout.deleteLater()

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