from copy import deepcopy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QCheckBox
from hypergraphx.viz.interactive_view.community_options.__community_options import CommunityOptions, CommunityOptionsName


class CommunityOptionsWindow(QWidget):
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
    modified_options = pyqtSignal(CommunityOptions)
    def __init__(self, community_options = CommunityOptions(), parent = None):
        super(CommunityOptionsWindow, self).__init__(parent)
        self.community_options = community_options
        self.setWindowTitle("Community Algorithm Options")
        self.layout = QVBoxLayout()
        attributes = self.community_options.get_options()

        for attribute_name in attributes:
            if "checkbox" in attribute_name:
                self.add_checkbox(attribute_name, attributes[attribute_name])
            elif "spinbox" in attribute_name:
                self.add_spinbox(attribute_name, attributes[attribute_name])
        self.setLayout(self.layout)
    def send_data(self) -> None:
        """
        Sends the modified options to the main menu.
        """
        self.modified_options.emit(self.community_options)
    def add_checkbox(self, name: str, value: bool) -> None:
        checkbox = QCheckBox(CommunityOptionsName[name].value)

        def checkbox_selection():
            if checkbox.isChecked():
                self.community_options.__setattr__(name, True)
            else:
                self.community_options.__setattr__(name, False)
            self.send_data()

        checkbox.stateChanged.connect(checkbox_selection)
        self.layout.addWidget(checkbox)
    def add_spinbox(self, name: str, value: int | float) -> None:
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
        hbox_btn = QHBoxLayout()
        label = QLabel(CommunityOptionsName[name].value)
        hbox_btn.addWidget(label)
        spinBox = QDoubleSpinBox()
        spinBox.setDecimals(0)
        spinBox.setRange(1, 1000)
        spinBox.setValue(value)
        spinBox.setSingleStep(1)

        def spinBox_selection():
            self.community_options.__setattr__(name, int(spinBox.value()))
            self.send_data()

        spinBox.valueChanged.connect(spinBox_selection)
        hbox_btn.addWidget(spinBox)
        self.layout.addLayout(hbox_btn)