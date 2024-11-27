from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
from fa2_modified import ForceAtlas2
from networkx import is_planar, planar_layout, kamada_kawai_layout

from hypergraphx import Hypergraph
from hypergraphx.representations.projections import (
    bipartite_projection,
    clique_projection, extra_node_projection,
)


def draw_bipartite(h: Hypergraph, pos=None, ax=None, align='vertical', **kwargs):
    """
    Draws a bipartite graph representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    align : str.
        The alignment of the nodes. Can be 'vertical' or 'horizontal'.
    Returns
    -------
    ax : matplotlib.axes.Axes.
        The axes the graph was drawn on.
    """
    g, id_to_obj = bipartite_projection(h)

    if pos is None:
        pos = nx.bipartite_layout(g, nodes=[n for n, d in g.nodes(data=True) if d['bipartite'] == 0])

    if ax is None:
        ax = plt.gca()

    nx.draw_networkx(g, pos=pos, ax=ax, **kwargs)
    plt.show()
    return ax


def draw_clique(
    h: Hypergraph,
    pos=None,
    ax: Optional[plt.Axes] = None,
    iterations: int = 1000,
    strong_gravity: bool = True,
    draw_labels=True,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    node_shape: str = "o",
    node_color: str = "#1f78b4",
    node_size: int = 300,
    edge_color: str = "#000000",
    edge_width: float = 2,
    **kwargs) -> None:
    """
    Draws a clique projection of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    iterations : int
        The number of iterations to run the position algorithm.
    strong_gravity : bool
        Decide if the ForceAtlas2 Algorithm must use strong gravity or no.
    draw_labels : bool
        Decide if the labels should be drawn.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    node_shape : str, optional
        The shape of the nodes in the image. Use standard MathPlotLib values.
    node_color : str, optional
        HEX value for the nodes color.
    node_size : int, optional
        The size of the nodes in the image.
    edge_color : str, optional
        HEX value for the edges color.
    edge_width : float, optional
        Width of the edges in the grid.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    Returns
    -------
    ax : matplotlib.axes.Axes. The axes the graph was drawn on.
    """
    g = clique_projection(h)

    forceatlas2 = ForceAtlas2(
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED
        scalingRatio=2.0,
        strongGravityMode=strong_gravity,
        gravity=1.0,
        verbose=True)

    if pos is None:
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, iterations=iterations, weight_attr="weight")
    else:
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, pos=pos,iterations=iterations, weight_attr="weight")

    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    labels = dict((n, n) for n in g.nodes())

    nx.draw_networkx_edges(G=g, pos=pos, ax=ax,edge_color=edge_color, width=edge_width)
    nx.draw_networkx_nodes(G=g, pos=pos, ax=ax, node_color=node_color, node_size=node_size, node_shape=node_shape)
    if draw_labels:
        nx.draw_networkx_labels(G=g, pos=pos, ax=ax, labels=labels)

    plt.axis('off')
    ax.axis('off')
    ax.set_aspect('equal')
    ax.autoscale(enable=True, axis='both')
    plt.autoscale(enable=True, axis='both')

