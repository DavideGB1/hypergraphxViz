from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QTableWidget, QHeaderView, QTableWidgetItem
from hypergraphx import DirectedHypergraph, TemporalHypergraph
from hypergraphx.viz.interactive_view.support import str_to_dict, str_to_int_or_float, str_to_tuple


class ReadOnlyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return

class ValidationDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            validator = QDoubleValidator(-10000000, 10000000,6, editor)
            editor.setValidator(validator)
        return editor

class HypergraphTable(QTableWidget):
    update_status = pyqtSignal(dict)
    def __init__(self, hypergraph, nodes = True  ):
        super(HypergraphTable, self).__init__()
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
        self.itemChanged.connect(self.__check_new_cell_value)

    def remove_row(self):
        self.removeRow(self.currentRow())

    def update_table(self, hypergraph):
        self.hypergraph = hypergraph
        self.loading = True
        if self.use_nodes:
            self.__update_table_nodes(hypergraph)
        else:
            self.__update_table_edges(hypergraph)
        self.loading = False

    def __update_table_nodes(self, hypergraph):
        num_row = hypergraph.num_nodes()
        num_col = 2
        self.metadata_col = 1
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        if self.use_nodes:
            self.setHorizontalHeaderLabels(['Name', 'Metadata'])
        curr_row = 0
        for node in hypergraph.get_nodes():
            metadata = hypergraph.get_node_metadata(node)
            if metadata is None:
                metadata = {}
            self.setItem(curr_row, 0, QTableWidgetItem(str(node)))
            self.setItem(curr_row, 1, QTableWidgetItem(str(metadata)))
            self.old_values[curr_row,1] = str(metadata)
            curr_row += 1

    def __update_table_edges(self, hypergraph):
        num_row = hypergraph.num_edges()
        config = self.__get_hypergraph_config(hypergraph)
        num_col = config["num_col"]
        idx = config["idx"]
        self.weight_col = config["weight_col"]
        self.metadata_col = config["metadata_col"]
        col_names = config["col_names"]
        if hypergraph.is_weighted():
            num_col += 1
            idx += 1
            self.weight_col += 1
            self.metadata_col += 1
            col_names.insert(idx, "Weight")
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        self.setHorizontalHeaderLabels(col_names)

        curr_row = 0
        for edge in hypergraph.get_edges():
            self.__set_edge_items(curr_row, edge)
            self.__update_weight_and_delegate(curr_row, edge)
            self.__update_metadata(curr_row, edge)
            curr_row += 1

    def __get_hypergraph_config(self, hypergraph):
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
        if self.hypergraph.is_weighted():
            if isinstance(self.hypergraph, TemporalHypergraph):
                weight = self.hypergraph.get_weight(edge[1], edge[0])
            else:
                weight = self.hypergraph.get_weight(edge)
            self.setItem(row, self.weight_col, QTableWidgetItem(str(weight)))
            self.setItemDelegateForColumn(self.weight_col, ValidationDelegate(self))

    def __update_metadata(self, row, edge):
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
        if self.loading:
            return
        if self.last_changes:
            self.last_changes = not self.last_changes
            return
        if item.column() == self.metadata_col:
            self.__modify_metadata(item)
        if item.column() == self.weight_col and self.hypergraph.is_weighted():
            self.__modify_weight(item)
        if item.column() == 1 and isinstance(self.hypergraph, TemporalHypergraph):
            self.__modify_time(item)
        self.update_status.emit({})

    def __modify_weight(self, item):
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
        time = int(item.text())
        edge = str_to_tuple(self.item(item.row(), 0).text())
        self.removeRow(item.row())
        self.hypergraph.add_edge(edge, time)
        self.update_table(self.hypergraph)
        self.update_status.emit({})

    def __modify_metadata(self, item):
        text = item.text()
        val = str_to_dict(text)
        txt = ""
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
                self.hypergraph.set_edge_metadata(edge, val)
            elif isinstance(self.hypergraph, TemporalHypergraph):
                row = item.row()
                edge = str_to_tuple(self.item(row, 0).text())
                time = int(self.item(row, 1).text())
                self.hypergraph.set_edge_metadata(edge, time, val)
            else:
                edge = str_to_tuple(self.item(item.row(), 0).text())
                self.hypergraph.set_edge_metadata(edge, val)