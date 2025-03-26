import random

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QCheckBox, QLabel, QDoubleSpinBox, QHBoxLayout, QPushButton, QColorDialog, \
    QComboBox, QVBoxLayout, QDockWidget, QSlider
from superqt import QRangeSlider

from hypergraphx.viz.interactive_view.graphic_enum import GraphicOptionsName


class LabelButton(QWidget):
    """
    LabelButton is a custom QWidget that contains a QCheckBox. It emits a signal whenever the checkbox is toggled to indicate whether the labels should be shown or not.

    Attributes
    ----------
    update_status : pyqtSignal
        A PyQt signal that emits a dictionary containing the current state of the checkbox.

    Methods
    -------
    __init__(parent=None)
        Initializes the LabelButton widget, sets up the checkbox, and connects the toggled signal to a handler function.

    Usage
    -----
    This component can be utilized in PyQt applications where toggling a checkbox is required to update some state logic related to labels.
    """
    update_status = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(LabelButton, self).__init__()
        self.button = QCheckBox("Show Labels")
        self.button.setChecked(True)
        def use_labels():
            self.update_status.emit({ "val" : self.button.isChecked()})
        self.button.toggled.connect(use_labels)

class IterationsSelector(QWidget):
    """
        A QWidget subclass that defines a UI component for selecting a number of iterations
        using a QDoubleSpinBox.

        Attributes
        ----------
        changed_value : pyqtSignal
            A signal emitted when the spinbox value is changed. Emits a dictionary with
            the key "use_last" set to False.

        Methods
        -------
        __init__(parent=None):
            Initializes the IterationsSelector widget, its label, spinbox, and layout.
            Configures the spinbox range, default value, and connects its valueChanged signal
            to trigger the custom signal.
    """
    changed_value = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(IterationsSelector, self).__init__()
        self.iterations_selector_label = QLabel("Number of Iterations:")
        self.spinbox = QDoubleSpinBox()
        def iterations_selector_funz():
            self.changed_value.emit({"use_last": False})
        self.spinbox.setDecimals(0)
        self.spinbox.setRange(0, 100000000)
        self.spinbox.setValue(1000)
        self.spinbox.setSingleStep(1)
        self.spinbox.valueChanged.connect(iterations_selector_funz)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.iterations_selector_label)
        self.hbox.addWidget(self.spinbox)
        self.setLayout(self.hbox)

class ComboBoxCustomWindget(QWidget):
    """
        Class ComboBoxCustomWindget

        A custom PyQt widget that combines a QLabel and a QComboBox. The widget is used
        to display a label and a combo box with selectable options. Upon changes in the
        combo box selection, the widget emits a signal with the updated status.

        Attributes
        ----------
        update_status : pyqtSignal
            Signal emitted when the combo box selection is changed. Emits a dictionary
            containing the updated key-value pair.

        Parameters
        ----------
        name : str
            The unique identifier or key associated with the custom widget.
        value : str
            The initial selected value in the combo box.
        translation_dictionary : dict
            A dictionary containing the mapping between keys and their translated
            strings to be displayed in the combo box.

        Methods
        -------
        comboBox_selection()
            Captures the current selected text from the combo box, determines its
            corresponding key in the given translation dictionary, and emits the
            `update_status` signal with the updated key-value pair.
    """
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
    """
    Class ColorPickerCustomWidget
    -----------------------------

    A custom widget for selecting and displaying a color using a QPushButton and a QColorDialog. The widget enables the user to choose a color and updates the associated attribute or extra data, emitting a signal upon updating the color.

    Parameters
    ----------
    name : str
        The name associated with the color attribute or graphic option.
    value : str
        The initial color value represented as a string (e.g., hexadecimal format).
    in_extra : bool
        A flag indicating whether the color value is part of extra attributes or graphic options.
    graphic_options : object
        The object containing graphic options as attributes.
    extra_attributes : dict
        A dictionary containing additional attributes, where the color value might be stored.

    Attributes
    ----------
    hbox : QHBoxLayout
        The layout container for arranging the label and color button.
    update_status : pyqtSignal
        A signal that emits a dictionary when the color is updated.

    Methods
    -------
    __init__(name, value, in_extra, graphic_options, extra_attributes)
        Initializes the widget, creates a label, a color button, and sets up the layout and functionality.
    color_picker()
        Launches a QColorDialog for selecting a new color, updates the associated value, and emits a signal.
    """
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

