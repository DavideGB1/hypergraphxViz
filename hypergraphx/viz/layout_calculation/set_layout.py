import colorsys
import random

import networkx as nx
import numpy as np
from networkx import kamada_kawai_layout, spring_layout
from scipy.spatial import ConvexHull

from hypergraphx import Hypergraph
from hypergraphx.representations.projections import set_projection
from hypergraphx.viz.layout_calculation.__layout_data import SetLayoutData
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
        weight_positioning,
        rounded_polygon,
        hyperedge_color_by_order,
        hyperedge_facecolor_by_order,
        hyperedge_alpha,
        scale,
        iterations,
        rounding_radius_size,
        polygon_expansion_factor,
        pos = None
) -> SetLayoutData:
    """
    Computes all layout and style information for the set visualization.
    This function handles data filtering, position calculation, and attribute preparation.
    It does not perform any drawing.
    """
    # Filter the Hypergraph nodes and edges
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

    # Prepare label info
    edge_labels_info = None
    if hypergraph.is_weighted():
        labels = nx.get_edge_attributes(G, 'original_weight')
        pos_higher = {n: (p[0], p[1] + 0.075) for n, p in pos.items()}
        edge_labels_info = (labels, pos_higher)

    dummy_nodes = list()
    for node in hypergraph.get_nodes():
        if hypergraph.get_node_metadata(node) == "dummy":
            dummy_nodes.append(node)

    result = SetLayoutData(
        hypergraph = hypergraph,
        pos=pos,
        graph=G,
        dummy_nodes=set(dummy_nodes),
        hyperedges_to_draw = hyperedges_to_draw,
        edge_labels_info = edge_labels_info
    )
    return result