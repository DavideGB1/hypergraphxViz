from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMainWindow, QToolBar, \
    QAction, QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QSpinBox, QPlainTextEdit, QPushButton, \
    QMenu, QMenuBar, QTextEdit, QLineEdit
from pyqt_vertical_tab_widget import VerticalTabWidget
import hypergraphx
from hypergraphx.generation import random_hypergraph
from hypergraphx.generation.random import random_uniform_hypergraph
from hypergraphx.readwrite.save import save_hypergraph
from hypergraphx.viz.interactive_view.__examples import examples_generator


class HypergraphTable(QTableWidget):
    update_status = pyqtSignal(dict)
    def __init__(self, hypergraph, nodes = True  ):
        super(HypergraphTable, self).__init__()
        self.use_nodes = nodes
        self.update_table(hypergraph)
        # Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    def remove_row(self):
        self.removeRow(self.currentRow())
    def update_table_nodes(self, hypergraph):

        num_row = hypergraph.num_nodes()
        num_col = 2
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        if self.use_nodes:
            self.setHorizontalHeaderLabels(['Name', 'Metadata'])
        curr_row = 0
        for node in hypergraph.get_nodes():
            self.setItem(curr_row, 0, QTableWidgetItem(str(node)))
            self.setItem(curr_row, 1, QTableWidgetItem(str(hypergraph.get_node_metadata(node))))
            curr_row += 1
    def update_table_eges(self, hypergraph):
        num_row = hypergraph.num_edges()
        if hypergraph.is_weighted():
            num_col = 3
            idx = 1
        else:
            num_col = 2
            idx = 0
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        if hypergraph.is_weighted():
            self.setHorizontalHeaderLabels(['Edge', 'Weight', 'Metadata'])
        else:
            self.setHorizontalHeaderLabels(['Edge', 'Metadata'])
        curr_row = 0

        for edge in hypergraph.get_edges():
            self.setItem(curr_row, 0, QTableWidgetItem(str(edge)))
            if hypergraph.is_weighted():
                self.setItem(curr_row, idx, QTableWidgetItem(str(hypergraph.get_weight(edge))))
            else:
                self.setItem(curr_row, idx+1, QTableWidgetItem(str(hypergraph.get_edge_metadata(edge))))
            curr_row += 1
    def update_table(self, hypergraph):
        if self.use_nodes:
            self.update_table_nodes(hypergraph)
        else:
            self.update_table_eges(hypergraph)
