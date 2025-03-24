from copy import deepcopy
from PyQt5.QtWidgets import QAction
from hypergraphx import Hypergraph, DirectedHypergraph, TemporalHypergraph


def examples_generator():
    examples = dict()
    normal = Hypergraph([(1,2,3),(4,5,6),(6,7,8,9),(10,11,12,1,4),(4,1),(3,6)])
    examples["Normal"] = normal
    weighted = Hypergraph(weighted=True)
    weighted.add_edge((1,2,3),12)
    weighted.add_edge((4,5,6),3)
    weighted.add_edge((6,7,8,9),1)
    weighted.add_edge((10,11,12,1,4),5)
    weighted.add_edge((4,1),1)
    weighted.add_edge((3,6),7)
    examples["Weighted"] = weighted

    directed = DirectedHypergraph()
    directed.add_edge(((1,2),(3,4)))
    directed.add_edge(((5,6,7,8), (10,3, 4)))
    directed.add_edge(((4,5,6),(6,7,8,9)))
    directed.add_edge(((1,), (8,9)))
    examples["Directed"] = directed

    weighted_directed = DirectedHypergraph(weighted=True)
    weighted_directed.add_edge(((1, 2), (3, 4)),1)
    weighted_directed.add_edge(((5, 6, 7, 8), (10, 3, 4)),5)
    weighted_directed.add_edge(((4, 5, 6), (6, 7, 8, 9)),13)
    weighted_directed.add_edge(((1,), (8, 9)),2)
    examples["Directed Weighted"] = weighted_directed


    temporal = TemporalHypergraph()
    temporal.add_edge((1, 2, 3), 1)
    temporal.add_edge((4, 5, 6), 1)
    temporal.add_edge((6, 7, 8, 9), 1)
    temporal.add_edge((1, 2), 2)
    temporal.add_edge((4, 5, 6,3), 2)
    temporal.add_edge((6, 7, 8, 9,1), 2)
    temporal.add_edge((1, 2,5), 3)
    temporal.add_edge((4, 5, 6, 3,9), 3)
    temporal.add_edge((6, 7, 8), 3)
    examples["Temporal"] = temporal

    temporal = TemporalHypergraph(weighted=True)
    temporal.add_edge((1, 2, 3), 1,13)
    temporal.add_edge((4, 5, 6), 1,34)
    temporal.add_edge((6, 7, 8, 9), 1,3)
    temporal.add_edge((1, 2), 2,12)
    temporal.add_edge((4, 5, 6, 3), 2,87)
    temporal.add_edge((6, 7, 8, 9, 1), 2,6)
    temporal.add_edge((1, 2, 5), 3,9)
    temporal.add_edge((4, 5, 6, 3, 9), 3,1)
    temporal.add_edge((6, 7, 8), 3,2)
    examples["Temporal Weighted"] = temporal
    actions = list()
    for k,v in examples.items():
        action = QExampleAction(k,v)
        actions.append(action)
    return actions

class QExampleAction(QAction):
    def __init__(self, name,hypergraph, parent=None):
        super(QExampleAction, self).__init__(parent)
        self.setText(name)
        self.hypergraph = deepcopy(hypergraph)
    def return_hypergraph(self):
        return deepcopy(self.hypergraph)
