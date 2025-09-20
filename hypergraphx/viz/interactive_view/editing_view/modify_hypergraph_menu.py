import gc

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QFileDialog, QMessageBox, QDialog, QMenu, QMenuBar, \
    QTabWidget

import hypergraphx
from hypergraphx import DirectedHypergraph, TemporalHypergraph, Hypergraph
from hypergraphx.generation import random_hypergraph
from hypergraphx.generation.random import random_uniform_hypergraph
from hypergraphx.readwrite.save import save_hypergraph
from hypergraphx.viz.interactive_view.controller import HypergraphType
from hypergraphx.viz.interactive_view.editing_view.connected_components_table import ConnectedComponentsTable
from hypergraphx.viz.interactive_view.editing_view.hypergraph_table import HypergraphTable
from hypergraphx.viz.interactive_view.__examples import examples_generator
from hypergraphx.viz.interactive_view.editing_view.add_edge_dialog import AddEdgeDialog
from hypergraphx.viz.interactive_view.editing_view.add_node_dialog import AddNodeDialog
from hypergraphx.viz.interactive_view.editing_view.random_graph_dialog import RandomGraphDialog
from hypergraphx.viz.interactive_view.editing_view.random_uniform_graph_dialog import RandomUniformGraphDialog


class ModifyHypergraphMenu(QMainWindow):
    updated_hypergraph = pyqtSignal(dict)

    def __init__(self, controller, parent=None):
        super(ModifyHypergraphMenu, self).__init__(parent)
        self.vertical_tab = QTabWidget(parent=parent)
        self.controller = controller
        self.controller.updated_hypergraph.connect(self.update_hypergraph)
        self.vertical_tab.setTabPosition(QTabWidget.West)
        self.new_cc = False

        # Create and add the toolbars
        self.__createMainToolBar()
        self.__createCCToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.main_toolbar)
        self.addToolBar(Qt.TopToolBarArea, self.cc_toolbar)

        # Setup tabs
        self.nodes_tab = HypergraphTable(controller = self.controller, nodes=True, parent=self)
        self.edges_tab = HypergraphTable(controller = self.controller, nodes=False, parent=self)
        self.edges_tab.update_status.connect(self.changed_weights)

        self.vertical_tab.addTab(self.nodes_tab, "Nodes")
        self.vertical_tab.addTab(self.edges_tab, "Edges")

        self.cc_tab = None
        if self.controller.hypergraph_type == HypergraphType.NORMAL:
            self.cc_tab = ConnectedComponentsTable(self.controller, parent=self)
            self.vertical_tab.addTab(self.cc_tab, "CC")
            self.cc_tab.update_status.connect(self.update_cc_components)

        # Connect the tab-changed signal to the new handler
        self.vertical_tab.currentChanged.connect(self.__on_tab_changed)
        self.vertical_tab.setObjectName("EditingTab")
        self.setCentralWidget(self.vertical_tab)
        self.__createMenuBar()
        # Set the initial state of the toolbars
        self.__on_tab_changed(self.vertical_tab.currentIndex())

    def __on_tab_changed(self, index):
        """
        Handles UI changes when the active tab is switched.
        - Updates action text for the main toolbar.
        - Toggles visibility of the main and CC toolbars.
        """
        current_widget = self.vertical_tab.widget(index)
        is_cc_tab_active = self.cc_tab is not None and current_widget is self.cc_tab

        # Toggle toolbar visibility
        self.main_toolbar.setVisible(not is_cc_tab_active)
        self.cc_toolbar.setVisible(is_cc_tab_active)

        # Update main toolbar action text if it's visible
        if not is_cc_tab_active:
            if current_widget is self.edges_tab:
                self.remove_action.setText("Remove Edge")
                self.add_action.setText("Add Edge")
            else:  # Assuming nodes_tab
                self.remove_action.setText("Remove Node")
                self.add_action.setText("Add Node")

    def __createMenuBar(self):
        """
        Creates and initializes the menu bar for the application's graphical user interface.
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
        self.controller.change_hypergraph(action.return_hypergraph())

    def __createMainToolBar(self):
        """
        Creates and configures the main toolbar for editing nodes and edges.
        This toolbar is visible for the Nodes and Edges tabs.
        """
        self.main_toolbar = QToolBar("Edit Toolbar", self)
        self.main_toolbar.setMovable(False)

        self.add_action = QAction("Add", self)
        self.add_action.setToolTip("Add a new node/edge to the Hypergraph.")
        self.add_action.triggered.connect(self.__add_row)

        self.remove_action = QAction("Remove", self)
        self.remove_action.setToolTip("Remove the selected nodes/edges from the Hypergraph.")
        self.remove_action.triggered.connect(self.__remove_row)

        self.main_toolbar.addAction(self.add_action)
        self.main_toolbar.addAction(self.remove_action)

    def __createCCToolBar(self):
        """
        Creates the toolbar that is only visible for the Connected Components tab.
        """
        self.cc_toolbar = QToolBar("Connected Components Toolbar", self)
        self.cc_toolbar.setMovable(False)

        self.update_cc_action = QAction("Draw Selected CCs", self)
        self.update_cc_action.triggered.connect(self.__update_cc)
        self.select_all_cc_action = QAction("Select All", self)
        self.select_all_cc_action.triggered.connect(self.select_all_cc)
        self.unselect_all_cc_action = QAction("Unselect All", self)
        self.unselect_all_cc_action.triggered.connect(self.unselect_all_cc)
        self.select_biggest_cc_action = QAction("Select Biggest CC", self)
        self.select_biggest_cc_action.triggered.connect(self.select_biggest_cc)


        self.cc_toolbar.addAction(self.update_cc_action)
        self.cc_toolbar.addAction(self.select_all_cc_action)
        self.cc_toolbar.addAction(self.unselect_all_cc_action)
        self.cc_toolbar.addAction(self.select_biggest_cc_action)

    def select_all_cc(self):
        curr_row = 0
        for component in self.cc_tab.components:
            self.cc_tab.item(curr_row, 1).setCheckState(QtCore.Qt.Checked)
            curr_row += 1

    def unselect_all_cc(self):
        curr_row = 0
        for component in self.cc_tab.components:
            self.cc_tab.item(curr_row, 1).setCheckState(QtCore.Qt.Unchecked)
            curr_row += 1

    def select_biggest_cc(self):
        self.unselect_all_cc()
        curr_row = 0
        max_index = 0
        max_len = 0
        for component in self.controller.cc:
            if max_len < len(component):
                max_len = len(component)
                max_index = curr_row
            curr_row += 1
        self.cc_tab.item(max_index, 1).setCheckState(QtCore.Qt.Checked)

    def __update_cc(self):
        sub_hg = Hypergraph()
        curr_row = 0
        selected = 0
        selected_cc = []
        for component in self.controller.cc:
            if self.cc_tab.item(curr_row, 1).checkState() == QtCore.Qt.Checked:
                selected += 1
                selected_cc.append(component)
            curr_row += 1
        if selected > 0:
            self.controller.update_selected_ccs(selected_cc)
        else:
            QMessageBox.critical(
                self,
                "No Connected Component",
                f"No Connected Component selected"
            )
            curr_row = 0
            for component in self.cc_tab.components:
                self.cc_tab.item(curr_row, 1).setCheckState(QtCore.Qt.Checked)
                curr_row += 1

    def __remove_row(self):
        if self.vertical_tab.currentWidget().currentItem() is not None:
            if self.vertical_tab.currentWidget().use_nodes:
                to_remove_nodes = []
                for item in self.vertical_tab.currentWidget().selectedItems():
                    to_remove_nodes.append(self.vertical_tab.currentWidget().item(item.row(), 0).text())
                self.controller.remove_nodes(to_remove_nodes)
            else:
                to_remove_edges = []
                for item in self.vertical_tab.currentWidget().selectedItems():
                    row = item.row()
                    match self.controller.hypergraph_type:
                        case HypergraphType.NORMAL:
                            to_remove_edges.append(eval(self.vertical_tab.currentWidget().item(row, 0).text()))
                        case HypergraphType.DIRECTED:
                            in_edge = eval(self.vertical_tab.currentWidget().item(row, 0).text())
                            out_edge = eval(self.vertical_tab.currentWidget().item(row, 1).text())
                            edge = (in_edge, out_edge)
                            to_remove_edges.append(edge)
                        case HypergraphType.TEMPORAL:
                            edge = eval(self.vertical_tab.currentWidget().item(row, 0).text())
                            time = int(self.vertical_tab.currentWidget().item(row, 1).text())
                            to_remove_edges.append((edge, time))
                self.controller.remove_edges(to_remove_edges)


    def __add_row(self):
        """
        Adds a new node or edge based on the currently active tab.
        """
        if self.vertical_tab.currentWidget().use_nodes:
            self.add_node_func()
        else:
            match self.controller.hypergraph_type:
                case HypergraphType.NORMAL:
                    self.add_edge("normal")
                case HypergraphType.DIRECTED:
                    self.add_edge("directed")
                case HypergraphType.TEMPORAL:
                    self.add_edge("temporal")

    def add_node_func(self):
        dialog = AddNodeDialog(self.controller.get_hypergraph(), self)
        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            self.controller.add_node(values)

    def add_edge(self, edge_type):
        """
        Opens a dialog to add an arc of a specific type.
        """
        dialog = AddEdgeDialog(self.controller.get_hypergraph(), edge_type, self)

        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            try:
                self.controller.add_edge(values)
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
                self.controller.load_from_file(file_path)
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
                    self.controller.save_to_file(file_path)
                elif "json" in selected_filter:
                    if not file_path.endswith('.json'):
                        file_path += '.json'
                    self.controller.save_to_file(file_path)
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
            try:
                self.controller.generate_random_hypergraph(dialog.get_values())
            except ValueError as e:
                QMessageBox.critical(self, "Generation Error", f"Could not generate the hypergraph.\n\nDetails: {e}")

        gc.collect()

    def random_uniform_graph(self):
        dialog = RandomUniformGraphDialog(self)

        if dialog.exec() == QDialog.Accepted:
            try:
                self.controller.generate_random_uniform_graph(dialog.get_values())
            except ValueError as e:
                QMessageBox.critical(self, "Generation Error", f"Could not generate the hypergraph.\n\nDetails: {e}")
        gc.collect()

    def update_hypergraph(self, values):
        """
        Refresh the view after a hypergraph change.
        This method is now safe, fast, and does not leak memory.
        Simply call the refresh methods on existing widgets.
        """
        self.nodes_tab.set_hypergraph()
        self.edges_tab.set_hypergraph()
        if not self.new_cc:
            if self.controller.hypergraph_type == HypergraphType.NORMAL:
                if self.cc_tab is None:
                    self.cc_tab = ConnectedComponentsTable(self.controller, parent=self)
                    self.vertical_tab.addTab(self.cc_tab, "CC")
                else:
                    if not values["updated_ccs"]:
                        self.cc_tab.set_hypergraph()
                        self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.cc_tab), True)
            else:
                if self.cc_tab is not None:
                    self.vertical_tab.setTabVisible(self.vertical_tab.indexOf(self.cc_tab), False)

        gc.collect()
        self.new_cc = False

    def update_cc_components(self, dictionary):
        self.hypergraph = dictionary["selected_components_hg"]
        self.new_cc = True
        self.update_hypergraph()

    def changed_weights(self):
        self.updated_hypergraph.emit({"hypergraph": self.controller.get_hypergraph()})