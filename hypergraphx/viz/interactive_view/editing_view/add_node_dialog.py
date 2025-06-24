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

        self.setStyleSheet("""
            QLineEdit {
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
    
            QTextEdit {
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
                padding-top: 1px; /* Sposta la freccia in giù */
            }
            QDoubleSpinBox::down-button:pressed {
                padding-top: 1px; /* Sposta la freccia in giù */
            }
    
            QDoubleSpinBox::up-button {
                subcontrol-position: top right;
                margin: 2px 2px 1px 0px;
            }
    
            QDoubleSpinBox::down-button {
                subcontrol-position: bottom right;
                margin: 1px 2px 2px 0px;
            }
    
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5D9CEC, stop: 1 #4A89DC);
                border: 1px solid #3A79CB;
                border-bottom: 4px solid #3A79CB;
                border-radius: 8px;
                padding: 6px 18px;
                margin-bottom: 4px;
            }
    
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6AACFF, stop: 1 #5D9CEC);
                border-color: #4A89DC;
                border-bottom-color: #4A89DC;
            }
    
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4A89DC, stop: 1 #3A79CB);
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
