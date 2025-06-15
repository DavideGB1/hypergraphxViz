from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox
from hypergraphx.viz.interactive_view.custom_widgets import LabelButton, IterationsSelector, SpinboxCustomWindget


class PAOHOptionsWidget(QWidget):
    """
        PAOHOptionsWidget
        ------------------

        A QWidget-based class that provides a user interface for adjusting PAOH widget options,
        with a focus on space optimization.

        Attributes
        ----------
        modified_options : pyqtSignal
            Signal emitted when the options are modified. Sends a dictionary of updated options.
        widget_list : list
            Internal list that stores reference to UI widgets created within the class.
        space_optimization : bool
            Indicates whether space optimization is enabled or disabled.
        vbox_PAOH_option : QVBoxLayout
            Vertical Box Layout instance for organizing the widgets visually.

        Methods
        -------
        send_data()
            Sends the modified options data as a dictionary through the `modified_options` signal.
        get_options()
            Returns a dictionary containing the current state of options.
    """
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

    def get_options(self):
        return {"space_optimization": self.space_optimization}

class RadialOptionsWidget(QWidget):
    """
    RadialOptionsWidget is a custom QWidget that provides options for radial functionalities.
    It contains a button widget to toggle the display of labels.

    Attributes
    ----------
    modified_options : pyqtSignal
        Signal emitted with a dictionary containing the modified options.

    Methods
    -------
    send_data()
        Sends the modified options to the main menu.

    get_options()
        Retrieves the current state of the radial options as a dictionary.
    """
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
        dict = {"draw_labels": self.labels_button.button.isChecked()}
        self.modified_options.emit(dict)

    def get_options(self):
        return {"draw_labels": self.labels_button.button.isChecked()}

class CliqueOptionsWidget(QWidget):
    """
        CliqueOptionsWidget
        A QWidget subclass that provides a user interface for configuring options related to clique operations. It includes
        controls for selecting the number of iterations, toggling label drawing, and handling user modifications.

        Attributes
        ----------
        modified_options : pyqtSignal
            Signal emitted with a dictionary of modified options.

        Methods
        -------
        __init__(parent=None)
            Initializes the CliqueOptionsWidget object and sets up the necessary widgets and signals.

        send_data(dict=None)
            Sends the current state of widget-derived options to the main menu via a signal.

        get_options()
            Retrieves the current state of the options configured by the user.
    """
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
        self.widget_list.append(self.iterations_selector)

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

    def get_options(self):
        try:
            self.use_last = dict["use_last"]
        except KeyError:
            self.use_last = True
        return {"draw_labels": self.labels_button.button.isChecked(), "iterations": int(self.iterations_selector.spinbox.value()),
                "use_last": self.use_last}

class ExtraNodeOptionsWidget(QWidget):
    """
    Provides a widget for configuring additional options related to node visualization. The class allows the user to adjust settings such as label display, iteration count, binary relation settings, planarity rules, and edge node display. Updated options are communicated via the `modified_options` signal.

    Attributes
    ----------
    modified_options : pyqtSignal
        Signal that emits a dictionary containing the updated widget options.
    use_last : bool
        Indicates whether the last-used configuration should be used.
    ignore_binary_relations : bool
        Determines whether binary relations should be ignored.
    ignore_planarity : bool
        Determines whether planarity constraints should be ignored.
    show_edge_nodes : bool
        Specifies whether to display additional nodes at the edges.
    widget_list : list
        List of widgets managed by this class.
    iterations_selector : IterationsSelector
        Custom widget for selecting the number of iterations.
    labels_button : LabelButton
        Custom button widget for label-related settings.

    Methods
    -------
    __init__(parent=None)
        Initializes the widget and sets up the internal state, including associated signals and slots for user interactions.
    send_data()
        Sends the current modified options to the main menu via the `modified_options` signal.
    get_options()
        Returns the current configuration options as a dictionary.
    """
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(ExtraNodeOptionsWidget, self).__init__(parent)
        self.use_last = True
        self.ignore_binary_relations = False
        self.ignore_planarity = True
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

        ignore_planarity_btn = QCheckBox("Ignore Planarity")
        def ignore_planarity_funz():
            if self.ignore_planarity:
                self.ignore_planarity = False
            else:
                self.ignore_planarity = True
            self.use_last = False
            self.send_data()

        ignore_planarity_btn.toggled.connect(ignore_planarity_funz)
        ignore_planarity_btn.setChecked(True)

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
        self.widget_list.append(ignore_planarity_btn)
        self.widget_list.append(self.iterations_selector)

    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        dict = {"draw_labels": self.labels_button.button.isChecked(), "iterations": int(self.iterations_selector.spinbox.value()), "use_last": self.use_last,
                "show_edge_nodes": self.show_edge_nodes, "ignore_binary_relations": self.ignore_binary_relations, "respect_planarity": self.ignore_planarity,}
        self.modified_options.emit(dict)
        self.use_last = True

    def get_options(self):
        return {"draw_labels": self.labels_button.button.isChecked(), "iterations": int(self.iterations_selector.spinbox.value()), "use_last": self.use_last,
                "show_edge_nodes": self.show_edge_nodes, "ignore_binary_relations": self.ignore_binary_relations, "respect_planarity": self.ignore_planarity,}

