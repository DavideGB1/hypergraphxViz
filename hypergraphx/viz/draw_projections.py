from typing import Optional, Dict, Any

import matplotlib.pyplot as plt
import networkx as nx
from networkx import is_planar, planar_layout, DiGraph
from networkx.drawing import spectral_layout

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.representations.projections import (
    bipartite_projection,
    clique_projection, extra_node_projection)
from hypergraphx.viz.__support import __filter_hypergraph, __ignore_unused_args, _get_community_info, _get_node_community, \
    _draw_node_community
from hypergraphx.viz.__graphic_options import GraphicOptions

# =============================================================================
# Bipartite Projection Drawing
# =============================================================================
@__ignore_unused_args

def _compute_bipartite_drawing_data(
    h: Hypergraph | DirectedHypergraph,
    cardinality: tuple[int, int] | int,
    x_heaviest: float,
    align: str,
    pos: Optional[dict],
    u: Optional[Any],
    k: int,
) -> dict:
    """
    Computes the necessary data for drawing the bipartite projection.
    """
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    g, id_to_obj = bipartite_projection(hypergraph)

    if pos is None:
        pos = nx.bipartite_layout(g, nodes=[n for n, d in g.nodes(data=True) if d['bipartite'] == 0], align=align)

    mapping, col = (None, None)
    if u is not None:
        mapping, col = _get_community_info(hypergraph, k)

    return {
        "graph": g,
        "hypergraph": hypergraph,
        "pos": pos,
        "id_to_obj": id_to_obj,
        "mapping": mapping,
        "col": col,
    }

@__ignore_unused_args

def _draw_bipartite_on_ax(
    ax: plt.Axes,
    data: dict,
    u: Optional[Any],
    draw_labels: bool,
    align: str,
    graphicOptions: GraphicOptions,
    **kwargs
) -> None:
    """
    Performs the actual drawing of the bipartite projection on a given Axes object.
    """
    g = data['graph']
    pos = data['pos']
    id_to_obj = data['id_to_obj']
    mapping = data['mapping']
    col = data['col']
    hypergraph = data['hypergraph']

    graphicOptions.check_if_options_are_valid(g)

    # Draw edges and nodes
    node_list = [x for x in g.nodes() if x.startswith('N')]
    is_directed = isinstance(hypergraph, DirectedHypergraph)

    for node in node_list:
        if u is None:
            nx.draw_networkx_nodes(g, ax=ax, pos=pos, nodelist=[node], node_shape=graphicOptions.node_shape[node],
                                   node_color=graphicOptions.node_color[node], node_size=graphicOptions.node_size[node],
                                   edgecolors=graphicOptions.node_facecolor[node], **kwargs)
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping, id_to_obj[node], u, col, 0.01)
            _draw_node_community(ax, node, pos[node], wedge_sizes, wedge_colors, graphicOptions, **kwargs)

    # Draw nodes that represent edges
    edge_list = [x for x in g.nodes() if x.startswith('E')]
    for edge in edge_list:
        nx.draw_networkx_nodes(g, ax=ax, pos=pos, node_shape=graphicOptions.edge_shape[edge],
                               edgecolors=graphicOptions.node_facecolor[edge],
                               node_color=graphicOptions.edge_node_color[edge], node_size=graphicOptions.node_size[edge],
                               nodelist=[edge], **kwargs)
    # Draw labels
    if draw_labels:
        labels = {n: id_to_obj[n] for n in g.nodes() if n.startswith('N')}
        labels_edge = {n: n for n in g.nodes() if n.startswith('E')}
        labels.update(labels_edge)
        nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size=graphicOptions.label_size,
                                font_color=graphicOptions.label_color)

    if hypergraph.is_weighted():
        labels = nx.get_node_attributes(g, 'weight')
        pos_offsetted = {}
        offset = 0.1
        for k_pos, v_pos in pos.items():
            pos_offsetted[k_pos] = (v_pos[0], v_pos[1] + offset) if align == 'horizontal' else (v_pos[0] + offset, v_pos[1])
        nx.draw_networkx_labels(g, ax=ax, pos=pos_offsetted, labels=labels, font_size=graphicOptions.weight_size,
                                font_color=graphicOptions.label_color)

    for edge in g.edges():
        color = graphicOptions.in_edge_color if isinstance(edge[1], str) and edge[1].startswith('E') else graphicOptions.out_edge_color
        node_size = max(graphicOptions.node_size[edge[0]],graphicOptions.node_size[edge[1]])
        nx.draw_networkx_edges(g, pos, edgelist=[edge], ax=ax, edge_color=color,
                               width=graphicOptions.edge_size[edge], arrows=is_directed, node_size = node_size,**kwargs)