class SpinboxCustomWindget(QWidget):
    """
    SpinboxCustomWindget is a customizable QWidget that integrates a QLabel and a QDoubleSpinBox with user-defined configurations. It allows emitting signals when the spinbox's value changes.

    Attributes
    ----------
    update_status : pyqtSignal
        Signal emitted when the value of the spinbox changes. Sends a dictionary with the shadow_name as the key and the spinbox's value as the value.

    label : QLabel
        Displays the name beside the spinbox.

    spinBox : QDoubleSpinBox
        The double spin box widget configured with user-defined attributes such as decimals, range, and step.

    hbox : QHBoxLayout
        Horizontal box layout to organize label and spinbox.

    Methods
    -------
    __init__(self, name, min, max, val, shadow_name = "", decimals = 0, step = 1)
        Initializes the widget setting up QLabel, QDoubleSpinBox, and layout. Connects the spinbox's valueChanged signal to emit `update_status` signal with the updated value.

    get_val(self)
        Returns the current value of the spinbox.
    """
    update_status = pyqtSignal(dict)
    def __init__(self, name, min, max,val, shadow_name = "", decimals = 0, step = 1):
        super(SpinboxCustomWindget, self).__init__()
        self.label = QLabel(name)
        self.spinBox = QDoubleSpinBox()
        self.spinBox.setDecimals(decimals)
        self.spinBox.setRange(min, max)
        self.spinBox.setValue(val)
        self.spinBox.setSingleStep(step)
        self.hbox = QHBoxLayout()
        def spinBox_selection():
            self.update_status.emit({shadow_name: self.spinBox.value()})

        self.spinBox.valueChanged.connect(spinBox_selection)
        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.spinBox)
        self.setLayout(self.hbox)
    def get_val(self):
        return self.spinBox.value()

class CheckBoxCustomWidget(QWidget):
    """
    A custom QWidget class containing a QCheckBox, which emits a signal when its state changes.

    Attributes
    ----------
    update_status : pyqtSignal(dict)
        A signal emitted when the checkbox state is toggled, providing a dictionary with the shadow name as the key
        and the checkbox's current checked state as the value.

    Parameters
    ----------
    name : str
        The label text for the checkbox.
    status : bool
        The initial checked state of the checkbox.
    shadow_name : str
        A unique identifier used as the key in the dictionary emitted by the update_status signal.

    Methods
    -------
    __init__(name, status, shadow_name)
        Initializes the custom checkbox widget and connects its state change to the update_status signal.
    """
    update_status = pyqtSignal(dict)
    def __init__(self, name, status, shadow_name):
        super(CheckBoxCustomWidget, self).__init__()
        self.check_box = QCheckBox(name)
        self.check_box.setChecked(status)
        def checkbox_selection():
            self.update_status.emit({shadow_name: self.check_box.isChecked()})
        self.check_box.toggled.connect(checkbox_selection)

class RandomSeedButton(QWidget):
    """
        A QPushButton widget that generates a random seed and emits it via a signal.

        This class defines a custom QPushButton that, when clicked, generates a random integer
        to be used as a seed and emits it using a PyQt signal. The emitted signal transmits a
        dictionary containing the generated seed.

        Attributes
        ----------
        update_status : pyqtSignal
            A signal that emits a dictionary containing the generated seed.

        Parameters
        ----------
        parent : QWidget or None, optional
            The parent widget of this button. Defaults to None.

        Methods
        -------
        None.
    """
    update_status = pyqtSignal(dict)
    def __init__(self, parent=None):
        super(RandomSeedButton, self).__init__()
        self.button = QPushButton("Random Seed")

        def new_seed():
            self.update_status.emit({"seed": random.randint(0,100000)})

        self.button.clicked.connect(new_seed)

