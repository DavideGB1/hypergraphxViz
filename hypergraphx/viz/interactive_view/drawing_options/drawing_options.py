from PyQt5.QtWidgets import QCheckBox, QPushButton

from hypergraphx.viz.interactive_view.custom_widgets.custom_iterator import IterationsSelector
from hypergraphx.viz.interactive_view.custom_widgets.custom_spinbox import SpinboxCustomWindget
from hypergraphx.viz.interactive_view.drawing_options.base_options import BaseOptionsWidget


class PAOHOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.space_optimization_btn = QCheckBox("Optimize Space Usage", self)
        self.space_optimization_btn.toggled.connect(self.send_data)
        self.main_layout.addWidget(self.space_optimization_btn)

    def get_options(self):
        return {"space_optimization": self.space_optimization_btn.isChecked(), "sort_nodes_by": False}

class RadialOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.labels_button = QCheckBox("Show Labels", self)
        self.labels_button.setChecked(True)
        self.labels_button.toggled.connect(self.send_data)
        self.main_layout.addWidget(self.labels_button)

    def get_options(self):
        return {"draw_labels": self.labels_button.isChecked()}


class CliqueOptionsWidget(BaseOptionsWidget):
    def _setup_widgets(self):
        self.labels_button = QCheckBox("Show Labels", self)
        self.labels_button.setChecked(True)
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
        self.labels_button.setChecked(True)
        self.labels_button.toggled.connect(self.send_data)

        self.ignore_binary_relations_btn = QCheckBox("Ignore Binary Relations", self)
        self.ignore_binary_relations_btn.setChecked(False)
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
        self.labels_button.setChecked(True)
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
        self.labels_button.setChecked(True)
        self.labels_button.toggled.connect(self.send_data)

        self.rounded_polygons_btn = QCheckBox("Draw Rounded Polygons", self)
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