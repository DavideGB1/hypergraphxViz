import gc
import re

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QToolBar, \
    QAction, QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QSpinBox, QPlainTextEdit, QPushButton, \
    QMenu, QMenuBar, QTextEdit, QLineEdit, QTabWidget, QDialogButtonBox

import hypergraphx
from hypergraphx import DirectedHypergraph, TemporalHypergraph, Hypergraph
from hypergraphx.generation import random_hypergraph
from hypergraphx.generation.random import random_uniform_hypergraph
from hypergraphx.readwrite.save import save_hypergraph
from hypergraphx.viz.interactive_view.HypergraphTable import HypergraphTable
from hypergraphx.viz.interactive_view.__examples import examples_generator
from hypergraphx.viz.interactive_view.support import str_to_tuple, str_to_dict, numerical_hypergraph


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

class AddEdgeDialog(QDialog):
    def __init__(self, hypergraph, edge_type, parent=None):
        super().__init__(parent)
        self.hypergraph = hypergraph
        self.edge_type = edge_type
        self.setWindowTitle("Add Edge")

        # Variabili per i widget di input
        self.edge_inputs = []
        self.time_spinbox = None
        self.weight_spinbox = None
        self.metadata_input = None
        self.generate_button = None

        self.__setup_ui()

    def _validate_edge_text(self, text):
        if not text:
            return False
        regex_num = r"^\s*\d+(?:\s*,\s*\d+)*\s*$"
        regex_word = r"^\s*[a-zA-Z\d_]+(?:\s*,\s*[a-zA-Z\d_]+)*\s*$"

        if numerical_hypergraph(self.hypergraph):
            return bool(re.match(regex_num, text))
        else:
            return bool(re.match(regex_word, text))

    def __update_button_state(self):
        """Abilita il pulsante 'Add Edge' solo se tutti gli input sono validi."""
        is_valid = all(self._validate_edge_text(edge_input.text()) for edge_input in self.edge_inputs)
        self.generate_button.setEnabled(is_valid)

    def __setup_ui(self):
        layout = QVBoxLayout(self)

        # --- Campi per l'Arco ---
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
            self.time_spinbox = QSpinBox(self)
            self.time_spinbox.setMinimum(1)
            layout.addWidget(QLabel("Time:", self))
            layout.addWidget(self.time_spinbox)

        if self.hypergraph.is_weighted():
            self.weight_spinbox = QSpinBox(self)
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

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_values(self):
        """Returns the values ​​selected by the user in a dictionary."""
        return {
            "num_nodes": self.n_nodes_spinbox.value(),
            "edge_size": self.size_spinbox.value(),
            "num_edges": self.n_edges_spinbox.value()
        }

