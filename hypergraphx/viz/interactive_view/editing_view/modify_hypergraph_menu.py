import gc

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QFileDialog, QMessageBox, QDialog, QMenu, QMenuBar, \
    QTabWidget

import hypergraphx
from hypergraphx import DirectedHypergraph, TemporalHypergraph, Hypergraph
from hypergraphx.generation import random_hypergraph
from hypergraphx.generation.random import random_uniform_hypergraph
from hypergraphx.readwrite.save import save_hypergraph
from hypergraphx.viz.interactive_view.editing_view.hypergraph_table import HypergraphTable
from hypergraphx.viz.interactive_view.__examples import examples_generator
from hypergraphx.viz.interactive_view.editing_view.add_edge_dialog import AddEdgeDialog
from hypergraphx.viz.interactive_view.editing_view.add_node_dialog import AddNodeDialog
from hypergraphx.viz.interactive_view.editing_view.random_graph_dialog import RandomGraphDialog
from hypergraphx.viz.interactive_view.editing_view.random_uniform_graph_dialog import RandomUniformGraphDialog
from hypergraphx.viz.interactive_view.support import str_to_tuple


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
                lambda checked, current_action=action: self.__load_hypergraph_from_action(current_action)
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
                if isinstance(self.hypergraph, Hypergraph):
                    self.hypergraph.remove_edge(str_to_tuple(self.vertical_tab.currentWidget().currentItem().text()))
                elif isinstance(self.hypergraph, DirectedHypergraph):
                    row = self.vertical_tab.currentWidget().selectedItems()[0].row()
                    in_edge = str_to_tuple(self.vertical_tab.currentWidget().item(row, 0).text())
                    out_edge = str_to_tuple(self.vertical_tab.currentWidget().item(row, 1).text())
                    edge = (in_edge, out_edge)
                    self.hypergraph.remove_edge(edge)
                elif isinstance(self.hypergraph, TemporalHypergraph):
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
            if isinstance(self.hypergraph, Hypergraph):
                self.add_edge("normal")
            elif isinstance(self.hypergraph, DirectedHypergraph):
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
