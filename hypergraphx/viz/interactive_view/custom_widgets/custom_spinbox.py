from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QDoubleSpinBox, QWidget


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

    def __init__(self, name, min, max, val, shadow_name="", decimals=0, step=1, parent=None):
        super(SpinboxCustomWindget, self).__init__(parent)
        self.label = QLabel(name, parent=self)
        self.spinBox = QDoubleSpinBox(parent=self)
        self.spinBox.setDecimals(decimals)
        self.spinBox.setRange(min, max)
        self.spinBox.setValue(val)
        self.spinBox.setSingleStep(step)

        self.hbox = QHBoxLayout()
        self.shadow_name = shadow_name

        self.spinBox.valueChanged.connect(self.on_value_changed)
        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.spinBox)
        self.setLayout(self.hbox)

    def on_value_changed(self, new_value):
        """Slot that manages the change of value."""
        self.update_status.emit({self.shadow_name: new_value})

    def setMax(self, max):
        self.spinBox.setMaximum(max)

    def setValue(self, value):
        self.spinBox.setValue(value)

    def value(self):
        return self.spinBox.value()