class ModifyHypergraphMenu(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, hypergraph, parent=None):
        super(ModifyHypergraphMenu, self).__init__(parent)
        self.vertical_tab = QTabWidget(parent=parent)
        self.vertical_tab.setTabPosition(QTabWidget.West)

        self.hypergraph = hypergraph
        self.__createToolBar()

        self.nodes_tab = HypergraphTable(self.hypergraph, nodes=True, parent=self)
        self.edges_tab = HypergraphTable(self.hypergraph, nodes=False, parent=self)

        self.edges_tab.update_status.connect(self.changed_weights)

        self.vertical_tab.addTab(self.nodes_tab, "Nodes")
        self.vertical_tab.addTab(self.edges_tab, "Edges")

        self.vertical_tab.currentChanged.connect(self.__change_name)
        self.vertical_tab.setObjectName("EditingTab")
        self.vertical_tab.setStyleSheet("""
            QTabWidget#EditingTab::pane {
                border: 1px solid #BDBDBD;
                background-color: white;
                margin-left: -1px;
            }
            
            QTabBar::tab:first {
                margin-top: 10px;
            }
            
            QTabWidget#EditingTab QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F5F5F5, stop: 1 #E0E0E0);
                border: 1px solid #BDBDBD;
                border-top-left-radius: 6px;
                border-bottom-left-radius: 6px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                padding: 5px 8px;
                margin-bottom: 3px;
                margin-left: 10px;
                color: #444;
                font-weight: bold;
                font-size: 12px;
                width: 30; 
                height: 50px;
            }
            
            QTabWidget#EditingTab QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFFFFF, stop: 1 #E8E8E8);
            }
            
            QTabWidget#EditingTab QTabBar::tab:selected {
                background-color: white;
                color: #005A9E;
                border-right-color: transparent; 
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
                margin-right: -1px;
                padding-right: 12px; 
            }
            
            QTabWidget#EditingTab QTabBar::tab:selected:hover {
                background-color: white;
            }
        """)
        self.setCentralWidget(self.vertical_tab)
        self.__createMenuBar()
        self.__change_name()

    def __change_name(self):
        """
        Swaps the localization between Add/Remove Node and Add/Remove Edge
        """
        if self.vertical_tab.currentIndex() == 1:
            self.remove_node.setText("Remove Edge")
            self.add_node.setText("Add Edge")
        else:
            self.remove_node.setText("Remove Node")
            self.add_node.setText("Add Node")

    def __createMenuBar(self):
        """
        Creates and initializes the menu bar for the application's graphical user interface.

        This method is responsible for creating the main menu bar and populating it with menus
        """
        toolbar = QMenuBar(parent=self)
        load_action = QAction("Load", self)
        load_action.triggered.connect(self.open_file)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        generate_menu = QMenu("Generate", self)
        random_generate_action = QAction("Random Hypergraph", self)
        random_generate_action.triggered.connect(self.random_graph)
        generate_menu.addAction(random_generate_action)
        random_uniform_generate_action = QAction("Random Uniform Hypergraph", self)
        random_uniform_generate_action.triggered.connect(self.random_uniform_graph)
        generate_menu.addAction(random_uniform_generate_action)

        example_menu = QMenu("Load Examples", self)
        self.actions = examples_generator()
        for action in self.actions:
             action.triggered.connect(
                 lambda checked,current_action=action: self.__load_hypergraph_from_action(current_action)
             )
             example_menu.addAction(action)
        toolbar.addAction(load_action)
        toolbar.addAction(save_action)
        toolbar.addMenu(generate_menu)
        toolbar.addMenu(example_menu)

        self.setMenuBar(toolbar)

    def __load_hypergraph_from_action(self, action):
        """
        Load an example hypergraph
        """
        self.hypergraph = action.return_hypergraph()
        self.update_hypergraph()

    def __createToolBar(self):
        """
        Creates and configures the toolbar for the user interface.

        The toolbar will include actions for adding and removing rows.
        The toolbar is set to be immovable, and the actions are connected to their respective slots for functionality.

        Actions:
            - Add Row: Triggers the __add_row method to add a new row.
            - Remove Row: Triggers the __remove_row method to remove an existing row.
        """
        toolbar = QToolBar(parent=self)
        toolbar.setMovable(False)

        self.remove_node = QAction("Remove Row", self)
        self.remove_node.triggered.connect(self.__remove_row)
        self.add_node = QAction("Add Row", self)
        self.add_node.triggered.connect(self.__add_row)

        toolbar.addAction(self.add_node)
        toolbar.addAction(self.remove_node)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def __remove_row(self):
        try:
            if self.vertical_tab.currentWidget().use_nodes:
                try:
                    self.hypergraph.remove_node(self.vertical_tab.currentWidget().currentItem().text(), True)
                except KeyError:
                    self.hypergraph.remove_node(int(self.vertical_tab.currentWidget().currentItem().text()), True)
            else:
                if isinstance(self.hypergraph,Hypergraph):
                    self.hypergraph.remove_edge(str_to_tuple(self.vertical_tab.currentWidget().currentItem().text()))
                elif isinstance(self.hypergraph, DirectedHypergraph):
                    row = self.vertical_tab.currentWidget().selectedItems()[0].row()
                    in_edge = str_to_tuple(self.vertical_tab.currentWidget().item(row, 0).text())
                    out_edge = str_to_tuple(self.vertical_tab.currentWidget().item(row, 1).text())
                    edge = (in_edge, out_edge)
                    self.hypergraph.remove_edge(edge)
                elif isinstance(self.hypergraph,TemporalHypergraph):
                    row = self.vertical_tab.currentWidget().selectedItems()[0].row()
                    edge = str_to_tuple(self.vertical_tab.currentWidget().item(row, 0).text())
                    time = int(self.vertical_tab.currentWidget().item(row, 1).text())
                    self.hypergraph.remove_edge(edge, time)
        except Exception:
            return
        self.vertical_tab.currentWidget().remove_row()
        self.update_hypergraph()

    def __add_row(self):
        """

        """
        if self.vertical_tab.currentWidget().use_nodes:
           self.add_node_func()
        else:
            if isinstance(self.hypergraph,Hypergraph):
                self.add_edge("normal")
            elif isinstance(self.hypergraph,DirectedHypergraph):
                self.add_edge("directed")
            elif isinstance(self.hypergraph, TemporalHypergraph):
                self.add_edge("temporal")

    def add_node_func(self):
        dialog = AddNodeDialog(self.hypergraph, self)
        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            self.hypergraph.add_node(values["name"], values["metadata"])
            self.update_hypergraph()

    def add_edge(self, edge_type):
        """
        Opens a dialog to add an arc of a specific type.
        """
        dialog = AddEdgeDialog(self.hypergraph, edge_type, self)

        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            try:
                if edge_type == "temporal":
                    self.hypergraph.add_edge(
                        values["edge_data"],
                        values["time"],
                        values["weight"],
                        values["metadata"]
                    )
                else:
                    self.hypergraph.add_edge(
                        values["edge_data"],
                        values["weight"],
                        values["metadata"]
                    )
                self.update_hypergraph()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Adding Edge",
                    f"An error occurred while adding the edge:\n{e}"
                )

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "JSON (*.json);;HGX (*.hgx)"
        )
        if not file_path:
            gc.collect()
            return
        else:
            try:
                if file_path.endswith(".hif.json"):
                    self.hypergraph = hypergraphx.readwrite.load_hif(file_path)
                else:
                    self.hypergraph = hypergraphx.readwrite.load_hypergraph(file_path)
                self.update_hypergraph()

            except (ValueError, KeyError) as e:
                QMessageBox.critical(
                    self,
                    "File Load Error",
                    f"Could not load the selected file.\n\nDetails: {e}"
                )
        gc.collect()

    def save_file(self):
        """
        Opens a dialog to save the current hypergraph
        in JSON or HGX format.
        """
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Hypergraph File",
            "",
            "HypergraphX Binary (*.hgx);;JSON File (*.json)"
        )

        if not file_path:
            gc.collect()
            return
        else:
            try:
                if "hgx" in selected_filter:
                    if not file_path.endswith('.hgx'):
                        file_path += '.hgx'
                    save_hypergraph(self.hypergraph, file_path, binary=True)

                elif "json" in selected_filter:
                    if not file_path.endswith('.json'):
                        file_path += '.json'
                    save_hypergraph(self.hypergraph, file_path, binary=False)
                else:
                    QMessageBox.warning(
                        self,
                        "Save Error",
                        "An unknown file type was selected. Could not save the file."
                    )
                    return

                QMessageBox.information(
                    self,
                    "Success",
                    f"Hypergraph saved successfully to:\n{file_path}"
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"An error occurred while saving the file.\n\nDetails: {e}"
                )
            gc.collect()

    def random_graph(self):
        dialog = RandomGraphDialog(self)

        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            try:
                self.hypergraph = random_hypergraph(
                    num_nodes=values["num_nodes"],
                    num_edges_by_size=values["edges_by_size"]
                )
                self.update_hypergraph()
            except ValueError as e:
                QMessageBox.critical(self, "Generation Error", f"Could not generate the hypergraph.\n\nDetails: {e}")

        gc.collect()

    def random_uniform_graph(self):
        dialog = RandomUniformGraphDialog(self)

        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            try:
                self.hypergraph = random_uniform_hypergraph(
                    values["num_nodes"],
                    values["edge_size"],
                    values["num_edges"]
                )
                gc.collect()
                self.update_hypergraph()
            except ValueError as e:
                QMessageBox.critical(self, "Generation Error", f"Could not generate the hypergraph.\n\nDetails: {e}")
        gc.collect()

    def update_hypergraph(self):
        """
        Refresh the view after a hypergraph change.
        This method is now safe, fast, and does not leak memory.
        Simply call the refresh methods on existing widgets.
        """
        self.nodes_tab.set_hypergraph(self.hypergraph)
        self.edges_tab.set_hypergraph(self.hypergraph)
        gc.collect()
        self.updated_hypergraph.emit({"hypergraph": self.hypergraph})

    def changed_weights(self):
        self.updated_hypergraph.emit({"hypergraph": self.hypergraph})
