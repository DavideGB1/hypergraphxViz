from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QDoubleSpinBox, QLabel, QWidget


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

    def __init__(self, parent=None):
        super(IterationsSelector, self).__init__(parent)
        self.iterations_selector_label = QLabel("Number of Iterations:", parent=self)
        self.spinbox = QDoubleSpinBox(parent=self)

        self.spinbox.setDecimals(0)
        self.spinbox.setRange(0, 100000000)
        self.spinbox.setValue(1000)
        self.spinbox.setSingleStep(1)
        self.spinbox.valueChanged.connect(self.on_value_changed)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.iterations_selector_label)
        self.hbox.addWidget(self.spinbox)
        self.setLayout(self.hbox)

    def value(self):
        return int(self.spinbox.value())

    def on_value_changed(self):
        self.changed_value.emit({"use_last": False})
