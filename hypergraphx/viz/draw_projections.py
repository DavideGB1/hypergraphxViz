import math
from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx

from hypergraphx import Hypergraph, DirectedHypergraph, TemporalHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __ignore_unused_args, _draw_node_community
from hypergraphx.viz.layout_calculation.__layout_data import CommunityData
from hypergraphx.viz.layout_calculation.bipartite_layout import _compute_bipartite_drawing_data
from hypergraphx.viz.layout_calculation.clique_layout import _compute_clique_drawing_data
from hypergraphx.viz.layout_calculation.extra_node_layout import _compute_extra_node_drawing_data


def __convert_temporal_to_list(h, figsize, dpi, ax=None):
    """Convert temporal hypergraph to list of hypergraphs for plotting."""
    hypergraphs = dict()
    if isinstance(h, TemporalHypergraph):
        hypergraphs = h.subhypergraph()
    else:
        hypergraphs[0] = h
    n_times = len(hypergraphs)
    n_rows = math.ceil(math.sqrt(n_times))
    n_cols = math.ceil(n_times / n_rows)
    if ax is None:
        if n_times == 1:
            fig, axs_flat = plt.subplots(figsize=figsize, dpi=dpi)
        else:
            fig, axs = plt.subplots(n_rows, n_cols, figsize=figsize, dpi=dpi)
            axs_flat = axs.flat
    else:
        axs_flat = ax

    return hypergraphs, n_times, axs_flat


# =============================================================================
# Bipartite Projection Drawing
# =============================================================================

