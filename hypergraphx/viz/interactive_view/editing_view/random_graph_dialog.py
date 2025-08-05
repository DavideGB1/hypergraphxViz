from PyQt5.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QDoubleSpinBox, \
    QSpinBox


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
    
            QPlainTextEdit {
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

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        ok_button.setStyleSheet("""QPushButton {
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
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setStyleSheet("""
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
