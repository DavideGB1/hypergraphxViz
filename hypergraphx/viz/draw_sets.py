import colorsys
import math
import random
from typing import Optional, Any

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx import kamada_kawai_layout, spring_layout
from scipy.spatial import ConvexHull

from hypergraphx import Hypergraph
from hypergraphx.representations.projections import set_projection
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __filter_hypergraph, _get_node_community, \
    _draw_node_community, _get_community_info, draw_networkx_edge_labels_clone
from hypergraphx.viz.draw_projections import __convert_temporal_to_list


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

def modify_color(hex_color, saturation_adjustment=0, lightness_adjustment=0):
    """
    Modify color saturation and lightness.

    Args:
        hex_color (str): The starting color in hexadecimal format (e.g., '#RRGGBB').
        saturation_adjustment (float): Value to add to saturation (between -1.0 and 1.0).
        lightness_adjustment (float): Value to add to lightness (between -1.0 and 1.0).

    Returns:
        str: The new color in hexadecimal format.
    """
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]

    if len(hex_color) != 6:
        raise ValueError("Invalid hexadecimal color format. Expected 6 characters after '#'.")
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        raise ValueError("Invalid hexadecimal color format.")

    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    new_saturation = max(0, min(1, s + saturation_adjustment))
    new_lightness = max(0, min(1, l + lightness_adjustment))
    r_new, g_new, b_new = colorsys.hls_to_rgb(h, new_lightness, new_saturation)
    r_int, g_int, b_int = int(r_new * 255), int(g_new * 255), int(b_new * 255)
    new_hex = f'#{r_int:02x}{g_int:02x}{b_int:02x}'

    return new_hex


def _compute_set_layout(
        hypergraph: Hypergraph,
        u,
        k,
        weight_positioning,
        cardinality,
        x_heaviest,
        rounded_polygon,
        hyperedge_color_by_order,
        hyperedge_facecolor_by_order,
        hyperedge_alpha,
        scale,
        iterations,
        rounding_radius_size,
        polygon_expansion_factor,
        pos,
) -> dict[str, Any]:
    """
    Computes all layout and style information for the set visualization.
    This function handles data filtering, position calculation, and attribute preparation.
    It does not perform any drawing.
    """
    # Filter the Hypergraph nodes and edges
    hypergraph = __filter_hypergraph(hypergraph, cardinality, x_heaviest)
    try:
        for node in hypergraph.isolated_nodes():
            hypergraph.remove_node(node)
    except AttributeError:
        pass

    # Extract node positions
    if pos is None:
        g, _ = set_projection(hypergraph)
        if hypergraph.is_weighted():
            for edge in g.edges():
                weight = g.get_edge_data(edge[0], edge[1])['weight']
                if weight_positioning == 0:
                    g[edge[0]][edge[1]]['weight'] = 1
                elif weight_positioning == 2:
                    g[edge[0]][edge[1]]['weight'] = 1 / weight

        pos = nx.spectral_layout(g)
        pos = kamada_kawai_layout(g, scale=scale, pos=pos)
        pos = spring_layout(g, pos=pos if pos else None, iterations=iterations, k=15)

    # Set default hyperedge colors
    if hyperedge_color_by_order is None:
        hyperedge_color_by_order = {2: "#FC7D2A", 3: "#0094B4", 4: "#6CA500FF", 5: "#CE1700", 6: "#621AAE"}
    if hyperedge_facecolor_by_order is None:
        hyperedge_facecolor_by_order = {2: "#fcbf97", 3: "#6DC7DB", 4: "#BDE17B", 5: "#D8796D", 6: "#AB7BDC"}

    # Create a NetworkX graph for binary interactions
    G = nx.Graph()
    G.add_nodes_from(hypergraph.get_nodes())
    for e in hypergraph.get_edges(order=1):
        weight = hypergraph.get_weight(e)
        graph_weight = 1
        if weight_positioning == 1:
            graph_weight = weight
        elif weight_positioning == 2:
            graph_weight = 1 / weight
        G.add_edge(e[0], e[1], weight=graph_weight, original_weight=weight)

    # Prepare hyperedge alpha values
    if isinstance(hyperedge_alpha, (float, int)):
        hyperedge_alpha_dict = {edge: hyperedge_alpha for edge in hypergraph.get_edges()}
    else:
        hyperedge_alpha_dict = hyperedge_alpha.copy() if hyperedge_alpha else {}
        for edge in hypergraph.get_edges():
            hyperedge_alpha_dict.setdefault(edge, 0.8)

    # Prepare data for drawing higher-order hyperedges
    hyperedges_to_draw = []
    for hye in hypergraph.get_edges():
        if len(hye) > 2 and all(node in pos for node in hye):
            points_with_orig = [(pos[node][0], pos[node][1], pos[node][0], pos[node][1]) for node in hye]
            x_c = np.mean([p[0] for p in points_with_orig])
            y_c = np.mean([p[1] for p in points_with_orig])
            points_with_orig.sort(key=lambda p: np.arctan2(p[1] - y_c, p[0] - x_c))

            order = len(hye) - 1 - sum(1 for node in hye if hypergraph.get_node_metadata(node) == "dummy")
            if order not in hyperedge_color_by_order.keys():
                color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                hyperedge_color_by_order.setdefault(order, modify_color(color, lightness_adjustment=-0.2))
                hyperedge_facecolor_by_order.setdefault(order, modify_color(color, saturation_adjustment=-0.3, lightness_adjustment=0.2))
            color = hyperedge_color_by_order.setdefault(order, "#" + "%06x" % random.randint(0, 0xFFFFFF))
            facecolor = hyperedge_facecolor_by_order.setdefault(order, "#" + "%06x" % random.randint(0, 0xFFFFFF))

            final_points = points_with_orig
            if rounded_polygon:
                expanded_points = [(x_c + polygon_expansion_factor * (p[0] - x_c),
                                    y_c + polygon_expansion_factor * (p[1] - y_c), p[2], p[3]) for p in
                                   points_with_orig]
                if len(expanded_points) >= 5:
                    points_dict = {(p[0], p[1]): (p[2], p[3]) for p in expanded_points}
                    hull = ConvexHull([(p[0], p[1]) for p in expanded_points])
                    hull_points_2d = [tuple(hull.points[v]) for v in hull.vertices]
                    final_points = [(x, y, points_dict[(x, y)][0], points_dict[(x, y)][1]) for x, y in hull_points_2d]
                else:
                    final_points = expanded_points

            hyperedges_to_draw.append({
                "points": final_points, "rounded": rounded_polygon, "radius": rounding_radius_size,
                "alpha": hyperedge_alpha_dict.get(hye, 0.8), "color": color, "facecolor": facecolor,
                "weight_label": str(hypergraph.get_weight(hye)) if hypergraph.is_weighted() else None,
                "weight_pos": (x_c, y_c)
            })

    # Prepare community and label info
    community_info = None
    if u is not None:
        mapping, col = _get_community_info(hypergraph, k)
        community_info = (mapping, col, u)

    edge_labels_info = None
    if hypergraph.is_weighted():
        labels = nx.get_edge_attributes(G, 'original_weight')
        pos_higher = {n: (p[0], p[1] + 0.075) for n, p in pos.items()}
        edge_labels_info = (labels, pos_higher)

    dummy_nodes = list()
    for node in hypergraph.get_nodes():
        if hypergraph.get_node_metadata(node) == "dummy":
            dummy_nodes.append(node)
    return {
        "pos": pos, "G": G, "dummy_nodes": dummy_nodes,
        "hyperedges_to_draw": hyperedges_to_draw, "community_info": community_info,
        "edge_labels_info": edge_labels_info
    }


