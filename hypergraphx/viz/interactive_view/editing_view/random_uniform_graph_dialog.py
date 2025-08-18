from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QDoubleSpinBox, QSpinBox


class RandomUniformGraphDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Random Uniform Hypergraph")
        self.n_nodes_spinbox = QSpinBox()
        self.size_spinbox = QSpinBox()
        self.n_edges_spinbox = QSpinBox()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Number of Nodes:"))
        self.n_nodes_spinbox.setRange(1, 1000000)
        self.n_nodes_spinbox.setValue(10)
        layout.addWidget(self.n_nodes_spinbox)

        layout.addWidget(QLabel("Edges Size (k):"))
        self.size_spinbox.setRange(1, 1000000)
        self.size_spinbox.setValue(3)
        layout.addWidget(self.size_spinbox)

        layout.addWidget(QLabel("Number of Edges:"))
        self.n_edges_spinbox.setRange(1, 1000000)
        self.n_edges_spinbox.setValue(15)
        layout.addWidget(self.n_edges_spinbox)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)


    def get_values(self):
        """Returns the values selected by the user in a dictionary."""
        return {
            "num_nodes": self.n_nodes_spinbox.value(),
            "edge_size": self.size_spinbox.value(),
            "num_edges": self.n_edges_spinbox.value()
        }
