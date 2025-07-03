from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem

from hypergraphx.utils.cc import connected_components


class ConnectedComponentsTable(QTableWidget):
    """
    QTableWidget with custom functions ad allows to modify the hypergraph.
    """
    update_status = pyqtSignal(dict)
    def __init__(self, hypergraph, parent = None):
        super(ConnectedComponentsTable, self).__init__(parent)
        self.hypergraph = hypergraph
        self.components = None
        self.set_hypergraph(hypergraph)
        # Table will fit the screen horizontally
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def set_hypergraph(self, hypergraph):
        """
        Updates the table with data from the provided hypergraph object.

        Parameters
        ----------
        hypergraph : obj
            The hypergraph object containing updated data to refresh the table.

        """
        self.clear()
        self.hypergraph = hypergraph
        self.components = connected_components(self.hypergraph)
        self.setRowCount(len(self.components))
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Component', 'In Use:'])
        curr_row = 0
        for component in self.components:
            self.setItem(curr_row, 0, QTableWidgetItem(str(component)))
            chkBoxItem = QTableWidgetItem("")
            chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            chkBoxItem.setCheckState(QtCore.Qt.Checked)
            chkBoxItem.setTextAlignment(QtCore.Qt.AlignCenter)

            self.setItem(curr_row, 1, chkBoxItem)
            curr_row += 1