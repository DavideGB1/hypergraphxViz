from copy import deepcopy
from PyQt5.QtWidgets import QAction
from hypergraphx import Hypergraph, DirectedHypergraph, TemporalHypergraph


def examples_generator():
    """
    Generate example hypergraphs and actions associated with them.

    This function creates and returns a list of `QExampleAction` instances, each
    representing a specific type of hypergraph (e.g., normal, weighted, directed,
    temporal, etc.). The hypergraphs constructed within this function include weighted
    and unweighted, directed and undirected, as well as temporal variants.

    Returns
    -------
    list of QExampleAction
        A list of `QExampleAction` instances, with each action corresponding to a specific
        type of hypergraph.

    Hypergraph Types Included
    -------------------------
    - Normal Hypergraph
    - Weighted Hypergraph
    - Directed Hypergraph (Weighted and Unweighted)
    - Temporal Hypergraph (Weighted and Unweighted)
    """
    examples = dict()
    normal = Hypergraph(
        [(1,2,3),(4,5,6),(6,7,8,9),(10,11,12,1,4),(4,1),(3,6)],
        weighted=False
    )

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
    """
        A QAction subclass that encapsulates an action with an associated hypergraph.

        Parameters
        ----------
        name : str
            The text label for the action.
        hypergraph : object
            A hypergraph object that is deep-copied and associated with the action.
        parent : QObject, optional
            The parent object for the action. Default is None.

        Methods
        -------
        return_hypergraph()
            Returns a deep copy of the associated hypergraph.
    """
    def __init__(self, name,hypergraph, parent=None):
        super(QExampleAction, self).__init__(parent)
        self.setText(name)
        self.hypergraph = deepcopy(hypergraph)
    def return_hypergraph(self):
        return self.hypergraph.copy()
