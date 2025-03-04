from typing import Optional

import matplotlib.pyplot as plt

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.core.temporal_hypergraph import TemporalHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __ignore_unused_args, __filter_hypergraph, __check_edge_intersection, \
    __support_to_normal_hypergraph, _get_community_info, _get_node_community
from typing import Optional

import matplotlib.pyplot as plt

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.core.temporal_hypergraph import TemporalHypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __ignore_unused_args, __filter_hypergraph, __check_edge_intersection, \
    __support_to_normal_hypergraph, _get_community_info, _get_node_community


@__ignore_unused_args
def draw_PAOH(
    h: Hypergraph | TemporalHypergraph | DirectedHypergraph,
    u = None,
    k = 2,
    cardinality: tuple[int,int]|int = -1,
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
    **kwargs) -> None:
    """
    Draws a PAOH representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph | TemporalHypergraph | DirectedHypergraph.
        The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    space_optimization: bool
        Flag used to determine if the column compression function should be used or not.
    y_label : str, optional
        Label for the y-axis.
    x_label : str, optional
        Label for the x-axis.
    time_font_size : int, optional
        Specify the font size for the time label.
    time_separation_line_color : str, optional
        Color of the lines that separates the timezones.
    time_separation_line_width: int, optional
        Width of the lines that separates the timezones.
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
    Returns
    -------
    """
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()
    #Filters the hypergraph
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    #Sets up the graphical options
    if graphicOptions is None:
        graphicOptions = GraphicOptions()

    #Creates a custom node mapping
    node_mapping = dict()
    idx = 0
    for node in sorted(hypergraph.get_nodes()):
        node_mapping[idx] = node
        idx += 1
    max_node = idx - 0.5
    #Mapping for the time stamps
    timestamp_mapping = dict()
    timestamps = []
    isDirected = False
    if isinstance(hypergraph, DirectedHypergraph):
        hypergraph, edge_directed_mapping = __support_to_normal_hypergraph(hypergraph)
        isDirected = True
    #What to if we are working with a Temporal Hypergraph
    if isinstance(hypergraph, TemporalHypergraph):
        #Places the edges in the correct timezones
        for edge in hypergraph.get_edges():
            if edge[0] not in timestamp_mapping:
                timestamp_mapping[edge[0]] = []
            timestamp_mapping[edge[0]].append(edge[1])
        if space_optimization:
            for edge_set in timestamp_mapping.values():
                timestamps.append(__PAOH_edge_placemente_calculation(edge_set))
        else:
            for edge_set in timestamp_mapping.values():
                new_list = []
                for edge in edge_set:
                    new_list.append([edge])
                timestamps.append(new_list)
    #In case of a normal Hypergraph
    else:
        #Get the edged position
        if space_optimization:
            column_list = __PAOH_edge_placemente_calculation(hypergraph.get_edges())
        else:
            column_list = []
            for edge in hypergraph.get_edges():
                column_list.append([edge])
        timestamps.append(column_list)
    idx = 0
    idx_timestamp = 0
    graphicOptions.check_if_options_are_valid(hypergraph)
    if u is not None:
        mapping, col = _get_community_info(hypergraph,k)
    #Draw each column
    for timestamp in timestamps:
        #Stamp the timestamp name
        if isinstance(hypergraph, TemporalHypergraph):
            ax.text(idx - 0.45, max_node - 0.175, "Time: " + str(list(timestamp_mapping.keys())[idx_timestamp]),
                    fontsize=time_font_size, **kwargs)
        #Plots the columns in the timestamp
        for column_set in timestamp:
            column_set = sorted(column_set)
            #Plot each column in the relative position
            for edge in column_set:
                original_edge = edge
                edge = tuple(sorted(edge))
                first_node = edge[0]
                last_node = edge[-1]
                ax.plot([idx, idx], [list(node_mapping.values()).index(first_node), list(node_mapping.values()).index(last_node)],
                        color=graphicOptions.edge_color[original_edge], linewidth = graphicOptions.edge_size[original_edge], zorder = -1,**kwargs)
                if hypergraph.is_weighted():
                    ax.text(idx, list(node_mapping.values()).index(last_node)+0.25, str(hypergraph.get_weight(original_edge)),
                            horizontalalignment='center', fontsize = graphicOptions.weight_size)
                if isDirected:
                    true_edge = edge_directed_mapping[original_edge]
                    edge_metadata =  hypergraph.get_edge_metadata(original_edge)
                    if edge_metadata != "I/O":
                        in_edge_color = graphicOptions.in_edge_color
                        out_edge_color = graphicOptions.out_edge_color
                    else:
                        in_edge_color = graphicOptions.default_node_color
                        out_edge_color = graphicOptions.default_node_color
                    for node in true_edge[0]:
                        ax.plot(idx, list(node_mapping.values()).index(node), marker=graphicOptions.node_shape[node],
                                color=in_edge_color, markeredgecolor=graphicOptions.node_facecolor[node],
                                markersize=graphicOptions.node_size[node]/30, **kwargs)
                    for node in true_edge[1]:
                        ax.plot(idx, list(node_mapping.values()).index(node), marker=graphicOptions.node_shape[node],
                                color=out_edge_color, markeredgecolor=graphicOptions.node_facecolor[node],
                                markersize=graphicOptions.node_size[node]/30, **kwargs)

                else:
                    for node in edge:
                        if u is None:
                            ax.plot(idx, list(node_mapping.values()).index(node), marker= graphicOptions.node_shape[node],
                            color=graphicOptions.node_color[node], markeredgecolor=graphicOptions.node_facecolor[node],
                            markersize=graphicOptions.node_size[node]/30, **kwargs)
                        else:
                            wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
                            ax.plot(idx, list(node_mapping.values()).index(node),
                                    marker=graphicOptions.node_shape[node],
                                    color=wedge_colors[0],
                                    markeredgecolor=graphicOptions.node_facecolor[node],
                                    markersize=graphicOptions.node_size[node]/30 , **kwargs)

            idx += 0.5
        #Plot the separating line for the timestamps
        if isinstance(hypergraph, TemporalHypergraph):
            ax.plot([idx, idx], [-0.5, max_node], color=time_separation_line_color,
                    linewidth=time_separation_line_width, **kwargs)
            idx_timestamp += 1
            idx += 0.5

    if isinstance(hypergraph, TemporalHypergraph):
        idx -= 0.5

    #Initiatiate the grid for the axes
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_xticks([])
    ax.set_xlim([-0.5, idx])
    ax.set_ylim([-0.5,len(hypergraph.get_nodes())])
    ax.set_yticks(range(len(hypergraph.get_nodes())))
    ax.set_yticklabels(sorted(hypergraph.get_nodes()))
    ax.grid(which="minor", ls="--", lw=1)


def __PAOH_edge_placemente_calculation(l: list)  -> list:
    """
    Calculate how to place the edges in order to optimize space in the grid.
    Parameters
    ----------
    l : list.
        The list of edges to order.
    Returns
    -------
    column_list : List of Set of Edges
        The list of the columns. Each column contain various edges
    """
    column_found = False
    good_column_set = True
    column_list = list()
    column_list.append(set())

    #For each edge decide in which column place them
    for edge in l:
        for column_set in column_list:
            # We check if there are intersections in the current column that we are exploring
            for edge_in_column in column_set:
                set1 = set(edge_in_column)
                set2 = set(edge)
                if __check_edge_intersection(set1, set2):
                    good_column_set = False
            # If the column has been found we stop
            if good_column_set:
                column_found = True
                column_set.add(edge)
                break
            else:
                good_column_set = True

        if not column_found:
            #If no sector has been found we simply add a new one
            column_list.append(set())
            column_list[len(column_list) - 1].add(edge)

        column_found = False
        good_column_set = True

    return column_list