@__ignore_unused_args
def draw_bipartite(
        hypergraph: Hypergraph | DirectedHypergraph | TemporalHypergraph,
        community_data: Optional[CommunityData] = None,

        draw_labels=True,
        align='vertical',
        pos=None,
        ax: Optional[plt.Axes] = None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = None,
        **kwargs
):
    """
    Draws a bipartite graph representation of the hypergraph.

    Parameters
    ----------
    h : Hypergraph | DirectedHypergraph
        The hypergraph to be projected.
    u : any, optional
        Represents the fuzzy partition of the nodes.
    k : int, optional
        The number of communities to consider for the fuzzy partition.
    cardinality : tuple[int,int] | int, optional
        Filters hyperedges based on their cardinality.
    x_heaviest : float, optional
        Filters hyperedges to show only the heaviest x percent.
    draw_labels : bool
        Whether to draw node and edge labels.
    align : str
        The alignment of the nodes ('vertical' or 'horizontal').
    pos : dict, optional
        A dictionary of node positions.
    ax : matplotlib.axes.Axes, optional
        The axes to draw the graph on.
    figsize : tuple, optional
        Figure size.
    dpi : int, optional
        Figure DPI.
    graphicOptions : Optional[GraphicOptions]
        Graphical settings for the representation.
    show : bool
        If True, call plt.show().
    kwargs : dict
        Keyword arguments passed to networkx.draw_networkx.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes the graph was drawn on.
    """
    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    if align not in {"vertical", "horizontal"}:
        raise ValueError("align must be 'vertical' or 'horizontal'.")

    hypergraphs, n_times, axs_flat = __convert_temporal_to_list(hypergraph, figsize, dpi, ax)
    user_pos = pos
    for i, (time, hypergraph) in enumerate(hypergraphs.items()):
        if n_times != 1:
            current_ax = axs_flat[i]
        else:
            current_ax = axs_flat

        layout_data = _compute_bipartite_drawing_data(
            hypergraph=hypergraph,
            align=align,
            pos = user_pos
        )
        g = layout_data.graph
        pos = layout_data.pos
        id_to_obj = layout_data.id_to_obj
        hypergraph = layout_data.hypergraph

        graphicOptions.check_if_options_are_valid(g)

        # Draw edges and nodes
        node_list = [x for x in g.nodes() if x.startswith('N')]
        is_directed = isinstance(hypergraph, DirectedHypergraph)

        for node in node_list:
            if community_data is None:
                nx.draw_networkx_nodes(
                    G=g, ax=current_ax,
                    pos=pos,
                    nodelist=[node],
                    node_shape=graphicOptions.node_shape[node],
                    node_color=graphicOptions.node_color[node],
                    node_size=graphicOptions.node_size[node]*10,
                    edgecolors=graphicOptions.node_facecolor[node],
                    **kwargs
                )
            else:
                wedge_sizes, wedge_colors = community_data.node_community_mapping[id_to_obj[node]]
                _draw_node_community(
                    ax=current_ax,
                    node=node,
                    pos=pos[node],
                    ratios=wedge_sizes,
                    colors=wedge_colors,
                    graphicOptions=graphicOptions,
                    **kwargs
                )

        # Draw nodes that represent edges
        edge_list = [x for x in g.nodes() if x.startswith('E')]
        for edge in edge_list:
            nx.draw_networkx_nodes(
                G=g,
                ax=current_ax,
                pos=pos,
                node_shape=graphicOptions.edge_shape[edge],
                edgecolors=graphicOptions.node_facecolor[edge],
                node_color=graphicOptions.edge_node_color[edge],
                node_size=graphicOptions.node_size[edge]*10,
                nodelist=[edge],
                **kwargs
            )

        # Draw labels
        if draw_labels:
            labels = {n: id_to_obj[n] for n in g.nodes() if n.startswith('N')}
            labels_edge = {n: n for n in g.nodes() if n.startswith('E')}
            labels.update(labels_edge)
            nx.draw_networkx_labels(
                G=g,
                ax=current_ax,
                pos=pos,
                labels=labels,
                font_size=graphicOptions.label_size,
                font_color=graphicOptions.label_color,
                **kwargs
            )

        if hypergraph.is_weighted():
            labels = nx.get_node_attributes(g, 'weight')
            pos_offsetted = {}
            offset = 0.1
            for k_pos, v_pos in pos.items():
                pos_offsetted[k_pos] = (
                    (v_pos[0], v_pos[1] + offset) if align == 'horizontal'
                    else (v_pos[0] + offset, v_pos[1])
                )
            nx.draw_networkx_labels(
                G=g,
                ax=current_ax,
                pos=pos_offsetted,
                labels=labels,
                font_size=graphicOptions.weight_size,
                font_color=graphicOptions.label_color,
                **kwargs
            )

        for edge in g.edges():
            if is_directed:
                color = (
                    graphicOptions.in_edge_color if isinstance(edge[1], str) and edge[1].startswith('E')
                    else graphicOptions.out_edge_color
                )
            else:
                color = graphicOptions.edge_color[edge]
            node_size = max(graphicOptions.node_size[edge[0]], graphicOptions.node_size[edge[1]])
            nx.draw_networkx_edges(
                G=g,
                pos=pos,
                edgelist=[edge],
                ax=current_ax,
                edge_color=color,
                width=graphicOptions.edge_size[edge],
                arrows=is_directed,
                node_size=node_size,
                **kwargs
            )

        current_ax.set_aspect('auto')
        current_ax.autoscale(enable=True, axis='both')
        current_ax.axis("off")

        if n_times != 1:
            current_ax.set_title(f"Hypergraph at time {time}")

    if n_times != 1:
        for ax_item in axs_flat[n_times:]:
            ax_item.set_visible(False)

    plt.tight_layout()


    return axs_flat

# =============================================================================
# Clique Projection Drawing
# =============================================================================

def draw_clique(
        hypergraph: Hypergraph | TemporalHypergraph,
        community_data: Optional[CommunityData] = None,

        draw_labels=True,
        iterations: int = 1000,
        pos=None,
        ax: Optional[plt.Axes] = None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = None,
        **kwargs
):
    """
    Draws a clique projection of the hypergraph.

    Parameters
    ----------
    hypergraph : Hypergraph
        The hypergraph to be projected.
    draw_labels : bool
        Whether to draw node labels.
    iterations : int
        Number of iterations for the spring layout algorithm.
    weight_positioning : int
        Controls how edge weights influence positioning.
    pos : dict, optional
        A dictionary of node positions.
    ax : matplotlib.axes.Axes, optional
        The axes to draw the graph on.
    figsize : tuple, optional
        Figure size.
    dpi : int, optional
        Figure DPI.
    graphicOptions : Optional[GraphicOptions]
        Graphical settings for the representation.
    kwargs : dict
        Keyword arguments passed to networkx.draw_networkx.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes the graph was drawn on.
    """
    if isinstance(hypergraph, DirectedHypergraph):
        raise ValueError("Clique Projections is not able to represent directed hypergraphs.")
    if hypergraph.is_weighted():
        print("WARNING: Clique Projections is not able to represent weighted hypergraphs. Weights will be ignored")
    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    hypergraphs, n_times, axs_flat = __convert_temporal_to_list(hypergraph, figsize, dpi, ax)
    user_pos = pos
    for i, (time, hypergraph) in enumerate(hypergraphs.items()):
        if n_times != 1:
            current_ax = axs_flat[i]
        else:
            current_ax = axs_flat

        layout_data = _compute_clique_drawing_data(
            hypergraph = hypergraph,
            iterations = iterations,
            pos = user_pos
        )
        g = layout_data.graph
        pos = layout_data.pos

        graphicOptions.check_if_options_are_valid(g)

        for edge in g.edges():
            nx.draw_networkx_edges(
                G=g,
                pos=pos,
                edgelist=[edge],
                ax=current_ax,
                edge_color=graphicOptions.edge_color[edge],
                width=graphicOptions.edge_size[edge],
                **kwargs
            )

        for node in g.nodes():
            if community_data is None:
                nx.draw_networkx_nodes(
                    G = g, pos = pos,
                    nodelist=[node],
                    node_size=graphicOptions.node_size[node]*10,
                    node_shape=graphicOptions.node_shape[node],
                    node_color=graphicOptions.node_color[node],
                    edgecolors=graphicOptions.node_facecolor[node],
                    ax=current_ax,
                    **kwargs
                )
            else:
                wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
                _draw_node_community(
                    ax = current_ax,
                    node = node,
                    center= pos[node],
                    ratios=wedge_sizes,
                    colors=wedge_colors,
                    graphicOptions=graphicOptions,
                    **kwargs
                )

        if draw_labels:
            labels = {n: n for n in g.nodes()}
            nx.draw_networkx_labels(
                G=g,
                pos=pos,
                ax=current_ax,
                labels=labels,
                font_size=graphicOptions.label_size,
                font_color=graphicOptions.label_color,
                **kwargs
            )

        current_ax.set_aspect('auto')
        current_ax.autoscale(enable=True, axis='both')
        current_ax.axis("off")

        if n_times != 1:
            current_ax.set_title(f"Hypergraph at time {time}")

    if n_times != 1:
        for ax_item in axs_flat[n_times:]:
            ax_item.set_visible(False)

    plt.tight_layout()

    return axs_flat

# =============================================================================
# Extra-Node Projection Drawing
# =============================================================================

@__ignore_unused_args
def draw_extra_node(
        h: Hypergraph | DirectedHypergraph | TemporalHypergraph,
        community_data: Optional[CommunityData] = None,
        weight_positioning=0,
        respect_planarity=False,
        draw_labels: bool = True,
        ignore_binary_relations: bool = True,
        show_edge_nodes=True,
        draw_edge_graph=False,
        pos: dict = None,
        iterations: int = 1000,
        ax=None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = None,
        **kwargs
):
    """
    Draws an extra-node projection of the hypergraph.

    Parameters
    ----------
    h : Hypergraph
        The hypergraph to be projected.
    weight_positioning : int
        Controls how edge weights influence node positioning.
    respect_planarity : bool
        If True, uses a planar layout for planar graphs.
    draw_labels : bool
        Whether to draw node labels.
    ignore_binary_relations : bool
        If True, edges of cardinality 2 are not considered for the layout.
    show_edge_nodes : bool
        If True, draws the nodes representing hyperedges.
    draw_edge_graph : bool
        If True, draws the intermediate graph of hyperedge relations.
    pos : dict, optional
        A dictionary of node positions.
    iterations : int
        Number of iterations for the spring layout algorithm.
    ax : matplotlib.axes.Axes, optional
        The axes to draw the graph on.
    figsize : tuple, optional
        Figure size.
    dpi : int, optional
        Figure DPI.
    graphicOptions : Optional[GraphicOptions]
        Graphical settings for the representation.
    kwargs : dict
        Keyword arguments passed to networkx.draw_networkx.
    """
    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    hypergraphs, n_times, axs_flat = __convert_temporal_to_list(h, figsize, dpi, ax)
    user_pos = pos
    for i, (time, hypergraph) in enumerate(hypergraphs.items()):
        if n_times != 1:
            current_ax = axs_flat[i]
        else:
            current_ax = axs_flat

        layout_data = _compute_extra_node_drawing_data(
            hypergraph, ignore_binary_relations,
            weight_positioning, respect_planarity, iterations, user_pos, draw_edge_graph
        )
        g = layout_data.graph
        pos = layout_data.pos
        hypergraph = layout_data.hypergraph

        graphicOptions.check_if_options_are_valid(g)

        is_directed = isinstance(hypergraph, DirectedHypergraph)
        is_weighted = hypergraph.is_weighted()

        # Draw edges and nodes
        node_list = [x for x in g.nodes() if not str(x).startswith('E')]
        for node in node_list:
            if community_data is None:
                nx.draw_networkx_nodes(
                    g, pos, nodelist=[node], node_size=graphicOptions.node_size[node]*10,
                    node_shape=graphicOptions.node_shape[node], node_color=graphicOptions.node_color[node],
                    edgecolors=graphicOptions.node_facecolor[node], ax=current_ax, **kwargs
                )
            else:
                wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
                _draw_node_community(
                    ax=current_ax,
                    node=node,
                    center=pos[node],
                    ratios=wedge_sizes,
                    colors=wedge_colors,
                    graphicOptions=graphicOptions,
                    **kwargs
                )

        # Draw nodes that represent edges
        if show_edge_nodes:
            edge_list = [x for x in g.nodes() if str(x).startswith('E')]
            for edge in edge_list:
                nx.draw_networkx_nodes(
                    g, pos, nodelist=[edge], node_size=graphicOptions.node_size[edge]*10,
                    node_shape=graphicOptions.edge_shape[edge], node_color=graphicOptions.edge_node_color[edge],
                    edgecolors=graphicOptions.node_facecolor[edge], ax=current_ax, **kwargs
                )
            if is_weighted:
                labels = nx.get_node_attributes(g, 'weight')
                nx.draw_networkx_labels(
                    g, ax=current_ax, pos=pos, labels=labels, font_size=graphicOptions.weight_size,
                    font_color=graphicOptions.label_color, **kwargs
                )

        # Draw labels
        if draw_labels:
            labels = {n: n for n in g.nodes() if not str(n).startswith('E')}
            nx.draw_networkx_labels(
                g, ax=current_ax, pos=pos, labels=labels, font_size=graphicOptions.label_size,
                font_color=graphicOptions.label_color, **kwargs
            )

        for edge in g.edges():
            if is_directed:
                color = (
                    graphicOptions.in_edge_color if isinstance(edge[1], str) and edge[1].startswith('E')
                    else graphicOptions.out_edge_color
                )
            else:
                color = graphicOptions.edge_color[edge]
            node_size = max(graphicOptions.node_size[edge[0]], graphicOptions.node_size[edge[1]])
            nx.draw_networkx_edges(
                g, pos, edgelist=[edge], ax=current_ax, edge_color=color,
                width=graphicOptions.edge_size[edge], arrows=is_directed, node_size=node_size, **kwargs
            )

        current_ax.set_aspect('auto')
        current_ax.autoscale(enable=True, axis='both')
        current_ax.axis("off")

        if n_times != 1:
            current_ax.set_title(f"Hypergraph at time {time}")

    if n_times != 1:
        for ax_item in axs_flat[n_times:]:
            ax_item.set_visible(False)

    plt.tight_layout()