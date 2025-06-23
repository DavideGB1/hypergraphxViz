import random

from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush, QPainter
from PyQt5.QtWidgets import QWidget, QLabel, QDoubleSpinBox, QHBoxLayout, QPushButton, QColorDialog, \
    QComboBox, QVBoxLayout, QDockWidget, QSlider, QProgressBar
from superqt import QRangeSlider

from hypergraphx.viz.interactive_view.graphic_enum import GraphicOptionsName


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
    def __init__(self,name, value, translation_dictionary, parent = None):
        super(ComboBoxCustomWindget, self).__init__(parent)

        self.name = name
        self.translation_dictionary = translation_dictionary
        self.key_list = list(translation_dictionary.keys())
        self.val_list = list(translation_dictionary.values())

        self.hbox = QHBoxLayout()
        self.label = QLabel(GraphicOptionsName[name].value, parent=self)
        self.hbox.addWidget(self.label)

        self.combobox = QComboBox(parent=self)
        self.combobox.addItems(translation_dictionary.values())
        self.combobox.setCurrentText(translation_dictionary[value])
        self.combobox.currentTextChanged.connect(self.on_selection_changed)

        self.hbox.addWidget(self.combobox)
        self.setLayout(self.hbox)

    def on_selection_changed(self, current_text):
        """This is the slot that handles the change."""
        try:
            position = self.val_list.index(current_text)
            key = self.key_list[position]
            self.update_status.emit({self.name: key})
        except ValueError:
            pass

class ColorPickerCustomWidget(QWidget):
    """
    Class ColorPickerCustomWidget
    -----------------------------
    A custom widget for selecting and displaying a color.
    """
    update_status = pyqtSignal(dict)

    def __init__(self, name, value, in_extra, graphic_options, extra_attributes, parent=None):
        super(ColorPickerCustomWidget, self).__init__(parent)

        self.name = name
        self.in_extra = in_extra
        self.graphic_options = graphic_options
        self.extra_attributes = extra_attributes

        self.color_btn = QPushButton(parent=self)
        self.update_button_color(QColor(value))
        self.color_btn.clicked.connect(self.open_color_picker)
        self.color_btn.setStyleSheet(
            """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #F5F5F5, stop:1 #E0E0E0);
                    border: 1px solid #BDBDBD;
                    border-radius: 5px;
                    width: 24px;
                    height: 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                                stop:0 #FFFFFF, stop:1 #E8E8E8);
                    border-color: #9E9E9E;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #E0E0E0, stop:1 #D0D0D0);
                    padding-top: 2px;
                }
            """
        )
        self.hbox = QHBoxLayout()
        label = QLabel(f"{name.replace('_', ' ').title()}:", parent=self)
        self.hbox.addWidget(label)
        self.hbox.addWidget(self.color_btn)
        self.setLayout(self.hbox)

    def update_button_color(self, color: QColor):
        size = 18
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        rect = QRectF(0, 0, size, size)
        radius = 4.0
        painter.drawRoundedRect(rect, radius, radius)

        painter.end()

        self.color_btn.setIcon(QIcon(pixmap))
        self.color_btn.setIconSize(pixmap.size())


    def open_color_picker(self):
        """
        Opens a dialog for choosing the color using the static method, updates the value and emits the signal.
        """
        if self.in_extra:
            current_color = QColor(self.extra_attributes[self.name])
        else:
            current_color = QColor(getattr(self.graphic_options, self.name))

        new_color = QColorDialog.getColor(current_color, self, "Choose a Color")

        if new_color.isValid():
            new_color_name = new_color.name()
            self.update_button_color(new_color)
            if self.in_extra:
                self.extra_attributes[self.name] = new_color_name
            else:
                setattr(self.graphic_options, self.name, new_color_name)
            self.update_status.emit({self.name: new_color_name})

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
    def __init__(self, name, min, max,val, shadow_name = "", decimals = 0, step = 1, parent=None):
        super(SpinboxCustomWindget, self).__init__(parent)
        self.label = QLabel(name, parent=self)
        self.spinBox = QDoubleSpinBox(parent=self)
        self.spinBox.setDecimals(decimals)
        self.spinBox.setRange(min, max)
        self.spinBox.setValue(val)
        self.spinBox.setSingleStep(step)

        self.spinBox.setStyleSheet(
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

class RandomSeedButton(QPushButton):
    """
    A QPushButton that generates a random seed and emits it via a signal.

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
    """
    update_status = pyqtSignal(dict)

    def __init__(self, parent=None):
        # Call the QPushButton constructor
        super().__init__("Random Seed", parent)
        # Connect the button's built-in clicked signal to our handler
        self.clicked.connect(self.on_button_clicked)
        # Initialize the seed when the button is created
        self.seed = random.randint(0, 100000)

    def on_button_clicked(self):
        """Slot that handles the button click."""
        self.seed = random.randint(0, 100000)
        self.update_status.emit({"seed": self.seed})

    def get_seed(self):
        """Returns the current random seed."""
        return self.seed

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
    def __init__(self,max_edge, parent=None):
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
        slider_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #5D9CEC, stop: 1 #4A89DC);
                border: 1px solid #3A79CB;
                border-bottom: 4px solid #3A79CB;
                border-radius: 8px;
                padding: 6px 18px;
                margin-bottom: 4px;
                min-height: 25px; 
            }

            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #6AACFF, stop: 1 #5D9CEC);
                border-color: #4A89DC;
                border-bottom-color: #4A89DC;
            }

            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #4A89DC, stop: 1 #3A79CB);
                border-bottom: 1px solid #3A79CB;
                margin-top: 4px;
                margin-bottom: 0px;
            }

            QPushButton:disabled {
                background: #B0BEC5;
                color: #78909C;
                border: 1px solid #90A4AE;
                border-bottom: 4px solid #78909C;
            }
        """)
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




class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("LoadingScreen")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.bar_layout = QVBoxLayout()

        label = QLabel("Loading...", self)
        label.setObjectName("LoadingLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_bar = QProgressBar(self)
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)

        self.bar_layout.addStretch()
        self.bar_layout.addWidget(label)
        self.bar_layout.addWidget(progress_bar)
        self.bar_layout.addStretch()
        self.bar_widget = QWidget(parent=self)
        self.bar_widget.setLayout(self.bar_layout)
        self.bar_widget.setFixedSize(500, 200)
        self.bar_widget.setStyleSheet("""