@__ignore_unused_args
def draw_bipartite(
    h: Hypergraph | DirectedHypergraph,
    u=None,
    k=2,
    cardinality: tuple[int, int] | int = -1,
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
    h : Hypergraph | DirectedHypergraph.
        The hypergraph to be projected.
    u : any, optional
        Represents the fuzzy partition of the nodes.
    k : int, optional
        The number of communities to consider for the fuzzy partition.
    cardinality: tuple[int,int]|int. optional
        Filters hyperedges based on their cardinality.
    x_heaviest: float, optional
        Filters hyperedges to show only the heaviest x percent.
    draw_labels : bool
        Whether to draw node and edge labels.
    align : str.
        The alignment of the nodes ('vertical' or 'horizontal').
    pos : dict.
        A dictionary of node positions.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    figsize : tuple, optional
        Figure size.
    dpi : int, optional
        Figure DPI.
    graphicOptions: Optional[GraphicOptions].
        Graphical settings for the representation.
    kwargs : dict.
        Keyword arguments passed to networkx.draw_networkx.
    """
    data = _compute_bipartite_drawing_data(h, cardinality, x_heaviest, align, pos, u, k, graphicOptions)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    _draw_bipartite_on_ax(ax, data, u, draw_labels, align, **kwargs)

    ax.set_aspect('auto')
    ax.autoscale(enable=True, axis='both')
    ax.axis("off")
    plt.tight_layout()


# =============================================================================
# Clique Projection Drawing
# =============================================================================
@__ignore_unused_args

def _compute_clique_drawing_data(
    h: Hypergraph,
    cardinality: tuple[int, int] | int,
    x_heaviest: float,
    iterations: int,
    pos: Optional[dict],
    u: Optional[Any],
    k: int,
    weight_positioning: int
) -> dict:
    """
    Computes the necessary data for drawing the clique projection.
    """
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    g = clique_projection(hypergraph)
    if hypergraph.is_weighted():
        for u_node, v_node, data in g.edges(data=True):
            if weight_positioning == 0:
                data['weight'] = 1
            elif weight_positioning == 2:
                data['weight'] = 1 / data['weight']
    if pos is None:
        pos = nx.kamada_kawai_layout(G=g, pos=pos,weight="weight")
        pos = nx.spring_layout(G=g, pos=pos, iterations=iterations, weight="weight")


    mapping, col = (None, None)
    if u is not None:
        mapping, col = _get_community_info(hypergraph, k)

    return {
        "graph": g,
        "hypergraph": hypergraph,
        "pos": pos,
        "mapping": mapping,
        "col": col,
    }

@__ignore_unused_args

def _draw_clique_on_ax(
    ax: plt.Axes,
    data: dict,
    u: Optional[Any],
    draw_labels: bool,
    graphicOptions: GraphicOptions,
    **kwargs
) -> None:
    """
    Performs the actual drawing of the clique projection on a given Axes object.
    """
    g = data['graph']
    pos = data['pos']
    mapping = data['mapping']
    col = data['col']
    graphicOptions.check_if_options_are_valid(g)

    for edge in g.edges():
        nx.draw_networkx_edges(G=g, pos=pos, edgelist=[edge], ax=ax, edge_color=graphicOptions.edge_color[edge],
                               width=graphicOptions.edge_size[edge], **kwargs)
    for node in g.nodes():
        if u is None:
            nx.draw_networkx_nodes(g, pos, nodelist=[node], node_size=graphicOptions.node_size[node],
                                   node_shape=graphicOptions.node_shape[node], node_color=graphicOptions.node_color[node],
                                   edgecolors=graphicOptions.node_facecolor[node], ax=ax, **kwargs)
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
            _draw_node_community(ax, node, pos[node], wedge_sizes, wedge_colors, graphicOptions, **kwargs)

    if draw_labels:
        labels = {n: n for n in g.nodes()}
        nx.draw_networkx_labels(G=g, pos=pos, ax=ax, labels=labels, font_size=graphicOptions.label_size,
                                font_color=graphicOptions.label_color, **kwargs)


@__ignore_unused_args
def draw_clique(
    h: Hypergraph,
    u=None,
    k=2,
    cardinality: tuple[int, int] | int = -1,
    x_heaviest: float = 1.0,
    draw_labels=True,
    iterations: int = 1000,
    weight_positioning: int  = 0,
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
    u : any, optional
        Represents the fuzzy partition of the nodes.
    k : int, optional
        The number of communities to consider for the fuzzy partition.
    cardinality: tuple[int,int]|int. optional
        Filters hyperedges based on their cardinality.
    x_heaviest: float, optional
        Filters hyperedges to show only the heaviest x percent.
    draw_labels : bool
        Whether to draw node labels.
    iterations : int
        Number of iterations for the spring layout algorithm.
    pos : dict.
        A dictionary of node positions.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    figsize : tuple, optional
        Figure size.
    dpi : int, optional
        Figure DPI.
    graphicOptions: Optional[GraphicOptions].
        Graphical settings for the representation.
    kwargs : dict.
        Keyword arguments passed to networkx.draw_networkx.
    Returns
    -------
    dict
        A dictionary of node positions.
    """
    data = _compute_clique_drawing_data(h, cardinality, x_heaviest, iterations, weight_positioning, pos, u, k,graphicOptions)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    _draw_clique_on_ax(ax, data, u, draw_labels, **kwargs)

    ax.set_aspect('auto')
    ax.axis("off")
    ax.autoscale(enable=True, axis='both')
    plt.tight_layout()
    return data['pos']


# =============================================================================
# Extra-Node Projection Drawing
# =============================================================================
@__ignore_unused_args

def _compute_extra_node_drawing_data(
    h: Hypergraph,
    cardinality: tuple[int, int] | int,
    x_heaviest: float,
    ignore_binary_relations: bool,
    weight_positioning: int,
    respect_planarity: bool,
    iterations: int,
    pos: Optional[dict],
    u: Optional[Any],
    k: int,
    draw_edge_graph: bool = False,
) -> dict:
    """
    Computes the necessary data for drawing the extra-node projection.
    """
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    g, obj_to_id = extra_node_projection(hypergraph)

    mapping, col = (None, None)
    if u is not None:
        mapping, col = _get_community_info(hypergraph, k)

    if ignore_binary_relations:
        binary_edges = [x for x in g.edges() if not (str(x[0]).startswith('E') or str(x[1]).startswith('E'))]
        g.remove_edges_from(binary_edges)
        g.remove_nodes_from(list(nx.isolates(g)))

    if hypergraph.is_weighted():
        for u_node, v_node, data in g.edges(data=True):
            if weight_positioning == 0:
                data['weight'] = 1
            elif weight_positioning == 2:
                data['weight'] = 1 / data['weight']

    clone_g = None
    if isinstance(g, DiGraph):
        clone_g = g
        g = g.to_undirected()

    if pos is None:
        if is_planar(g) and respect_planarity:
            pos = planar_layout(g)
        else:
            edgeList = [x for x in g.nodes() if str(x).startswith('E')]
            hyperedges_relations = _hyperedges_relations_detection(hypergraph, obj_to_id)
            posEdges = _edges_graph_creation(hyperedges_relations, edgeList, drawing=draw_edge_graph)
            if len(posEdges) > 0:
                pos = nx.spring_layout(G=g, pos=posEdges, iterations=iterations, weight="weight", fixed=edgeList)
            else:
                pos = nx.spring_layout(G=g, iterations=iterations, weight="weight")

    if clone_g is not None:
        g = clone_g

    return {
        "graph": g,
        "hypergraph": hypergraph,
        "pos": pos,
        "mapping": mapping,
        "col": col,
    }

@__ignore_unused_args

def _draw_extra_node_on_ax(
    ax: plt.Axes,
    data: dict,
    u: Optional[Any],
    show_edge_nodes: bool,
    draw_labels: bool,
    graphicOptions: GraphicOptions,
    **kwargs
) -> None:
    """
    Performs the actual drawing of the extra-node projection on a given Axes object.
    """
    g = data['graph']
    pos = data['pos']
    mapping = data['mapping']
    col = data['col']
    graphicOptions.check_if_options_are_valid(g)
    hypergraph = data['hypergraph']
    is_directed = isinstance(hypergraph, DirectedHypergraph)
    is_weighted = hypergraph.is_weighted()

    # Draw edges and nodes
    node_list = [x for x in g.nodes() if not str(x).startswith('E')]
    for node in node_list:
        if mapping is None:
            nx.draw_networkx_nodes(g, pos, nodelist=[node], node_size=graphicOptions.node_size[node],
                                   node_shape=graphicOptions.node_shape[node], node_color=graphicOptions.node_color[node],
                                   edgecolors=graphicOptions.node_facecolor[node], ax=ax, **kwargs)
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
            _draw_node_community(ax, node, pos[node], wedge_sizes, wedge_colors, graphicOptions, **kwargs)

    # Draw nodes that represent edges
    if show_edge_nodes:
        edge_list = [x for x in g.nodes() if str(x).startswith('E')]
        for edge in edge_list:
            nx.draw_networkx_nodes(g, pos, nodelist=[edge], node_size=graphicOptions.node_size[edge],
                                   node_shape=graphicOptions.edge_shape[edge], node_color=graphicOptions.edge_node_color[edge],
                                   edgecolors=graphicOptions.node_facecolor[edge], ax=ax, **kwargs)
        if is_weighted:
            labels = nx.get_node_attributes(g, 'weight')
            nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size=graphicOptions.weight_size,
                                    font_color=graphicOptions.label_color, **kwargs)
    # Draw labels
    if draw_labels:
        labels = {n: n for n in g.nodes() if not str(n).startswith('E')}
        nx.draw_networkx_labels(g, ax=ax, pos=pos, labels=labels, font_size=graphicOptions.label_size,
                                font_color=graphicOptions.label_color, **kwargs)
    for edge in g.edges():
        color = graphicOptions.in_edge_color if isinstance(edge[1], str) and edge[1].startswith('E') else graphicOptions.out_edge_color
        node_size = max(graphicOptions.node_size[edge[0]],graphicOptions.node_size[edge[1]])
        nx.draw_networkx_edges(g, pos, edgelist=[edge], ax=ax, edge_color=color,
                               width=graphicOptions.edge_size[edge], arrows=is_directed, node_size = node_size, **kwargs)


