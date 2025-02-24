from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QCheckBox
import random

class CommunityOptionsDict(dict):
    def __init__(self):
        super().__init__()
        self.dictionary = dict()
        self["number_communities"] = 2
        self["realizations"] = 10
        self["seed"] = random.randint(0,10000)
        self["max_iterations"] = 500
        self["check_convergence_every"] = 1
        self["normalizeU"] = True
        self["baseline_r0"] = False
        self["assortative"] = True
    def update(self, dictionary, **kwargs):
        for (k,v) in dictionary.items():
            try:
                self[k] = dictionary[k]
            except KeyError:
                pass

class SpectralClusteringOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(SpectralClusteringOptionsWidget, self).__init__(parent)
        self.widget_list = list()

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 1000,2, "number_communities")
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations")
        self.realizations.update_status.connect(self.send_data)

        self.random_seed = RandomSeedButton()
        self.random_seed.update_status.connect(self.send_data)

        self.widget_list.append(self.realizations)
        self.widget_list.append(self.n_communities)
        self.widget_list.append(self.random_seed.button)

    def send_data(self):
        """
        Sends the modified options to the main menu.
        """
        dict = {"realizations": int(self.realizations.spinBox.value()), "number_communities": int(self.n_communities.spinBox.value()),
                "seed" :random.randint(0,100000) }
        self.modified_options.emit(dict)

class MTOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(MTOptionsWidget, self).__init__(parent)
        self.widget_list = list()

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 1000, 2, "number_communities")
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations")
        self.realizations.update_status.connect(self.send_data)

        self.max_iterations = SpinboxCustomWindget("Max Iterations", 1, 1000, 500, "max_iterations")
        self.max_iterations.update_status.connect(self.send_data)

        self.check_convergence = SpinboxCustomWindget("Check Convergence Every", 1, 1000, 1, "check_convergence_every")
        self.check_convergence.update_status.connect(self.send_data)

        self.normalizeU = CheckBoxCustomWidget("Normalize Output", True, "normalizeU")
        self.normalizeU.update_status.connect(self.send_data)

        self.baseline_r0 = CheckBoxCustomWidget("Baseline R0", False, "baseline_r0")
        self.baseline_r0.update_status.connect(self.send_data)

        self.random_seed = RandomSeedButton()
        self.random_seed.update_status.connect(self.send_data)

        self.widget_list.append(self.realizations)
        self.widget_list.append(self.n_communities)
        self.widget_list.append(self.max_iterations)
        self.widget_list.append(self.check_convergence)
        self.widget_list.append(self.normalizeU.check_box)
        self.widget_list.append(self.baseline_r0.check_box)
        self.widget_list.append(self.random_seed.button)

    def send_data(self):
        """
        Sends the modified options to the main menu.
        """
        dict = {"realizations": int(self.realizations.spinBox.value()), "number_communities": int(self.n_communities.spinBox.value()),
                "seed" :random.randint(0,100000), "max_iterations": int(self.max_iterations.spinBox.value()),
                "check_convergence_every": int(self.check_convergence.spinBox.value()), "normalizeU": self.normalizeU.check_box.isChecked(),
                "baseline_r0": self.baseline_r0.check_box.isChecked(),}
        self.modified_options.emit(dict)

class MMSBMOptionsWidget(QWidget):
    modified_options = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(MMSBMOptionsWidget, self).__init__(parent)
        self.widget_list = list()

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 1000, 2, "number_communities")
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations")
        self.realizations.update_status.connect(self.send_data)

        self.max_iterations = SpinboxCustomWindget("Max Iterations", 1, 1000, 500, "max_iterations")
        self.max_iterations.update_status.connect(self.send_data)

        self.assortative = CheckBoxCustomWidget("Assortative", True, "assortative")
        self.assortative.update_status.connect(self.send_data)

        self.widget_list.append(self.realizations)
        self.widget_list.append(self.n_communities)
        self.widget_list.append(self.max_iterations)
        self.widget_list.append(self.assortative.check_box)

    def send_data(self):
        """
        Sends the modified options to the main menu.
        """
        dict = {"realizations": int(self.realizations.spinBox.value()), "number_communities": int(self.n_communities.spinBox.value()),
                "seed" :random.randint(0,100000), "assortative": self.assortative.check_box.isChecked(), }
        self.modified_options.emit(dict)

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
            self.update_status.emit({shadow_name: int(self.spinBox.value())})

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
