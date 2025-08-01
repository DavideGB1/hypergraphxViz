from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QWidget, QVBoxLayout, QScrollArea

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.custom_widgets.color_picker import ColorPickerCustomWidget
from hypergraphx.viz.interactive_view.custom_widgets.custom_combobox import ComboBoxCustomWindget
from hypergraphx.viz.interactive_view.custom_widgets.custom_spinbox import SpinboxCustomWindget
from hypergraphx.viz.interactive_view.graphic_options.graphic_enum import GraphicOptionsName


class BaseGraphicOptionsWidget(QWidget):
    """
    Base class for graphical options widgets.
    Provides helper methods to create input widgets and handles common logic.
    """
    modified_options = pyqtSignal(tuple)

    def __init__(self, graphic_options: GraphicOptions, extra_attributes: dict = None, parent=None):
        super().__init__(parent)
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(container_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.scroll_content_widget = QWidget()
        scroll_area.setWidget(self.scroll_content_widget)

        self.main_layout = QVBoxLayout(self.scroll_content_widget)
        self.main_layout.setContentsMargins(9, 9, 9, 9)
        self.main_layout.setSpacing(10)

        container_layout.addWidget(scroll_area)
        self.graphic_options = graphic_options.copy()
        self.extra_attributes = extra_attributes or {}

        self.node_size_spinbox = None
        self.label_size_spinbox = None
        self.balance_checkbox = None
        self.scroll_content_widget.setObjectName("GraphicOptionsContent")
        self.scroll_content_widget.setStyleSheet("""
                    QWidget#GraphicOptionsContent {
                        background-color: white;
                        border: 1px solid #dcdcdc;
                        border-radius: 5px;
                        border-top-left-radius: 0px;
                    }
                """)
        self._setup_widgets()

    def _setup_widgets(self):
        """Virtual method that subclasses must implement."""
        raise NotImplementedError("Le sottoclassi devono implementare questo metodo.")

    def send_data(self):
        """Outputs the modified data."""
        self.modified_options.emit((self.graphic_options, self.extra_attributes))

    def get_data(self):
        """Returns the modified data."""
        return (self.graphic_options, self.extra_attributes)

    def _create_and_add_widgets(self, option_names: list):
        """
        Helper method that iterates over options and creates corresponding widgets.
        """
        attributes = self.graphic_options.__dict__
        attributes.update(self.extra_attributes)

        for name in option_names:
            value = attributes.get(name)
            if value is None:
                continue

            if "color" in name:
                self.add_color_picker(name, value)
            elif "shape" in name:
                self.add_combobox(name, value)
            elif any(s in name for s in ["size", "factor", "alpha", "radius"]):
                in_extra = name in self.extra_attributes
                spinbox = self.add_spinbox(name, value, in_extra)
                if name == "node_size":
                    self.node_size_spinbox = spinbox
                elif name == "label_size":
                    self.label_size_spinbox = spinbox

        if self.node_size_spinbox and self.label_size_spinbox:
            self._add_balance_size_feature()

    def add_color_picker(self, name: str, value: str):
        color_picker = ColorPickerCustomWidget(name, value, False, self.graphic_options, self.extra_attributes, self)
        color_picker.update_status.connect(self.send_data)
        self.main_layout.addWidget(color_picker)
        return color_picker

    def add_combobox(self, name: str, value: str):
        translation = {'.': "Small Circle", 'o': "Big Circle", 'v': "Down Triangle", '^': "Up Triangle",
                       '<': "Left Triangle", '>': "Right Triangle", '8': "Octagon", 's': "Square", 'p': "Pentagon",
                       '*': "Star", 'h': "Vertical Hexagon", 'H': "Horizontal Hexagon", 'D': "Regular Rhombus",
                       'd': "Rhombus", 'P': "Plus", 'X': "Cross"}

        combobox = ComboBoxCustomWindget(name, value, translation, self)

        def update_shape():
            key = next((k for k, v in translation.items() if v == combobox.combobox.currentText()), '.')
            self.graphic_options.__setattr__(name, key)
            self.send_data()

        combobox.update_status.connect(update_shape)
        self.main_layout.addWidget(combobox)
        return combobox

    def add_spinbox(self, name: str, value: int | float, in_extra: bool = False):
        params = self._get_spinbox_params(name, value)
        spinbox = SpinboxCustomWindget(*params, parent=self)

        def on_value_changed():
            if in_extra:
                self.extra_attributes[name] = spinbox.value()
            else:
                self.graphic_options.__setattr__(name, spinbox.value())
            self.send_data()

        spinbox.update_status.connect(on_value_changed)
        self.main_layout.addWidget(spinbox)
        return spinbox

    def _get_spinbox_params(self, name, value):
        """Helper to return correct parameters for Spinbox Custom Windget."""
        label = GraphicOptionsName[name].value if name in GraphicOptionsName.__members__ else name.replace("_"," ").title()
        if name == "hyperedge_alpha":
            return (label, 0, 1, value, name, 2, 0.1)
        if isinstance(value, float):
            return (label, 0.01, 1000, value, name, 2, 0.1)
        if isinstance(value, int):
            return (label, 1, 1000000000, value, name)
        return (label, 0, 1, value, name, 2, 0.1)  # Fallback

    def _add_balance_size_feature(self):
        """Adds checkbox and logic to balance node and label sizes."""
        self.balance_checkbox = QCheckBox("Balance Node and Label Sizes", self)
        self.balance_checkbox.setStyleSheet(
            """
                QCheckBox {
                    spacing: 10px;
                    color: #333;
                    font-size: 13px;
                    padding-bottom: 3px; 
                }

                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 5px;
                }

                QCheckBox::indicator:unchecked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F5F5F5, stop: 1 #E0E0E0);
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
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #5D9CEC, stop: 1 #4A89DC);
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
        self.balance_checkbox.setChecked(True)
        self.main_layout.addWidget(self.balance_checkbox)

        self.node_size_spinbox.update_status.disconnect()
        self.label_size_spinbox.update_status.disconnect()

        def update_node_size():
            new_val = self.node_size_spinbox.value()
            self.graphic_options.node_size = new_val
            if self.balance_checkbox.isChecked():
                self.label_size_spinbox.spinBox.blockSignals(True)
                self.label_size_spinbox.spinBox.setValue(new_val / 30)
                self.graphic_options.label_size = new_val / 30
                self.label_size_spinbox.spinBox.blockSignals(False)
            self.send_data()

        def update_label_size():
            new_val = self.label_size_spinbox.value()
            self.graphic_options.label_size = new_val
            if self.balance_checkbox.isChecked():
                self.node_size_spinbox.spinBox.blockSignals(True)
                self.node_size_spinbox.spinBox.setValue(new_val * 30)
                self.graphic_options.node_size = new_val * 30
                self.node_size_spinbox.spinBox.blockSignals(False)
            self.send_data()

        self.node_size_spinbox.update_status.connect(update_node_size)
        self.label_size_spinbox.update_status.connect(update_label_size)