@__ignore_unused_args
def draw_extra_node(
    h: Hypergraph,
    u=None,
    k=2,
    weight_positioning=0,
    respect_planarity=False,
    cardinality: tuple[int, int] | int = -1,
    x_heaviest: float = 1.0,
    draw_labels: bool = True,
    ignore_binary_relations: bool = True,
    show_edge_nodes=True,
    draw_edge_graph=False,
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
    h : Hypergraph.
        The hypergraph to be projected.
    u : any, optional
        Represents the fuzzy partition of the nodes.
    k : int, optional
        The number of communities to consider for the fuzzy partition.
    weight_positioning : int
        Controls how edge weights influence node positioning.
    respect_planarity : bool
        If True, uses a planar layout for planar graphs.
    cardinality: tuple[int,int]|int. optional
        Filters hyperedges based on their cardinality.
    x_heaviest: float, optional
        Filters hyperedges to show only the heaviest x percent.
    draw_labels : bool
        Whether to draw node labels.
    ignore_binary_relations : bool
        If True, edges of cardinality 2 are not considered for the layout.
    show_edge_nodes : bool
        If True, draws the nodes representing hyperedges.
    draw_edge_graph: bool
        If True, draws the intermediate graph of hyperedge relations.
    pos : dict.
        A dictionary of node positions.
    iterations : int
        Number of iterations for the spring layout algorithm.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    figsize : tuple, optional
        Figure size.
    dpi : int, optional
        Figure DPI.
    graphicOptions: Optional[GraphicOptions].
        Graphical settings for the representation.
    kwargs : dict.
        Keyword arguments passed to networkx.draw_networkx.
    Returns
    -------
    dict
        A dictionary of node positions.
    """
    data = _compute_extra_node_drawing_data(h, cardinality, x_heaviest, ignore_binary_relations,
                                            weight_positioning, respect_planarity, draw_edge_graph,
                                            iterations, pos, u, k, graphicOptions)
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    _draw_extra_node_on_ax(ax, data, u, show_edge_nodes, draw_labels, **kwargs)

    ax.set_aspect('auto')
    ax.autoscale(enable=True, axis='both')
    ax.axis("off")
    plt.tight_layout()
    return data['pos']


# =============================================================================
# Internal Helpers for Extra-Node Drawing
# =============================================================================

def _edges_graph_creation(hyperedges_relations: dict, edgeList: list, drawing: bool = False) -> dict:
    """
    Create a graph using the relations between hyperedges..
    """
    edges_graph = nx.Graph()
    edges_graph.add_nodes_from(edgeList)

    for edge_pair, weight in hyperedges_relations.items():
        edges_graph.add_edge(edge_pair[0], edge_pair[1], weight=weight)

    if is_planar(edges_graph):
        posEdges = nx.planar_layout(edges_graph)
    else:
        pos = nx.spectral_layout(edges_graph)
        toImprovePos = nx.kamada_kawai_layout(edges_graph, pos=pos)
        posEdges = nx.spring_layout(edges_graph, k=0.5, pos=toImprovePos, weight="weight")

    if drawing:
        plt.figure(figsize=(12, 12))
        nx.draw_networkx(edges_graph, pos=posEdges, with_labels=True)
        plt.title("Hyperedge Relation Graph")
        plt.show()

    return posEdges


def _hyperedges_relations_detection(h: Hypergraph, obj_to_id: dict) -> dict:
    """
    Calculate the number of common nodes between pairs of hyperedges.
    """
    hyperedges_relations = {}
    edges = list(h.get_edges())

    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            edge1, edge2 = edges[i], edges[j]
            if len(edge1) > 2 and len(edge2) > 2:
                id1, id2 = obj_to_id[edge1], obj_to_id[edge2]
                if id1 != id2:
                    common_nodes = len(set(edge1).intersection(set(edge2)))
                    if common_nodes > 0:
                        pair = tuple(sorted((id1, id2)))
                        hyperedges_relations.setdefault(pair, 0)
                        hyperedges_relations[pair] += common_nodes

    return hyperedges_relations