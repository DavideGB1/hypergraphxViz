import math
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import _get_node_community
from hypergraphx.viz.interactive_view.pyqtgraph_functions.support import _draw_community_nodes, _draw_single_node_pyqt


def _draw_radial_elements_pyqt(
    data: dict,
    draw_labels: bool,
    font_spacing_factor: float,
    graphicOptions: GraphicOptions,
    widget: Optional[pg.GraphicsLayoutWidget] = None,
    **kwargs
) -> pg.GraphicsLayoutWidget:
    """

    Draws the elements of the radial layout onto a given matplotlib Axes object.
    """
    # Unpack computed data for clarity
    h = data["hypergraph"]
    if widget is None:
        widget = pg.GraphicsLayoutWidget()
        widget.resize(1000, 800)

    if h.num_nodes() == 0:
        return  widget

    pos = data["pos"]
    radius, alpha = data["radius"], data["alpha"]
    nodes_mapping = data["nodes_mapping"]
    sector_list, binary_edges = data["sector_list"], data["binary_edges"]
    is_directed, edge_directed_mapping = data["is_directed"], data["edge_directed_mapping"]
    community_info = data["community_info"]
    if graphicOptions is None:
        graphicOptions = GraphicOptions()
    graphicOptions.check_if_options_are_valid(h)

    plot = widget.addPlot()
    plot.setLabel('left', "", **{'font-size': '0pt'})
    plot.setLabel('bottom', "", **{'font-size': '0pt'})
    plot.showGrid(x=False, y=True, alpha=0.3)
    plot.getAxis('bottom').setTicks([])
    plot.getAxis('left').setTicks([])


    # Draw binary edges
    for edge in binary_edges:
        p1, p2 = pos[edge[0]], pos[edge[1]]

        # Disegna la linea dell'edge
        edge_color = graphicOptions.edge_color.get(edge, 'k')
        edge_width = graphicOptions.edge_size.get(edge, 2)

        # Converti colore matplotlib in formato PyQtGraph
        pen = pg.mkPen(color=edge_color, width=edge_width)

        line = pg.PlotDataItem([p1[0], p2[0]], [p1[1], p2[1]], pen=pen)
        plot.addItem(line)
        if h.is_weighted():
            weight_val = h.get_weight(edge)
            weight_text = pg.TextItem(str(weight_val), anchor=(0.5, 0.5), color=(0, 0, 0))
            wx = (p1[0] + p2[0]) / 2
            wy = (p1[1] + p2[1]) / 2
            weight_text.setPos(wx, wy+0.25)
            weight_text.setFont(QtGui.QFont('Arial', graphicOptions.weight_size))
            weight_text.setZValue(100)
            plot.addItem(weight_text)

    # Draw nodes and labels
    bounds = {"max_x": -math.inf, "min_x": math.inf, "max_y": -math.inf, "min_y": math.inf}
    for node in h.get_nodes():
        vx, vy = pos[node]
        bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], vx), min(bounds["min_x"], vx)
        bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], vy), min(bounds["min_y"], vy)

        if community_info:
            mapping, col, u = community_info
            wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
            _draw_community_nodes(
                plot = plot,
                node = node,
                graphicOptions = graphicOptions,
                pos = pos[node],
                data=wedge_sizes,
                wedge_colors = wedge_colors,
            )
        else:
            _draw_single_node_pyqt(
                plot=plot,
                x=vx, y=vy,
                node=node,
                graphicOptions = graphicOptions,
            )
        if draw_labels:
            lx, ly = vx * font_spacing_factor, vy * font_spacing_factor
            node_label = pg.TextItem(str(node), anchor=(0.5, 0.5), color=(0, 0, 0))
            node_label.setPos(lx, ly)
            node_label.setFont(QtGui.QFont('Arial', graphicOptions.weight_size))
            node_label.setZValue(100)
            plot.addItem(node_label)
            bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], lx), min(bounds["min_x"], lx)
            bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], ly), min(bounds["min_y"], ly)

    # Draw sectors and hyperedges
    sector_depth = font_spacing_factor + 1 if draw_labels else 1
    sector_depth += 0.5
    for sector in sector_list:
        for edge in sorted(sector):
            sorted_edge_nodes = sorted(edge)
            start_idx = nodes_mapping.transform([sorted_edge_nodes[0]])[0]
            end_idx = nodes_mapping.transform([sorted_edge_nodes[-1]])[0]

            theta = np.linspace(alpha * start_idx, alpha * end_idx, 100)
            arc_x = [round(math.cos(a), 5) * radius * sector_depth for a in theta]
            arc_y = [round(math.sin(a), 5) * radius * sector_depth for a in theta]
            arc = pg.PlotCurveItem(
                arc_x, arc_y,
                pen=pg.mkPen(color=graphicOptions.edge_color[edge],
                             width=graphicOptions.edge_size[edge])
            )
            plot.addItem(arc)
            # Place nodes along the arc
            for node in sorted_edge_nodes:
                vx, vy = pos[node][0] * sector_depth, pos[node][1] * sector_depth
                bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], vx), min(bounds["min_x"], vx)
                bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], vy), min(bounds["min_y"], vy)

                if is_directed:
                    true_edge = edge_directed_mapping[edge]
                    color = graphicOptions.in_edge_color if node in true_edge[0] else graphicOptions.out_edge_color
                    _draw_single_node_pyqt(
                        plot=plot,
                        x=vx, y=vy,
                        node=node,
                        graphicOptions=graphicOptions,
                        node_color=color,
                        edge_node=True
                    )
                else:
                    _draw_single_node_pyqt(
                        plot=plot,
                        x=vx, y=vy,
                        node=node,
                        graphicOptions = graphicOptions,
                        edge_node=True
                    )

            # Draw weight labels for hyperedges
            if h.is_weighted():
                mid_angle = (alpha * start_idx + alpha * end_idx) / 2
                wx = round(math.cos(mid_angle), 5) * radius * (sector_depth + 0.15)
                wy = round(math.sin(mid_angle), 5) * radius * (sector_depth + 0.15)
                weight_val = h.get_weight(edge)
                weight_label = pg.TextItem(str(weight_val), anchor=(0.5, 0.5), color=(0, 0, 0))
                weight_label.setPos(wx, wy)
                weight_label.setFont(QtGui.QFont('Arial', graphicOptions.weight_size))
                weight_label.setZValue(100)
                plot.addItem(weight_label)


        sector_depth += 0.35

    # Finalize axis
    max_dim_x = max(bounds["max_x"], abs(bounds["min_x"]))
    max_dim_y = max(bounds["max_y"], abs(bounds["min_y"]))
    plot.setXRange(-max_dim_x - 1, max_dim_x + 1, padding=0)
    plot.setYRange(-max_dim_y - 1, max_dim_y + 1, padding=0)
    plot.setAspectLocked(True)
    plot.hideAxis('left')
    plot.hideAxis('bottom')

    return widget

#Fix position labels
#Check if hyperdges are actually working correctly
#Temporal not working