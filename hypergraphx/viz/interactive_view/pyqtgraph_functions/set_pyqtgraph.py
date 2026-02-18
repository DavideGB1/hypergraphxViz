import math
from typing import Optional

import numpy as np
import pyqtgraph as pg
from IPython.external.qt_for_kernel import QtCore
from PyQt5 import QtGui

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import _get_node_community
from hypergraphx.viz.interactive_view.pyqtgraph_functions.support import _draw_community_nodes, _draw_single_node_pyqt, \
    _draw_edge, _draw_node_label


def create_fixed_rounded_polygon(points, radius):
    path = QtGui.QPainterPath()
    n = len(points)
    if n < 3: return path

    # Convertiamo in QPointF per comodità
    pts = [QtCore.QPointF(p[0], p[1]) for p in points]

    for i in range(n):
        # Tre punti consecutivi: precedente, attuale (l'angolo), successivo
        p1 = pts[(i - 1) % n]
        p2 = pts[i]
        p3 = pts[(i + 1) % n]

        # Vettori dei lati che convergono nell'angolo p2
        v1 = p1 - p2
        v2 = p3 - p2

        # Normalizzazione dei vettori
        len1 = np.sqrt(v1.x() ** 2 + v1.y() ** 2)
        len2 = np.sqrt(v2.x() ** 2 + v2.y() ** 2)

        # Accorciamo il raggio se i segmenti sono troppo corti
        current_radius = min(radius, len1 / 2, len2 / 2)

        # Punti di inizio e fine della curva (distanti 'radius' dal vertice)
        start_point = p2 + (v1 / len1) * current_radius
        end_point = p2 + (v2 / len2) * current_radius

        if i == 0:
            path.moveTo(start_point)
        else:
            path.lineTo(start_point)

        # Crea la curva usando il vertice p2 come punto di controllo
        path.quadTo(p2, end_point)

    path.closeSubpath()
    return path

def _draw_set_pyqtgraph(
        data: dict,
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        widget: Optional[pg.GraphicsLayoutWidget] = None,
        **kwargs
) -> pg.GraphicsLayoutWidget:
    """
    Draws the elements of the set visualization onto a given matplotlib Axes object.
    This function uses pre-computed layout and style information.
    """
    pos, G, dummy_nodes = data["pos"], data["G"], data["dummy_nodes"]
    if widget is None:
        widget = pg.GraphicsLayoutWidget()
        widget.resize(1000, 800)

    if graphicOptions is None:
        graphicOptions = GraphicOptions()
    graphicOptions.check_if_options_are_valid(G)

    plot = widget.addPlot()
    plot.setLabel('left', "", **{'font-size': '0pt'})
    plot.setLabel('bottom', "", **{'font-size': '0pt'})
    plot.showGrid(x=False, y=True, alpha=0.3)
    plot.getAxis('bottom').setTicks([])
    plot.getAxis('left').setTicks([])


    # 1. Draw higher-order hyperedges
    for hye_info in data["hyperedges_to_draw"]:
        facecolor = QtGui.QColor(hye_info["facecolor"])
        facecolor.setAlpha(int(255 * hye_info["alpha"]))
        face_brush = pg.mkBrush(color=facecolor)
        edge_pen = pg.mkPen(color=hye_info["color"], width=1.5)

        if hye_info["rounded"]:
            """_draw_hyperedge_set(
                points=hye_info["points"], radius=hye_info["radius"], hyperedge_alpha=hye_info["alpha"],
                border_color=hye_info["color"], face_color=hye_info["facecolor"], ax=ax
            )"""
            rounded_path = create_fixed_rounded_polygon(points=hye_info["points"], radius=hye_info["radius"],)
            polygon = pg.QtWidgets.QGraphicsPathItem(rounded_path)
        else:
            polygon = pg.QtWidgets.QGraphicsPolygonItem(
                QtGui.QPolygonF([QtCore.QPointF(p[0], p[1]) for p in hye_info["points"]])
            )
        polygon.setBrush(face_brush)
        polygon.setPen(edge_pen)
        plot.addItem(polygon)

        if hye_info["weight_label"]:
            _draw_node_label(
                plot=plot,
                x = hye_info["weight_pos"][0], y = hye_info["weight_pos"][1],
                text=hye_info["weight_label"],
                font_size=graphicOptions.weight_size,
                text_color=graphicOptions.label_color,
            )

    # 2. Draw binary edges and their labels
    if data["edge_labels_info"]:
        labels, pos_higher = data["edge_labels_info"]
    for edge in G.edges():
        _draw_edge(
            plot=plot,
            pos_source=pos[edge[0]], pos_destination=pos[edge[1]],
            width=graphicOptions.edge_size[edge],
            edge_color=graphicOptions.edge_color[edge],
        )
        if data["edge_labels_info"]:
            pos_x = (pos[edge[0]][0]+pos[edge[1]][0])/2
            pos_y = (pos[edge[0]][1]+pos[edge[1]][1])/2

            _draw_node_label(
                plot=plot,
                x=pos_x, y=pos_y+0.05,
                text=labels[edge],
                font_size=graphicOptions.weight_size,
                text_color=graphicOptions.label_color
            )

    # 3. Draw nodes
    community_info = data["community_info"]
    for node in G.nodes():
        if node not in dummy_nodes:
            if not community_info:

                _draw_single_node_pyqt(
                    plot=plot,
                    x=pos[node][0], y=pos[node][1],
                    node=node, graphicOptions=graphicOptions,
                )
            else:
                mapping, col, u = community_info
                wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
                _draw_community_nodes(
                    plot=plot,
                    node=node, graphicOptions=graphicOptions,
                    pos=pos[node],
                    data=wedge_sizes, wedge_colors=wedge_colors
                )

    # 4. Draw node labels
    if draw_labels:
        labels = {n: n for n in G.nodes() if n not in dummy_nodes}
        for node in labels.keys():
            _draw_node_label(
                plot=plot,
                x=pos[node][0], y=pos[node][1],
                text=labels[node],
                font_size=int(graphicOptions.label_size),
                text_color=graphicOptions.label_color
            )

    return widget

#Pesi non va
#Polygon expansion factor più dinamico in base a dove arriva il nodo 8così lo incapsula sempr