from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QScrollArea

from hypergraphx.viz.interactive_view.custom_widgets.custom_spinbox import SpinboxCustomWindget


class AggregationWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(container_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self.scroll_content_widget = QWidget()
        scroll_area.setWidget(self.scroll_content_widget)
        self.scroll_content_widget.setObjectName("GraphicOptionsContent")

        self.main_layout = QVBoxLayout(self.scroll_content_widget)
        self.main_layout.setContentsMargins(9, 9, 9, 9)
        self.main_layout.setSpacing(10)
        container_layout.addWidget(scroll_area)

        self.enable_aggregation_button = QCheckBox("Use Simplification Techniques", self)
        self.aggregation_threshold_spinbox = SpinboxCustomWindget("Aggregation Threshold", 0, 1,0.8, "aggregation_threshold", decimals=2, step=0.05, parent=self)
        self.polygonal_button = QCheckBox("Polygonal Simplification", self)

        self.main_layout.addWidget(self.enable_aggregation_button)
        self.main_layout.addWidget(self.aggregation_threshold_spinbox)
        self.main_layout.addWidget(self.polygonal_button)
        self.main_layout.addStretch()

    def get_options(self):
        return {
            "use_simplification": self.enable_aggregation_button.isChecked(),
            "aggregation_threshold": self.aggregation_threshold_spinbox.value(),
            "use_polygonal_simplification": self.polygonal_button.isChecked()
        }