class ModifyHypergraphMenu(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, hypergraph):
        super(ModifyHypergraphMenu, self).__init__()
        self.vertical_tab = VerticalTabWidget()
        self.hypergraph = hypergraph
        self._createToolBar()
        self.nodes_tab = HypergraphTable(self.hypergraph)
        self.edges_tab = HypergraphTable(self.hypergraph, False)

        self.vertical_tab.addTab(self.nodes_tab, "Nodes")
        self.vertical_tab.addTab(self.edges_tab, "Edges")
        self.vertical_tab.currentChanged.connect(self._change_name)
        self.setCentralWidget(self.vertical_tab)
        self._createMenuBar()
        self._change_name()

    def _change_name(self):
        if self.vertical_tab.currentIndex() == 1:
            self.remove_node.setText("Remove Edge")
            self.add_node.setText("Add Edge")
        else:
            self.remove_node.setText("Remove Node")
            self.add_node.setText("Add Node")

    def _createMenuBar(self):
       toolbar = QMenuBar()
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
                lambda checked,current_action=action: self.load_hypergraph_from_action(current_action)
            )
            example_menu.addAction(action)
       toolbar.addAction(load_action)
       toolbar.addAction(save_action)
       toolbar.addMenu(generate_menu)
       toolbar.addMenu(example_menu)

       self.setMenuBar(toolbar)
    def load_hypergraph_from_action(self, action):

        self.hypergraph = action.return_hypergraph()
        self.update_hypergraph()

    def _createToolBar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)

        self.remove_node = QAction("Remove Row", self)
        self.remove_node.triggered.connect(self.remove_row)
        self.add_node = QAction("Add Row", self)
        self.add_node.triggered.connect(self.add_row)

        toolbar.addAction(self.add_node)
        toolbar.addAction(self.remove_node)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def remove_row(self):
        try:
            if self.vertical_tab.currentWidget().use_nodes:
                try:
                    self.hypergraph.remove_node(self.vertical_tab.currentWidget().currentItem().text(), True)
                except KeyError:
                    self.hypergraph.remove_node(int(self.vertical_tab.currentWidget().currentItem().text()), True)
            else:
                self.hypergraph.remove_edge(eval(self.vertical_tab.currentWidget().currentItem().text()))
        except Exception:
            pass
        self.vertical_tab.currentWidget().remove_row()
        self.update_hypergraph()
    def add_row(self):
        if self.vertical_tab.currentWidget().use_nodes:
           self.add_node_func()
        else:
            self.add_edge()
    def add_node_func(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Node")
        layout = QVBoxLayout()
        n_nodes_label = QLabel("Node Name:")
        n_nodes_textarea = QLineEdit()
        layout.addWidget(n_nodes_label)
        layout.addWidget(n_nodes_textarea)

        metadata_label = QLabel("Node Metadata:")
        metadata_textarea = QTextEdit()
        metadata_textarea.setPlaceholderText("Insert the metadata (example class:CS, gender:M).")
        layout.addWidget(metadata_label)
        layout.addWidget(metadata_textarea)
        generate = QPushButton("Add Node")
        generate.clicked.connect(dialog.accept)
        layout.addWidget(generate)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.Accepted:
            self.hypergraph.add_node(n_nodes_textarea.text().replace("\n",""), str_to_dict(metadata_textarea.toPlainText()))
            self.update_hypergraph()
    def add_edge(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Edge")
        layout = QVBoxLayout()
        edge_label = QLabel("Edge:")
        edge_textarea = QLineEdit()
        edge_textarea.setPlaceholderText("Insert the edge like 1,2,3,4.\n")
        layout.addWidget(edge_label)
        layout.addWidget(edge_textarea)
        if self.hypergraph.is_weighted():
            weight_label = QLabel("Weight:")
            weight_spinbox = QSpinBox()
            weight_spinbox.setValue(1)
            weight_spinbox.setMinimum(1)
            weight_spinbox.setSingleStep(1)
            layout.addWidget(weight_label)
            layout.addWidget(weight_spinbox)
        metadata_label = QLabel("Edge Metadata:")
        metadata_textarea = QTextEdit()
        metadata_textarea.setPlaceholderText("Insert the metadata (example class:CS, gender:M).\n")
        layout.addWidget(metadata_label)
        layout.addWidget(metadata_textarea)
        generate = QPushButton("Add Edge")
        generate.clicked.connect(dialog.accept)
        layout.addWidget(generate)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.Accepted:
            weight = 1
            if self.hypergraph.is_weighted():
                weight = int(weight_spinbox.value())
            self.hypergraph.add_edge(str_to_tuple(edge_textarea.text()),weight, str_to_dict(metadata_textarea.toPlainText()))
            self.update_hypergraph()

    def open_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setNameFilters(["JSON (*.json)", "HGX (*.hgx)"])

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()
            try:
                self.hypergraph = hypergraphx.readwrite.load_hypergraph(selected_file[0])
                self.update_hypergraph()
            except ValueError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error: Invalid Input File")
                msg.setInformativeText('Input File is not .json | .hgx')
                msg.setWindowTitle("Error")
                msg.exec_()

    def save_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Save File")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setNameFilters(["JSON (*.json)", "HGX (*.hgx)"])

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            if ".hgx" in selected_file:
                save_hypergraph(self.hypergraph, selected_file,True)
            elif ".json" in selected_file:
                save_hypergraph(self.hypergraph, selected_file, False)
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error: Invalid File Type")
                msg.setInformativeText('File Type is not .json | .hgx')
                msg.setWindowTitle("Error")
                msg.exec_()

    def random_graph(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Random Hypergraph")
        layout = QVBoxLayout()
        n_nodes_label = QLabel("Number of Nodes:")
        n_nodes_spinbox = QSpinBox()
        n_nodes_spinbox.setValue(1)
        n_nodes_spinbox.setMinimum(1)
        n_nodes_spinbox.setSingleStep(1)
        layout.addWidget(n_nodes_label)
        layout.addWidget(n_nodes_spinbox)
        edges_label = QLabel("Edges Dictionary:")
        text = QPlainTextEdit()
        text.insertPlainText("Insert the edges dictionary (example 2:14).\n")
        button = QPushButton("Add Edges")
        edges_dictionary = dict()
        current_edges_label = QLabel("Current Edges:")
        edges_text = QPlainTextEdit()
        edges_text.setReadOnly(True)
        edges_text.setPlainText("")


        def edges_dictionary_converter():
            edges_dict = {}
            print(text.toPlainText())
            values = text.toPlainText().replace("Insert the edges dictionary (example 2:14).\n",'')
            values = values.split(",")
            for pair in values:
                try:
                    k, v = pair.split(":")
                    if int(k) <= n_nodes_spinbox.value():
                        edges_dict[int(k.strip())] = int(v.strip())
                except ValueError:
                    pass
            edges_dictionary.update(edges_dict)
            edges_text.setPlainText(str(edges_dictionary))
        button.clicked.connect(edges_dictionary_converter)

        generate = QPushButton("Generate")
        generate.clicked.connect(dialog.accept)
        layout.addWidget(edges_label)
        layout.addWidget(text)
        layout.addWidget(button)
        layout.addWidget(current_edges_label)
        layout.addWidget(edges_text)
        layout.addWidget(generate)
        dialog.setLayout(layout)
        if dialog.exec()== QDialog.Accepted:
            try:
                self.hypergraph = random_hypergraph(num_nodes=n_nodes_spinbox.value(), num_edges_by_size=edges_dictionary)
                self.update_hypergraph()
            except ValueError:
                pass

    def random_uniform_graph(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Generate Random Uniform Hypergraph")
        layout = QVBoxLayout()
        n_nodes_label = QLabel("Number of Nodes:")
        n_nodes_spinbox = QSpinBox()
        n_nodes_spinbox.setValue(1)
        n_nodes_spinbox.setMinimum(1)
        n_nodes_spinbox.setSingleStep(1)
        layout.addWidget(n_nodes_label)
        layout.addWidget(n_nodes_spinbox)

        size_label = QLabel("Edges Size:")
        size_spinbox = QSpinBox()
        size_spinbox.setValue(1)
        size_spinbox.setMinimum(1)
        size_spinbox.setSingleStep(1)
        layout.addWidget(size_label)
        layout.addWidget(size_spinbox)

        n_edges_label = QLabel("Number of Edges:")
        n_edges_spinbox = QSpinBox()
        n_edges_spinbox.setValue(1)
        n_edges_spinbox.setMinimum(1)
        n_edges_spinbox.setSingleStep(1)
        layout.addWidget(n_edges_label)
        layout.addWidget(n_edges_spinbox)

        generate = QPushButton("Generate")
        generate.clicked.connect(dialog.accept)
        layout.addWidget(generate)
        dialog.setLayout(layout)
        if dialog.exec()== QDialog.Accepted:
            try:
                self.hypergraph = random_uniform_hypergraph(n_nodes_spinbox.value(),size_spinbox.value(), n_edges_spinbox.value())
                self.update_hypergraph()
            except ValueError:
                pass

    def update_hypergraph(self):
        self.edges_tab.update_table(self.hypergraph)
        self.nodes_tab.update_table(self.hypergraph)

        self.updated_hypergraph.emit({ "hypergraph": self.hypergraph})

def str_to_dict(string: str):
    dict = {}
    values = string.split(",")
    for pair in values:
        try:
            k, v = pair.split(":")
            dict[k.strip()] = v.strip()
        except ValueError:
            pass
    return dict
def str_to_tuple(string: str):
    res = string.split(",")
    vals = []
    for val in res:
        try:
            if val.isnumeric():
                vals.append(int(val))
            else:
                vals.append(val)
        except ValueError:
            pass

    return tuple(vals)