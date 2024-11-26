import inspect
import re

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox

from hypergraphx.viz.__graphic_options import GraphicOptions


class MenuWindow(QWidget):

    modified_options = pyqtSignal(GraphicOptions)
    def __init__(self, graphic_options = GraphicOptions(), parent = None):
        super(MenuWindow, self).__init__(parent)
        self.graphic_options = graphic_options
        self.setWindowTitle("Options")
        self.layout = QVBoxLayout()
        attributes = self.graphic_options.__dict__
        to_remove = [attribute for attribute in attributes if "default" in attribute]
        for attribute in to_remove:
            attributes.pop(attribute)
        for attribute_name in attributes:
            if "color" in attribute_name:
                self.add_lineEdit(attribute_name, attributes[attribute_name], True)
            elif "shape" in attribute_name:
                self.add_combobox(attribute_name, attributes[attribute_name])
            elif "size" in attribute_name:
                if attributes[attribute_name] is not None:
                    self.add_spinbox(attribute_name, attributes[attribute_name])
        self.setLayout(self.layout)
    def send_data(self):
        self.modified_options.emit(self.graphic_options)

    def add_lineEdit(self, name, value, color = False):
        hbox_btn = QHBoxLayout()
        label = QLabel(name)
        hbox_btn.addWidget(label)
        lineEdit = QLineEdit(str(value))
        def lineEdit_selection():
            if color:
                hex_pattern = r'^#[0-9a-fA-F]{6}$'
                if re.match(hex_pattern, lineEdit.text()):
                    self.graphic_options.__setattr__(name, lineEdit.text())
            else:
                self.graphic_options.__setattr__(name, lineEdit.text())
            self.send_data()

        lineEdit.textChanged.connect(lineEdit_selection)
        hbox_btn.addWidget(lineEdit)
        self.layout.addLayout(hbox_btn)

    def add_combobox(self, name, value):
        hbox_btn = QHBoxLayout()
        label = QLabel(name)
        hbox_btn.addWidget(label)
        combobox = QComboBox()
        translation_dictionary = dict()
        translation_dictionary['.'] = "Small Circle"
        translation_dictionary['o'] = "Big Circle"
        translation_dictionary['v'] = "Down Triangle"
        translation_dictionary['^'] = "Up Triangle"
        translation_dictionary['<'] = "Left Triangle"
        translation_dictionary['>'] = "Right Triangle"
        translation_dictionary['8'] = "Octagon"
        translation_dictionary['s'] = "Square"
        translation_dictionary['p'] = "Pentagon"
        translation_dictionary['*'] = "Star"
        translation_dictionary['h'] = "Vertical Hexagon"
        translation_dictionary['H'] = "Horizontal Hexagon"
        translation_dictionary['D'] = "Regular Rhombus"
        translation_dictionary['d'] = "Rhombus"
        translation_dictionary['P'] = "Plus"
        translation_dictionary['X'] = "Cross"

        combobox.addItems(translation_dictionary.values())
        combobox.setCurrentText(translation_dictionary[value])

        def comboBox_selection():
            key_list = list(translation_dictionary.keys())
            val_list = list(translation_dictionary.values())
            position = val_list.index(combobox.currentText())
            self.graphic_options.__setattr__(name, key_list[position])
            self.send_data()

        combobox.currentTextChanged.connect(comboBox_selection)
        hbox_btn.addWidget(combobox)
        self.layout.addLayout(hbox_btn)

    def add_spinbox(self, name, value):
        hbox_btn = QHBoxLayout()
        label = QLabel(name)
        hbox_btn.addWidget(label)
        spinBox = QDoubleSpinBox()
        spinBox.setDecimals(0)
        spinBox.setRange(1, 100000000)
        spinBox.setValue(value)
        spinBox.setSingleStep(1)

        def spinBox_selection():
            self.graphic_options.__setattr__(name, spinBox.value())
            self.send_data()

        spinBox.valueChanged.connect(spinBox_selection)
        hbox_btn.addWidget(spinBox)
        self.layout.addLayout(hbox_btn)

def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }