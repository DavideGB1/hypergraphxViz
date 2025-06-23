import math
from math import cos, sin
from typing import Optional, Any

import numpy as np
from matplotlib import pyplot as plt

from hypergraphx.viz.__support import __check_edge_intersection, __filter_hypergraph, __ignore_unused_args, \
    __support_to_normal_hypergraph, _get_node_community, _draw_node_community, _get_community_info
from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions


def __radial_edge_placement_calculation(h: Hypergraph) -> (list, list):
    """
    Calculate how to place the edges in order to optimize space in the grid.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    Returns
    -------
    sector_list : List of Set of Edges
        The sectors' list. Each sector contain various edges
    """
    sector_found = False
    good_sector_set = True
    sector_list = list()
    sector_list.append(set())
    binary_edges = list()
    # For each edge decide in which sector place them
    for edge in h.get_edges():
        if len(edge) != 2:
            for sector_set in sector_list:
                # We check if there are intersections in the current sector that we are exploring
                for edge_in_column in sector_set:
                    set1 = set(edge_in_column)
                    set2 = set(edge)
                    if __check_edge_intersection(set1, set2):
                        good_sector_set = False
                # If the sector has been found we stop
                if good_sector_set:
                    sector_found = True
                    sector_set.add(edge)
                    break
                else:
                    good_sector_set = True
        else:
            # No sector if the relationship is binary
            binary_edges.append(edge)
            sector_found = True
        if not sector_found:
            # If no sector has been found we simply add a new one
            sector_list.append(set())
            sector_list[len(sector_list) - 1].add(edge)

        sector_found = False
        good_sector_set = True

    return sector_list, binary_edges


def __calculate_node_position(h: Hypergraph, alpha: float, radius: float) -> dict:
    """
    Calculate the position of each node in the image.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    alpha : float
        Starting angle position needed for the edge placement.
    radius : float
        Radius of the inner circle.
    Returns
    -------
    pos : Dictionary
        Dictionary with the position of each node
    """
    pos = dict()
    for node in h.get_nodes():
        nodes_mapping = h.get_mapping()
        value_x = cos(alpha * nodes_mapping.transform([node])[0]) * radius
        value_x = round(value_x, 2)
        value_y = sin(alpha * nodes_mapping.transform([node])[0]) * radius
        value_y = round(value_y, 2)
        pos[node] = (value_x, value_y)

    return pos


def _compute_radial_layout(
        h: Hypergraph | DirectedHypergraph,
        u,
        k,
        cardinality,
        x_heaviest,
        radius_scale_factor,
) -> dict[str, Any]:
    """
    Performs all calculations for the radial layout without drawing.
    This includes filtering, positioning, sector allocation, and data preparation.
    """
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)

    is_directed = False
    edge_directed_mapping = None
    if isinstance(hypergraph, DirectedHypergraph):
        hypergraph, edge_directed_mapping = __support_to_normal_hypergraph(hypergraph)
        is_directed = True

    # Remove isolated nodes
    isolated_nodes = [node for node in hypergraph.get_nodes() if hypergraph.degree(node) == 0]
    hypergraph.remove_nodes(isolated_nodes)

    # Calculate core layout parameters
    num_nodes = hypergraph.num_nodes()
    if num_nodes == 0:
        return {"hypergraph": hypergraph, "pos": {}}  # Handle empty graph case

    radius = (num_nodes * radius_scale_factor) / (2 * np.pi)
    alpha = (2 * np.pi) / num_nodes

    # Perform calculations
    nodes_mapping = hypergraph.get_mapping()
    sector_list, binary_edges = __radial_edge_placement_calculation(hypergraph)
    pos = __calculate_node_position(hypergraph, alpha, radius)

    community_info = None
    if u is not None:
        mapping, col = _get_community_info(hypergraph, k)
        community_info = (mapping, col, u)

    return {
        "hypergraph": hypergraph,
        "pos": pos,
        "radius": radius,
        "alpha": alpha,
        "nodes_mapping": nodes_mapping,
        "sector_list": sector_list,
        "binary_edges": binary_edges,
        "is_directed": is_directed,
        "edge_directed_mapping": edge_directed_mapping,
        "community_info": community_info,
    }


