import math
from math import cos, sin
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import _draw_node_community
from hypergraphx.viz.draw_projections import __convert_temporal_to_list
from hypergraphx.viz.layout_calculation.__layout_data import CommunityData, RadialLayoutData
from hypergraphx.viz.layout_calculation.radial_layout import _compute_radial_layout


def __draw_radial_single_layout(
    ax: plt.Axes,
    layout_data: RadialLayoutData,
    graphicOptions: GraphicOptions,
    community_data: Optional[CommunityData] = None,
    draw_labels: bool = False,
    font_spacing_factor: float = 1.5,
    **kwargs
) -> None:
    """

    Draws the elements of the radial layout onto a given matplotlib Axes object.
    """
    # Unpack computed data for clarity
    h = layout_data.hypergraph
    if h.num_nodes() == 0:
        return  # Nothing to draw

    pos = layout_data.pos
    radius, alpha = layout_data.radius, layout_data.alpha
    nodes_mapping = layout_data.nodes_mapping
    sector_list, binary_edges = layout_data.sector_list, layout_data.binary_edges
    is_directed, edge_directed_mapping = layout_data.is_directed, layout_data.edge_directed_mapping

    graphicOptions.check_if_options_are_valid(h)

    # Draw binary edges
    for edge in binary_edges:
        p1, p2 = pos[edge[0]], pos[edge[1]]
        ax.plot(
            [p1[0], p2[0]], [p1[1], p2[1]],
            color=graphicOptions.edge_color[edge],
            linewidth=graphicOptions.edge_size[edge],
            zorder=3,
            **kwargs
        )
        if h.is_weighted():
            ax.text(
                (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2,
                s=str(h.get_weight(edge)),
                horizontalalignment='center',
                fontsize=graphicOptions.weight_size,
                zorder=5,
                **kwargs
            )

    # Draw nodes and labels
    bounds = {"max_x": -math.inf, "min_x": math.inf, "max_y": -math.inf, "min_y": math.inf}
    for node in h.get_nodes():
        vx, vy = pos[node]
        bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], vx), min(bounds["min_x"], vx)
        bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], vy), min(bounds["min_y"], vy)

        if community_data:
            wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
            _draw_node_community(
                ax, node,
                center=(vx, vy),
                ratios=wedge_sizes,
                colors=wedge_colors,
                graphicOptions=graphicOptions,
                zoder=4,
                **kwargs
            )
        else:
            ax.plot(
                vx, vy,
                marker=graphicOptions.node_shape[node],
                color=graphicOptions.node_color[node],
                markersize=graphicOptions.node_size[node],
                markeredgecolor=graphicOptions.node_facecolor[node],
                zorder=4,
                **kwargs
            )
        if draw_labels:
            lx, ly = vx * font_spacing_factor, vy * font_spacing_factor
            ax.text(
                lx, ly,
                s = node,
                fontsize=graphicOptions.label_size,
                color=graphicOptions.label_color,
                zorder=5,
                **kwargs
            )
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
            ax.plot(
                arc_x, arc_y,
                color=graphicOptions.edge_color[edge],
                linewidth=graphicOptions.edge_size[edge],
                zorder=3,
                **kwargs
            )

            # Place nodes along the arc
            for node in sorted_edge_nodes:
                vx, vy = pos[node][0] * sector_depth, pos[node][1] * sector_depth
                bounds["max_x"], bounds["min_x"] = max(bounds["max_x"], vx), min(bounds["min_x"], vx)
                bounds["max_y"], bounds["min_y"] = max(bounds["max_y"], vy), min(bounds["min_y"], vy)

                if is_directed:
                    true_edge = edge_directed_mapping[edge]
                    color = graphicOptions.in_edge_color if node in true_edge[0] else graphicOptions.out_edge_color
                    ax.plot(
                        vx, vy,
                        marker=graphicOptions.edge_shape[node],
                        color=color,
                        markeredgecolor=graphicOptions.node_facecolor[node],
                        markersize=graphicOptions.node_size[node],
                        zorder=4,
                        **kwargs
                    )
                else:
                    ax.plot(
                        vx, vy,
                        marker=graphicOptions.edge_shape[node],
                        color=graphicOptions.edge_node_color[node],
                        markersize=graphicOptions.node_size[node],
                        markeredgecolor=graphicOptions.node_facecolor[node],
                        zorder=4,
                        **kwargs
                    )

            # Draw weight labels for hyperedges
            if h.is_weighted():
                mid_angle = (alpha * start_idx + alpha * end_idx) / 2
                wx = round(cos(mid_angle), 5) * radius * (sector_depth + 0.15)
                wy = round(sin(mid_angle), 5) * radius * (sector_depth + 0.15)
                ax.text(
                    wx, wy,
                    s = str(h.get_weight(edge)),
                    ha='center', va='center',
                    fontsize=graphicOptions.weight_size,
                    color=graphicOptions.label_color,
                    zorder=5,
                    **kwargs
                )

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


def draw_radial_layout(
        hypergraph: Hypergraph | DirectedHypergraph,
        community_data: Optional[CommunityData] = None,

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

    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    hypergraphs, n_times, axs_flat = __convert_temporal_to_list(hypergraph, figsize, dpi, ax)
    for i, (time, hypergraph) in enumerate(hypergraphs.items()):
        if n_times != 1:
            ax = axs_flat[i]
        else:
            ax = axs_flat
        computed_data = _compute_radial_layout(
            hypergraph = hypergraph,
            radius_scale_factor = radius_scale_factor
        )
        __draw_radial_single_layout(
            ax=ax,
            layout_data = computed_data,
            graphicOptions = graphicOptions,
            community_data=community_data,
            draw_labels = draw_labels,
            font_spacing_factor = font_spacing_factor,
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