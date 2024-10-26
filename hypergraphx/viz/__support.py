import inspect
import math
from math import trunc

from hypergraphx import Hypergraph
from matplotlib import pyplot as plt


def __check_edge_intersection(set1, set2):
    """
    Check if two sets overlaps.
    Parameters
    ----------
        set1 : Set.
        set2 : Set.
    Returns
    -------
        res : Bool
    """
    set1 = sorted(set1)
    set2 = sorted(set2)
    res = False
    for x in set2:
        if set1[0] <= x <= set1[-1]:
            res = True
            break

    return res

def __draw_line(layout, palette : list, path : list, i:int, idx: int, passo: int, ax : plt.Axes) -> None:
    """
    Draw the metro line of the node.
    Parameters
    ----------
        layout : dict
            Position of all the nodes in the 2D plane.
        palette : list
            A list of colors.
        path : list
            The path to draw.
        i : int
            Current path's node.
        idx : int
            Path identifier used to choose the color.
        passo : int
            value used to determine where to place the line.
        ax : plt.Axes
            Axes of the Image.
    Returns
    -------
    """
    offset = (passo * 3)
    pos = __find_pos(layout, path[i], path[i + 1])
    if pos == "vertical":
        ax.plot([layout[path[i]][0]+ offset, layout[path[i + 1]][0] + offset],
             [layout[path[i]][1], layout[path[i + 1]][1]], linewidth=1,
             color=palette[idx])
    elif pos == "horizontal":
        ax.plot([layout[path[i]][0], layout[path[i + 1]][0]],
                 [layout[path[i]][1] + offset, layout[path[i + 1]][1] + offset], linewidth=1,
                 color=palette[idx])
    elif pos == "oblique":
        ax.plot([layout[path[i]][0] + offset, layout[path[i + 1]][0] + offset],
                 [layout[path[i]][1] + offset, layout[path[i + 1]][1] + offset], linewidth=1,
                 color=palette[idx])

def __calculate_incidence(node : [int | str | tuple], edges : list[list]) -> set:
    """
    Return the number of edges incident to a node.
    Parameters
    ----------
        node : int|str|tuple.
        edges : list.
    Returns
    -------
        incident_edges : set
    """
    if type(node) is tuple:
        node = set(node)
    else:
        node = {node}
    incident_edges = set()
    for edge in edges:
        edge = set(edge)
        if len(edge.intersection(node)) > 0:
            incident_edges.add(tuple(edge))

    return incident_edges
def __distance(layout, node1, node2):
    """
    Given a layout, return the euclidian distance between two nodes.
    Parameters
    ----------
        layout : dict
        node1 : int|str|tuple.
        node2 : int|str|tuple.
    Returns
    -------
        res : float
    """
    x1, y1 = layout[node1]
    x2, y2 = layout[node2]
    return ((x1 - x2)**2 + (y1-y2)**2)**(1/2)
def __find_pos(layout, node1, node2):
    """
    Given a layout, tells if the two nodes are arranged vertically or not.
    Parameters
    ----------
        layout : dict
        node1 : int|str|tuple.
        node2 : int|str|tuple.
    Returns
    -------
        res : str
    """
    x1, y1 = layout[node1]
    x2, y2 = layout[node2]

    if trunc(x1) == trunc(x2):
        return "vertical"
    else:
        return "horizontal"

def x_heaviest_edges_hypergraph(h, x_heaviest):
    edge_list = h.get_edges()
    weight_dict = dict()
    for edge in edge_list:
        weight_dict[edge] = h.get_weight(edge)
    weight_list = weight_dict.values()
    weight_list = sorted(weight_list, reverse=True)
    num_weights = int(math.ceil(len(weight_list) * x_heaviest))
    weight_list = weight_list[:num_weights]
    hypergraph = Hypergraph(weighted=True)
    for node in h.get_nodes():
        hypergraph.add_node(node)
    key_list = list(weight_dict.keys())
    for weight in weight_list:
        hypergraph.add_edge(key_list[weight_list.index(weight)], weight)

    return hypergraph

def cardinality_hypergraph(h, cardinality):
    if h.is_weighted():
        hypergraph = Hypergraph(weighted=True)
    else:
        hypergraph = Hypergraph()
    for node in h.get_nodes():
        hypergraph.add_node(node)
    if isinstance(cardinality, tuple):
        for edge in h.get_edges():
            if cardinality[0] <= len(edge) <= cardinality[1]:
                if h.is_weighted():
                    hypergraph.add_edge(edge, h.get_weight(edge))
                else:
                    hypergraph.add_edge(edge)
    else:
        for edge in h.get_edges():
            if len(edge) == cardinality:
                if h.is_weighted():
                    hypergraph.add_edge(edge, h.get_weight(edge))
                else:
                    hypergraph.add_edge(edge)
    return hypergraph

def filter_hypergraph(h, cardinality, x_heaviest):
    if cardinality != -1:
        hypergraph = cardinality_hypergraph(h, cardinality)
    else:
        hypergraph = h
    if x_heaviest != 1.0:
        if hypergraph.is_weighted():
            hypergraph = x_heaviest_edges_hypergraph(hypergraph, x_heaviest)
    else:
        pass

    return hypergraph

def ignore_unused_args(func):
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return func(*args, **kwargs)

    return wrapper
