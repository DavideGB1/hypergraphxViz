from typing import Optional
import matplotlib.pyplot as plt
import networkx as nx
from networkx import is_planar, planar_layout
from __support import __filter_hypergraph, __ignore_unused_args, _get_community_info, _get_node_community, \
    _draw_node_community
from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.readwrite import load_hypergraph
from hypergraphx.representations.projections import (
    bipartite_projection,
    clique_projection, extra_node_projection)
from hypergraphx.viz.__graphic_options import GraphicOptions


@__ignore_unused_args
def draw_bipartite(
    h: Hypergraph,
    u = None,
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
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
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
                               width=graphicOptions.edge_size[edge])
    if u is not None:
        mapping, col = _get_community_info(hypergraph)
    for node in node_list:
        if u is None:
            nx.draw_networkx_nodes(g, ax=ax, pos=pos, nodelist=[node], node_shape=graphicOptions.node_shape[node],
                           node_color=graphicOptions.node_color[node], node_size=graphicOptions.node_size[node],
                            edgecolors = graphicOptions.node_facecolor[node], **kwargs)
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping,id_to_obj[node], u, col,0.01)
            _draw_node_community(ax, node, center=pos[node], radius = 0.03,wedge_sizes= wedge_sizes, wedge_colors = wedge_colors, graphicOptions = graphicOptions )

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
                                font_color=graphicOptions.label_color)
    if h.is_weighted():
        labels = nx.get_node_attributes(g, 'weight')
        pos_offsetted = {}
        offset = 0.1
        for k, v in pos.items():
            if align == 'horizontal':
                pos_offsetted[k] = (v[0], v[1] + offset)
            else:
                pos_offsetted[k] = (v[0] + offset, v[1])
        nx.draw_networkx_labels(g, ax=ax, pos=pos_offsetted, labels=labels, font_size = graphicOptions.weight_size,
                                font_color=graphicOptions.label_color)
    ax.axis("off")


@__ignore_unused_args
def draw_clique(
    h: Hypergraph,
    u=None,
    cardinality: tuple[int,int]|int = -1,
    x_heaviest: float = 1.0,
    draw_labels=True,
    iterations: int = 1000,
    pos=None,
    ax: Optional[plt.Axes] = None,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = GraphicOptions(),
    **kwargs) -> dict:
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
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    g = clique_projection(hypergraph)

    #Calculate positions if not provided
    if pos is None:
        pos = nx.spring_layout(G=g, iterations=iterations, weight="weight")

    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    graphicOptions.check_if_options_are_valid(g)
    for edge in g.edges():
        nx.draw_networkx_edges(G=g, pos=pos, edgelist=[edge], ax=ax, edge_color=graphicOptions.edge_color[edge],
                               width=graphicOptions.edge_size[edge], **kwargs)
    if u is not None:
        mapping, col = _get_community_info(hypergraph)
    for node in g.nodes():
        if u is None:
            nx.draw_networkx_nodes(G=g, pos=pos, ax=ax, node_color=graphicOptions.node_color[node],
                               node_size=graphicOptions.node_size[node], node_shape=graphicOptions.node_shape[node],
                               edgecolors = graphicOptions.node_facecolor[node], **kwargs)
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping,node, u, col,0.1)
            _draw_node_community(ax, node, center=pos[node], radius = 0.03,wedge_sizes= wedge_sizes, wedge_colors = wedge_colors, graphicOptions = graphicOptions )

    if draw_labels:
        labels = dict((n, n) for n in g.nodes())
        nx.draw_networkx_labels(G=g, pos=pos, ax=ax, labels=labels, font_size=graphicOptions.label_size,
                                font_color=graphicOptions.label_color, **kwargs)

    ax.set_aspect('equal')
    ax.axis("off")
    ax.autoscale(enable=True, axis='both')
    return pos