class WaitingScreen(QWidget):
    """
        A QWidget subclass that displays a waiting screen with a centered label.

        The WaitingScreen class creates a simple full-screen placeholder that
        displays a message indicating ongoing calculations. This can be utilized
        to provide feedback during time-consuming operations.

        Methods
        -------
        __init__(parent=None):
            Constructs the WaitingScreen with a centered QLabel and a default message.
    """
    def __init__(self, parent=None):
        super(WaitingScreen, self).__init__()
        self.layout = QVBoxLayout()
        #self.icon = QIcon()
        #self.layout.addWidget(self.icon)
        self.layout.setAlignment(Qt.AlignCenter)
        self.label = QLabel("Calculation in progress...")
        self.label.setFont(QFont("Arial", 20))
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class SliderDockWidget(QDockWidget):
    """
        A custom QDockWidget class that incorporates a slider with dynamic range settings.
        This widget is designed to allow users to toggle between a basic slider and a range slider
        to select either a single or a range of values for edge cardinality.

        Methods
        -------
        __init__(self, max_edge)
            Initializes the slider dock widget with a default maximum edge value.

        change_slider_type(self)
            Toggles the slider type between a single value slider and a range slider based on its current state.

        slider_value_changed(self)
            Updates the slider label to display the current slider value(s) and emits the `update_value` signal with the slider's current value.

        update_max(self, new_max_edge)
            Updates the maximum edge value for the slider, and resets the slider's value to keep it within the new maximum range.
    """
    update_value = pyqtSignal(tuple)
    def __init__(self, max_edge):
        super().__init__()
        self.slider = QSlider()
        self.max_edge = max_edge
        self.ranged = False
        self.slider_label = QLabel()
        self.slider_label.setAlignment(Qt.AlignLeft)
        self.slider_hbox = QHBoxLayout()
        self.change_slider_type()
        slider_button = QPushButton("Change Slider Type")
        slider_button.setChecked(True)
        slider_button.toggle()
        slider_button.clicked.connect(self.change_slider_type)
        self.slider_hbox.addWidget(self.slider_label)
        self.slider_hbox.addWidget(self.slider)
        self.slider_hbox.addWidget(slider_button)
        self.widget = QWidget()
        self.widget.setLayout(self.slider_hbox)
        self.slider_label.setText("Edge Cardinality: " + str(self.slider.value()))
        self.setWidget(self.widget)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.slider_value_changed()

    def change_slider_type(self):
        """
        Toggle the type of slider between a standard range slider and a ranged slider.

        This method switches the type of slider used in the interface. If the current slider
        is of ranged type, it replaces it with a standard range slider; otherwise, it will
        replace the standard range slider with a ranged slider. The newly created slider is
        configured with min, max, tick intervals, and valueChanged signal connection.
        The method also updates the layout by replacing the old slider widget with the new one.

        Attributes
        ----------
        ranged : bool
            Indicates whether the slider is ranged or not.
        max_edge : int
            The maximum allowable value for the slider.
        slider : QSlider or QRangeSlider
            The currently active slider.
        slider_hbox : QLayout
            The layout containing the slider widget.
        """
        if self.ranged:
            self.ranged = False
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(2)
            slider.setMaximum(self.max_edge)
        else:
            self.ranged = True
            slider = QRangeSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(2)
            slider.setMaximum(self.max_edge)
            slider.setValue((2, self.max_edge))
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(1)
        slider.setPageStep(0)
        slider.valueChanged.connect(self.slider_value_changed)
        self.slider_hbox.replaceWidget(self.slider, slider)
        self.slider_hbox.removeWidget(self.slider)
        self.slider = slider
        self.slider_value_changed()

    def slider_value_changed(self):
        """
        Handles the event when the slider value is changed by the user. Updates the slider label text to reflect the current value of the slider and emits the updated value.

        Notes
        -----
        - If the slider value is a tuple, it emits the value as-is.
        - If the slider value is not a tuple, it adjusts the value to a tuple form (value, value) and then emits it.
        """
        self.slider_label.setText("Edge Cardinality: " + str(self.slider.value()))
        value = self.slider.value()
        if isinstance(value,tuple):
            self.update_value.emit(self.slider.value())
        else:
            self.update_value.emit((value, value))

    def update_max(self, new_max_edge):
        """
        Parameters
        ----------
        new_max_edge : int
            The new maximum value to set for the slider's upper edge.

        Notes
        -----
        This method updates the maximum edge value for the slider. It adjusts the slider's maximum range according to the provided value. If the object operates in a ranged mode, the slider values are updated as a tuple starting from 2 up to the new maximum edge. Otherwise, the single slider value is reset to 2.
        """
        self.max_edge = new_max_edge
        self.slider.setMaximum(self.max_edge)
        if self.ranged:
            self.slider.setValue((2, self.max_edge))
        else:
            self.slider.setValue(2)