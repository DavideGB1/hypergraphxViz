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

        self.spinbox.setStyleSheet(
            """
                QDoubleSpinBox {
                    background-color: white;
                    border: 1px solid #BDBDBD;
                    border-top-color: #A0A0A0; 
                    border-left-color: #A0A0A0;
                    border-radius: 8px;
                    padding: 4px;
                    font-size: 13px;
                    color: #333;
                    padding-left: 10px; 
                }

                QDoubleSpinBox:hover {
                    border-color: #5D9CEC;
                }

                QDoubleSpinBox:focus {
                    border-color: #4A89DC;
                }

                QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                    subcontrol-origin: border;
                    width: 22px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6AACFF, stop:1 #4A89DC);
                    border: 1px solid #3A79CB;
                    border-bottom: 2px solid #3A79CB; 
                    border-radius: 4px;
                }

                QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7BCFFF, stop:1 #5D9CEC);
                }

                QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4A89DC, stop:1 #3A79CB);
                    border-bottom: 1px solid #3A79CB;
                }

                QDoubleSpinBox::up-button:pressed {
                    padding-top: 1px;
                }
                QDoubleSpinBox::down-button:pressed {
                    padding-top: 1px;
                }

                QDoubleSpinBox::up-button {
                    subcontrol-position: top right;
                    margin: 2px 2px 1px 0px;
                }

                QDoubleSpinBox::down-button {
                    subcontrol-position: bottom right;
                    margin: 1px 2px 2px 0px;
                }
            """
        )

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.iterations_selector_label)
        self.hbox.addWidget(self.spinbox)
        self.setLayout(self.hbox)

    def value(self):
        return int(self.spinbox.value())

    def on_value_changed(self):
        self.changed_value.emit({"use_last": False})
