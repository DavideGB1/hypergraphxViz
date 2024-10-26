import re

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox

from hypergraphx.viz.interactive_view.__options import Options


class MenuWindow(QWidget):

    modified_options = pyqtSignal(Options)
    def __init__(self, options = Options(), parent = None):
        super(MenuWindow, self).__init__(parent)
        self.options = options
        self.setWindowTitle("Options")
        self.layout = QVBoxLayout()
        for x in options.lineEdit_dict.items():
            self.add_lineEdit(x[0], x[1])
        for x in options.lineEditColor_dict.items():
            self.add_lineEdit(x[0], x[1], color=True)
        for x in options.combobox_dict.items():
            self.add_combobox(x[0], x[1])
        for x in options.spinbox_dict.items():
            self.add_spinbox(x[0], x[1])
        self.setLayout(self.layout)
    def send_data(self):
        self.modified_options.emit(self.options)

    def add_lineEdit(self, name, value, color = False):
        hbox_btn = QHBoxLayout()
        label = QLabel(name)
        hbox_btn.addWidget(label)
        lineEdit = QLineEdit(str(value))
        def lineEdit_selection():
            if color:
                hex_pattern = r'^#[0-9a-fA-F]{6}$'
                if re.match(hex_pattern, lineEdit.text()):
                    self.options.lineEditColor_dict[name] = lineEdit.text()
            else:
                self.options.lineEdit_dict[name] = lineEdit.text()
            self.send_data()

        lineEdit.textChanged.connect(lineEdit_selection)
        hbox_btn.addWidget(lineEdit)
        self.layout.addLayout(hbox_btn)

    def add_combobox(self, name, value):
        hbox_btn = QHBoxLayout()
        label = QLabel(name)
        hbox_btn.addWidget(label)
        combobox = QComboBox()
        combobox.addItems(['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X'])
        combobox.setCurrentText(value)

        def comboBox_selection():
            self.options.combobox_dict[name] = combobox.currentText()
            self.send_data()

        combobox.currentTextChanged.connect(comboBox_selection)
        hbox_btn.addWidget(combobox)
        self.layout.addLayout(hbox_btn)

    def add_spinbox(self, name, value):
        hbox_btn = QHBoxLayout()
        label = QLabel(name)
        hbox_btn.addWidget(label)
        spinBox = QDoubleSpinBox()
        spinBox.setDecimals(0)
        spinBox.setRange(1, 100000000)
        spinBox.setValue(value)
        spinBox.setSingleStep(1)

        def spinBox_selection():
            self.options.spinbox_dict[name] = spinBox.value()
            self.send_data()

        spinBox.valueChanged.connect(spinBox_selection)
        hbox_btn.addWidget(spinBox)
        self.layout.addLayout(hbox_btn)
