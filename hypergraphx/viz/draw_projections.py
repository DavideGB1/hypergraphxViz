from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
from fa2_modified import ForceAtlas2

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
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        node_shape: str = "o",
        node_color: str = "#1f78b4",
        node_size: int = 300,
        edge_color: str = "#000000",
        edge_width: float = 2,
        iterations: int = 1000,
        strong_gravity: bool = True,
        **kwargs):
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
        HEX value for the edges color.edge_width: float = 2
    edge_width : float, optional
        Width of the edges in the grid.
    iterations : int
        The number of iterations to run the position algorithm.
    strong_gravity : bool
        Decide if the ForceAtlas2 Algorithm must use strong gravity or no.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.

    Returns
    -------
    ax : matplotlib.axes.Axes. The axes the graph was drawn on.
    """
    g = clique_projection(h)

    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,

        # Performance
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED

        # Tuning
        scalingRatio=2.0,
        strongGravityMode=strong_gravity,
        gravity=1.0,
        # Log
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
    nx.draw_networkx_labels(G=g, pos=pos, ax=ax, labels=labels)

    plt.axis('off')
    ax.axis('off')
    ax.set_aspect('equal')
    ax.autoscale(enable=True, axis='both')
    plt.autoscale(enable=True, axis='both')

def draw_extra_node(h: Hypergraph, pos=None, ax=None, ignore_binary_relations: bool = True, show_edge_nodes=True, iterations: int = 50000, **kwargs):
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
    iterations : int
        The number of iterations to run the position algorithm.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.

    Returns
    -------
        ax : matplotlib.axes.Axes. The axes the graph was drawn on.
    """
    g, binary_edges = extra_node_projection(h)

    if ax is None:
        ax = plt.gca()

    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,

        # Performance
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED

        # Tuning
        scalingRatio=2.0,
        strongGravityMode=False,
        gravity=1.0,
        # Log
        verbose=True)

    if ignore_binary_relations:
        isolated = list(nx.isolates(g))
        g.remove_nodes_from(isolated)
    else:
        for edge in binary_edges:
            g.add_edge(edge[0], edge[1])
    if is_planar(g):
        pos = planar_layout(g)
        __draw_in_plot(g, pos, show_edge_nodes=show_edge_nodes, **kwargs)
    else:
        if pos is None:
            pos = kamada_kawai_layout(g)

        pos = forceatlas2.forceatlas2_networkx_layout(G=g, pos=pos, iterations=iterations, weight_attr="weight")
        __draw_in_plot(g, pos, show_edge_nodes=show_edge_nodes, **kwargs)

    ax.autoscale(enable=True, axis='both', tight=True)
    plt.axis('off')
    return ax

def __draw_in_plot(g, pos, node_shapes = None, colors = None, show_edge_nodes: bool = False,**kwargs):
    ax = plt.gca()
    labels = dict((n, n) for n in g.nodes() if n.startswith('N'))
    if node_shapes is None:
        node_shapes = {"node": "o", "edge_node": "p"}
    if colors is None:
        colors = {"node": "#3264a8", "edge_node": "#8a0303"}

    node_list = [x for x in g.nodes() if x.startswith('N')]
    edge_list = [x for x in g.nodes() if x.startswith('E')]

    nx.draw_networkx_edges(g, pos, ax=ax)
    nx.draw_networkx_nodes(g, ax=ax, pos=pos, nodelist=node_list, node_shape=node_shapes["node"],node_color=colors["node"], **kwargs)
    if show_edge_nodes:
        labels_edges = dict((n, n) for n in g.nodes() if n.startswith('E'))
        labels.update(labels_edges)
        nx.draw_networkx_nodes(g, ax=ax, pos=pos, node_shape=node_shapes["edge_node"], node_color=colors["edge_node"],nodelist=edge_list, **kwargs)

    nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels)
