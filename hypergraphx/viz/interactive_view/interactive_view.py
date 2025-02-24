import copy
import ctypes
import sys
from tkinter.ttk import Combobox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QSlider, QWidget, QHBoxLayout, QLabel, \
    QDoubleSpinBox, QFileDialog, QSpacerItem, QLayout, QCheckBox, QComboBox, QMessageBox, QListWidget, \
    QListWidgetItem
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from superqt import QRangeSlider
import hypergraphx.readwrite
from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.communities.hy_mmsbm.model import HyMMSBM
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.communities.hypergraph_mt.model import HypergraphMT
from hypergraphx.measures.degree import degree_sequence
from hypergraphx.utils import normalize_array
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_metroset import draw_metroset
from hypergraphx.viz.draw_projections import draw_extra_node, draw_bipartite, draw_clique
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.draw_sets import draw_sets
from hypergraphx.viz.interactive_view.__drawing_options import PAOHOptionsWidget, RadialOptionsWidget, \
    CliqueOptionsWidget, ExtraNodeOptionsWidget, BipartiteOptionsWidget, SetOptionsWidget
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import CommunityOptionsWindow
from hypergraphx.viz.interactive_view.community_options.__community_options import CommunityOptions
from hypergraphx.viz.interactive_view.graphic_options.__graphic_option_menu import GraphicOptionsWindow


