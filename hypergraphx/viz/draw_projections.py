from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
from fa2_modified import ForceAtlas2
from networkx import is_planar, planar_layout, kamada_kawai_layout

from hypergraphx import Hypergraph
from hypergraphx.representations.projections import (
    bipartite_projection,
    clique_projection, extra_node_projection)


from __support import filter_hypergraph, ignore_unused_args
from hypergraphx.viz.__options import GraphicOptions


@ignore_unused_args
def draw_bipartite(
    h: Hypergraph,
    cardinality: tuple[int,int]|int = -1,
    x_heaviest: float = 1.0,
    draw_labels=True,
    align='vertical',
    pos=None,
    ax: Optional[plt.Axes] = None,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = GraphicOptions(),
    **kwargs):
    """
    Draws a bipartite graph representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    draw_labels : bool
        Decide if the labels should be drawn.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    align : str.
        The alignment of the nodes. Can be 'vertical' or 'horizontal'.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    graphicOptions: Optional[GraphicOptions].
        Object used to store all the common graphical settings among the representation methods.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    """
    hypergraph = filter_hypergraph(h,cardinality, x_heaviest)
    g, id_to_obj = bipartite_projection(hypergraph)

    if pos is None:
        pos = nx.bipartite_layout(g, nodes=[n for n, d in g.nodes(data=True) if d['bipartite'] == 0],align=align)

    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    graphicOptions.check_if_options_are_valid(g)
    # Draw edges and nodes
    node_list = [x for x in g.nodes() if x.startswith('N')]
    for edge in g.edges():
        nx.draw_networkx_edges(g, pos, edgelist= [edge], ax=ax, edge_color=graphicOptions.edge_color[edge],
                               width=graphicOptions.edge_width[edge])
    for node in node_list:
        nx.draw_networkx_nodes(g, ax=ax, pos=pos, nodelist=[node], node_shape=graphicOptions.node_shape[node],
                           node_color=graphicOptions.node_color[node], node_size=graphicOptions.node_size[node],
                            edgecolors = graphicOptions.node_facecolor[node], **kwargs)
    # Draw nodes that represents edges
    edge_list = [x for x in g.nodes() if x.startswith('E')]
    for edge in edge_list:
        nx.draw_networkx_nodes(g, ax=ax, pos=pos, node_shape=graphicOptions.edge_shape[edge], edgecolors = graphicOptions.node_facecolor[edge],
                               node_color=graphicOptions.edge_node_color[edge], node_size=graphicOptions.node_size[edge],
                               nodelist=[edge], **kwargs)
    # Draw labels
    if draw_labels:
        labels = dict((n, n) for n in g.nodes())
        nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size=graphicOptions.label_size,
            font_color=graphicOptions.label_col)

@ignore_unused_args
def draw_clique(
    h: Hypergraph,
    cardinality: tuple[int,int]|int = -1,
    x_heaviest: float = 1.0,
    draw_labels=True,
    iterations: int = 1000,
    strong_gravity: bool = True,
    pos=None,
    ax: Optional[plt.Axes] = None,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = GraphicOptions(),
    **kwargs) -> None:
    """
    Draws a clique projection of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    draw_labels : bool
        Decide if the labels should be drawn.
    iterations : int
        The number of iterations to run the position algorithm.
    strong_gravity : bool
        Decide if the ForceAtlas2 Algorithm must use strong gravity or no.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    graphicOptions: Optional[GraphicOptions].
        Object used to store all the common graphical settings among the representation methods.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    """
    hypergraph = filter_hypergraph(h, cardinality, x_heaviest)
    g = clique_projection(hypergraph)

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
    #Calculate positions if not provided
    if pos is None:
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, iterations=iterations, weight_attr="weight")
    #Ues provided positions as a base for the calculation
    else:
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, pos=pos,iterations=iterations, weight_attr="weight")

    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    graphicOptions.check_if_options_are_valid(g)
    for edge in g.edges():
        nx.draw_networkx_edges(G=g, pos=pos, edgelist=[edge],ax=ax, edge_color=graphicOptions.edge_color[edge],
                               width=graphicOptions.edge_width[edge], **kwargs)
    for node in g.nodes():
        nx.draw_networkx_nodes(G=g, pos=pos, ax=ax, node_color=graphicOptions.node_color[node],
                               node_size=graphicOptions.node_size[node], node_shape=graphicOptions.node_shape[node],
                               edgecolors = graphicOptions.node_facecolor[node], **kwargs)
    if draw_labels:
        labels = dict((n, n) for n in g.nodes())
        nx.draw_networkx_labels(G=g, pos=pos, ax=ax, labels=labels, font_size=graphicOptions.label_size,
            font_color=graphicOptions.label_col, **kwargs)

    ax.set_aspect('equal')
    ax.autoscale(enable=True, axis='both')

