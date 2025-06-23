from PyQt5.QtWidgets import QDialog, QSpinBox, QPlainTextEdit, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox


class RandomGraphDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Random Hypergraph")

        self.num_nodes = 1
        self.edges_dictionary = {}

        self.n_nodes_spinbox = QSpinBox()
        self.edges_input_text = QPlainTextEdit()
        self.edges_display_text = QPlainTextEdit()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Number of Nodes:"))
        self.n_nodes_spinbox.setValue(1)
        self.n_nodes_spinbox.setMinimum(1)
        self.n_nodes_spinbox.valueChanged.connect(self._update_edges_dictionary)
        layout.addWidget(self.n_nodes_spinbox)

        layout.addWidget(QLabel("Edges Dictionary (e.g., 2:14, 3:5):"))
        self.edges_input_text.setPlaceholderText("Insert pairs of <size>:<count>, separated by commas.")
        layout.addWidget(self.edges_input_text)

        add_edges_button = QPushButton("Parse and Add Edges")
        add_edges_button.clicked.connect(self._update_edges_dictionary)
        layout.addWidget(add_edges_button)

        layout.addWidget(QLabel("Current Edges Dictionary:"))
        self.edges_display_text.setReadOnly(True)
        layout.addWidget(self.edges_display_text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _update_edges_dictionary(self):
        """Class method to process input and update state."""
        current_max_nodes = self.n_nodes_spinbox.value()

        parsed_dict = {}
        input_text = self.edges_input_text.toPlainText()
        pairs = input_text.split(",")

        for pair in pairs:
            if ":" not in pair:
                continue
            try:
                k, v = pair.split(":")
                k, v = int(k.strip()), int(v.strip())
                if k <= current_max_nodes and k > 0:
                    parsed_dict[k] = v
            except (ValueError, TypeError):
                pass

        self.edges_dictionary = parsed_dict
        self.edges_display_text.setPlainText(str(self.edges_dictionary))

    def get_values(self):
        """Public method to get results after dialogue is accepted."""
        self._update_edges_dictionary()
        return {
            "num_nodes": self.n_nodes_spinbox.value(),
            "edges_by_size": self.edges_dictionary
        }
