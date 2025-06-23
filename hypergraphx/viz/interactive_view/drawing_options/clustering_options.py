from PyQt5.QtWidgets import QCheckBox

from hypergraphx.viz.interactive_view.custom_widgets.custom_spinbox import SpinboxCustomWindget
from hypergraphx.viz.interactive_view.custom_widgets.random_seed_button import RandomSeedButton
from hypergraphx.viz.interactive_view.drawing_options.base_options import BaseOptionsWidget


class SpectralClusteringOptionsWidget(BaseOptionsWidget):

    def _setup_widgets(self):

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 2,2, "number_communities", parent=self)
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations", parent=self)
        self.realizations.update_status.connect(self.send_data)

        self.random_seed = RandomSeedButton(parent=self)
        self.random_seed.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.realizations)
        self.main_layout.addWidget(self.n_communities)
        self.main_layout.addWidget(self.random_seed)
    def set_max_communities(self, n_nodes):
        self.n_communities.setMax(n_nodes)
        self.n_communities.setValue(2)
    def get_options(self):
        return {
            "number_communities": int(self.n_communities.value()),
            "realizations":int( self.realizations.value()),
            "seed": self.random_seed.get_seed(),
        }

class MTOptionsWidget(BaseOptionsWidget):

    def _setup_widgets(self):

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 2,2, "number_communities")
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations", parent=self)
        self.realizations.update_status.connect(self.send_data)

        self.max_iterations = SpinboxCustomWindget("Max Iterations", 1, 1000, 500, "max_iterations", parent=self)
        self.max_iterations.update_status.connect(self.send_data)

        self.check_convergence = SpinboxCustomWindget("Check Convergence Every", 1, 1000, 1, "check_convergence_every", parent=self)
        self.check_convergence.update_status.connect(self.send_data)

        self.normalizeU = QCheckBox("Normalize Output", parent=self)
        self.normalizeU.setChecked(True)
        self.normalizeU.toggled.connect(self.send_data)

        self.baseline_r0 = QCheckBox("Baseline R0", parent=self)
        self.baseline_r0.setChecked(False)
        self.baseline_r0.toggled.connect(self.send_data)

        self.random_seed = RandomSeedButton(parent=self)
        self.random_seed.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.realizations)
        self.main_layout.addWidget(self.n_communities)
        self.main_layout.addWidget(self.max_iterations)
        self.main_layout.addWidget(self.check_convergence)
        self.main_layout.addWidget(self.normalizeU)
        self.main_layout.addWidget(self.baseline_r0)
        self.main_layout.addWidget(self.random_seed)
    def set_max_communities(self, n_nodes):
        self.n_communities.setMax(n_nodes)
        self.n_communities.setValue(2)
    def get_options(self):
        return {
            "number_communities": int(self.n_communities.value()),
            "realizations":int( self.realizations.value()),
            "seed" :self.random_seed.get_seed(),
            "max_iterations": int(self.max_iterations.spinBox.value()),
            "check_convergence_every": int(self.check_convergence.spinBox.value()),
            "normalizeU": self.normalizeU.isChecked(),
            "baseline_r0": self.baseline_r0.isChecked()
        }

class MMSBMOptionsWidget(BaseOptionsWidget):

    def _setup_widgets(self):

        self.n_communities = SpinboxCustomWindget("Number of Communities", 2, 2,2, "number_communities", parent=self)
        self.n_communities.update_status.connect(self.send_data)

        self.realizations = SpinboxCustomWindget("Realizations", 1, 1000, 10, "realizations", parent=self)
        self.realizations.update_status.connect(self.send_data)

        self.assortative = QCheckBox("Assortative", parent = self)
        self.assortative.setChecked(True)
        self.assortative.toggled.connect(self.send_data)


        self.random_seed = RandomSeedButton(parent=self)
        self.random_seed.update_status.connect(self.send_data)

        self.main_layout.addWidget(self.realizations)
        self.main_layout.addWidget(self.n_communities)
        self.main_layout.addWidget(self.assortative)
        self.main_layout.addWidget(self.random_seed)
    def set_max_communities(self, n_nodes):
        self.n_communities.setMax(n_nodes)
        self.n_communities.setValue(2)
    def get_options(self):
        return {
            "number_communities": int(self.n_communities.value()),
            "realizations":int( self.realizations.value()),
            "assortative": self.assortative.isChecked(),
            "seed": self.random_seed.get_seed(),
        }