def _draw_radial_elements(
    ax: plt.Axes,
    data: dict,
    draw_labels: bool,
    font_spacing_factor: float,
    graphicOptions: GraphicOptions,
    **kwargs
) -> None:
    """

    Draws the elements of the radial layout onto a given matplotlib Axes object.
    """
    # Unpack computed data for clarity
    h = data["hypergraph"]
    if h.num_nodes() == 0:
        return  # Nothing to draw

    pos = data["pos"]
    radius, alpha = data["radius"], data["alpha"]
    nodes_mapping = data["nodes_mapping"]
    sector_list, binary_edges = data["sector_list"], data["binary_edges"]
    is_directed, edge_directed_mapping = data["is_directed"], data["edge_directed_mapping"]
    community_info = data["community_info"]
    graphicOptions.check_if_options_are_valid(h)

    # Draw binary edges
    for edge in binary_edges:
        p1, p2 = pos[edge[0]], pos[edge[1]]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=graphicOptions.edge_color[edge], linewidth=graphicOptions.edge_size[edge], zorder=-1,
                **kwargs)
        if h.is_weighted():
            ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, str(h.get_weight(edge)))

    # Draw nodes and labels
    bounds = {"max_x": -math.inf, "min_x": math.inf, "max_y": -math.inf, "min_y": math.inf}
    for node in h.get_nodes():
        vx, vy = pos[node]
        bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], vx), min(bounds["min_x"], vx)
        bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], vy), min(bounds["min_y"], vy)

        ax.plot(vx, vy, graphicOptions.node_shape[node], color=graphicOptions.node_color[node], markersize=graphicOptions.node_size[node] / 30,
                markeredgecolor=graphicOptions.node_facecolor[node], zorder=-1, **kwargs)
        if draw_labels:
            lx, ly = vx * font_spacing_factor, vy * font_spacing_factor
            ax.text(lx, ly, node, fontsize=graphicOptions.label_size, color=graphicOptions.label_color, **kwargs)
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
            arc_x = [round(cos(a), 5) * radius * sector_depth for a in theta]
            arc_y = [round(sin(a), 5) * radius * sector_depth for a in theta]
            ax.plot(arc_x, arc_y, color=graphicOptions.edge_color[edge], linewidth=graphicOptions.edge_size[edge], zorder=-1, **kwargs)

            # Place nodes along the arc
            for node in sorted_edge_nodes:
                vx, vy = pos[node][0] * sector_depth, pos[node][1] * sector_depth
                bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], vx), min(bounds["min_x"], vx)
                bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], vy), min(bounds["min_y"], vy)

                if is_directed:
                    true_edge = edge_directed_mapping[edge]
                    color = graphicOptions.in_edge_color if node in true_edge[0] else graphicOptions.out_edge_color
                    ax.plot(vx, vy, marker=graphicOptions.node_shape[node], color=color,
                            markeredgecolor=graphicOptions.node_facecolor[node],
                            markersize=graphicOptions.node_size[node] / 30, **kwargs)
                elif community_info:
                    mapping, col, u = community_info
                    wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
                    _draw_node_community(ax, node, (vx, vy), wedge_sizes, wedge_colors, graphicOptions, 30, **kwargs)
                else:
                    ax.plot(vx, vy, graphicOptions.edge_shape[node], color=graphicOptions.edge_node_color[node],
                            markersize=graphicOptions.node_size[node] / 30,
                            markeredgecolor=graphicOptions.node_facecolor[node], **kwargs)

            # Draw weight labels for hyperedges
            if h.is_weighted():
                mid_angle = (alpha * start_idx + alpha * end_idx) / 2
                wx = round(cos(mid_angle), 5) * radius * (sector_depth + 0.15)
                wy = round(sin(mid_angle), 5) * radius * (sector_depth + 0.15)
                ax.text(wx, wy, str(h.get_weight(edge)), ha='center', va='center', fontsize=graphicOptions.weight_size)

        sector_depth += 0.35

    # Finalize axis
    max_dim_x = max(bounds["max_x"], abs(bounds["min_x"]))
    max_dim_y = max(bounds["max_y"], abs(bounds["min_y"]))
    ax.set_xlim([-max_dim_x - 1, max_dim_x + 1])
    ax.set_ylim([-max_dim_y - 1, max_dim_y + 1])
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")


@__ignore_unused_args
def draw_radial_layout(
        h: Hypergraph | DirectedHypergraph,
        u=None,
        k=2,
        cardinality: tuple[int, int] | int = -1,
        x_heaviest: float = 1.0,
        draw_labels: bool = True,
        radius_scale_factor: float = 1.0,
        font_spacing_factor: float = 1.5,
        ax: Optional[plt.Axes] = None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = None,
        **kwargs) -> None:
    """
    Draws a Radial representation of the hypergraph.
    This is a wrapper function that orchestrates the calculation and drawing steps.

    Parameters
    ----------
    h : Hypergraph | DirectedHypergraph.
       The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    draw_labels : bool
        Decide if the labels should be drawn.
    radius_scale_factor : float, optional
        Scale for the Radius value.
    font_spacing_factor : float, optional
        Value used to place the labels in a circle different from the inner one. 0 means that the labels position is
        the inner circle position.
    ax : plt.Axes, optional
        Axis if the user wants to specify an image.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    graphicOptions: Optional[GraphicOptions].
        Object used to store all the common graphical settings among the representation methods.
    kwargs : dict.
        Keyword arguments to be passed to the various MathPlotLib function.
    """
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.subplot(1, 1, 1)

    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    # 1. Compute all layout and style information.
    computed_data = _compute_radial_layout(
        h, u, k, cardinality, x_heaviest, radius_scale_factor, graphicOptions
    )

    # 2. Draw the elements onto the axes.
    _draw_radial_elements(
        ax,
        computed_data,
        draw_labels,
        font_spacing_factor,
        **kwargs
    )

    # Finalize plot aesthetics.
    plt.axis("off")
    plt.tight_layout()