@ignore_unused_args
def draw_extra_node(
    h: Hypergraph,
    cardinality: tuple[int,int]|int = -1,
    x_heaviest: float = 1.0,
    draw_labels: bool = True,
    ignore_binary_relations: bool = True,
    show_edge_nodes=True,
    iterations: int = 1000,
    strong_gravity: bool = True,
    pos=None,
    ax=None,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = GraphicOptions(),
    **kwargs) -> None:
    """
    Draws an extra-node projection of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    draw_labels : bool
        Decide if the labels should be drawn.
    ignore_binary_relations : bool
        Decide if the function should show nodes that are only in binary relations.
    show_edge_nodes : bool
        Decide if the function should draw nodes in the conjunction point of the hyperedges.
    iterations : int
        The number of iterations to run the position algorithm.
    strong_gravity : bool
        Decide if the ForceAtlas2 Algorithm must use strong gravity or no.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    graphicOptions: Optional[GraphicOptions].
        Object used to store all the common graphical settings among the representation methods.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    """
    hypergraph = filter_hypergraph(h, cardinality, x_heaviest)
    g, binary_edges = extra_node_projection(hypergraph)

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
            #First layout to optimize
            pos = kamada_kawai_layout(g)
        pos = forceatlas2.forceatlas2_networkx_layout(G=g, pos=pos, iterations=iterations, weight_attr="weight")
        # Ensure that all the nodes have the graphical attributes specified

    graphicOptions.check_if_options_are_valid(g)

    __draw_in_plot(g, pos, ax = ax, show_edge_nodes=show_edge_nodes, draw_labels=draw_labels,
                   graphicOptions = graphicOptions, **kwargs)

    ax.set_aspect('equal')
    ax.autoscale(enable=True, axis='both')

def __draw_in_plot(
    g,
    pos,
    graphicOptions: GraphicOptions,
    ax = None,
    show_edge_nodes: bool = False,
    draw_labels: bool = True,
    **kwargs) -> None:
    """
    Draws an extra-node projection of the hypergraph.
    Parameters
    ----------
    g : Graph.
        The graph to be drawn.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    graphicOptions: Optional[GraphicOptions].
        Object used to store all the common graphical settings among the representation methods.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    show_edge_nodes : bool
        Decide if the function should draw nodes in the conjunction point of the hyperedges.
    draw_labels : bool
        Decide if the labels should be drawn.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    """
    if ax is None:
        ax = plt.gca()

    #Draw edges and nodes
    node_list = [x for x in g.nodes() if not str(x).startswith('E')]
    for edge in g.edges():
        nx.draw_networkx_edges(g, pos, edgelist=[edge], ax=ax, edge_color=graphicOptions.edge_color[edge],
                               width=graphicOptions.edge_width[edge], **kwargs)
    for node in node_list:
        nx.draw_networkx_nodes(
            g,
            pos,
            nodelist = [node],
            node_size=graphicOptions.node_size[node],
            node_shape=graphicOptions.node_shape[node],
            node_color=graphicOptions.node_color[node],
            edgecolors=graphicOptions.node_facecolor[node],
            ax=ax,
            **kwargs
        )
    #Draw nodes that represents edges
    if show_edge_nodes:
        edge_list = [x for x in g.nodes() if str(x).startswith('E')]
        for edge in edge_list:
            nx.draw_networkx_nodes(g, nodelist=[edge], ax=ax, pos=pos, node_shape=graphicOptions.edge_shape[edge],
                                   node_color=graphicOptions.edge_node_color[edge], **kwargs)
    #Draw labels
    if draw_labels:
        labels = dict((n, n) for n in g.nodes() if not str(n).startswith('E'))
        if show_edge_nodes:
            labels_edges = dict((n, n) for n in g.nodes() if str(n).startswith('E'))
            labels.update(labels_edges)
        nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size=graphicOptions.label_size,
            font_color=graphicOptions.label_col, **kwargs)