from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox

from hypergraphx.viz.interactive_view.support import numerical_hypergraph, str_to_dict


class AddNodeDialog(QDialog):
    def __init__(self, hypergraph, parent=None):
        super(AddNodeDialog, self).__init__(parent)
        self.hypergraph = hypergraph
        self.setWindowTitle("Add Node")

        # Setup del layout e dei widget
        self.layout = QVBoxLayout(self)
        self.nodes_name_label = QLabel("Node Name:")
        self.name_input = QLineEdit(parent=self)
        self.metadata_label = QLabel("Node Metadata:")
        self.metadata_input = QTextEdit(parent=self)
        self.metadata_input.setPlaceholderText("Insert the metadata (example class:CS, gender:M).")
        self.generate_button = QPushButton("Add Node",parent=self)
        self.generate_button.clicked.connect(self.send_input)

        self.layout.addWidget(self.nodes_name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.metadata_label)
        self.layout.addWidget(self.metadata_input)
        self.layout.addWidget(self.generate_button)

    def validate_input(self) -> bool:
        txt = self.name_input.text()
        is_valid = True
        message = ""
        message_title = ""
        if numerical_hypergraph(self.hypergraph):
            if not txt.isnumeric():
                message_title = "Error: Invalid Node Name"
                message = "Invalid Node Name: the node name must be a number"
                is_valid =  False
            elif int(txt) in self.hypergraph.get_nodes():
                message_title = "Error: Duplicated Node"
                message = "Duplicated Node: in the hypergraph there is a node with the same name"
                is_valid =  False
        else:
            if txt.isnumeric():
                message_title = "Error: Invalid Node Name"
                message = "Invalid Node Name: the node name must be a string"
                is_valid =  False
            elif txt in self.hypergraph.get_nodes():
                message_title = "Error: Duplicated Node"
                message = "Duplicated Node: in the hypergraph there is a node with the same name"
                is_valid =  False
        if is_valid:
            return True
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(message_title)
            msg.setInformativeText(message)
            msg.setWindowTitle(message_title)
            msg.exec_()
            return False

    def send_input(self):
        if self.validate_input():
            self.accept()

    def get_values(self):
        return {
            "name": self.name_input.text().replace("\n", ""),
            "metadata": str_to_dict(self.metadata_input.toPlainText())
        }
