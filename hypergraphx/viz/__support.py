import collections
import inspect
import itertools
import math
import colorcet as cc
from math import trunc
from typing import Tuple
import matplotlib
import networkx as nx
import numpy as np
import seaborn as sns
from networkx.drawing.nx_pylab import FancyArrowFactory

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

import matplotlib as mpl
class CurvedArrowText(mpl.text.Text):
    """
    Clone of CurvedArrowText. Needed in other to avoid a problem if multiprocessing
    """
    def __init__(
        self,
        arrow,
        *args,
        label_pos=0.5,
        labels_horizontal=False,
        ax=None,
        **kwargs,
    ):
        # Bind to FancyArrowPatch
        self.arrow = arrow
        # how far along the text should be on the curve,
        # 0 is at start, 1 is at end etc.
        self.label_pos = label_pos
        self.labels_horizontal = labels_horizontal
        if ax is None:
            ax = plt.gca()
        self.ax = ax
        self.x, self.y, self.angle = self._update_text_pos_angle(arrow)

        # Create text object
        super().__init__(self.x, self.y, *args, rotation=self.angle, **kwargs)
        # Bind to axis
        self.ax.add_artist(self)

    def _get_arrow_path_disp(self, arrow):
        """
        This is part of FancyArrowPatch._get_path_in_displaycoord
        It omits the second part of the method where path is converted
            to polygon based on width
        The transform is taken from ax, not the object, as the object
            has not been added yet, and doesn't have transform
        """
        dpi_cor = arrow._dpi_cor
        # trans_data = arrow.get_transform()
        trans_data = self.ax.transData
        if arrow._posA_posB is not None:
            posA = arrow._convert_xy_units(arrow._posA_posB[0])
            posB = arrow._convert_xy_units(arrow._posA_posB[1])
            (posA, posB) = trans_data.transform((posA, posB))
            _path = arrow.get_connectionstyle()(
                posA,
                posB,
                patchA=arrow.patchA,
                patchB=arrow.patchB,
                shrinkA=arrow.shrinkA * dpi_cor,
                shrinkB=arrow.shrinkB * dpi_cor,
            )
        else:
            _path = trans_data.transform_path(arrow._path_original)
        # Return is in display coordinates
        return _path

    def _update_text_pos_angle(self, arrow):
        # Fractional label position
        path_disp = self._get_arrow_path_disp(arrow)
        (x1, y1), (cx, cy), (x2, y2) = path_disp.vertices
        # Text position at a proportion t along the line in display coords
        # default is 0.5 so text appears at the halfway point
        t = self.label_pos
        tt = 1 - t
        x = tt**2 * x1 + 2 * t * tt * cx + t**2 * x2
        y = tt**2 * y1 + 2 * t * tt * cy + t**2 * y2
        if self.labels_horizontal:
            # Horizontal text labels
            angle = 0
        else:
            # Labels parallel to curve
            change_x = 2 * tt * (cx - x1) + 2 * t * (x2 - cx)
            change_y = 2 * tt * (cy - y1) + 2 * t * (y2 - cy)
            angle = (np.arctan2(change_y, change_x) / (2 * np.pi)) * 360
            # Text is "right way up"
            if angle > 90:
                angle -= 180
            if angle < -90:
                angle += 180
        (x, y) = self.ax.transData.inverted().transform((x, y))
        return x, y, angle

    def draw(self, renderer):
        # recalculate the text position and angle
        self.x, self.y, self.angle = self._update_text_pos_angle(self.arrow)
        self.set_position((self.x, self.y))
        self.set_rotation(self.angle)
        # redraw text
        super().draw(renderer)


