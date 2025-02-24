import sys
from copy import deepcopy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QColorDialog, \
    QPushButton, QCheckBox, QApplication, QMainWindow
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.graphic_options.__graphic_options_enum import GraphicOptionsName


class PAOHOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(PAOHOptionsWidget, self).__init__(parent)
        self.widget_list = list()
        self.space_optimization = False
        self.vbox_PAOH_option = QVBoxLayout()
        space_optimization_option_btn = QCheckBox("Optimize Space Usage")
        space_optimization_option_btn.setChecked(False)

        def optimize_space_usage():
            if self.space_optimization:
                self.space_optimization = False
            else:
                self.space_optimization = True
            self.send_data()

        space_optimization_option_btn.toggled.connect(optimize_space_usage)
        self.widget_list.append(space_optimization_option_btn)
    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        dict = {"space_optimization": self.space_optimization}
        self.modified_options.emit(dict)

class RadialOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(RadialOptionsWidget, self).__init__(parent)
        self.widget_list = list()
        self.labels_button = LabelButton()

        self.labels_button.update_status.connect(self.send_data)
        self.widget_list.append(self.labels_button.button)

    def send_data(self):
        """
        Sends the modified options to the main menu.
        """
        print("roce")
        dict = {"draw_labels": self.labels_button.button.isChecked()}
        self.modified_options.emit(dict)

class CliqueOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(CliqueOptionsWidget, self).__init__(parent)
        self.use_last = True
        self.widget_list = list()

        self.iterations_selector = IterationsSelector()
        self.iterations_selector.changed_value.connect(self.send_data)

        self.labels_button = LabelButton()
        self.labels_button.update_status.connect(self.send_data)

        self.widget_list.append(self.labels_button.button)
        self.widget_list.append(self.iterations_selector.iterations_selector_label)
        self.widget_list.append(self.iterations_selector.spinbox)

    def send_data(self, dict = None):
        """
        Sends the modified options to the main menu.
        """
        try:
            self.use_last = dict["use_last"]
        except KeyError:
            self.use_last = True
        dict = {"draw_labels": self.labels_button.button.isChecked(), "iterations": int(self.iterations_selector.spinbox.value()),
                "use_last": self.use_last}
        self.modified_options.emit(dict)
        self.use_last = True

class ExtraNodeOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(ExtraNodeOptionsWidget, self).__init__(parent)
        self.use_last = True
        self.ignore_binary_relations = False
        self.show_edge_nodes = False
        self.widget_list = list()
        self.iterations_selector = IterationsSelector()
        self.iterations_selector.changed_value.connect(self.send_data)

        self.labels_button = LabelButton()
        self.labels_button.update_status.connect(self.send_data)

        ignore_binary_relations_btn = QCheckBox("Ignore Binary Relations")
        def ignore_binary_relations_funz():
            if self.ignore_binary_relations:
                self.ignore_binary_relations = False
            else:
                self.ignore_binary_relations = True
            self.use_last = False
            self.send_data()
        ignore_binary_relations_btn.toggled.connect(ignore_binary_relations_funz)
        ignore_binary_relations_btn.setChecked(True)

        edge_nodes_btn = QCheckBox("Show Edge Nodes")
        def activate_edge_nodes():
            if self.show_edge_nodes:
                self.show_edge_nodes = False
            else:
                self.show_edge_nodes = True
            self.use_last = False
            self.send_data()
        edge_nodes_btn.toggled.connect(activate_edge_nodes)
        edge_nodes_btn.setChecked(True)

        self.widget_list.append(self.labels_button.button)
        self.widget_list.append(ignore_binary_relations_btn)
        self.widget_list.append(edge_nodes_btn)
        self.widget_list.append(self.iterations_selector.iterations_selector_label)
        self.widget_list.append(self.iterations_selector.spinbox)
    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        dict = {"draw_labels": self.labels_button.button.isChecked(), "iterations": int(self.iterations_selector.spinbox.value()), "use_last": self.use_last,
                "show_edge_nodes": self.show_edge_nodes, "ignore_binary_relations": self.ignore_binary_relations,}
        self.modified_options.emit(dict)
        self.use_last = True

class BipartiteOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(BipartiteOptionsWidget, self).__init__(parent)
        self.widget_list = list()
        self.alignment = "horizontal"
        def change_alignment():
            if self.alignment == "vertical":
                self.alignment = "horizontal"
            else:
                self.alignment = "vertical"
            self.send_data()

        change_alignment_btn = QPushButton("Change Alignment")
        change_alignment_btn.setChecked(True)
        change_alignment_btn.clicked.connect(change_alignment)

        self.labels_button = LabelButton()
        self.labels_button.update_status.connect(self.send_data)

        self.widget_list.append(self.labels_button.button)
        self.widget_list.append(change_alignment_btn)
    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        dict = {"align": self.alignment, "draw_labels": self.labels_button.button.isChecked()}
        self.modified_options.emit(dict)

class SetOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(SetOptionsWidget, self).__init__(parent)
        self.widget_list = list()
        self.rounded_polygons = True
        self.labels_button = LabelButton()
        self.labels_button.update_status.connect(self.send_data)

        self.rounded_polygons_btn = QCheckBox("Draw Rounded Polygons")
        def rounded_polygons():
            if self.rounded_polygons:
                self.rounded_polygons = False
            else:
                self.rounded_polygons = True
            self.use_last = False
            self.send_data()
        self.rounded_polygons_btn.toggled.connect(rounded_polygons)
        self.rounded_polygons_btn.setChecked(True)

        self.widget_list.append(self.labels_button.button)
        self.widget_list.append(self.rounded_polygons_btn)
    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        dict = {"rounded_polygon":self.rounded_polygons_btn.isChecked(),"draw_labels": self.labels_button.button.isChecked()}
        self.modified_options.emit(dict)

class LabelButton(QWidget):
    update_status = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(LabelButton, self).__init__()
        self.button = QCheckBox("Show Labels")
        self.button.setChecked(True)
        def use_labels():
            self.update_status.emit({ "val" : self.button.isChecked()})
        self.button.toggled.connect(use_labels)

class IterationsSelector(QWidget):
    changed_value = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(IterationsSelector, self).__init__()
        self.iterations_selector_label = QLabel()
        self.iterations_selector_label.setText("Number of Iterations:")
        self.spinbox = QDoubleSpinBox()
        def iterations_selector_funz():
            self.changed_value.emit({"use_last": False})
        self.spinbox.setDecimals(0)
        self.spinbox.setRange(0, 100000000)
        self.spinbox.setValue(1000)
        self.spinbox.setSingleStep(1)
        self.spinbox.valueChanged.connect(iterations_selector_funz)
