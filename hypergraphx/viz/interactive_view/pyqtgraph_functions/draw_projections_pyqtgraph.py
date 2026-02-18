from typing import Optional, Any

import networkx as nx

from hypergraphx import DirectedHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __ignore_unused_args, _get_node_community
from hypergraphx.viz.interactive_view.pyqtgraph_functions.support import _draw_community_nodes, _draw_single_node_pyqt, \
    _draw_node_label, _draw_edge
import pyqtgraph as pg


@__ignore_unused_args
def _draw_bipartite_pyqtgraph(
        data: dict,
        u: Optional[Any],
        draw_labels: bool,
        align: str,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,
) -> pg.GraphicsLayoutWidget:
    """Performs the actual drawing of the bipartite projection on a given Axes object."""
    g = data['graph']
    pos = data['pos']
    id_to_obj = data['id_to_obj']
    mapping = data['mapping']
    col = data['col']
    hypergraph = data['hypergraph']

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

    # Draw edges and nodes
    node_list = [x for x in g.nodes() if x.startswith('N')]
    is_directed = isinstance(hypergraph, DirectedHypergraph)

    for node in node_list:
        if u is None:
            _draw_single_node_pyqt(
                plot = plot,
                x = pos[node][0], y = pos[node][1],
                node = node,
                graphicOptions = graphicOptions,
            )
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping, id_to_obj[node], u, col, 0.01)
            _draw_community_nodes(
                plot=plot,
                node=node,
                graphicOptions=graphicOptions,
                pos=pos[node],
                data=wedge_sizes,
                wedge_colors=wedge_colors,
            )

    # Draw nodes that represent edges
    edge_list = [x for x in g.nodes() if x.startswith('E')]
    for edge in edge_list:
        _draw_single_node_pyqt(
            plot=plot,
            x=pos[edge][0], y=pos[edge][1],
            node=edge,
            graphicOptions=graphicOptions,
            edge_node=True
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
        data: dict,
        u: Optional[Any],
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,

) -> pg.GraphicsLayoutWidget:
    """Performs the actual drawing of the clique projection on a given Axes object."""
    g = data['graph']
    pos = data['pos']
    mapping = data['mapping']
    col = data['col']

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

    for edge in g.edges():
        _draw_edge(
            plot=plot,
            pos_source=pos[edge[0]],
            pos_destination=pos[edge[1]],
            width=graphicOptions.edge_size[edge],
            edge_color=graphicOptions.edge_color[edge],
        )

    for node in g.nodes():
        if u is None:
            _draw_single_node_pyqt(
                plot=plot,
                x=pos[node][0], y=pos[node][1],
                node=node,
                graphicOptions=graphicOptions,
            )
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.01)
            _draw_community_nodes(
                plot=plot,
                node=node,
                graphicOptions=graphicOptions,
                pos=pos[node],
                data=wedge_sizes,
                wedge_colors=wedge_colors,
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
        data: dict,
        u: Optional[Any],
        show_edge_nodes: bool,
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,
        **kwargs
) -> pg.GraphicsLayoutWidget:
    """Performs the actual drawing of the extra-node projection on a given Axes object."""
    g = data['graph']
    pos = data['pos']
    mapping = data['mapping']
    col = data['col']
    hypergraph = data['hypergraph']

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

    is_directed = isinstance(hypergraph, DirectedHypergraph)
    is_weighted = hypergraph.is_weighted()

    # Draw edges and nodes
    node_list = [x for x in g.nodes() if not str(x).startswith('E')]
    for node in node_list:
        if mapping is None:
            _draw_single_node_pyqt(
                plot, x=pos[node][0], y=pos[node][1],
                node=node, graphicOptions=graphicOptions
            )
        else:
            wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
            _draw_community_nodes(
                plot=plot,
                node=node, graphicOptions=graphicOptions,
                pos=pos[node],
                data=wedge_sizes, wedge_colors=wedge_colors,
            )

    # Draw nodes that represent edges
    if show_edge_nodes:
        edge_list = [x for x in g.nodes() if str(x).startswith('E')]
        for edge in edge_list:
            _draw_single_node_pyqt(
                plot, x=pos[edge][0], y=pos[edge][1],
                node=edge, graphicOptions=graphicOptions,
                edge_node = True
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