/* Stile per il widget principale con ID #LoadingScreen */
#LoadingScreen {
    background-color: #4a4a4a; /* Sfondo grigio scuro */
    border: 2px solid #5a5a5a;
    border-radius: 15px; /* Angoli arrotondati */
}

/* Stile per tutte le QLabel dentro a #LoadingScreen */
#LoadingScreen QLabel {
    color: black; /* Colore del testo quasi bianco */
    font-size: 18pt;
    font-weight: bold;
}

/* Stile per la QProgressBar */
QProgressBar {
    border: 2px solid #666666;
    border-radius: 8px;
    background-color: #333333; /* Sfondo della barra (la "traccia") */
    text-align: center; /* Anche se non c'è testo, è una buona pratica */
    height: 25px; /* Aumentiamo l'altezza per un effetto più visibile */
}

/* Stile per la parte "piena" della barra (il "chunk") */
QProgressBar::chunk {
    /* Usiamo un gradiente lineare per dare un effetto 3D bombato */
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #0078d7, stop: 1 #005a9e
    );
    border-radius: 6px;
    /* Aggiungiamo un margine per creare spazio tra il chunk e il bordo della barra */
    margin: 2px; 
}
""")
        self.container_layout = QVBoxLayout(parent = self)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addStretch()
        self.h_layout = QHBoxLayout()
        self.h_layout.addStretch()
        self.h_layout.addWidget(self.bar_widget)
        self.h_layout.addStretch()
        self.container_layout.addLayout(self.h_layout)
        self.container_layout.addStretch()
        self.setLayout(self.container_layout)



