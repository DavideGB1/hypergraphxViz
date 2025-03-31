from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QCheckBox
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.community_options.__community_option_menu import SpinboxCustomWindget
from hypergraphx.viz.interactive_view.custom_widgets import ComboBoxCustomWindget, ColorPickerCustomWidget
from hypergraphx.viz.interactive_view.graphic_enum import GraphicOptionsName


def get_PAOH_options(weighted = False, is_directed = False):
    """
    Parameters
    ----------
    weighted : bool, optional
        If True, includes options specific to weighted graphs such as "weight_size".
    is_directed : bool, optional
        If True, includes options specific to directed graphs such as "in_edge_color" and "out_edge_color".

    Returns
    -------
    list of str
        A list of customizable options for graph visualization, such as "node_size", "node_shape", and others.
        Additional options are included based on whether the graph is weighted and/or directed.
    """
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
    """
    Parameters
    ----------
    weighted : bool, optional
        Determines whether the graph uses weighted edges. If True, options related to edge weights are included.
    is_directed : bool, optional
        Determines whether the graph is directed. If True, options related to directionality of edges are included.

    Returns
    -------
    list
        A list of available radial layout configuration options including node, edge, and label properties. Additional options may be included depending on the weighted and is_directed parameters.
    """
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
    """
    Parameters
    ----------
    weighted : bool, optional
        Determines if additional options related to edge weights should be included.
    is_directed : bool, optional
        Determines if additional options related to directed edges should be included.

    Returns
    -------
    list
        A list of strings representing available node and edge customization options.
    """
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
    """
    Generates a list of visualization options for a bipartite graph based on the graph's attributes.

    Parameters
    ----------
    weighted : bool, optional
        Determines whether to include options related to edge weights. If True, adds weight-based visualization options.
    is_directed : bool, optional
        Determines whether the graph is directed. If True, adds options for in-edge and out-edge color specifications.

    Returns
    -------
    list
        A list of strings representing the visualization customization options available for bipartite graphs.
    """
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
    """
    Parameters
    ----------
    weighted : bool, optional
        Indicates whether the graph is weighted. If True, additional weighted options are included.
    is_directed : bool, optional
        Indicates whether the graph is directed. If True, additional directed options are included.

    Returns
    -------
    list
        A list of configuration options for graph visualization based on the specified parameters.
    """
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
    """
        Generates a list of options related to the customization of a graph's visual appearance.

        Returns
        -------
        list
            A list of strings representing different customization options for graph styles, including nodes, edges, and labels.
    """
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
    GraphicOptionsWidget is a widget class used to dynamically create and manage graphical configuration options for user-defined customization of a graphical user interface. It provides functionality for adding various input controls like color pickers, spinboxes, and comboboxes based on the attributes of a given graphic options object and optionally extra attributes.

    Attributes
    ----------
    modified_options : pyqtSignal
        Signal that is emitted when graphical options are modified, sending the updated configuration.
    label_size_spinbox : SpinboxCustomWindget or None
        Spinbox widget for configuring label size.
    node_size_spinbox : SpinboxCustomWindget or None
        Spinbox widget for configuring node size.
    balance_node_label_sizes : bool
        Flag to indicate whether node and label sizes should be balanced automatically.
    balance_n_l_size : QCheckBox
        Checkbox option for enabling or disabling the balance between node and label sizes.
    graphic_options : GraphicOptions
        Stores a deep copy of the input graphic options for modification.
    extra_attributes : dict
        Stores additional attributes provided for customization.
    widget_list : list
        List of widgets created and added to the user interface dynamically.

    Methods
    -------
    __init__(graphic_options=GraphicOptions(), extra_attributes=None, relevant=get_PAOH_options(), parent=None)
        Initializes the widget and dynamically creates input controls based on provided attributes.

    send_data()
        Sends the modified options to the main application via the `modified_options` signal.

    add_color_picker(name, value, in_extra=False)
        Adds a color picker to the main layout.

    add_combobox(name, value)
        Adds a combobox to the main layout for selecting from predefined options.

    add_spinbox(name, value, in_extra=False)
        Adds a spinbox to the main layout with integer or float values, providing options for numerical input.
    """
    modified_options = pyqtSignal(tuple)
    def __init__(self,graphic_options = GraphicOptions(),extra_attributes = None, relevant = get_PAOH_options(), parent = None):
        super(GraphicOptionsWidget, self).__init__(parent)
        self.label_size_spinbox = None
        self.node_size_spinbox = None
        self.balance_node_label_sizes = True
        self.balance_n_l_size = QCheckBox("Balance Node and Label Sizes")
        self.balance_n_l_size.setChecked(True)
        self.graphic_options = graphic_options.copy()
        self.extra_attributes = dict()
        self.extra_attributes = extra_attributes
        self.widget_list = list()
        self.widget_list.append(self.balance_n_l_size)
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
        send_data()

        Sends the collected data by emitting a signal containing the graphic options and any additional attributes.

        Attributes, if not defined earlier, are initialized as an empty dictionary before emitting the signal.

        Raises
        ------
        None
        """
        if self.extra_attributes is None:
            self.extra_attributes = dict()
        self.modified_options.emit((self.graphic_options, self.extra_attributes))

    def add_color_picker(self, name: str, value: str, in_extra: bool = False) -> None:
        """
        Adds a custom color picker widget to the interface.

        The color picker widget is created using the provided parameters and is configured to interact with the existing system through event connections.
        It is then added to the widget list for further use.

        Parameters
        ----------
        name : str
            The unique name or identifier for the color picker widget.
        value : str
            The default value or initial color selection for the color picker.
        in_extra : bool, optional
            Indicates whether the color picker belongs to an additional attributes section (default is False).
        """
        color_picker = ColorPickerCustomWidget(name,value, in_extra, self.graphic_options,self.extra_attributes)
        color_picker.update_status.connect(self.send_data)
        self.widget_list.append(color_picker)

    def add_combobox(self, name: str, value: str) -> None:
        """
        Adds a ComboBox widget with predefined symbol translation options to the interface.

        Parameters
        ----------
        name : str
            The name of the ComboBox, used for identifying its purpose in the interface.

        value : str
            The initial value of the ComboBox, which corresponds to one of the symbols in the translation dictionary.

        Notes
        -----
        This method uses a predefined dictionary `translation_dictionary` that maps symbols to descriptive text.
        The function creates a ComboBox widget with these options and updates the associated attribute in `self.graphic_options` whenever the selection is changed.
        The updated data is sent through `self.send_data()`.
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
        Adds a spinbox widget to the UI.

        Parameters
        ----------
        name : str
            The name of the graphic option to configure with the spinbox widget.
        value : int or float
            The default value to set in the spinbox widget.
        in_extra : bool, optional
            Indicates if the value adjusted by the spinbox is part of extra attributes
            or standard graphic options (default is False).
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
        if name == "node_size":
            self.node_size_spinbox = spinbox
            def spinBox_selection_ns():
                if self.balance_n_l_size.isChecked():
                    ls = spinbox.get_val()/30
                    try:
                        self.label_size_spinbox.spinBox.setValue(ls)
                    except Exception:
                        pass
                self.graphic_options.__setattr__(name, spinbox.get_val())
                self.send_data()
            spinbox.update_status.connect(spinBox_selection_ns)
        if name == "label_size":
            self.label_size_spinbox = spinbox
            def spinBox_selection_ls():
                if self.balance_n_l_size.isChecked():
                    ns = spinbox.get_val()*30
                    try:
                        self.node_size_spinbox.spinBox.setValue(ns)
                    except Exception:
                        pass
                self.graphic_options.__setattr__(name, spinbox.get_val())
                self.send_data()
            spinbox.update_status.connect(spinBox_selection_ls)
        else:
            def spinBox_selection():
                if in_extra:
                    self.extra_attributes[name] = spinbox.get_val()
                else:
                    self.graphic_options.__setattr__(name, spinbox.get_val())
                self.send_data()
            spinbox.update_status.connect(spinBox_selection)

        self.widget_list.append(spinbox)