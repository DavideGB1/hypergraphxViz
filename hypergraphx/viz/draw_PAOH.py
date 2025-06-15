from typing import Optional, Any, Dict
import matplotlib.pyplot as plt
from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.core.temporal_hypergraph import TemporalHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import (__ignore_unused_args, __filter_hypergraph, __check_edge_intersection,
                                       __support_to_normal_hypergraph, _get_community_info, _get_node_community,
                                       _draw_node_community)

@__ignore_unused_args
def calculate_paoh_layout(
        h: Hypergraph | TemporalHypergraph | DirectedHypergraph,
        u=None,
        k=2,
        cardinality: tuple[int, int] | int = -1,
        x_heaviest: float = 1.0,
        space_optimization: bool = False,
        **kwargs
) -> Dict[str, Any]:
    """
    Calculates all the necessary data and layout for a PAOH plot without drawing.
    This function is designed to be run in a separate process to avoid blocking the GUI.

    Returns
    -------
    dict
        A dictionary containing all the pre-calculated data needed for drawing.
    """
    #Apply filters to the Hypergraph
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)

    #Create Node Mapping
    node_mapping = {node: i for i, node in enumerate(sorted(hypergraph.get_nodes()))}

    #Manage Directed Hypergraphs
    isDirected = isinstance(h, DirectedHypergraph)

    edge_directed_mapping = {}
    if isDirected:
        hypergraph, edge_directed_mapping = __support_to_normal_hypergraph(hypergraph)

    #Manage Temporal Hypergraphs
    isTemporal = isinstance(h, TemporalHypergraph)

    timestamp_mapping = {}
    timestamps_layout = []

    if isTemporal:
        for edge in hypergraph.get_edges():
            if edge[0] not in timestamp_mapping:
                timestamp_mapping[edge[0]] = []
            timestamp_mapping[edge[0]].append(edge[1])

        sorted_timestamps = sorted(timestamp_mapping.keys())
        for ts_key in sorted_timestamps:
            edge_set = timestamp_mapping[ts_key]
            if space_optimization:
                timestamps_layout.append(__PAOH_edge_placemente_calculation(edge_set))
            else:
                timestamps_layout.append([[edge] for edge in edge_set])
    else:
        edges = hypergraph.get_edges()
        if space_optimization:
            column_list = __PAOH_edge_placemente_calculation(edges)
        else:
            column_list = [[edge] for edge in edges]
        timestamps_layout.append(column_list)

    #If needed get communities data
    community_mapping = None
    community_colors = None
    if u is not None:
        community_mapping, community_colors = _get_community_info(hypergraph, k)

    #Get plot width
    final_idx = 0
    for timestamp_group in timestamps_layout:
        for _ in timestamp_group:
            final_idx += 0.5
        if isTemporal:
            final_idx += 0.5
    if isTemporal:
        final_idx -= 0.5

    #Return the needed datas
    calculation_data = {
        "hypergraph": hypergraph,
        "node_mapping": node_mapping,
        "isDirected": isDirected,
        "isTemporal": isTemporal,
        "isWeighted": hypergraph.is_weighted(),
        "timestamps_layout": timestamps_layout,
        "timestamp_mapping": timestamp_mapping,
        "edge_directed_mapping": edge_directed_mapping,
        "u": u,
        "community_mapping": community_mapping,
        "community_colors": community_colors,
        "final_idx_width": final_idx
    }
    return calculation_data