class BipartiteOptionsWidget(QWidget):
    """
    BipartiteOptionsWidget

    A widget for managing options related to a bipartite graphical representation.
    It provides controls for toggling alignment and enabling or disabling label display.

    Attributes
    ----------
    modified_options : pyqtSignal
        Signal to emit the current state of the options as a dictionary.
    widget_list : list
        Container to store widget references used in the UI.
    alignment : str
        Stores the current alignment option, either "vertical" or "horizontal".

    Methods
    -------
    __init__(parent=None)
        Initializes the widget and its components, sets up the default alignment,
        and connects the relevant signals.

    change_alignment()
        Toggles the alignment option between "vertical" and "horizontal",
        and emits the updated options via the `send_data` method.

    send_data()
        Emits the modified options as a dictionary to the `modified_options` signal.

    get_options()
        Returns the current options as a dictionary containing alignment and label status.
    """
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(BipartiteOptionsWidget, self).__init__(parent)
        self.widget_list = list()
        self.alignment = "vertical"
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

    def get_options(self):
        return {"align": self.alignment, "draw_labels": self.labels_button.button.isChecked()}

class SetOptionsWidget(QWidget):
    """
    SetOptionsWidget class

    A PyQt widget that provides options for configuring settings such as drawing labels, enabling rounded polygons,
    iterations, and scale factors. It emits the modified options as a signal whenever changes are made to its components.

    Attributes
    ----------
    modified_options : pyqtSignal(dict)
        Signal emitted with a dictionary containing the updated options.
    widget_list : list
        A list of widgets in the SetOptionsWidget.
    rounded_polygons : bool
        A boolean to track the state of rounded polygons.
    labels_button : LabelButton
        A button for toggling label drawing.
    iterations_selector : IterationsSelector
        A widget to configure the iteration count.
    scale_spinbox : SpinboxCustomWindget
        A spin box for setting the scale factor.
    rounded_polygons_btn : QCheckBox
        A checkbox to toggle drawing of rounded polygons.

    Methods
    -------
    send_data()
        Sends the modified options to the main menu by emitting the `modified_options` signal with a dictionary of values.
    get_options()
        Returns the current configuration as a dictionary.
    """
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(SetOptionsWidget, self).__init__(parent)
        self.widget_list = list()
        self.rounded_polygons = True
        self.labels_button = LabelButton()
        self.labels_button.update_status.connect(self.send_data)
        self.iterations_selector = IterationsSelector()
        self.iterations_selector.changed_value.connect(self.send_data)
        self.scale_spinbox= SpinboxCustomWindget("Scale Factor",0.1,100,1,"scale_factor", 2,0.1)
        self.scale_spinbox.update_status.connect(self.send_data)
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
        self.widget_list.append(self.iterations_selector)
        self.widget_list.append(self.scale_spinbox)

    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        dict = {"rounded_polygon":self.rounded_polygons_btn.isChecked(),"draw_labels": self.labels_button.button.isChecked(),
                "iterations": int(self.iterations_selector.spinbox.value()), "scale_factor": self.scale_spinbox.spinBox.value()}
        self.modified_options.emit(dict)

    def get_options(self):
        return {"rounded_polygon":self.rounded_polygons_btn.isChecked(),"draw_labels": self.labels_button.button.isChecked(),
                "iterations": int(self.iterations_selector.spinbox.value()), "scale_factor": self.scale_spinbox.spinBox.value()}