class Window(QWidget):

    # constructor
    def __init__(self,hypergraph: Hypergraph|TemporalHypergraph|DirectedHypergraph, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("HypergraphX Visualizer")
        self.setWindowIcon(QIcon("logo_cropped.svg"))
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        #Set Default Values
        self.algorithm_options_dict = dict()
        self.list = None
        self.use_last = False
        self.centrality = None
        self.options_dict = dict()
        self.spin_box_label = QLabel()
        self.spin_box = QDoubleSpinBox()
        self.vbox = QVBoxLayout()
        self.current_function = draw_PAOH
        self.community_options = CommunityOptions()
        self.slider = None
        self.ranged = True
        self.community_option_menu = None
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
        self.centrality_on = False
        for edge in h.get_edges():
            if len(edge) > self.max_edge:
                self.max_edge = len(edge)
        #Defines Canvas and Options Toolbar
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_hbox.addWidget(self.canvas, 80)
        self.community_model = None
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
                self.option_menu = GraphicOptionsWindow(self.graphic_options, self.extra_attributes)
                self.option_menu.modified_options.connect(self.get_new_option)
                self.option_menu.show()
            else:
                self.option_menu = None

        button.clicked.connect(open_options)
        return button
    def get_new_community_option(self, new_options: CommunityOptions) -> None:
        self.community_options = new_options
        self.use_community_detection_algorithm()
        self.use_last = True
        self.plot()
    def add_community_options_button(self):
        button = QPushButton("Options")
        def open_options():
            if self.community_option_menu is None:
                self.community_option_menu = CommunityOptionsWindow(self.community_options)
                self.community_option_menu.modified_options.connect(self.get_new_community_option)
                self.community_option_menu.show()
            else:
                self.community_option_menu = None

        button.clicked.connect(open_options)
        return button
    #Drawing
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
        if self.use_last:
            last_pos = self.last_pos
        else:
            last_pos = None
        if self.centrality is not None:
            self.graphic_options.add_centrality_factor_dict(self.centrality)
        else:
            self.graphic_options.add_centrality_factor_dict(None)
        #Plot and draw the hypergraph using it's function
        self.last_pos = self.current_function(self.hypergraph, cardinality= self.slider_value, x_heaviest = float(self.spin_box.value()/100), ax=ax,
                time_font_size = time_font_size, time_separation_line_color = time_separation_line_color,
                graphicOptions=copy.deepcopy(self.graphic_options), radius_scale_factor=radius_scale_factor, font_spacing_factor=font_spacing_factor,
                time_separation_line_width = time_separation_line_width, polygon_expansion_factor = polygon_expansion_factor,
                rounding_radius_size = rounding_radius_size, hyperedge_alpha = hyperedge_alpha,pos = last_pos, u = self.community_model, **self.algorithm_options_dict)
        self.use_last = False
        self.canvas.draw()
    def redraw(self):
        self.use_last = False
        self.plot()

    def get_new_option(self, new_options: tuple[GraphicOptions,dict]) -> None:
        """
        Update the graphic options with the one sent from the option menu.
        Parameters
        ----------
        new_options: tuple[GraphicOptions, dict]
            The tuple inside the signal received from the option menu.
        """
        self.graphic_options, self.extra_attributes = new_options
        self.use_last = True
        self.plot()
    def heaviest_edges(self) -> None:
        """
        Updates the label showing what % of edges we are considering.
        """
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.plot()
    #Get Drawing Algorithm Options
    def get_drawing_algorithm_options(self, dict):
        self.algorithm_options_dict = dict
        try:
            self.use_last = dict["use_last"]
        except KeyError:
            self.use_last = True
        self.plot()
    def add_drawing_algorithm_options_button(self, widget):
        self.list.clear()
        for x in widget.widget_list:
            myQListWidgetItem = QListWidgetItem(self.list)
            myQListWidgetItem.setSizeHint(x.sizeHint())
            self.list.addItem(myQListWidgetItem)
            self.list.setItemWidget(myQListWidgetItem, x)
        widget.modified_options.connect(self.get_drawing_algorithm_options)
    #Assign Drawing Function
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
        self.drawing_options = PAOHOptionsWidget()
        self.add_drawing_algorithm_options_button(self.drawing_options)
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
        #Create the new custom options for the radial function
        self.drawing_options = RadialOptionsWidget()
        self.add_drawing_algorithm_options_button(self.drawing_options)
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
        self.drawing_options = CliqueOptionsWidget()
        self.add_drawing_algorithm_options_button(self.drawing_options)
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
        self.drawing_options = ExtraNodeOptionsWidget()
        self.add_drawing_algorithm_options_button(self.drawing_options)
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
        self.drawing_options = BipartiteOptionsWidget()
        self.add_drawing_algorithm_options_button(self.drawing_options)
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
        self.drawing_options = SetOptionsWidget()
        self.add_drawing_algorithm_options_button(self.drawing_options)
        self.plot()
    #Community
    def use_community_detection_algorithm(self):
        self.community_options.algorithm = self.community_combobox.currentText()
        self.community_options.update_options()
        self.options_community[self.community_combobox.currentText()]()
    def create_community_detection_options(self) -> Combobox:
        """
        Create the selection list for the visualization function
        """
        self.community_combobox = QComboBox()
        self.options_community = {"None": self.no_community,
                                  "Hypergraph Spectral Clustering": self.use_spectral_clustering,
                                  "Hypergraph-MT": self.use_MT,
                                  "Hy-MMSBM": self.use_MMSBM}

        self.community_combobox.addItems(list(self.options_community.keys()))
        self.community_combobox.currentTextChanged.connect(self.use_community_detection_algorithm)
        return self.community_combobox
    def use_spectral_clustering(self):
        model = HySC(
            seed=self.community_options.seed,
            n_realizations=self.community_options.spinbox_n_realizations
        )
        self.community_model = model.fit(
            self.hypergraph,
            K=int(self.community_options.spinbox_K),
            weighted_L=False
        )
        self.redraw()
    def use_MT(self):
        model = HypergraphMT(
            n_realizations=self.community_options.spinbox_n_realizations,
            max_iter=self.community_options.spinbox_max_iter,
            check_convergence_every=self.community_options.spinbox_check_convergence_every,
            verbose=False
        )
        u_HypergraphMT, w_HypergraphMT, _ = model.fit(
            self.hypergraph,
            K=self.community_options.spinbox_K,
            seed=self.community_options.seed,
            normalizeU=self.community_options.checkbox_normalizeU,
            baseline_r0=self.community_options.checkbox_baseline_r0,
        )
        u_HypergraphMT = normalize_array(u_HypergraphMT, axis=1)
        self.community_model = u_HypergraphMT
        self.redraw()
    def use_MMSBM(self):
        best_model = None
        best_loglik = float("-inf")
        for j in range(self.community_options.spinbox_n_realizations):
            model = HyMMSBM(
                K=self.community_options.spinbox_K,
                assortative=self.community_options.checkbox_assortative
            )
            model.fit(
                self.hypergraph,
                n_iter=self.community_options.spinbox_max_iter,
            )

            log_lik = model.log_likelihood(self.hypergraph)
            if log_lik > best_loglik:
                best_model = model
                best_loglik = log_lik

        u_HyMMSBM = best_model.u
        u_HyMMSBM = normalize_array(u_HyMMSBM, axis=1)

        self.community_model = u_HyMMSBM
        self.redraw()
    def no_community(self):
        self.community_model = None
        self.redraw()
    def add_community_detection_options(self) -> Combobox:
        """
        Create the selection list for the community detection function
        """


    def option_vbox(self) -> None:
        """
        Creates the standard options for the visualization functions
        """
        self.vbox = QVBoxLayout()
        self.spin_box = QDoubleSpinBox()
        self.spin_box.setDecimals(0)
        self.spin_box.setRange(0, 100)
        self.spin_box.setValue(100)
        self.spin_box_label = QLabel()
        self.spin_box_label.setText("Show {value}% Heaviest Edges".format(value=self.spin_box.value()))
        self.spin_box_label.setAlignment(Qt.AlignTop)
        self.spin_box.setAlignment(Qt.AlignTop)
        self.spin_box.valueChanged.connect(self.heaviest_edges)
        if not self.hypergraph.is_weighted():
            self.spin_box.setVisible(False)
            self.spin_box_label.setVisible(False)

        combobox = self.create_algorithm_options()
        redraw = QPushButton("Redraw")
        redraw.clicked.connect(self.redraw)
        open_file_button = QPushButton("Open from File")
        def open_file():
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("Open File")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
            file_dialog.setNameFilters(["JSON (*.json)", "HGR (*.hgr)","HGX (*.hgx)"])

            if file_dialog.exec():
                selected_file = file_dialog.selectedFiles()
                try:
                    hypergraph = hypergraphx.readwrite.load_hypergraph(selected_file[0])
                    self.hypergraph = hypergraph
                    for edge in self.hypergraph.get_edges():
                        if len(edge) > self.max_edge:
                            self.max_edge = len(edge)
                    if self.hypergraph.is_weighted():
                        self.spin_box.setVisible(True)
                        self.spin_box_label.setVisible(True)
                    else:
                        self.spin_box.setVisible(False)
                        self.spin_box_label.setVisible(False)
                    self.plot()
                except ValueError:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error: Invalid Input File")
                    msg.setInformativeText('Input File is not .hgr | .json | .hgx')
                    msg.setWindowTitle("Error")
                    msg.exec_()

        open_file_button.clicked.connect(open_file)
        centrality_combobox = QComboBox()
        centrality_combobox.addItems(["No Centrality","Degree Centrality"])

        def centrality_calculate():
            if centrality_combobox.currentText() == "Off":
                self.centrality = None
            if centrality_combobox.currentText() == "Degree Centrality":
                self.centrality = degree_sequence(self.hypergraph)
                mean = sum(self.centrality.values())/len(self.centrality)
                for k,v in self.centrality.items():
                    self.centrality[k] = v/mean
            self.use_last = True
            self.plot()

        centrality_combobox.currentTextChanged.connect(centrality_calculate)

        def activate_function():
            self.options_dict[combobox.currentText()]()

        combobox_communities = self.create_community_detection_options()
        combobox.currentTextChanged.connect(activate_function)
        self.vbox.addWidget(open_file_button)
        self.vbox.addWidget(combobox)
        community_label = QLabel("Community Detection Algorithm:")
        self.vbox.addWidget(community_label)
        hbox = QHBoxLayout()
        hbox.addWidget(combobox_communities,75)
        option_community = self.add_community_options_button()
        hbox.addWidget(option_community,25)
        self.vbox.addLayout(hbox)
        centrality_label = QLabel("Centrality Calculation Method:")
        self.vbox.addWidget(centrality_label)
        self.vbox.addWidget(centrality_combobox)
        self.vbox.addWidget(self.spin_box_label)
        self.vbox.addWidget(self.spin_box)
        self.vbox.addWidget(self.add_options_button())
        self.vbox.addWidget(redraw)
        self.list = QListWidget()
        self.vbox.addWidget(self.list)
        self.canvas_hbox.addLayout(self.vbox, 20)
    def create_algorithm_options(self) -> Combobox:
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
                            }
            if not self.hypergraph.is_weighted():
                self.options_dict["Clique"] = self.assign_clique_projection

        combobox.addItems(list(self.options_dict.keys()))
        def activate_function():
            self.options_dict[combobox.currentText()]()
        combobox.currentTextChanged.connect(activate_function)
        return combobox
    def add_centrality_button(self):
        labels_button = QCheckBox("Show Centrality")
        labels_button.setChecked(True)
        labels_button.toggled.connect(self.show_centrality)
    def show_centrality(self):
        if self.centrality_on:
            self.active_labels = False
            self.plot()
        else:
            self.centrality_on = True
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

h = Hypergraph([(1,2,3),(4,5,6),(6,7,8,9),(10,11,12,1,4),(4,1),(3,6)])
#h = DirectedHypergraph()
#h.add_edge(((1,2),(3,4)))
#h = Hypergraph(weighted=True)
#h.add_edge((1,2,3),12)
#h.add_edge((4,5,6),3)
#h.add_edge((6,7,8,9),1)
#h.add_edge((10,11,12,1,4),5)
#h.add_edge((4,1),1)
#h.add_edge((3,6),7)
start_interactive_view(h)