import inspect
import re
from copy import deepcopy
from typing import Dict

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, \
    QColorDialog, QPushButton

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.__options_enum import OptionsName


class MenuWindow(QWidget):

    modified_options = pyqtSignal(tuple)
    def __init__(self, graphic_options = GraphicOptions(),extra_attributes = None, parent = None):
        super(MenuWindow, self).__init__(parent)
        self.graphic_options = deepcopy(graphic_options)
        self.extra_attributes = dict()
        self.extra_attributes = extra_attributes
        self.setWindowTitle("Options")
        self.layout = QVBoxLayout()
        attributes = self.graphic_options.__dict__
        to_remove = [attribute for attribute in attributes if "default" in attribute]
        for attribute in to_remove:
            attributes.pop(attribute)
        try:
            attributes.pop("in_edge_color")
        except KeyError:
            pass
        try:
            attributes.pop("out_edge_color")
        except KeyError:
            pass
        attributes.update(extra_attributes)

        for attribute_name in attributes:
            if "color" in attribute_name:
                self.add_color_picker(attribute_name, attributes[attribute_name])
            elif "shape" in attribute_name:
                self.add_combobox(attribute_name, attributes[attribute_name])
            elif "size" in attribute_name:
                if attributes[attribute_name] is not None:
                    self.add_spinbox(attribute_name, attributes[attribute_name])
            elif "factor" in attribute_name:
                self.add_spinbox(attribute_name, attributes[attribute_name], True, True)
            elif "alpha" in attribute_name:
                self.add_spinbox(attribute_name, attributes[attribute_name], True, True)
        self.setLayout(self.layout)
    def send_data(self):
        self.modified_options.emit((self.graphic_options, self.extra_attributes))
    def add_color_picker(self, name, value, in_extra = False):
        hbox_btn = QHBoxLayout()
        label = QLabel(OptionsName[name].value)
        hbox_btn.addWidget(label)
        color_btn = QPushButton()
        pixmap = QPixmap(int(color_btn.width()*0.95), int(color_btn.height()*0.9))
        pixmap.fill(QColor(value))
        color_btn.setIcon(QIcon(pixmap))

        def color_picker():
            dialog = QColorDialog(self)
            if in_extra:
                dialog.setCurrentColor(QColor(self.extra_attributes[name]))
            else:
                dialog.setCurrentColor(QColor(self.graphic_options.__getattribute__(name)))
            dialog.exec_()
            new_color = dialog.currentColor()
            pixmap = QPixmap(int(color_btn.width() * 0.95), int(color_btn.height() * 0.9))
            pixmap.fill(QColor(new_color))
            color_btn.setIcon(QIcon(pixmap))
            if in_extra:
                self.extra_attributes[name] = value
            else:
                self.graphic_options.__setattr__(name, new_color.name())
            self.send_data()

        color_btn.clicked.connect(color_picker)
        hbox_btn.addWidget(color_btn)
        self.layout.addLayout(hbox_btn)
    def add_lineEdit(self, name, value, color = False):
        hbox_btn = QHBoxLayout()
        label = QLabel(OptionsName[name].value)
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
        label = QLabel(OptionsName[name].value)
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
    def add_spinbox(self, name, value, decimals = False, in_extra = False):
        hbox_btn = QHBoxLayout()
        label = QLabel(OptionsName[name].value)
        hbox_btn.addWidget(label)
        spinBox = QDoubleSpinBox()
        if decimals:
            spinBox.setDecimals(2)
            spinBox.setRange(0.01, 1000)
            spinBox.setValue(value)
            spinBox.setSingleStep(0.1)
        else:
            spinBox.setDecimals(0)
            spinBox.setRange(1, 100000000)
            spinBox.setValue(value)
            spinBox.setSingleStep(1)

        def spinBox_selection():
            if in_extra:
                self.extra_attributes[name] = spinBox.value()
            else:
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