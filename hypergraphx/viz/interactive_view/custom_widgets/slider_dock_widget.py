from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDockWidget, QSlider, QLabel, QHBoxLayout, QPushButton, QWidget
from superqt import QRangeSlider


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

    def __init__(self, max_edge, parent=None):
        super().__init__(parent)
        self.slider = QSlider(parent=self)
        self.max_edge = max_edge
        self.ranged = False
        self.slider_label = QLabel(parent=self)
        self.slider_label.setObjectName("CardinalityLabel")
        self.slider_label.setAlignment(Qt.AlignLeft)
        self.slider_hbox = QHBoxLayout()
        self.change_slider_type()
        slider_button = QPushButton("Change Slider Type", parent=self)

        slider_button.setChecked(True)
        slider_button.toggle()
        slider_button.clicked.connect(self.change_slider_type)

        self.slider_hbox.addWidget(self.slider_label)
        self.slider_hbox.addWidget(self.slider)
        self.slider_hbox.addWidget(slider_button)
        self.widget = QWidget(parent=self)
        self.widget.setLayout(self.slider_hbox)
        self.slider_label.setText("Edge Cardinality: " + str(self.slider.value()))
        self.widget.setObjectName("SliderContainer")
        self.widget.setStyleSheet(
            """
                QWidget#SliderContainer {
                    border-top: 1px solid #dcdcdc;
                }
                QLabel#CardinalityLabel {
                    color: #ffffff;          
                    font-size: 14px;
                    font-weight: bold;

                    background-color: #5D9CEC;
                    border: 1px solid #4A89DC;
                    border-radius: 5px;

                    padding: 5px 10px;
                    min-width: 160px;
                    max-height: 25px;
                    qproperty-alignment: 'AlignCenter'; 
                }
            """)
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
        old_slider = self.slider
        if self.ranged:
            self.ranged = False
            slider = QSlider(Qt.Horizontal, parent=self)
            slider.setMinimum(2)
            slider.setMaximum(self.max_edge)

        else:
            self.ranged = True
            slider = QRangeSlider(Qt.Orientation.Horizontal, parent=self)
            slider.barColor = QColor("#a5c8f2")
            slider.setMinimum(2)
            slider.setMaximum(self.max_edge)
            slider.setValue((2, self.max_edge))
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(1)
        slider.setPageStep(0)
        slider.valueChanged.connect(self.slider_value_changed)
        self.slider_hbox.replaceWidget(self.slider, slider)

        old_slider.deleteLater()

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
        if isinstance(value, tuple):
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