@__ignore_unused_args
def draw_extra_node(
    h: Hypergraph,
    u = None,
    cardinality: tuple[int,int]|int = -1,
    x_heaviest: float = 1.0,
    draw_labels: bool = True,
    ignore_binary_relations: bool = True,
    show_edge_nodes=True,
    draw_edge_graph = False,
    pos: dict = None,
    iterations: int = 1000,
    ax=None,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = GraphicOptions(),
    **kwargs) -> dict:
    """
    Draws an extra-node projection of the hypergraph.
    Parameters
    ----------
    pos
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
    draw_edge_graph: bool
        Let you draw the edge graph used in the first part of the node position algorithm
    iterations : int
        The number of iterations to run the position algorithm.
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
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    g, obj_to_id = extra_node_projection(hypergraph)
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()
    if u is not None:
        mapping, col = _get_community_info(hypergraph)

    #Removed the binary edges in order to reduce useless occlusion
    if ignore_binary_relations:
        binary_edges = [x for x in g.edges() if not(str(x[0]).startswith('E') or str(x[1]).startswith('E')) ]
        for binary_edge in binary_edges:
            g.remove_edge(*binary_edge)
        isolated = list(nx.isolates(g))
        g.remove_nodes_from(isolated)
    if pos is None:
        if is_planar(g):
            pos = planar_layout(g)
        else:
            #Calculate the position of each edge node and then fixes it in the final drawing
            edgeList = [x for x in g.nodes() if str(x).startswith('E')]
            hyperedges_relations = __hyperedges_relations_detection(h, obj_to_id)
            posEdges = __edges_graph_creation(hyperedges_relations, edgeList, drawing=draw_edge_graph)
            pos = nx.spring_layout(G=g, pos=posEdges, iterations=iterations, weight="weight", fixed=edgeList)

    # Ensure that all the nodes have the graphical attributes specified
    graphicOptions.check_if_options_are_valid(g)

    __draw_in_plot(g, pos, u = u,mapping = mapping, col = col, ax = ax, show_edge_nodes=show_edge_nodes, draw_labels=draw_labels,
                   graphicOptions = graphicOptions,isDirected=isinstance(h, DirectedHypergraph), isWeighted = hypergraph.is_weighted(), **kwargs)

    ax.set_aspect('equal')
    ax.autoscale(enable=True, axis='both')
    ax.axis("off")
    return pos

def __edges_graph_creation(hyperedges_relations: dict, edgeList: list, drawing: bool = False) -> dict:
    """
    Create a graph using the relations between hyperedges..
    Parameters
    ----------
    hyperedges_relations: dict
        Dictionary with the relations between the hyperedges
    edgeList: list
        List with the edges
    drawing: bool
        Used to decide if the EdgeGraph should be drawn
    Returns
    -------
    dict
        A dictionary with the EdgeGraph nodes position.
    """
    edges_graph = nx.Graph()
    for x in edgeList:
        edges_graph.add_node(x)

    for edge in hyperedges_relations:
        edges_graph.add_edge(edge[0], edge[1], weight=hyperedges_relations[edge])

    if is_planar(edges_graph):
        posEdges = nx.planar_layout(edges_graph)
    else:
        toImprovePos = nx.kamada_kawai_layout(edges_graph)
        posEdges = nx.spring_layout(edges_graph, k=0.5, pos=toImprovePos, weight="weight")

    if drawing:
        plt.figure(3, figsize=(50, 50))
        nx.draw_networkx(edges_graph, pos=posEdges, with_labels=True)
        plt.show()

    return posEdges


def __hyperedges_relations_detection(h: Hypergraph, obj_to_id: dict) -> dict:
    """
    Calculate the relations between hyperedges, that are simply the number of common nodes between two of them.
    Parameters
    ----------
    h : Hypergraph.
    obj_to_id : dict.
        Mapping from actual object to is id
    Returns
    -------
    dict
        A dictionary with the relations.
    """
    hyperedges_relations = dict()

    for i, edge1 in enumerate(h.get_edges()):
        for j, edge2 in enumerate(h.get_edges()):
            if i >= j:
                continue
            if len(edge1) != 2 and len(edge2) != 2:
                if obj_to_id[edge1] != obj_to_id[edge2]:
                    z = set(edge1).intersection(set(edge2))
                    if len(z) != 0:
                        if (obj_to_id[edge1], obj_to_id[edge2]) not in hyperedges_relations:
                            hyperedges_relations[(obj_to_id[edge1], obj_to_id[edge2])] = 0
                        hyperedges_relations[(obj_to_id[edge1], obj_to_id[edge2])] += 1

    return hyperedges_relations

def __draw_in_plot(
    g,
    pos,
    graphicOptions: GraphicOptions,
    isDirected: bool = False,
    isWeighted: bool = False,
    ax = None,
    show_edge_nodes: bool = False,
    draw_labels: bool = True,
    mapping=None,
    col=None,
    u = None,
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
    isDirected : bool, optional
        Used to determine if a directed hypergraph should be drawn or a normal one.
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
                               width=graphicOptions.edge_size[edge], arrows = isDirected, **kwargs)
    for node in node_list:
        if mapping is None:
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
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping,node, u, col,0.1)
            _draw_node_community(ax, node, center=pos[node], radius = 0.03,wedge_sizes= wedge_sizes, wedge_colors = wedge_colors, graphicOptions = graphicOptions )

    #Draw nodes that represents edges
    if show_edge_nodes:
        edge_list = [x for x in g.nodes() if str(x).startswith('E')]
        for edge in edge_list:
            nx.draw_networkx_nodes(
                g,
                pos,
                nodelist=[edge],
                node_size=graphicOptions.node_size[edge],
                node_shape=graphicOptions.edge_shape[edge],
                node_color=graphicOptions.edge_node_color[edge],
                edgecolors=graphicOptions.node_facecolor[edge],
                ax=ax,
                **kwargs
            )
        if isWeighted:
            labels = nx.get_node_attributes(g, 'weight')
            nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size=graphicOptions.label_size,
                                    font_color=graphicOptions.label_color, **kwargs)
    #Draw labels
    if draw_labels:
        labels = dict((n, n) for n in g.nodes() if not str(n).startswith('E'))
        nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size = graphicOptions.weight_size,
                                font_color=graphicOptions.label_color, **kwargs)