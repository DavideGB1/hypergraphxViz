from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QScrollArea

from hypergraphx.viz.interactive_view.custom_widgets import IterationsSelector, SpinboxCustomWindget, RandomSeedButton


class BaseOptionsWidget(QWidget):
    """
    Base class for options widgets.
    It manages layout, change signals, and data submission logic,
    leaving subclasses to create specific widgets and define how to collect options.
    """
    modified_options = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(
            """
                QCheckBox {
                    spacing: 10px;
                    color: #333;
                    font-size: 13px;
                    /* Aggiungiamo un po' di spazio sotto per l'ombra */
                    padding-bottom: 3px; 
                }
                
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 5px;
                }
                
                QCheckBox::indicator:unchecked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #F5F5F5, stop: 1 #E0E0E0);
                    border: 1px solid #BDBDBD;
                    border-bottom: 2px solid #B0B0B0; 
                }
                
                QCheckBox::indicator:unchecked:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #FFFFFF, stop: 1 #E8E8E8);
                    border-color: #9E9E9E;
                }
                
                QCheckBox::indicator:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #4A89DC, stop: 1 #3A79CB);
                    border: 1px solid #3A79CB;
                    margin-top: 2px;
                }
                
                QCheckBox::indicator:checked:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5D9CEC, stop: 1 #4A89DC); /* Gradiente più chiaro al hover */
                }
                
                QCheckBox::check-mark {
                    subcontrol-origin: indicator;
                    subcontrol-position: center center;
                    image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'><path fill='white' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>);
                }
                
                QCheckBox::indicator:disabled {
                    background: #E0E0E0;
                    border: 1px solid #C0C0C0;
                    border-bottom: 2px solid #BDBDBD;
                }
                
                QCheckBox::check-mark:disabled {
                    image: none;
                }
            """
        )

        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(container_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.scroll_content_widget = QWidget()
        scroll_area.setWidget(self.scroll_content_widget)
        self.scroll_content_widget.setObjectName("GraphicOptionsContent")
        self.scroll_content_widget.setStyleSheet("""
                            QWidget#GraphicOptionsContent {
                                background-color: white;
                                border: 1px solid #dcdcdc; /* Il nostro solito colore per i bordi */
                                border-radius: 5px;
                                border-top-left-radius: 0px;
                            }
                        """)

        self.main_layout = QVBoxLayout(self.scroll_content_widget)
        self.main_layout.setContentsMargins(9, 9, 9, 9)
        self.main_layout.setSpacing(10)
        container_layout.addWidget(scroll_area)
        self._setup_widgets()
        self.main_layout.addStretch()

    def _setup_widgets(self):
        """
        Virtual method that subclasses must implement to create and add their specific widgets.
        """
        raise NotImplementedError("Subclasses must implement _setup_widgets()")

    def get_options(self):
        """
        Virtual method that subclasses must implement
        to return a dictionary with their options status.
        """
        raise NotImplementedError("Subclasses must implement get_options()")

    def send_data(self):
        """
        Gets options using get_options() and emits the signal.
        This method is connected to the change signal of the widgets.
        """
        options = self.get_options()
        self.modified_options.emit(options)

class PAOHOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.space_optimization_btn = QCheckBox("Optimize Space Usage", self)
        self.space_optimization_btn.toggled.connect(self.send_data)
        self.main_layout.addWidget(self.space_optimization_btn)

    def get_options(self):
        return {"space_optimization": self.space_optimization_btn.isChecked()}


class RadialOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.labels_button = QCheckBox("Show Labels", self)
        self.labels_button.toggled.connect(self.send_data)
        self.main_layout.addWidget(self.labels_button)

    def get_options(self):
        return {"draw_labels": self.labels_button.isChecked()}


class CliqueOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.labels_button = QCheckBox("Show Labels", self)
        self.labels_button.toggled.connect(self.send_data)

        self.iterations_selector = IterationsSelector(self)
        self.iterations_selector.changed_value.connect(self.send_data)

        self.main_layout.addWidget(self.labels_button)
        self.main_layout.addWidget(self.iterations_selector)

    def get_options(self):
        return {
            "draw_labels": self.labels_button.isChecked(),
            "iterations": self.iterations_selector.value()
        }


class ExtraNodeOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.labels_button = QCheckBox("Show Labels", self)
        self.labels_button.toggled.connect(self.send_data)

        self.ignore_binary_relations_btn = QCheckBox("Ignore Binary Relations", self)
        self.ignore_binary_relations_btn.setChecked(True)
        self.ignore_binary_relations_btn.toggled.connect(self.send_data)

        self.respect_planarity_btn = QCheckBox("Respect Planarity", self)
        self.respect_planarity_btn.setChecked(False)
        self.respect_planarity_btn.toggled.connect(self.send_data)

        self.edge_nodes_btn = QCheckBox("Show Edge Nodes", self)
        self.edge_nodes_btn.setChecked(True)
        self.edge_nodes_btn.toggled.connect(self.send_data)

        self.iterations_selector = IterationsSelector(self)
        self.iterations_selector.changed_value.connect(self.send_data)

        self.main_layout.addWidget(self.labels_button)
        self.main_layout.addWidget(self.edge_nodes_btn)
        self.main_layout.addWidget(self.ignore_binary_relations_btn)
        self.main_layout.addWidget(self.respect_planarity_btn)
        self.main_layout.addWidget(self.iterations_selector)

    def get_options(self):
        return {
            "draw_labels": self.labels_button.isChecked(),
            "iterations": self.iterations_selector.value(),
            "show_edge_nodes": self.edge_nodes_btn.isChecked(),
            "ignore_binary_relations": self.ignore_binary_relations_btn.isChecked(),
            "respect_planarity": self.respect_planarity_btn.isChecked(),
        }


class BipartiteOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.alignment = "vertical"

        self.labels_button = QCheckBox("Show Labels", self)
        self.labels_button.toggled.connect(self.send_data)

        self.change_alignment_btn = QPushButton("Alignment: Vertical", self)
        self.change_alignment_btn.clicked.connect(self._toggle_alignment)

        self.main_layout.addWidget(self.labels_button)
        self.main_layout.addWidget(self.change_alignment_btn)

    def _toggle_alignment(self):
        if self.alignment == "vertical":
            self.alignment = "horizontal"
            self.change_alignment_btn.setText("Alignment: Horizontal")
        else:
            self.alignment = "vertical"
            self.change_alignment_btn.setText("Alignment: Vertical")
        self.send_data()

    def get_options(self):
        return {
            "align": self.alignment,
            "draw_labels": self.labels_button.isChecked()
        }


class SetOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.labels_button = QCheckBox("Show Labels", self)

        self.labels_button.toggled.connect(self.send_data)

        self.rounded_polygons_btn = QCheckBox("Draw Rounded Polygons", self)
        self.rounded_polygons_btn.setChecked(True)
        self.rounded_polygons_btn.toggled.connect(self.send_data)

        self.iterations_selector = IterationsSelector(self)
        self.iterations_selector.changed_value.connect(self.send_data)

        self.scale_spinbox = SpinboxCustomWindget("Scale Factor", 0.1, 100, 1, "scale_factor", 2, 0.1, self)
        self.scale_spinbox.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.labels_button)
        self.main_layout.addWidget(self.rounded_polygons_btn)
        self.main_layout.addWidget(self.iterations_selector)
        self.main_layout.addWidget(self.scale_spinbox)

    def get_options(self):
        return {
            "draw_labels": self.labels_button.isChecked(),
            "rounded_polygon": self.rounded_polygons_btn.isChecked(),
            "iterations": self.iterations_selector.value(),
            "scale_factor": self.scale_spinbox.value()
        }