def _draw_set_elements(
        ax: plt.Axes,
        data: dict,
        draw_labels: bool,
        graphicOptions: GraphicOptions,
        **kwargs) -> None:
    """
    Draws the elements of the set visualization onto a given matplotlib Axes object.
    This function uses pre-computed layout and style information.
    """
    pos, G, dummy_nodes = data["pos"], data["G"], data["dummy_nodes"]
    graphicOptions.check_if_options_are_valid(G)


    # 1. Draw higher-order hyperedges
    for hye_info in data["hyperedges_to_draw"]:
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
    for edge in G.edges():
        nx.draw_networkx_edges(G, pos, edgelist=[edge], width=graphicOptions.edge_size[edge], edge_color=graphicOptions.edge_color[edge],
                               ax=ax, **kwargs)
    if data["edge_labels_info"]:
        labels, pos_higher = data["edge_labels_info"]
        draw_networkx_edge_labels_clone(G, pos_higher, edge_labels=labels, bbox={'alpha': 0, 'pad': 1},
                                        verticalalignment="top")

    # 3. Draw nodes
    community_info = data["community_info"]
    for node in G.nodes():
        if node not in dummy_nodes:
            if not community_info:
                nx.draw_networkx_nodes(
                    G, pos, nodelist=[node], node_size=graphicOptions.node_size[node], node_shape=graphicOptions.node_shape[node],
                    node_color=graphicOptions.node_color[node], edgecolors=graphicOptions.node_facecolor[node], ax=ax, **kwargs
                )
            else:
                mapping, col, u = community_info
                wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
                _draw_node_community(ax, node, pos[node], wedge_sizes, wedge_colors, graphicOptions, **kwargs)

    # 4. Draw node labels
    if draw_labels:
        nx.draw_networkx_labels(
            G, pos, labels={n: n for n in G.nodes() if n not in dummy_nodes},
            font_size=graphicOptions.label_size, font_color=graphicOptions.label_color, ax=ax, **kwargs
        )


def draw_sets(
        hypergraph: Hypergraph,
        u=None,
        k=0,
        weight_positioning=0,
        cardinality: tuple[int, int] | int = -1,
        x_heaviest: float = 1.0,
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

    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    hypergraphs, n_times, axs_flat = __convert_temporal_to_list(hypergraph, figsize, dpi, ax)
    for i, (time, hypergraph) in enumerate(hypergraphs.items()):
        if n_times != 1:
            ax = axs_flat[i]
        else:
            ax = axs_flat
        computed_data = _compute_set_layout(
            hypergraph, u, k, weight_positioning, cardinality, x_heaviest,
            rounded_polygon, hyperedge_color_by_order, hyperedge_facecolor_by_order,
            hyperedge_alpha, scale, iterations, rounding_radius_size,
            polygon_expansion_factor, pos
        )
        _draw_set_elements(
            ax=ax,
            data=computed_data,
            draw_labels=draw_labels,
            graphicOptions=graphicOptions,
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