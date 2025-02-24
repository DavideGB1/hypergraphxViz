from copy import deepcopy
from enum import Enum

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDoubleSpinBox, QColorDialog, QPushButton
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import SpinboxCustomWindget

class GraphicOptionsName(Enum):
    """
    Enum used to translate some GUI labels into normal strings
    """
    node_shape = "Node Shape"
    edge_shape = "Edge Shape"
    node_color = "Node Color"
    node_facecolor = "Node Face Color"
    label_color = "Label Color"
    in_edge_color = "In-Edge Color"
    out_edge_color = "Out-Edge Color"
    edge_node_color = "Edge Node Color"
    edge_color = "Edge Color"
    edge_size = "Edge Size"
    label_size = "Label Size"
    node_size = "Node Size"
    radius_scale_factor = "Radius Scale Factor"
    font_spacing_factor = "Font Spacing Factor"
    rounding_radius_factor = "Rounding Radius Size"
    polygon_expansion_factor = "Polygon Expansion Factor"
    hyperedge_alpha = "Hyperedge Alpha"
    weight_size = "Weights Size"

def get_PAOH_options(weighted = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    if weighted:
        options.append("weight_size")
    return options

def get_Radial_options(weighted = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    options.append("edge_shape")
    options.append("edge_node_color")
    options.append("label_size")
    options.append("label_color")
    options.append("radius_scale_factor")
    options.append("font_spacing_factor")
    if weighted:
        options.append("weight_size")
    return options

def get_ExtraNode_options(weighted = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    options.append("edge_shape")
    options.append("edge_node_color")
    options.append("label_size")
    options.append("label_color")
    if weighted:
        options.append("weight_size")
    return options

def get_Bipartite_options(weighted = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    options.append("edge_shape")
    options.append("edge_node_color")
    options.append("label_size")
    options.append("label_color")
    if weighted:
        options.append("weight_size")
    return options

def get_Sets_options(weighted = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    options.append("label_size")
    options.append("label_color")
    options.append("hyperedge_alpha")
    options.append("rounding_radius_factor")
    options.append("polygon_expansion_factor")
    if weighted:
        options.append("weight_size")
    return options

def get_Clique_options(weighted = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    options.append("label_size")
    options.append("label_color")
    return options

class GraphicOptionsWidget(QWidget):
    """
    Class used to represent the Graphic Options Menu.
    ...
    Attributes
    ----------
    graphic_options : GraphicOptions
        Graphic Options that determine what to show to the user.
    extra_attributes : dict
        Extra attributes not found in the generic graphic options.
    layout : QVBoxLayout
        Basic layout of the menu.
    Methods
    -------
    send_data():
        Sends the modified options to the main menu.
    add_color_picker(name, value, in_extra = False):
        Adds a color picker option to the main layout.
    add_combobox(name, value):
        Adds a ComboBox option to the main layout.
    add_spinbox(name, value, decimals = False, in_extra = False):
        Adds a SpinBox option to the main layout.
    """
    modified_options = pyqtSignal(tuple)
    def __init__(self,graphic_options = GraphicOptions(),extra_attributes = None, relevant = get_PAOH_options(), parent = None):
        super(GraphicOptionsWidget, self).__init__(parent)
        self.graphic_options = graphic_options
        self.extra_attributes = dict()
        self.extra_attributes = extra_attributes
        self.widget_list = list()
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
        try:
            attributes.update(extra_attributes)
        except TypeError:
            pass

        for attribute_name in attributes:
            if attribute_name in relevant:
                if "color" in attribute_name:
                    self.add_color_picker(attribute_name, attributes[attribute_name])
                elif "shape" in attribute_name:
                    self.add_combobox(attribute_name, attributes[attribute_name])
                elif "size" in attribute_name:
                    if attributes[attribute_name] is not None:
                        self.add_spinbox(attribute_name, attributes[attribute_name])
                elif "factor" in attribute_name:
                    self.add_spinbox(attribute_name, attributes[attribute_name], True)
                elif "alpha" in attribute_name:
                    self.add_spinbox(attribute_name, attributes[attribute_name], True)
    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        if self.extra_attributes is None:
            self.extra_attributes = dict()
        self.modified_options.emit((self.graphic_options, self.extra_attributes))
    def add_color_picker(self, name: str, value: str, in_extra: bool = False) -> None:
        """
        Adds a color picker option to the main layout.
        Parameters
        ----------
        name : str
            Name of the new color picker entry.
        value : str
            Starting value of the new color picker entry.
        in_extra : bool
            Determines if the new color picker value is related to the extra-attributes.
        """
        color_picker = ColorPickerCustomWidget(name,value, in_extra, self.graphic_options,self.extra_attributes)
        color_picker.update_status.connect(self.send_data)
        self.widget_list.append(color_picker)
    def add_combobox(self, name: str, value: str) -> None:
        """
        Adds a combobox option to the main layout.
        Parameters
        ----------
        name : str
            Name of the new combobox entry.
        value : str
            Starting value of the new combobox entry.
        """
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

        combobox = ComboBoxCustomWindget(name,value, translation_dictionary)
        def update_data():
            key_list = list(translation_dictionary.keys())
            val_list = list(translation_dictionary.values())
            position = val_list.index(combobox.combobox.currentText())
            self.graphic_options.__setattr__(name, key_list[position])
            self.send_data()
        combobox.update_status.connect(update_data)
        self.widget_list.append(combobox)

    def add_spinbox(self, name: str, value: int | float, in_extra: bool = False) -> None:
        """
        Adds a spinbox option to the main layout.
        Parameters
        ----------
        name : str
            Name of the new spinbox entry.
        value : int | float
            Starting value of the spinbox entry.
        in_extra : bool
            Determines if the new spinbox value is related to the extra-attributes.
        """
        spinbox = None
        if name == "hyperedge_alpha":
            spinbox = SpinboxCustomWindget(GraphicOptionsName[name].value, 0,1,value, "hyperedge_alpha", 2, 0.1)
        elif isinstance(value, float):
            spinbox = SpinboxCustomWindget(GraphicOptionsName[name].value, 0.01,1000,value, name, 2, 0.1)
        elif isinstance(value, int):
            spinbox = SpinboxCustomWindget(GraphicOptionsName[name].value, 1,1000000000,value, name)
        else:
            spinbox = SpinboxCustomWindget("", 0,1,value, "", 2, 0.1)

        def spinBox_selection():
            if in_extra:
                self.extra_attributes[name] = spinbox.get_val()
            else:
                self.graphic_options.__setattr__(name, spinbox.get_val())
            self.send_data()

        spinbox.update_status.connect(spinBox_selection)
        self.widget_list.append(spinbox)

class ComboBoxCustomWindget(QWidget):
    update_status = pyqtSignal(dict)
    def __init__(self,name, value, translation_dictionary):
        super(ComboBoxCustomWindget, self).__init__()
        self.hbox = QHBoxLayout()
        self.label = QLabel(GraphicOptionsName[name].value)
        self.hbox.addWidget(self.label)
        self.combobox = QComboBox()


        self.combobox.addItems(translation_dictionary.values())
        self.combobox.setCurrentText(translation_dictionary[value])

        def comboBox_selection():
            key_list = list(translation_dictionary.keys())
            val_list = list(translation_dictionary.values())
            position = val_list.index(self.combobox.currentText())
            self.update_status.emit({name: key_list[position]})

        self.combobox.currentTextChanged.connect(comboBox_selection)
        self.hbox.addWidget(self.combobox)
        self.setLayout(self.hbox)

class ColorPickerCustomWidget(QWidget):
    update_status = pyqtSignal(dict)
    def __init__(self, name, value, in_extra, graphic_options, extra_attributes):
        super(ColorPickerCustomWidget, self).__init__()
        self.hbox = QHBoxLayout()
        label = QLabel(GraphicOptionsName[name].value)
        self.hbox.addWidget(label)
        color_btn = QPushButton()
        pixmap = QPixmap(int(color_btn.width() * 0.95), int(color_btn.height() * 0.9))
        pixmap.fill(QColor(value))
        color_btn.setIcon(QIcon(pixmap))

        def color_picker():
            dialog = QColorDialog(self)
            if in_extra:
                dialog.setCurrentColor(QColor(extra_attributes[name]))
            else:
                dialog.setCurrentColor(QColor(graphic_options.__getattribute__(name)))
                pass
            dialog.exec_()
            new_color = dialog.currentColor()
            pixmap = QPixmap(int(color_btn.width() * 0.95), int(color_btn.height() * 0.9))
            pixmap.fill(QColor(new_color))
            color_btn.setIcon(QIcon(pixmap))
            if in_extra:
                extra_attributes[name] = value
            else:
                graphic_options.__setattr__(name, new_color.name())
            self.update_status.emit(dict())
        color_btn.clicked.connect(color_picker)
        self.hbox.addWidget(color_btn)
        self.setLayout(self.hbox)