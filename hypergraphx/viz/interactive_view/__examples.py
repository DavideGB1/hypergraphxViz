from copy import deepcopy
from copy import deepcopy

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from hypergraphx import Hypergraph, DirectedHypergraph


def examples_generator():
    examples = dict()
    widgets = list()
    normal = Hypergraph([(1,2,3),(4,5,6),(6,7,8,9),(10,11,12,1,4),(4,1),(3,6)])
    examples["Normal"] = normal
    directed = DirectedHypergraph()
    directed.add_edge(((1,2),(3,4)))
    directed.add_edge(((5,6,7,8), (10,3, 4)))
    directed.add_edge(((4,5,6),(6,7,8,9)))
    directed.add_edge(((1,), (8,9)))
    examples["Directed"] = directed
    weighted = Hypergraph(weighted=True)
    weighted.add_edge((1,2,3),12)
    weighted.add_edge((4,5,6),3)
    weighted.add_edge((6,7,8,9),1)
    weighted.add_edge((10,11,12,1,4),5)
    weighted.add_edge((4,1),1)
    weighted.add_edge((3,6),7)
    examples["Weighted"] = weighted
    for (k,v) in examples.items():
        widgets.append(PushButtonExamples(k,v))

    return widgets

class PushButtonExamples(QWidget):
    new_hypergraph = pyqtSignal(dict)
    def __init__(self, name, hypergraph, parent = None):
        super(PushButtonExamples, self).__init__()
        self.layout = QHBoxLayout()
        self.button = QPushButton(name)
        self.layout.addWidget(self.button)
        def update():
            print("esisto")
            self.new_hypergraph.emit({ "hypergraph": deepcopy(hypergraph)})
        self.button.clicked.connect(update)
        self.setLayout(self.layout)
