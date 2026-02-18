import copy
from typing import Optional, Any

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from hypergraphx.viz.__graphic_options import GraphicOptions

class PieNodeItem(QtWidgets.QGraphicsObject):
    def __init__(self, x, y, data, colors, size=20, border_color=None):
        super().__init__()
        self.x = x
        self.y = y
        self.data = data
        self.colors = [pg.mkColor(c) for c in colors]
        self.size = size/500
        self.border_color = border_color
        self.total = sum(data)

        self.setPos(x, y)
        self.setZValue(10)

    def paint(self, painter, option, widget):
        radius = self.size / 2
        rect = QtCore.QRectF(-radius, -radius, self.size, self.size)

        start_angle = 0
        for i, value in enumerate(self.data):
            if value <= 0: continue

            span_angle = (value / self.total) * 360

            path = QtGui.QPainterPath()
            path.moveTo(0, 0)
            path.arcTo(rect, start_angle, span_angle)

            painter.setBrush(self.colors[i])
            painter.setPen(pg.mkPen(self.border_color, width=0.5))
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.drawPath(path)

            start_angle += span_angle

    def boundingRect(self):
        radius = self.size / 2
        return QtCore.QRectF(-radius, -radius, self.size, self.size)

def _draw_single_node_pyqt(
        plot: pg.PlotItem,
        x: float,
        y: float,
        node: Any,
        graphicOptions: GraphicOptions,
        node_color: Optional[str] = None,
        edge_node: bool = False
) -> None:
    """
    Disegna un singolo nodo nel plot PyQtGraph.
    """
    # Ottieni le proprietà del nodo
    plot.setAspectLocked(True)
    if edge_node:
        color = node_color if node_color else graphicOptions.edge_node_color.get(node, 'r')
    else:
        color = node_color if node_color else graphicOptions.node_color.get(node, 'r')
    if edge_node:
        shape = graphicOptions.edge_shape.get(node, 'o')
    else:
        shape = graphicOptions.node_shape.get(node, 'o')
    edge_color = graphicOptions.node_facecolor.get(node, 'k')
    size = graphicOptions.node_size.get(node, 20)

    # Disegna il nodo
    scatter = pg.ScatterPlotItem(
        [x], [y],
        size=size/500,
        symbol=shape,
        brush=pg.mkBrush(color),
        pen=pg.mkPen(edge_color, width=1),
        pxMode=False
    )
    scatter.setZValue(10)
    plot.addItem(scatter)



# --- Classe per il Nodo PieChart ---


# --- Funzione richiesta ---

def _draw_community_nodes(
        plot: pg.PlotItem,
        node, graphicOptions: GraphicOptions,
        pos: tuple[float, float],
        data: list[float],
        wedge_colors: list,
) -> None:
    """
    Disegna un nodo a forma di pie chart in una specifica posizione del plot.
    """
    x, y = pos
    if len(data) > 1:
        border_color = graphicOptions.node_facecolor.get(node, 'k')
        size = graphicOptions.node_size.get(node, 20)

        pie_node = PieNodeItem(
            x=x,
            y=y,
            data=data,
            colors=wedge_colors,
            size=size,
            border_color=border_color
        )

        # Lo aggiungiamo al plot
        plot.addItem(pie_node)
    else:
        _draw_single_node_pyqt(
            plot, x, y,
            node, graphicOptions,
            node_color = wedge_colors[0]
        )

def _draw_node_label(
    plot: pg.PlotItem,
    x: float,
    y: float,
    text: str,
    font_size: int,
    text_color: Optional[tuple[int,int,int]] = (0,0,0),
):
    label = pg.TextItem(str(text), anchor=(0.5, 0.5), color=text_color)
    label.setPos(x,y)
    label.setFont(QtGui.QFont('Arial', font_size))
    label.setZValue(100)
    plot.addItem(label)

def _draw_edge(
    plot: pg.PlotItem,
    pos_source: tuple[float, float],
    pos_destination: tuple[float, float],
    width: int,
    edge_color: Optional[tuple[int,int,int]] = (0,0,0),
    is_directed: bool = False,
    node_size: Optional[int] = None,
):
    x1, y1 = pos_source
    x2, y2 = pos_destination
    pen = pg.mkPen(edge_color, width=width)
    line = pg.PlotCurveItem([x1, x2], [y1, y2], pen=pen)
    line.setZValue(0)
    plot.addItem(line)
    if is_directed:
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx ** 2 + dy ** 2)
        if length > 0:
            pixel_size = plot.getViewBox().viewPixelSize()
            px_w, px_h = pixel_size[0], pixel_size[1]

            dx_norm = dx / length
            dy_norm = dy / length
            arrow_x = x2-(dx_norm * (node_size/2) * px_w)
            arrow_y = y2-(dy_norm * (node_size/2) * px_h)
            angle = np.degrees(np.arctan2(dy, dx))
            arrow = pg.ArrowItem()
            arrow.setStyle(angle=180 - angle, tipAngle=30, headLen=20, pen=pen, brush=edge_color, pxMode=True)
            arrow.setPos(arrow_x, arrow_y)
            arrow.setZValue(1)
            plot.addItem(arrow)

    #Non scala bene la freccia
    #rendere la dimensione da px a unità?