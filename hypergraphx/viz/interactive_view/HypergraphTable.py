from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QTableWidget, QHeaderView, QTableWidgetItem
from hypergraphx import DirectedHypergraph, TemporalHypergraph
from hypergraphx.viz.interactive_view.support import str_to_dict, str_to_int_or_float, str_to_tuple


class ReadOnlyDelegate(QStyledItemDelegate):
    """
    QStyledItemDelegate subclass to add validation for QLineEdit editors, that turns an item into read-only.
    """
    def createEditor(self, parent, option, index):
        return

class ValidationDelegate(QStyledItemDelegate):
    """
    QStyledItemDelegate subclass to add validation for QLineEdit editors, that allows only numbers in the
    item.
    """
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            validator = QDoubleValidator(-10000000, 10000000,6, editor)
            editor.setValidator(validator)
        return editor

class HypergraphTable(QTableWidget):
    """
    QTableWidget with custom functions ad allows to modify the hypergraph.
    """
    update_status = pyqtSignal(dict)
    def __init__(self, hypergraph, nodes = True  ):
        super(HypergraphTable, self).__init__()
        self.itemChanged.connect(self.__check_new_cell_value)
        self.weight_col = 0
        self.metadata_col = 0
        self.loading = False
        self.last_changes = False
        self.valid_col = 1
        self.use_nodes = nodes
        self.old_values = dict()
        self.hypergraph = hypergraph
        self.update_table(hypergraph)
        # Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setItemDelegateForColumn(0, ReadOnlyDelegate(self))

    def remove_row(self):
        """
        Removes the currently selected row in a data model.
        """
        self.removeRow(self.currentRow())

    def update_table(self, hypergraph):
        """
        Updates the table with data from the provided hypergraph object.

        Parameters
        ----------
        hypergraph : obj
            The hypergraph object containing updated data to refresh the table.

        """
        self.hypergraph = hypergraph
        self.loading = True
        if self.use_nodes:
            self.__update_table_nodes()
        else:
            self.__update_table_edges()
        self.loading = False

    def __update_table_nodes(self):
        """
        Updates the table to display the nodes of a hypergraph and their associated metadata.
        """
        num_row = self.hypergraph.num_nodes()
        num_col = 2
        self.metadata_col = 1
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        if self.use_nodes:
            self.setHorizontalHeaderLabels(['Name', 'Metadata'])
        curr_row = 0
        for node in self.hypergraph.get_nodes():
            metadata = self.hypergraph.get_node_metadata(node)
            if metadata is None:
                metadata = {}
            self.setItem(curr_row, 0, QTableWidgetItem(str(node)))
            self.setItem(curr_row, 1, QTableWidgetItem(str(metadata)))
            self.old_values[curr_row,1] = str(metadata)
            curr_row += 1

    def __update_table_edges(self):
        """
        Updates the table representation of the hypergraph's edges.
        This method adjusts the table's row and column count based on the
        current state of the hypergraph's edges and configuration. If the
        hypergraph is weighted, it modifies the configuration accordingly,
        updates the column names, and appends a "Weight" column.
        For each edge in the hypergraph, this method populates the table
        with edge-specific information by invoking related helper methods.
        """
        num_row = self.hypergraph.num_edges()
        config = self.__get_hypergraph_config()
        num_col = config["num_col"]
        idx = config["idx"]
        self.weight_col = config["weight_col"]
        self.metadata_col = config["metadata_col"]
        col_names = config["col_names"]
        if self.hypergraph.is_weighted():
            num_col += 1
            idx += 1
            self.weight_col += 1
            self.metadata_col += 1
            col_names.insert(idx, "Weight")
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        self.setHorizontalHeaderLabels(col_names)

        curr_row = 0
        for edge in self.hypergraph.get_edges():
            self.__set_edge_items(curr_row, edge)
            self.__update_weight_and_delegate(curr_row, edge)
            self.__update_metadata(curr_row, edge)
            curr_row += 1

    def __get_hypergraph_config(self):
        """
        Gets the configuration settings for the hypergraph type.

        Returns the appropriate configuration dictionary based on the type of the hypergraph.
        Each configuration specifies the number of columns, indices of specific values,
        and column names. The function determines the configuration for the following types of hypergraphs:
        DirectedHypergraph, TemporalHypergraph, or other general types.

        Returns
        -------
        dict
            A dictionary containing configuration parameters including:
            - `num_col` (int): Number of columns in the hypergraph structure.
            - `idx` (int): Index identifying a specific property in the hypergraph structure.
            - `weight_col` (int): Column index for weight information.
            - `metadata_col` (int): Column index for metadata.
            - `col_names` (list of str): Descriptive names for each column.

        """
        if isinstance(self.hypergraph, DirectedHypergraph):
            return {"num_col": 3, "idx": 1, "weight_col": 1, "metadata_col": 2,
                    "col_names": ["Edge Source", "Edge Destination", "Metadata"]}
        elif isinstance(self.hypergraph, TemporalHypergraph):
            return {"num_col": 3, "idx": 1, "weight_col": 1, "metadata_col": 2,
                    "col_names": ["Edge", "Time", "Metadata"]}
        else:
            return {"num_col": 2, "idx": 0, "weight_col": 0, "metadata_col": 1,
                    "col_names": ["Edge", "Metadata"]}

    def __set_edge_items(self,row, edge):
        """
        Sets the cells that show the edge's nodes.

        Parameters
        ----------
        row : int
            The row index in the table where edge data will be set.
        edge : tuple or object
            Represents the edge data. Its structure varies depending on the type of hypergraph being used.

        Notes
        -----
        - If the hypergraph is a `DirectedHypergraph`, the function assumes that `edge` contains two elements
          and sets the first element at column 0 and the second at column 1.
        - If the hypergraph is a `TemporalHypergraph`, the function assumes that `edge` contains two elements
          but reverses their order when setting values (edge[1] in column 0, edge[0] in column 1),
          and applies a `ValidationDelegate` to column 1.
        - For other hypergraph types, the function interprets `edge` as a single value and sets it in column 0.
        """
        if isinstance(self.hypergraph, DirectedHypergraph):
            self.setItem(row, 0, QTableWidgetItem(str(edge[0])))
            self.setItem(row, 1, QTableWidgetItem(str(edge[1])))
        elif isinstance(self.hypergraph, TemporalHypergraph):
            self.setItem(row, 0, QTableWidgetItem(str(edge[1])))
            self.setItem(row, 1, QTableWidgetItem(str(edge[0])))
            self.setItemDelegateForColumn(1, ValidationDelegate(self))
        else:
            self.setItem(row, 0, QTableWidgetItem(str(edge)))

    def __update_weight_and_delegate(self, row, edge):
        """
        Updates the weight of a hypergraph edge in a table row and assigns a validation delegate for the weight column.

        Parameters
        ----------
        row : int
            The table row to be updated with the edge weight.

        edge : tuple
            The edge whose weight is to be retrieved and updated in the table. The format of the edge depends on the hypergraph type.

        """
        if self.hypergraph.is_weighted():
            if isinstance(self.hypergraph, TemporalHypergraph):
                weight = self.hypergraph.get_weight(edge[1], edge[0])
            else:
                weight = self.hypergraph.get_weight(edge)
            self.setItem(row, self.weight_col, QTableWidgetItem(str(weight)))
            self.setItemDelegateForColumn(self.weight_col, ValidationDelegate(self))

    def __update_metadata(self, row, edge):
        """
        Updates the metadata for a given row and edge in the hypergraph and sets the corresponding table item.

        Parameters
        ----------
        row : int
            The row in the table for which metadata needs to be updated.
        edge : tuple
            The edge in the hypergraph for which metadata is retrieved and updated.

        """
        if isinstance(self.hypergraph, TemporalHypergraph):
            metadata = self.hypergraph.get_edge_metadata(edge[1], edge[0]) or {}
        else:
            metadata = self.hypergraph.get_edge_metadata(edge)
        if self.hypergraph.is_weighted():
            metadata.pop("weight", None)
        if isinstance(self.hypergraph, TemporalHypergraph):
            metadata.pop("time", None)
        self.setItem(row, self.metadata_col, QTableWidgetItem(str(metadata)))
        self.old_values[row, self.metadata_col] = str(metadata)

    def __check_new_cell_value(self, item):
        """
        Checks and processes a new cell value from the user interface.
        The behavior of this method depends on the current state of the object and the column of the modified cell.

        Parameters
        ----------
        item : object
            The table cell item that contains the new value to be processed.

        Notes
        -----
        - The method will not perform any action if the `loading` state is True.
        - If there are pending changes (`last_changes` is True), the method toggles `last_changes` to False and aborts further processing.
        - Actions are column-dependent:
          - Metadata column processing is currently not implemented.
          - Weight column invokes weight modification if the hypergraph is weighted.
          - Column 1 invokes time modification if the hypergraph is an instance of `TemporalHypergraph`.
        - Emits a signal to update the status after handling the new value.
        """
        if self.loading:
            return
        if self.last_changes:
            self.last_changes = not self.last_changes
            return
        if item.column() == self.metadata_col:
            self.__modify_metadata(item)
        elif item.column() == self.weight_col and self.hypergraph.is_weighted():
            self.__modify_weight(item)
        elif item.column() == 1 and isinstance(self.hypergraph, TemporalHypergraph):
            self.__modify_time(item)
        self.update_status.emit({})

    def __modify_weight(self, item):
        """
        Modifies the weight of a specific edge in the hypergraph.

        Parameters
        ----------
        item : An object representing a data element in a tabular format (e.g., a table cell),
               which contains information about an edge and its corresponding weight.

        """
        weight = str_to_int_or_float(item.text())
        if isinstance(self.hypergraph, DirectedHypergraph):
            edge_src = str_to_tuple(self.item(item.row(), 0).text())
            edge_trg = str_to_tuple(self.item(item.row(), 1).text())
            edge = (edge_src, edge_trg)
            self.hypergraph.set_weight(edge, weight)
        elif isinstance(self.hypergraph, TemporalHypergraph):
            row = item.row()
            edge = str_to_tuple(self.item(row, 0).text())
            time = int(self.item(row, 1).text())
            self.hypergraph.set_weight(set(edge), time, weight)
        else:
            edge = list(str_to_tuple(self.itemAt(item.row(), 0).text()))
            self.hypergraph.set_weight(edge, weight)

    def __modify_time(self, item):
        """
        Modifies the time of an edge in the temporal hypergraph and updates the associated table.

        Parameters
        ----------
        item : QTableWidgetItem
            The table widget item that contains the new time value and refers to the edge being modified.
        """
        time = int(item.text())
        edge = str_to_tuple(self.item(item.row(), 0).text())
        self.removeRow(item.row())
        self.hypergraph.add_edge(edge, time)
        self.update_table(self.hypergraph)
        self.update_status.emit({})

    def __modify_metadata(self, item):
        text = item.text()
        val = str_to_dict(text)
        if val == {}:
            txt = self.old_values[item.row(), item.column()]
        else:
            txt = str(val)
            self.old_values[item.row(), item.column()] = txt
        self.last_changes = not self.last_changes
        item.setText(txt)
        if self.use_nodes:
            node_str = self.item(item.row(), 0).text()
            node = str_to_int_or_float(node_str)
            self.hypergraph.set_node_metadata(node, val)
        else:
            if isinstance(self.hypergraph, DirectedHypergraph):
                edge_src = str_to_tuple(self.item(item.row(), 0).text())
                edge_trg = str_to_tuple(self.item(item.row(), 1).text())
                edge = (edge_src, edge_trg)
                if self.hypergraph.is_weighted():
                    val["weight"] = self.hypergraph.get_weight(edge)
                self.hypergraph.set_edge_metadata(edge, val)
            elif isinstance(self.hypergraph, TemporalHypergraph):
                row = item.row()
                edge = str_to_tuple(self.item(row, 0).text())
                time = int(self.item(row, 1).text())
                if self.hypergraph.is_weighted():
                    val["weight"] = self.hypergraph.get_weight(edge, time)
                val["time"] = time
                self.hypergraph.set_edge_metadata(edge, time, val)
            else:
                edge = str_to_tuple(self.item(item.row(), 0).text())
                if self.hypergraph.is_weighted():
                    val["weight"] = self.hypergraph.get_weight(edge)
                self.hypergraph.set_edge_metadata(edge, val)