class SpectralClusteringOptionsWidget(BaseOptionsWidget):

    def _setup_widgets(self):

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 2,2, "number_communities", parent=self)
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations", parent=self)
        self.realizations.update_status.connect(self.send_data)

        self.random_seed = RandomSeedButton(parent=self)
        self.random_seed.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.realizations)
        self.main_layout.addWidget(self.n_communities)
        self.main_layout.addWidget(self.random_seed)
    def set_max_communities(self, n_nodes):
        self.n_communities.setMax(n_nodes)
        self.n_communities.setValue(2)
    def get_options(self):
        return {
            "number_communities": int(self.n_communities.value()),
            "realizations":int( self.realizations.value()),
            "seed": self.random_seed.get_seed(),
        }

class MTOptionsWidget(BaseOptionsWidget):

    def _setup_widgets(self):

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 2,2, "number_communities")
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations", parent=self)
        self.realizations.update_status.connect(self.send_data)

        self.max_iterations = SpinboxCustomWindget("Max Iterations", 1, 1000, 500, "max_iterations", parent=self)
        self.max_iterations.update_status.connect(self.send_data)

        self.check_convergence = SpinboxCustomWindget("Check Convergence Every", 1, 1000, 1, "check_convergence_every", parent=self)
        self.check_convergence.update_status.connect(self.send_data)

        self.normalizeU = QCheckBox("Normalize Output", parent=self)
        self.normalizeU.setChecked(True)
        self.normalizeU.toggled.connect(self.send_data)

        self.baseline_r0 = QCheckBox("Baseline R0", parent=self)
        self.baseline_r0.setChecked(False)
        self.baseline_r0.toggled.connect(self.send_data)

        self.random_seed = RandomSeedButton(parent=self)
        self.random_seed.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.realizations)
        self.main_layout.addWidget(self.n_communities)
        self.main_layout.addWidget(self.max_iterations)
        self.main_layout.addWidget(self.check_convergence)
        self.main_layout.addWidget(self.normalizeU)
        self.main_layout.addWidget(self.baseline_r0)
        self.main_layout.addWidget(self.random_seed)
    def set_max_communities(self, n_nodes):
        self.n_communities.setMax(n_nodes)
        self.n_communities.setValue(2)
    def get_options(self):
        return {
            "number_communities": int(self.n_communities.value()),
            "realizations":int( self.realizations.value()),
            "seed" :self.random_seed.get_seed(),
            "max_iterations": int(self.max_iterations.spinBox.value()),
            "check_convergence_every": int(self.check_convergence.spinBox.value()),
            "normalizeU": self.normalizeU.isChecked(),
            "baseline_r0": self.baseline_r0.isChecked()
        }

class MMSBMOptionsWidget(BaseOptionsWidget):

    def _setup_widgets(self):

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 2,2, "number_communities", parent=self)
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations", parent=self)
        self.realizations.update_status.connect(self.send_data)

        self.assortative = QCheckBox("Assortative", parent = self)
        self.assortative.setChecked(True)
        self.assortative.toggled.connect(self.send_data)


        self.random_seed = RandomSeedButton(parent=self)
        self.random_seed.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.realizations)
        self.main_layout.addWidget(self.n_communities)
        self.main_layout.addWidget(self.assortative)
        self.main_layout.addWidget(self.random_seed)
    def set_max_communities(self, n_nodes):
        self.n_communities.setMax(n_nodes)
        self.n_communities.setValue(2)
    def get_options(self):
        return {
            "number_communities": int(self.n_communities.value()),
            "realizations":int( self.realizations.value()),
            "assortative": self.assortative.isChecked(),
            "seed": self.random_seed.get_seed(),
        }