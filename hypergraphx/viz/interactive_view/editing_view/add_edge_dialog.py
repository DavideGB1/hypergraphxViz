import re

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QDoubleSpinBox

from hypergraphx.viz.interactive_view.support import numerical_hypergraph, str_to_dict, str_to_tuple


class AddEdgeDialog(QDialog):
    def __init__(self, hypergraph, edge_type, parent=None):
        super().__init__(parent)
        self.hypergraph = hypergraph
        self.edge_type = edge_type
        self.setWindowTitle("Add Edge")

        self.edge_inputs = []
        self.time_spinbox = None
        self.weight_spinbox = None
        self.metadata_input = None
        self.generate_button = None

        self.__setup_ui()

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

    def _validate_edge_text(self, text):
        if not text:
            return False

        regex_number = r"[0-9]+ *, *[0-9]+ *(, *[0-9]+ *)*"
        regex_word = r"[a-zA-Z]+[0-9]* *, *[a-zA-Z]+[0-9]* *(, *[a-zA-Z]+[0-9]+ *)*"

        if numerical_hypergraph(self.hypergraph):
            return re.fullmatch(regex_number, text) is not None
        else:
            return re.fullmatch(regex_word, text) is not None

    def __update_button_state(self):
        """Enable the 'Add Edge' button only if all inputs are valid."""
        is_valid = all(self._validate_edge_text(edge_input.text()) for edge_input in self.edge_inputs)
        self.generate_button.setEnabled(is_valid)

    def __setup_ui(self):
        layout = QVBoxLayout(self)

        if self.edge_type == "normal":
            fields = [("Edge:", "Insert the edge like 1,2,3,4.")]
        elif self.edge_type == "directed":
            fields = [
                ("Edge Source:", "Insert the edge source (e.g., 1,2)."),
                ("Edge Target:", "Insert the edge target (e.g., 3,4)."),
            ]
        elif self.edge_type == "temporal":
            fields = [("Edge:", "Insert the edge like 1,2,3,4.")]

        for label_text, placeholder in fields:
            label = QLabel(label_text, self)
            line_edit = QLineEdit(self)
            line_edit.setPlaceholderText(placeholder)
            line_edit.textChanged.connect(self.__update_button_state)
            self.edge_inputs.append(line_edit)
            layout.addWidget(label)
            layout.addWidget(line_edit)

        if self.edge_type == "temporal":
            self.time_spinbox = QDoubleSpinBox(self)
            self.time_spinbox.setMinimum(1)
            layout.addWidget(QLabel("Time:", self))
            layout.addWidget(self.time_spinbox)

        if self.hypergraph.is_weighted():
            self.weight_spinbox = QDoubleSpinBox(self)
            self.weight_spinbox.setMinimum(1)
            self.weight_spinbox.setValue(1)
            layout.addWidget(QLabel("Weight:", self))
            layout.addWidget(self.weight_spinbox)

        self.metadata_input = QTextEdit(self)
        self.metadata_input.setPlaceholderText("Insert metadata (e.g., class:CS, year:2023).")
        layout.addWidget(QLabel("Edge Metadata:", self))
        layout.addWidget(self.metadata_input)

        self.generate_button = QPushButton("Add Edge", self)
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self.accept)
        layout.addWidget(self.generate_button)

    def get_values(self):
        """Returns a dictionary with the values entered by the user."""
        values = {
            "weight": 1,
            "time": None,
            "metadata": str_to_dict(self.metadata_input.toPlainText())
        }

        if self.weight_spinbox:
            values["weight"] = self.weight_spinbox.value()
        if self.time_spinbox:
            values["time"] = self.time_spinbox.value()

        if self.edge_type == "directed":
            source = str_to_tuple(self.edge_inputs[0].text())
            target = str_to_tuple(self.edge_inputs[1].text())
            values["edge_data"] = (source, target)
        else:
            values["edge_data"] = str_to_tuple(self.edge_inputs[0].text())

        return values
