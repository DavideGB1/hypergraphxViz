import math
from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import _draw_node_community, draw_networkx_edge_labels_clone
from hypergraphx.viz.draw_projections import __convert_temporal_to_list
from hypergraphx.viz.layout_calculation.__layout_data import SetLayoutData, CommunityData
from hypergraphx.viz.layout_calculation.set_layout import _compute_set_layout


def _draw_hyperedge_set(
        points: list[tuple[float, float, float, float]],
        radius: Optional[float] = 0.1,
        hyperedge_alpha: Optional[float] = 0.8,
        border_color: Optional[str] = "FFBC79",
        face_color: Optional[str] = "FFBC79",
        ax: Optional[plt.Axes] = None) -> None:
    """
    Support function used to draw each hyperedge as a polygon with rounded corners.
    Parameters
    ----------
    points: list[tuple[float, float,float,float]]
        Vertexes of the polygon saved two times.
    radius: float, optional
        Used to scale the rounding of the corners.
    hyperedge_alpha: float, optional
        Alpha value of the polygon surface.
    border_color: str, optional
        Color of the polygon border.
    face_color: str, optional
        Color of the polygon surface.
    ax: plt.Axes, optional
        The axes to draw the set on.
    """
    lenPoints = len(points)
    vertexes_x = []
    vertexes_y = []
    for i in range(lenPoints):
        # Find the pivot vertex and the adjacent ones
        p1 = points[i]
        p = points[(i + 1) % lenPoints]
        p2 = points[(i + 2) % lenPoints]
        # Create the vectors that describe the corner
        v1 = __vector(p, p1)
        v2 = __vector(p, p2)
        # Calculate the various angles
        sinA = v1.nx * v2.ny - (v1.ny * v2.nx)
        sinA90 = v1.nx * v2.nx - (v1.ny * (-v2.ny))
        angle = math.asin(max(-1, min(1, sinA)))
        # Checks used to determine how to draw the rounded corner
        radDirection = 1
        drawDirection = False
        magic = False
        if sinA90 < 0:
            if angle < 0:
                angle = np.pi + angle
            else:
                angle = np.pi - angle
                radDirection = -1
                drawDirection = True
                magic = True
        else:
            if angle > 0:
                radDirection = -1
            else:
                drawDirection = True
        # Calculate the correct distance of the points
        halfAngle = angle / 2
        try:
            lenOut = abs(math.cos(halfAngle) * radius / math.sin(halfAngle))
        except ZeroDivisionError:
            lenOut = abs(math.cos(halfAngle) * radius / 0.01)
        if lenOut > min(v1.length / 2, v2.length / 2):
            lenOut = min(v1.length / 2, v2.length / 2)
            cRadius = abs(lenOut * math.sin(halfAngle) / math.cos(halfAngle))
        else:
            cRadius = radius
        # Caulculate the arc center
        o = (
            p[0] + v2.nx * lenOut - v2.ny * cRadius * radDirection,
            p[1] + v2.ny * lenOut + v2.nx * cRadius * radDirection
        )
        # Calculate start and ending angle
        start_angle = v1.ang + (np.pi / 2 * radDirection)
        end_angle = v2.ang - (np.pi / 2 * radDirection)
        # Modify the angles so we draw the correct arc
        if end_angle < 0 and radDirection != -1:
            end_angle += 2 * np.pi
        if not drawDirection:
            tmp = start_angle + 2 * np.pi
            if start_angle < 0 and tmp < end_angle:
                start_angle = tmp
        elif end_angle < start_angle and radDirection != -1:
            end_angle += 2 * np.pi
        # Calculate some angles for the arch
        theta = np.linspace(start_angle, end_angle, 100)
        point_angle = math.atan2(p[2], p[3])
        # Determine if the center is inside or outside the arc
        in_arc = True
        if point_angle < 0:
            point_angle += 2 * np.pi
        if not start_angle <= point_angle <= end_angle:
            in_arc = False
        if (p[2] ** 2 + p[3] ** 2) > radius * radius:
            in_arc = False
        if not in_arc and not magic:
            o = (p[2], p[3])
        # Calculate the actual points
        x = o[0] + cRadius * np.cos(theta)
        y = o[1] + cRadius * np.sin(theta)
        vertexes_x.extend(x)
        vertexes_y.extend(y)

    # Create and draw the polygon
    polygon = plt.Polygon(np.column_stack([vertexes_x, vertexes_y]), closed=True, fill=True, alpha=hyperedge_alpha)
    polygon.set_facecolor(face_color)
    polygon.set_edgecolor(border_color)
    ax.add_patch(polygon)


class __vector:
    """
    Support class for the set drawing
    """

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.x = p2[0] - p1[0]
        self.y = p2[1] - p1[1]
        self.length = math.sqrt((self.x ** 2) + (self.y ** 2))
        self.nx = self.x / self.length
        self.ny = self.y / self.length
        self.ang = math.atan2(self.ny, self.nx)