def draw_networkx_edge_labels_clone(
    G,
    pos,
    edge_labels=None,
    label_pos=0.5,
    font_size=10,
    font_color="k",
    font_family="sans-serif",
    font_weight="normal",
    alpha=None,
    bbox=None,
    horizontalalignment="center",
    verticalalignment="center",
    ax=None,
    rotate=True,
    clip_on=True,
    node_size=300,
    nodelist=None,
    connectionstyle="arc3",
    hide_ticks=True,
):
    """
    Clone of draw_networkx_edge_labels_clone without the internal class CurvedArrowText. Needed in other to avoid a problem if multiprocessing
    """

    # use default box of white with white border
    if bbox is None:
        bbox = {"boxstyle": "round", "ec": (1.0, 1.0, 1.0), "fc": (1.0, 1.0, 1.0)}

    if isinstance(connectionstyle, str):
        connectionstyle = [connectionstyle]
    elif np.iterable(connectionstyle):
        connectionstyle = list(connectionstyle)
    else:
        raise nx.NetworkXError(
            "draw_networkx_edges arg `connectionstyle` must be"
            "string or iterable of strings"
        )

    if ax is None:
        ax = plt.gca()

    if edge_labels is None:
        kwds = {"keys": True} if G.is_multigraph() else {}
        edge_labels = {tuple(edge): d for *edge, d in G.edges(data=True, **kwds)}
    # NOTHING TO PLOT
    if not edge_labels:
        return {}
    edgelist, labels = zip(*edge_labels.items())

    if nodelist is None:
        nodelist = list(G.nodes())

    # set edge positions
    edge_pos = np.asarray([(pos[e[0]], pos[e[1]]) for e in edgelist])

    if G.is_multigraph():
        key_count = collections.defaultdict(lambda: itertools.count(0))
        edge_indices = [next(key_count[tuple(e[:2])]) for e in edgelist]
    else:
        edge_indices = [0] * len(edgelist)

    # Used to determine self loop mid-point
    # Note, that this will not be accurate,
    #   if not drawing edge_labels for all edges drawn
    h = 0
    if edge_labels:
        miny = np.amin(np.ravel(edge_pos[:, :, 1]))
        maxy = np.amax(np.ravel(edge_pos[:, :, 1]))
        h = maxy - miny
    selfloop_height = h if h != 0 else 0.005 * np.array(node_size).max()
    fancy_arrow_factory = FancyArrowFactory(
        edge_pos,
        edgelist,
        nodelist,
        edge_indices,
        node_size,
        selfloop_height,
        connectionstyle,
        ax=ax,
    )

    individual_params = {}

    def check_individual_params(p_value, p_name):
        if isinstance(p_value, list):
            if len(p_value) != len(edgelist):
                raise ValueError(f"{p_name} must have the same length as edgelist.")
            individual_params[p_name] = p_value.iter()

    # Don't need to pass in an edge because these are lists, not dicts
    def get_param_value(p_value, p_name):
        if p_name in individual_params:
            return next(individual_params[p_name])
        return p_value

    check_individual_params(font_size, "font_size")
    check_individual_params(font_color, "font_color")
    check_individual_params(font_weight, "font_weight")
    check_individual_params(alpha, "alpha")
    check_individual_params(horizontalalignment, "horizontalalignment")
    check_individual_params(verticalalignment, "verticalalignment")
    check_individual_params(rotate, "rotate")
    check_individual_params(label_pos, "label_pos")

    text_items = {}
    for i, (edge, label) in enumerate(zip(edgelist, labels)):
        if not isinstance(label, str):
            label = str(label)  # this makes "1" and 1 labeled the same

        n1, n2 = edge[:2]
        arrow = fancy_arrow_factory(i)
        if n1 == n2:
            connectionstyle_obj = arrow.get_connectionstyle()
            posA = ax.transData.transform(pos[n1])
            path_disp = connectionstyle_obj(posA, posA)
            path_data = ax.transData.inverted().transform_path(path_disp)
            x, y = path_data.vertices[0]
            text_items[edge] = ax.text(
                x,
                y,
                label,
                size=get_param_value(font_size, "font_size"),
                color=get_param_value(font_color, "font_color"),
                family=get_param_value(font_family, "font_family"),
                weight=get_param_value(font_weight, "font_weight"),
                alpha=get_param_value(alpha, "alpha"),
                horizontalalignment=get_param_value(
                    horizontalalignment, "horizontalalignment"
                ),
                verticalalignment=get_param_value(
                    verticalalignment, "verticalalignment"
                ),
                rotation=0,
                transform=ax.transData,
                bbox=bbox,
                zorder=1,
                clip_on=clip_on,
            )
        else:
            text_items[edge] = CurvedArrowText(
                arrow,
                label,
                size=get_param_value(font_size, "font_size"),
                color=get_param_value(font_color, "font_color"),
                family=get_param_value(font_family, "font_family"),
                weight=get_param_value(font_weight, "font_weight"),
                alpha=get_param_value(alpha, "alpha"),
                horizontalalignment=get_param_value(
                    horizontalalignment, "horizontalalignment"
                ),
                verticalalignment=get_param_value(
                    verticalalignment, "verticalalignment"
                ),
                transform=ax.transData,
                bbox=bbox,
                zorder=1,
                clip_on=clip_on,
                label_pos=get_param_value(label_pos, "label_pos"),
                labels_horizontal=not get_param_value(rotate, "rotate"),
                ax=ax,
            )

    if hide_ticks:
        ax.tick_params(
            axis="both",
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )

    return text_items