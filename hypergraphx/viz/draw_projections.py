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


def draw_clique(h: Hypergraph, pos=None, ax=None, **kwargs):
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
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.

    Returns
    -------
    ax : matplotlib.axes.Axes. The axes the graph was drawn on.
    """
    g = clique_projection(h)

    if pos is None:
        pos = nx.spring_layout(g)

    if ax is None:
        ax = plt.gca()

    nx.draw_networkx(g, pos=pos, ax=ax, **kwargs)
    plt.show()
    return ax

def draw_extra_node(h: Hypergraph, pos=None, ax=None, ignore_binary_relations: bool = True, show_edge_nodes=True, iterations: int = 1000, **kwargs):
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
    g, obj_to_id, binary_edges = extra_node_projection(h)

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
    if pos is None:
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, iterations=iterations, weight_attr="weight")
        __draw_in_plot(g, pos, show_edge_nodes=show_edge_nodes, **kwargs)
    else:
        if ignore_binary_relations:
            isolated = list(nx.isolates(g))
            g.remove_nodes_from(isolated)
            pos = forceatlas2.forceatlas2_networkx_layout(G=g, iterations=iterations, weight_attr="weight")
            __draw_in_plot(g, pos, show_edge_nodes=show_edge_nodes, **kwargs)
        else:
            for edge in binary_edges:
                g.add_edge(edge[0], edge[1])
            pos = forceatlas2.forceatlas2_networkx_layout(G = g, iterations= iterations, weight_attr = "weight")
            __draw_in_plot(g,pos, show_edge_nodes=show_edge_nodes, **kwargs)

    return ax

def __draw_in_plot(g, pos, node_shapes = None, colors = None, show_edge_nodes: bool = False,**kwargs):
    px = 1 / plt.rcParams['figure.dpi']
    dim = (g.number_of_nodes()*50)*px
    dim = min(dim, 2**16)
    plt.figure(3, figsize=(dim,dim))
    ax = plt.gca()
    labels = dict((n, n) for n in g.nodes() if n.startswith('N'))
    if node_shapes is None:
        node_shapes = {"node": "s", "edge_node": "p"}
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
    plt.show()