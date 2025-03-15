from copy import deepcopy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import SpinboxCustomWindget
from hypergraphx.viz.interactive_view.custom_widgets import ComboBoxCustomWindget, ColorPickerCustomWidget
from hypergraphx.viz.interactive_view.graphic_enum import GraphicOptionsName


def get_PAOH_options(weighted = False, is_directed = False):
    options = list()
    options.append("node_size")
    options.append("node_shape")
    options.append("node_color")
    options.append("node_facecolor")
    options.append("edge_size")
    options.append("edge_color")
    if weighted:
        options.append("weight_size")
    if is_directed:
        options.append("in_edge_color")
        options.append("out_edge_color")
    return options

def get_Radial_options(weighted = False, is_directed = False):
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
    if is_directed:
        options.append("in_edge_color")
        options.append("out_edge_color")
    return options

def get_ExtraNode_options(weighted = False, is_directed = False):
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
    if is_directed:
        options.append("in_edge_color")
        options.append("out_edge_color")
    return options

def get_Bipartite_options(weighted = False, is_directed = False):
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
    if is_directed:
        options.append("in_edge_color")
        options.append("out_edge_color")
    return options

def get_Sets_options(weighted = False, is_directed = False):
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
    if is_directed:
        options.append("in_edge_color")
        options.append("out_edge_color")
    return options

def get_Clique_options():
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
        self.graphic_options = deepcopy(graphic_options)
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

        for attribute_name in attributes.keys():
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