def _draw_set_elements(
        ax: plt.Axes,
        layout_data: SetLayoutData,
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        community_data: Optional[CommunityData] = None,
        **kwargs
) -> None:
    """
    Draws the elements of the set visualization onto a given matplotlib Axes object.
    This function uses pre-computed layout and style information.
    """
    pos = layout_data.pos
    graph = layout_data.graph
    dummy_nodes = layout_data.dummy_nodes
    hyperedges_to_draw = layout_data.hyperedges_to_draw
    edge_labels_info = layout_data.edge_labels_info

    graphicOptions.check_if_options_are_valid(graph)


    # 1. Draw higher-order hyperedges
    for hye_info in hyperedges_to_draw:
        if hye_info["rounded"]:
            _draw_hyperedge_set(
                points=hye_info["points"], radius=hye_info["radius"], hyperedge_alpha=hye_info["alpha"],
                border_color=hye_info["color"], face_color=hye_info["facecolor"], ax=ax
            )
        else:
            polygon = plt.Polygon(
                np.column_stack([[p[0] for p in hye_info["points"]], [p[1] for p in hye_info["points"]]]),
                closed=True, fill=True, alpha=hye_info["alpha"],
                facecolor=hye_info["facecolor"], edgecolor=hye_info["color"]
            )
            ax.add_patch(polygon)
        if hye_info["weight_label"]:
            ax.text(hye_info["weight_pos"][0], hye_info["weight_pos"][1], hye_info["weight_label"],
                    fontsize=graphicOptions.weight_size)

    # 2. Draw binary edges and their labels
    for edge in graph.edges():
        nx.draw_networkx_edges(graph, pos, edgelist=[edge], width=graphicOptions.edge_size[edge], edge_color=graphicOptions.edge_color[edge],
                               ax=ax, **kwargs)
    if edge_labels_info:
        labels, pos_higher = edge_labels_info
        draw_networkx_edge_labels_clone(graph, pos_higher, edge_labels=labels, bbox={'alpha': 0, 'pad': 1},
                                        verticalalignment="top")

    # 3. Draw nodes
    for node in graph.nodes():
        if node not in dummy_nodes:
            if not community_data:
                nx.draw_networkx_nodes(
                    graph, pos, nodelist=[node], node_size=graphicOptions.node_size[node]*10, node_shape=graphicOptions.node_shape[node],
                    node_color=graphicOptions.node_color[node], edgecolors=graphicOptions.node_facecolor[node], ax=ax, **kwargs
                )
            else:
                wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
                _draw_node_community(
                    ax=ax,
                    node=node,
                    center=pos[node],
                    ratios=wedge_sizes,
                    colors=wedge_colors,
                    graphicOptions=graphicOptions,
                    **kwargs
                )

    # 4. Draw node labels
    if draw_labels:
        nx.draw_networkx_labels(
            graph, pos, labels={n: n for n in graph.nodes() if n not in dummy_nodes},
            font_size=graphicOptions.label_size, font_color=graphicOptions.label_color, ax=ax, **kwargs
        )


def draw_sets(
        hypergraph: Hypergraph | TemporalHypergraph,
        community_data: Optional[CommunityData] = None,
        weight_positioning=0,
        draw_labels: bool = True,
        rounded_polygon: bool = True,
        hyperedge_color_by_order: Optional[dict] = None,
        hyperedge_facecolor_by_order: Optional[dict] = None,
        hyperedge_alpha: float | dict = 0.8,
        scale: int = 1,
        iterations: int = 1000,
        rounding_radius_size: float = 0.1,
        polygon_expansion_factor: float = 1.8,
        pos: Optional[dict] = None,
        ax: Optional[plt.Axes] = None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = GraphicOptions(),
        **kwargs):
    """
    Draws a set projection of the hypergraph.
    This is a wrapper function that first computes the layout and then draws the elements.

    Parameters
    ----------
    hypergraph: Hypergraph.
        The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    draw_labels : bool
        Decide if the labels should be drawn.
    rounded_polygon: bool
        Decide if the polygon should be rounded and expanded.
    hyperedge_color_by_order: dict, optional
        Used to determine the border color of each hyperedge using its order.
    hyperedge_facecolor_by_order: dict, optional
        Used to determine the color of each hyperedge using its order.
    hyperedge_alpha: dict | float, optional
        It's used to specify the alpha gradient of each hyperedge polygon. Each hyperedge can have its own alpha.
    scale: int, optional
        Used to influence the distance between nodes
    rounding_radius_size: float, optional
        Radius for the rounded corners of the polygons.
    polygon_expansion_factor: float, optional
        Scale factor for the polygon expansion.
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

    if isinstance(hypergraph, DirectedHypergraph):
        raise ValueError("Set Projections is not able to represent directed hypergraphs.")

    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    hypergraphs, n_times, axs_flat = __convert_temporal_to_list(hypergraph, figsize, dpi, ax)
    for i, (time, hypergraph) in enumerate(hypergraphs.items()):
        if n_times != 1:
            ax = axs_flat[i]
        else:
            ax = axs_flat
        layout_data = _compute_set_layout(
            hypergraph, weight_positioning,
            rounded_polygon, hyperedge_color_by_order, hyperedge_facecolor_by_order,
            hyperedge_alpha, scale, iterations, rounding_radius_size,
            polygon_expansion_factor, pos
        )
        _draw_set_elements(
            ax=ax,
            layout_data=layout_data,
            draw_labels=draw_labels,
            graphicOptions=graphicOptions,
            community_data=community_data,
            **kwargs
        )
        ax.set_aspect('auto')
        ax.autoscale(enable=True, axis='both')
        ax.axis("off")
        if n_times != 1:
            ax.set_title(f"Hypergraph at time {time}")
    if n_times != 1:
        for ax in axs_flat[n_times:]:
            ax.set_visible(False)