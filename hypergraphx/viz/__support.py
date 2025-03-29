import inspect
import math
import colorcet as cc
from math import trunc
from typing import Tuple
import matplotlib
import numpy as np
import seaborn as sns
from hypergraphx import Hypergraph, DirectedHypergraph, TemporalHypergraph
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
    if set1[0]<set2[0] and set1[1]>set2[1]:
        set1, set2 = set2, set1
    for x in set1:
        if set2[0] <= x <= set2[-1]:
            return True

    return False
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
def __x_heaviest_edges_hypergraph(
        h: Hypergraph | DirectedHypergraph | TemporalHypergraph,
        x_heaviest: float
    ) -> Hypergraph | DirectedHypergraph | TemporalHypergraph:
    """
    Returns an hypergraph with only the x% heaviest edges.
    Parameters
    ----------
    h: Hypergraph
        The hypergraph to manipulate.
    x_heaviest: float
        % value used to determine the top x% heaviest edges to take.
    Returns
    -------
        hypergraph: Hypergraph
    """
    if h.is_weighted():
        hypergraph = h.copy()
        edge_list = hypergraph.get_edges()
        weight_dict = dict()
        for edge in edge_list:
            weight_dict[edge] = hypergraph.get_weight(edge)
        edge_list = [(edge, weight_dict[edge]) for edge in edge_list]
        edge_list = sorted(edge_list, key=lambda tup: tup[1], reverse=True)
        num_weights = int(math.ceil(len(edge_list) * x_heaviest))
        edges_to_maintain = edge_list[:num_weights]
        edges_to_maintain = [edge[0] for edge in edges_to_maintain]
        edge_list = hypergraph.get_edges()
        for edge in edge_list:
            if edge not in edges_to_maintain:
                hypergraph.remove_edge(edge)
        return hypergraph
    else:
        return h

def __cardinality_hypergraph(
        h: Hypergraph | TemporalHypergraph | DirectedHypergraph,
        cardinality: int | tuple[int,int]
    ) -> Hypergraph | TemporalHypergraph | DirectedHypergraph:
    """
    Returns an hypergraph with only the edges of the desired cardinality.
    Parameters
    ----------
    h: Hypergraph | TemporalHypergraph | DirectedHypergraph
        The hypergraph to manipulate.
    cardinality: int | tuple[int,int]
        The cardinality to respect. It can be and int or a [a,b] set.
    Returns
    -------
        hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph
    """
    hypergraph = h.copy()
    edge_list = hypergraph.get_edges()
    if isinstance(cardinality, tuple):
        for edge in edge_list:
            if not (cardinality[0] <= len(edge) <= cardinality[1]):
                hypergraph.remove_edge(edge)
    else:
        for edge in edge_list:
            if not (len(edge) == cardinality):
                hypergraph.remove_edge(edge)
    return hypergraph

def __filter_hypergraph(
        h: Hypergraph | TemporalHypergraph | DirectedHypergraph,
        cardinality: int | tuple[int,int],
        x_heaviest: float
    ) -> Hypergraph | TemporalHypergraph | DirectedHypergraph:
    """
    Filters and hypergraph using the parameters.
    Parameters
    ----------
    h: Hypergraph | TemporalHypergraph | DirectedHypergraph
        The hypergraph to manipulate.
    cardinality: int | tuple[int,int]
        The cardinality to respect. It can be and int or a [a,b] set.
    x_heaviest: float
        % value used to determine the top x% heaviest edges to take.
    Returns
    -------
    hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph
    """
    if cardinality != -1:
        hypergraph = __cardinality_hypergraph(h, cardinality)
    else:
        hypergraph = h
    if x_heaviest != 1.0:
        if hypergraph.is_weighted():
            hypergraph = __x_heaviest_edges_hypergraph(hypergraph, x_heaviest)
    else:
        pass
    return hypergraph
def __ignore_unused_args(func):
    """
    Removes unused arguments from a function call.
    """
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return func(*args, **kwargs)

    return wrapper