@__ignore_unused_args
def draw_paoh_from_data(
        ax: plt.Axes,
        data: Dict[str, Any],
        graphicOptions: GraphicOptions,
        y_label: str = "Nodes",
        x_label: str = "Edges",
        time_font_size: int = 18,
        time_separation_line_color: str = "#000000",
        time_separation_line_width: int = 4,
        **kwargs
) -> None:
    """
    Draws a PAOH plot on a given matplotlib axis using pre-calculated data.
    """
    #Unpack the data
    hypergraph = data["hypergraph"]
    node_mapping = data["node_mapping"]
    isDirected = data["isDirected"]
    isTemporal = data["isTemporal"]
    isWeighted = data["isWeighted"]
    timestamps_layout = data["timestamps_layout"]
    timestamp_mapping = data["timestamp_mapping"]
    edge_directed_mapping = data["edge_directed_mapping"]
    u = data["u"]
    community_mapping = data["community_mapping"]
    community_colors = data["community_colors"]
    final_idx_width = data["final_idx_width"]

    #Get and Validate the Graphic Options
    if graphicOptions is None:
        graphicOptions = GraphicOptions()
    graphicOptions.check_if_options_are_valid(hypergraph)


    sorted_nodes = sorted(node_mapping.keys(), key=lambda n: node_mapping[n])
    max_node_y = len(sorted_nodes) - 0.5

    idx = 0
    idx_timestamp = 0

    #Main drawing cycle
    for timestamp_group in timestamps_layout:
        if isTemporal:
            ts_key = sorted(timestamp_mapping.keys())[idx_timestamp]
            ax.text(idx - 0.45, max_node_y - 0.175, f"Time: {ts_key}",
                    fontsize=time_font_size, **kwargs)

        for column_set in timestamp_group:
            for edge in sorted(column_set):
                original_edge = (ts_key, edge) if isTemporal else edge

                first_node, last_node = min(edge), max(edge)
                y1, y2 = node_mapping[first_node], node_mapping[last_node]

                ax.plot([idx, idx], [y1, y2],
                        color=graphicOptions.edge_color.get(original_edge),
                        linewidth=graphicOptions.edge_size.get(original_edge),
                        zorder=-1, **kwargs)

                if isWeighted:
                    weight = str(hypergraph.get_weight(edge, ts_key) if isTemporal else hypergraph.get_weight(edge))
                    ax.text(idx, y2 + 0.25, weight,
                            horizontalalignment='center', fontsize=graphicOptions.weight_size)

                if isDirected:
                    true_edge_in, true_edge_out = edge_directed_mapping[original_edge]
                    in_color = graphicOptions.in_edge_color
                    out_color = graphicOptions.out_edge_color
                    for node in true_edge_in:
                        ax.plot(idx, node_mapping[node], marker=graphicOptions.node_shape[node], color=in_color,
                                markeredgecolor=graphicOptions.node_facecolor[node],
                                markersize=graphicOptions.node_size[node] / 20, **kwargs)
                    for node in true_edge_out:
                        ax.plot(idx, node_mapping[node], marker=graphicOptions.node_shape[node], color=out_color,
                                markeredgecolor=graphicOptions.node_facecolor[node],
                                markersize=graphicOptions.node_size[node] / 20, **kwargs)
                else:
                    for node in edge:
                        if u is None:
                            ax.plot(idx, node_mapping[node], marker=graphicOptions.node_shape[node],
                                    color=graphicOptions.node_color[node],
                                    markeredgecolor=graphicOptions.node_facecolor[node],
                                    markersize=graphicOptions.node_size[node] / 20, **kwargs)
                        else:
                            wedge_sizes, wedge_colors = _get_node_community(community_mapping, node, u,
                                                                            community_colors, 0.1)
                            _draw_node_community(ax, node, (idx, node_mapping[node]),
                                                 wedge_sizes, wedge_colors, graphicOptions, 20, **kwargs)
            idx += 0.5

        if isTemporal:
            ax.plot([idx, idx], [-0.5, max_node_y], color=time_separation_line_color,
                    linewidth=time_separation_line_width, **kwargs)
            idx_timestamp += 1
            idx += 0.5

    #Finalize axis options
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_xticks([])
    ax.set_xlim([-0.5, final_idx_width])
    ax.set_ylim([-0.5, len(sorted_nodes)])
    ax.set_yticks(range(len(sorted_nodes)))
    ax.set_yticklabels(sorted_nodes)
    ax.grid(which="minor", ls="--", lw=1)


@__ignore_unused_args
def draw_PAOH(
        h: Hypergraph | TemporalHypergraph | DirectedHypergraph,
        u=None,
        k=2,
        cardinality: tuple[int, int] | int = -1,
        x_heaviest: float = 1.0,
        space_optimization: bool = False,
        y_label: str = "Nodes",
        x_label: str = "Edges",
        time_font_size: int = 18,
        time_separation_line_color: str = "#000000",
        time_separation_line_width: int = 4,
        ax: Optional[plt.Axes] = None,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        graphicOptions: Optional[GraphicOptions] = None,
        **kwargs
) -> None:
    """
    Draws a PAOH representation of the hypergraph.
    This function acts as a wrapper, first calculating the layout and then drawing it.

    (Il resto della docstring originale può essere mantenuto qui)
    """

    calculation_data = calculate_paoh_layout(
        h=h,
        u=u,
        k=k,
        cardinality=cardinality,
        x_heaviest=x_heaviest,
        space_optimization=space_optimization,
        graphicOptions=graphicOptions,
        **kwargs
    )

    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        ax = plt.subplot(1, 1, 1)

    draw_paoh_from_data(
        ax=ax,
        data=calculation_data,
        y_label=y_label,
        x_label=x_label,
        time_font_size=time_font_size,
        time_separation_line_color=time_separation_line_color,
        time_separation_line_width=time_separation_line_width,
        **kwargs
    )


def __PAOH_edge_placemente_calculation(l: list) -> list:
    column_found = False
    column_list = list()
    column_list.append(set())
    for edge in l:
        for column_set in column_list:
            good_column_set = all(
                not __check_edge_intersection(set(edge_in_column), set(edge)) for edge_in_column in column_set)
            if good_column_set:
                column_found = True
                column_set.add(edge)
                break
        if not column_found:
            column_list.append({edge})
        column_found = False
    return [list(s) for s in column_list]