def draw_extra_node(
    h: Hypergraph,
    pos=None,
    ax=None,
    ignore_binary_relations: bool = True,
    show_edge_nodes=True,
    strong_gravity: bool = True,
    draw_labels: bool = True,
    iterations: int = 1000,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    node_shape: str = "o",
    node_color: str = "#1f78b4",
    node_size: int = 300,
    edge_shape: str = 'p',
    edge_node_color: str = '#8a0303',
    edge_color: str = "#000000",
    edge_width: float = 2,
    **kwargs) -> None:
    """
    Draws an extra-node projection of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    ignore_binary_relations : bool
        Decide if the function should show nodes that are only in binary relations.
    show_edge_nodes : bool
        Decide if the function should draw nodes in the conjunction point of the hyperedges.
    strong_gravity : bool
        Decide if the ForceAtlas2 Algorithm must use strong gravity or no.
    draw_labels : bool
        Decide if the labels should be drawn.
    iterations : int
        The number of iterations to run the position algorithm.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    node_shape : str, optional
        The shape of the nodes in the image. Use standard MathPlotLib values.
    node_color : str, optional
        HEX value for the nodes color.
    node_size : int, optional
        The size of the nodes in the image.
    edge_shape : str, optional
        The shape of the nodes used to represent edges. Use standard MathPlotLib values.
    edge_node_color : str, optional
        HEX value for the nodes color of the nodes that represents edges.
    edge_color : str, optional
        HEX value for the edges color.
    edge_width : float, optional
        Width of the edges in the grid.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    Returns
    -------
        ax : matplotlib.axes.Axes. The axes the graph was drawn on.
    """
    g, binary_edges = extra_node_projection(h)

    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    forceatlas2 = ForceAtlas2(
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED
        scalingRatio=2.0,
        strongGravityMode=strong_gravity,
        gravity=1.0,
        verbose=True)

    if ignore_binary_relations:
        isolated = list(nx.isolates(g))
        g.remove_nodes_from(isolated)
    else:
        for edge in binary_edges:
            g.add_edge(edge[0], edge[1])
    if is_planar(g):
        pos = planar_layout(g)
    else:
        if pos is None:
            pos = kamada_kawai_layout(g)
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, pos=pos, iterations=iterations, weight_attr="weight")

    __draw_in_plot(g, pos, ax = ax, show_edge_nodes=show_edge_nodes, draw_labels=draw_labels, node_shape=node_shape,
                   node_color=node_color, node_size=node_size, edge_shape=edge_shape, edge_node_color=edge_node_color,
                   edge_color=edge_color, edge_width=edge_width, **kwargs)
    ax.autoscale(enable=True, axis='both', tight=True)

def __draw_in_plot(
    g,
    pos,
    ax = None,
    show_edge_nodes: bool = False,
    draw_labels: bool = True,
    node_shape: str = 'o',
    node_color: str = '#1f78b4',
    node_size: int = 300,
    edge_shape: str = 'p',
    edge_node_color: str = '#8a0303',
    edge_color: str = "#000000",
    edge_width: float = 2,
    **kwargs) -> None:
    """
    Draws an extra-node projection of the hypergraph.
    Parameters
    ----------
    g : Graph.
        The graph to be drawn.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    show_edge_nodes : bool
        Decide if the function should draw nodes in the conjunction point of the hyperedges.
    draw_labels : bool
        Decide if the labels should be drawn.
    node_shape : str, optional
        The shape of the nodes in the image. Use standard MathPlotLib values.
    node_color : str, optional
        HEX value for the nodes color.
    node_size : int, optional
        The size of the nodes in the image.
    edge_shape : str, optional
        The shape of the nodes used to represent edges. Use standard MathPlotLib values.
    edge_node_color : str, optional
        HEX value for the nodes color of the nodes that represents edges.
    edge_color : str, optional
        HEX value for the edges color.
    edge_width : float, optional
        Width of the edges in the grid.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    Returns
    -------
        ax : matplotlib.axes.Axes. The axes the graph was drawn on.
    """
    if ax is None:
        ax = plt.gca()

    labels = dict((n, n) for n in g.nodes() if n.startswith('N'))
    node_list = [x for x in g.nodes() if x.startswith('N')]
    nx.draw_networkx_edges(g, pos, ax=ax, edge_color=edge_color, width=edge_width)
    nx.draw_networkx_nodes(g, ax=ax, pos=pos, nodelist=node_list, node_shape=node_shape,node_color=node_color, node_size=node_size, **kwargs)

    if show_edge_nodes:
        edge_list = [x for x in g.nodes() if x.startswith('E')]
        labels_edges = dict((n, n) for n in g.nodes() if n.startswith('E'))
        labels.update(labels_edges)
        nx.draw_networkx_nodes(g, ax=ax, pos=pos, node_shape=edge_shape, node_color=edge_node_color,nodelist=edge_list, **kwargs)
    if draw_labels:
        nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels)