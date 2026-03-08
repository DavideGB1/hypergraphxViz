from typing import Optional

import networkx as nx

from hypergraphx import DirectedHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __ignore_unused_args
from hypergraphx.viz.interactive_view.pyqtgraph_functions.support import _draw_community_nodes, _draw_single_node_pyqt, \
    _draw_node_label, _draw_edge
import pyqtgraph as pg

from hypergraphx.viz.layout_calculation.__layout_data import BipartiteLayoutData, CommunityData, CliqueLayoutData, ExtraNodeLayoutData


def _adjust_pos_for_node_radius(pos: dict, node_size: float, padding_factor: float = 1.1) -> dict:
    """
    Rescales Y positions so that vertically stacked nodes have
    enough space between them based on their radius.

    node_size: radius of the nodes (same for all nodes in this case)
    padding_factor: extra multiplier > 1.0 to add a small gap between nodes
    """
    # Separate N and E nodes (they have independent Y columns)
    n_nodes = {k: v for k, v in pos.items() if k.startswith('N')}
    e_nodes = {k: v for k, v in pos.items() if k.startswith('E')}

    def rescale_column(nodes: dict) -> dict:
        if len(nodes) < 2:
            return nodes
        sorted_nodes = sorted(nodes.items(), key=lambda item: item[1][1])
        # Calcola lo spacing minimo richiesto
        min_spacing =  node_size * padding_factor
        # Calcola lo spacing attuale tra nodi adiacenti
        ys = [v[1] for _, v in sorted_nodes]
        current_spacing = abs(ys[1] - ys[0]) if len(ys) > 1 else min_spacing
        # Se lo spacing attuale è già sufficiente, non fare nulla
        if current_spacing >= min_spacing:
            return nodes
        scale = min_spacing / current_spacing
        # Applica il riscalamento mantenendo il centro verticale
        center_y = (ys[0] + ys[-1]) / 2
        rescaled = {}
        for k, v in nodes.items():
            new_y = center_y + (v[1] - center_y) * scale
            rescaled[k] = (v[0], new_y)
        return rescaled

    result = {}
    result.update(rescale_column(n_nodes))
    result.update(rescale_column(e_nodes))
    return result

@__ignore_unused_args
def _draw_bipartite_pyqtgraph(
        layout_data: BipartiteLayoutData,
        draw_labels: bool,
        align: str,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,
        community_data: Optional[CommunityData] = None
) -> pg.GraphicsLayoutWidget:
    """Performs the actual drawing of the bipartite projection on a given Axes object."""
    g = layout_data.graph
    pos = layout_data.pos
    id_to_obj = layout_data.id_to_obj
    hypergraph = layout_data.hypergraph

    if widget is None:
        widget = pg.GraphicsLayoutWidget()
        widget.resize(1000, 800)

    graphicOptions.check_if_options_are_valid(g)

    plot = widget.addPlot()
    plot.setLabel('left', "", **{'font-size': '0pt'})
    plot.setLabel('bottom', "", **{'font-size': '0pt'})
    plot.showGrid(x=False, y=True, alpha=0.3)
    plot.getAxis('bottom').setTicks([])
    plot.getAxis('left').setTicks([])
    plot.setAspectLocked(True)
    # Draw edges and nodes
    node_list = [x for x in g.nodes() if x.startswith('N')]
    is_directed = isinstance(hypergraph, DirectedHypergraph)
    pixel_size = max(plot.getViewBox().viewPixelSize())
    node_radius = graphicOptions.node_size[list(pos.keys())[0]] * pixel_size
    pos = _adjust_pos_for_node_radius(pos, node_radius, padding_factor=1.1)
    for node in node_list:
        if community_data is None:
            _draw_single_node_pyqt(
                plot = plot,
                x = pos[node][0], y = pos[node][1],
                node_color = graphicOptions.node_color[node],
                edge_color = graphicOptions.node_facecolor[node],
                size= graphicOptions.node_size[node]*pixel_size,
                shape= graphicOptions.node_shape[node]
            )
        else:
            wedge_sizes, wedge_colors = community_data.node_community_mapping[id_to_obj[node]]
            _draw_community_nodes(
                plot=plot,
                pos=pos[node],
                data=wedge_sizes,
                wedge_colors=wedge_colors,
                edge_color=graphicOptions.node_facecolor[node],
                size=graphicOptions.node_size[node]*pixel_size
            )

    # Draw nodes that represent edges
    edge_list = [x for x in g.nodes() if x.startswith('E')]
    for edge in edge_list:
        _draw_single_node_pyqt(
            plot=plot,
            x=pos[edge][0], y=pos[edge][1],
            node_color=graphicOptions.edge_node_color[edge],
            edge_color=graphicOptions.node_facecolor[edge],
            size=graphicOptions.node_size[edge]*pixel_size,
            shape=graphicOptions.edge_shape[edge]
        )

    # Draw labels
    if draw_labels:
        labels = {n: id_to_obj[n] for n in g.nodes() if n.startswith('N')}
        labels_edge = {n: n for n in g.nodes() if n.startswith('E')}
        labels.update(labels_edge)
        for node in g.nodes():
            _draw_node_label(
                plot=plot,
                x = pos[node][0], y = pos[node][1],
                text=labels[node],
                font_size=graphicOptions.label_size,
                text_color= graphicOptions.label_color
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
        for node in edge_list:
            _draw_node_label(
                plot=plot,
                x=pos_offsetted[node][0], y=pos_offsetted[node][1],
                text=labels[node],
                font_size=graphicOptions.weight_size,
                text_color=graphicOptions.label_color
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
        _draw_edge(
            plot=plot,
            pos_source=pos[edge[0]],
            pos_destination=pos[edge[1]],
            width=graphicOptions.edge_size[edge],
            is_directed=is_directed,
            node_size=node_size,
            edge_color=color,
        )

    return widget

@__ignore_unused_args
def _draw_clique_pyqtgraph(
        layout_data: CliqueLayoutData,
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,
        community_data: Optional[CommunityData] = None,
) -> pg.GraphicsLayoutWidget:
    """Performs the actual drawing of the clique projection on a given Axes object."""
    g = layout_data.graph
    pos = layout_data.pos

    if widget is None:
        widget = pg.GraphicsLayoutWidget()
        widget.resize(1000, 800)

    graphicOptions.check_if_options_are_valid(g)

    plot = widget.addPlot()
    plot.setLabel('left', "", **{'font-size': '0pt'})
    plot.setLabel('bottom', "", **{'font-size': '0pt'})
    plot.showGrid(x=False, y=True, alpha=0.3)
    plot.getAxis('bottom').setTicks([])
    plot.getAxis('left').setTicks([])
    plot.setAspectLocked(True)

    for edge in g.edges():
        _draw_edge(
            plot=plot,
            pos_source=pos[edge[0]],
            pos_destination=pos[edge[1]],
            width=graphicOptions.edge_size[edge],
            edge_color=graphicOptions.edge_color[edge],
        )

    pixel_size = max(plot.getViewBox().viewPixelSize())
    for node in g.nodes():
        if community_data is None:
            _draw_single_node_pyqt(
                plot=plot,
                x=pos[node][0], y=pos[node][1],
                node_color=graphicOptions.node_color[node],
                edge_color=graphicOptions.node_facecolor[node],
                size=graphicOptions.node_size[node] * pixel_size,
                shape=graphicOptions.node_shape[node]
            )
        else:
            wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
            _draw_community_nodes(
                plot=plot,
                pos=pos[node],
                data=wedge_sizes,
                wedge_colors=wedge_colors,
                edge_color=graphicOptions.node_facecolor[node],
                size=graphicOptions.node_size[node] * pixel_size
            )

    if draw_labels:
        labels = {n: n for n in g.nodes()}
        for node in g.nodes():
            _draw_node_label(
                plot=plot,
                x=pos[node][0], y=pos[node][1],
                text=labels[node],
                font_size=graphicOptions.label_size,
                text_color=graphicOptions.label_color
            )

    return widget

@__ignore_unused_args
def _draw_extra_node_pyqtgraph(
        layout_data: ExtraNodeLayoutData,
        show_edge_nodes: bool,
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,
        community_data: Optional[CommunityData] = None,
) -> pg.GraphicsLayoutWidget:
    """Performs the actual drawing of the extra-node projection on a given Axes object."""
    g = layout_data.graph
    pos = layout_data.pos
    hypergraph = layout_data.hypergraph

    if widget is None:
        widget = pg.GraphicsLayoutWidget()
        widget.resize(1000, 800)

    graphicOptions.check_if_options_are_valid(g)

    plot = widget.addPlot()
    plot.setLabel('left', "", **{'font-size': '0pt'})
    plot.setLabel('bottom', "", **{'font-size': '0pt'})
    plot.showGrid(x=False, y=True, alpha=0.3)
    plot.getAxis('bottom').setTicks([])
    plot.getAxis('left').setTicks([])
    plot.setAspectLocked(True)

    is_directed = isinstance(hypergraph, DirectedHypergraph)
    is_weighted = hypergraph.is_weighted()

    # Draw edges and nodes
    node_list = [x for x in g.nodes() if not str(x).startswith('E')]
    pixel_size = max(plot.getViewBox().viewPixelSize())
    for node in node_list:
        if community_data is None:
            _draw_single_node_pyqt(
                plot=plot,
                x=pos[node][0], y=pos[node][1],
                node_color=graphicOptions.node_color[node],
                edge_color=graphicOptions.node_facecolor[node],
                size=graphicOptions.node_size[node] * pixel_size,
                shape=graphicOptions.node_shape[node]
            )
        else:
            wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
            _draw_community_nodes(
                plot=plot,
                pos=pos[node],
                data=wedge_sizes,
                wedge_colors=wedge_colors,
                edge_color=graphicOptions.node_facecolor[node],
                size=graphicOptions.node_size[node] * pixel_size
            )

    # Draw nodes that represent edges
    if show_edge_nodes:
        edge_list = [x for x in g.nodes() if str(x).startswith('E')]
        for edge in edge_list:
            _draw_single_node_pyqt(
                plot=plot,
                x=pos[edge][0], y=pos[edge][1],
                node_color=graphicOptions.edge_node_color[edge],
                edge_color=graphicOptions.node_facecolor[edge],
                size=graphicOptions.node_size[edge] * pixel_size,
                shape=graphicOptions.edge_shape[edge]
            )
        if is_weighted:
            labels = nx.get_node_attributes(g, 'weight')
            for edge in edge_list:
                _draw_node_label(
                    plot=plot,
                    x=pos[edge][0], y=pos[edge][1],
                    text=labels[edge],
                    font_size=graphicOptions.weight_size,
                    text_color=graphicOptions.label_color
                )

    # Draw labels
    if draw_labels:
        labels = {n: n for n in g.nodes() if not str(n).startswith('E')}
        node_list = [n for n in g.nodes() if not str(n).startswith('E')]
        for node in node_list:
            _draw_node_label(
                plot=plot,
                x=pos[node][0], y=pos[node][1],
                text=labels[node],
                font_size=graphicOptions.label_size,
                text_color=graphicOptions.label_color
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
        _draw_edge(
            plot=plot,
            pos_source=pos[edge[0]],
            pos_destination=pos[edge[1]],
            width=graphicOptions.edge_size[edge],
            is_directed=is_directed,
            node_size=node_size,
            edge_color=color,
        )

    return widget