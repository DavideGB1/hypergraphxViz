from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox

from hypergraphx.viz.interactive_view.custom_widgets.custom_spinbox import SpinboxCustomWindget


class AggregationWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)

        self.enable_aggregation_button = QCheckBox("Use Simplification Techniques", self)
        self.aggregation_threshold_spinbox = SpinboxCustomWindget("Aggregation Threshold", 0, 1,0.8, "aggregation_threshold", decimals=2, step=0.05, parent=self)
        self.polygonal_button = QCheckBox("Polygonal Simplification", self)

        self.layout.addWidget(self.enable_aggregation_button)
        self.layout.addWidget(self.aggregation_threshold_spinbox)
        self.layout.addWidget(self.polygonal_button)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def get_options(self):
        return {
            "use_simplification": self.enable_aggregation_button.isChecked(),
            "aggregation_threshold": self.aggregation_threshold_spinbox.value(),
            "use_polygonal_simplification": self.polygonal_button.isChecked()
        }