from typing import Optional

import matplotlib.pyplot as plt

from hypergraphx import Hypergraph, DirectedHypergraph, TemporalHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import _draw_node_community
from hypergraphx.viz.layout_calculation.__layout_data import CommunityData
from hypergraphx.viz.layout_calculation.paoh_layout import calculate_paoh_layout
from matplotlib.axes import Axes

def draw_PAOH(
        hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph,
        community_data: Optional[CommunityData] = None,
        space_optimization: bool = False,
        sort_nodes_by: bool = False,
        sorting_mapping: dict = None,
        y_label: str = "Nodes",
        x_label: str = "Edges",
        axis_labels_size: int = 30,
        nodes_name_size: int = 25,
        ax: Optional[plt.Axes] = None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = None,
        **kwargs
) -> Axes:
    """
    Draws a PAOH representation of the hypergraph.
    This function acts as a wrapper, first calculating the layout and then drawing it.
    """
    if sort_nodes_by and space_optimization:
        raise ValueError("It's not possible to sort nodes and optimize space at the same time.")

    if sort_nodes_by and sorting_mapping is None:
        raise ValueError("A Sorting Mapping must be provided is the nodes are going to be sorted")

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    layout_data = calculate_paoh_layout(
        hypergraph=hypergraph,
        space_optimization=space_optimization,
        sort_nodes_by=sort_nodes_by,
        sorting_mapping = sorting_mapping,
    )

    hypergraph = layout_data.hypergraph
    node_mapping = layout_data.node_mapping
    isDirected = layout_data.is_directed
    isTemporal = layout_data.is_temporal
    isWeighted = hypergraph.is_weighted()
    timestamps_layout = layout_data.timestamps_layout
    timestamp_mapping = layout_data.timestamp_mapping
    edge_directed_mapping = layout_data.edge_directed_mapping

    # Get and Validate the Graphic Options
    if graphicOptions is None:
        graphicOptions = GraphicOptions()
    graphicOptions.check_if_options_are_valid(hypergraph)

    sorted_nodes = sorted(node_mapping.keys(), key=lambda n: node_mapping[n])
    max_node_y = len(sorted_nodes) - 0.5

    idx = 0
    idx_timestamp = 0
    max_timestamp = len(timestamps_layout) - 1
    # Main drawing cycle
    for timestamp_group in timestamps_layout:
        if isTemporal:
            ts_key = sorted(timestamp_mapping.keys())[idx_timestamp]
            ax.text(
                idx - 0.45, max_node_y + 0.15,
                s=f"Epoch: {ts_key}",
                fontsize=graphicOptions.time_font_size,
                zorder=5,
                **kwargs
            )

        for column_set in timestamp_group:
            for edge in sorted(column_set):
                original_edge = (ts_key, edge) if isTemporal else edge

                first_node, last_node = min(edge), max(edge, key=lambda n: node_mapping[n])
                y1, y2 = node_mapping[min(edge, key=lambda n: node_mapping[n])], node_mapping[last_node]

                ax.plot(
                    [idx, idx], [y1, y2],
                     color=graphicOptions.edge_color.get(original_edge),
                    linewidth=graphicOptions.edge_size.get(original_edge),
                    zorder=3,
                    **kwargs
                )

                if isWeighted:
                    weight = str(hypergraph.get_weight(edge, ts_key) if isTemporal else hypergraph.get_weight(edge))
                    ax.text(
                        idx, y2 + 0.35,
                        s=weight,
                        horizontalalignment='center',
                        fontsize=graphicOptions.weight_size,
                        zorder=5,
                        **kwargs
                    )

                if isDirected:
                    true_edge_in, true_edge_out = edge_directed_mapping[original_edge]
                    in_color = graphicOptions.in_edge_color
                    out_color = graphicOptions.out_edge_color
                    for node in true_edge_in:
                        ax.plot(
                            idx, node_mapping[node],
                            marker=graphicOptions.node_shape[node],
                            color=in_color,
                            markeredgecolor=graphicOptions.node_facecolor[node],
                            markersize=graphicOptions.node_size[node],
                            zorder=4,
                            **kwargs
                        )
                    for node in true_edge_out:
                        ax.plot(
                            idx, node_mapping[node],
                            marker=graphicOptions.node_shape[node],
                            color=out_color,
                            markeredgecolor=graphicOptions.node_facecolor[node],
                            markersize=graphicOptions.node_size[node],
                            zorder=4,
                            **kwargs
                        )
                else:
                    for node in edge:
                        ax.plot(
                            idx, node_mapping[node],
                            marker=graphicOptions.node_shape[node],
                            color=graphicOptions.node_color[node],
                            markeredgecolor=graphicOptions.node_facecolor[node],
                             markersize=graphicOptions.node_size[node],
                            zorder=4,
                            **kwargs
                        )
            idx += 0.5

        if community_data is not None:
            for node in hypergraph.get_nodes():
                wedge_sizes, wedge_colors = community_data.node_community_mapping[node]
                _draw_node_community(
                    ax = ax, node = node,
                    center = (-0.35, node_mapping[node]),
                    ratios = wedge_sizes, colors=wedge_colors,
                    graphicOptions=graphicOptions,
                    zorder=4,
                    **kwargs
                )

        if isTemporal and idx_timestamp != max_timestamp:
            ax.plot(
                [idx, idx], [-0.5, max_node_y],
                color=graphicOptions.time_separation_line_color,
                linewidth=graphicOptions.time_separation_line_size,
                zorder=5,
                **kwargs
            )
            idx_timestamp += 1
            idx += 0.5

    # Finalize axis options
    ax.set_ylabel(y_label, fontsize=axis_labels_size)
    ax.set_xlabel(x_label, fontsize=axis_labels_size)
    ax.set_xticks([])
    ax.tick_params(axis='both', which='major', labelsize=nodes_name_size)

    ax.set_ylim([-0.5, len(sorted_nodes) - 0.5])
    ax.set_yticks(range(len(sorted_nodes)))
    ax.set_yticklabels(sorted_nodes)
    ax.grid( ls="--", lw=1, alpha = 0.8)

    return ax