def __support_to_normal_hypergraph(
        directe_hg: DirectedHypergraph
    ) -> tuple[Hypergraph, dict]:
    """
    Given a directed Hypergraph returns a normal hypergraph with a mapping to the edge directions.
    Parameters
    ----------
    directe_hg: DirectedHypergraph
    Returns
    -------
    new_hypergraph: Hypergraph
    edge_directed_mapping: dict
    """
    orginal_edges = directe_hg.get_edges()
    new_hypergraph = Hypergraph(weighted=directe_hg.is_weighted())
    edge_directed_mapping = dict()
    for edge in orginal_edges:
        compressed_edge = []
        for node in edge[0]:
            compressed_edge.append(node)
        for node in edge[1]:
            compressed_edge.append(node)
        edge_directed_mapping[tuple(sorted(compressed_edge))] = edge
        if tuple(sorted(compressed_edge)) not in new_hypergraph.get_edges():
            new_hypergraph.add_edge(compressed_edge)
            new_hypergraph.set_weight(compressed_edge, directe_hg.get_weight(edge))
        else:
            new_hypergraph.set_edge_metadata(compressed_edge, "I/O")
    return new_hypergraph, edge_directed_mapping

def extract_pie_properties(
    i: int, u: np.array, colors: dict, threshold: float = 0.1
) -> Tuple[np.array, np.array]:
    """Given a node, it extracts the wedge sizes and the respective colors for the pie chart
    that represents its membership.

    Parameters
    ----------
    i: node id.
    u: membership matrix.
    colors: dictionary of colors, where key represent the group id and values are colors.
    threshold: threshold for node membership.

    Returns
    -------
    wedge_sizes: wedge sizes.
    wedge_colors: sequence of colors through which the pie chart will cycle.
    """
    valid_groups = np.where(u[i] > threshold)[0]
    wedge_sizes = u[i][valid_groups]
    wedge_colors = [colors[k] for k in valid_groups]
    return wedge_sizes, wedge_colors

def _draw_node_community(ax, node, center, ratios, colors, graphicOptions,scale=17,**kwargs):
    if len(ratios) > 1:
        if len(ratios) != len(colors):
            raise ValueError("Number of ratios and colors must be equal.")

        cumulative_ratio = 0
        for i, ratio in enumerate(ratios):
            start_angle = cumulative_ratio
            end_angle = cumulative_ratio + ratio

            x_vals = np.cos(2 * np.pi * np.linspace(start_angle, end_angle))
            y_vals = np.sin(2 * np.pi * np.linspace(start_angle, end_angle))
            xy = np.row_stack([[0, 0], np.column_stack([x_vals, y_vals])])

            ax.plot(center[0], center[1], marker=xy, ms=graphicOptions.node_size[node]/scale, markerfacecolor=colors[i],
                    markeredgecolor=graphicOptions.node_facecolor[node])

            cumulative_ratio = end_angle
    else:
        ax.plot(center[0], center[1],
                marker=graphicOptions.node_shape[node],
                color=colors[0],
                markeredgecolor=graphicOptions.node_facecolor[node],
                markersize=graphicOptions.node_size[node] / scale, **kwargs)


def _get_community_info(hypergraph, p = 2,col=None,):
    _, mappingID2Name = hypergraph.binary_incidence_matrix(return_mapping=True)
    mappingName2ID = {n: i for i, n in mappingID2Name.items()}
    if col is None:
        cmap = sns.color_palette(cc.glasbey, n_colors=p)
        col = {k: matplotlib.colors.to_hex(cmap[k], keep_alpha=False) for k in np.arange(p)}
    return mappingName2ID, col
def _get_node_community(mappingName2ID, node, u, col,threshold ):
    wedge_sizes, wedge_colors = extract_pie_properties(
        mappingName2ID[node], u, col, threshold=threshold
    )
    return wedge_sizes, wedge_colors