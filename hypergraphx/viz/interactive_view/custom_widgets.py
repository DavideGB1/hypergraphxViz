import random

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QCheckBox, QLabel, QDoubleSpinBox, QHBoxLayout, QPushButton, QColorDialog, \
    QComboBox, QVBoxLayout, QDockWidget, QSlider
from superqt import QRangeSlider

from hypergraphx.viz.interactive_view.graphic_enum import GraphicOptionsName


class LabelButton(QWidget):
    update_status = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(LabelButton, self).__init__()
        self.button = QCheckBox("Show Labels")
        self.button.setChecked(True)
        def use_labels():
            self.update_status.emit({ "val" : self.button.isChecked()})
        self.button.toggled.connect(use_labels)

class IterationsSelector(QWidget):
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
class SpinboxCustomWindget(QWidget):
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
    update_status = pyqtSignal(dict)
    def __init__(self, name, status, shadow_name):
        super(CheckBoxCustomWidget, self).__init__()
        self.check_box = QCheckBox(name)
        self.check_box.setChecked(status)
        def checkbox_selection():
            self.update_status.emit({shadow_name: self.check_box.isChecked()})
        self.check_box.toggled.connect(checkbox_selection)

class RandomSeedButton(QWidget):
    update_status = pyqtSignal(dict)
    def __init__(self, parent=None):
        super(RandomSeedButton, self).__init__()
        self.button = QPushButton("Random Seed")

        def new_seed():
            self.update_status.emit({"seed": random.randint(0,100000)})

        self.button.clicked.connect(new_seed)

class WaitingScreen(QWidget):
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
        self.slider_label.setText("Edge Cardinality: " + str(self.slider.value()))
        value = self.slider.value()
        if isinstance(value,tuple):
            self.update_value.emit(self.slider.value())
        else:
            self.update_value.emit((value, value))
    def update_max(self, new_max_edge):
        self.max_edge = new_max_edge
        self.slider.setMaximum(self.max_edge)
        if self.ranged:
            self.slider.setValue((2, self.max_edge))
        else:
            self.slider.setValue(2)