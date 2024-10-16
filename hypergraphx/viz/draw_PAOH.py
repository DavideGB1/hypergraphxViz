from typing import Optional

import matplotlib.pyplot as plt
from hypergraphx import Hypergraph
from hypergraphx.core import TemporalHypergraph
from hypergraphx.viz.__support import __check_edge_intersection


def draw_PAOH(
    h: Hypergraph | TemporalHypergraph,
    space_optimization: bool = False,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    ax: Optional[plt.Axes] = None,
    node_shape: str = "o",
    node_color: str = "#FFFFFF",
    node_size: int = 10,
    edge_color: str = "#000000",
    edge_width: float = 2,
    marker_edge_color: str = "#000000",
    marker_edge_width: int = 3,
    y_label: str = "Nodes",
    x_label: str = "Edges",
    time_font_size: int = 18,
    time_separation_line_color: str = "#000000",
    time_separation_line_width: int = 4,
    **kwargs) -> None:
    """
    Draws a PAOH representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    space_optimization: bool
        Flag used to determine if the column compression function should be used or not.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    ax : plt.Axes, optional
         Axis if the user wants to specify an image.
    node_shape : str, optional
        The shape of the nodes in the image. Use standard MathPlotLib values.
    node_color : str, optional
        HEX value for the nodes color.
    node_size : int, optional
        The size of the nodes in the image.
    edge_color : str, optional
        HEX value for the edges color.edge_width: float = 2
    edge_width : float, optional
        Width of the edges in the grid.
    marker_edge_color : str, optional
        Color of the node markers in each hyperedge.
    marker_edge_width : int, optional
        Width of the node markers in each hyperedge.
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
    kwargs : dict.
        Keyword arguments to be passed to the various MathPlotLib function.
    Returns
    -------
    """
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    node_mapping = dict()
    idx = 0
    for node in h.get_nodes():
        node_mapping[idx] = node
        idx += 1
    max_node = idx - 0.5
    timestamp_mapping = dict()
    timestamps = []
    if isinstance(h, TemporalHypergraph):
        for edge in h.get_edges():
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
    else:
        #Get the edged position
        if space_optimization:
            column_list = __PAOH_edge_placemente_calculation(h.get_edges())
        else:
            column_list = []
            for edge in h.get_edges():
                column_list.append([edge])
        timestamps.append(column_list)
    idx = 0
    idx_timestamp = 0
    #Draw each column
    for timestamp in timestamps:
        if isinstance(h, TemporalHypergraph):
            ax.text(idx - 0.45, max_node - 0.175, "Time: " + str(list(timestamp_mapping.keys())[idx_timestamp]),
                    fontsize=time_font_size, **kwargs)
        for column_set in timestamp:
            column_set = sorted(column_set)
            #Plo each column in the relative position
            for edge in column_set:
                edge = tuple(sorted(edge))
                first_node = edge[0]
                last_node = edge[len(edge) - 1]
                ax.plot([idx, idx], [list(node_mapping.values()).index(first_node), list(node_mapping.values()).index(last_node)],
                     color=edge_color, linewidth = edge_width, **kwargs)
                for y in edge:
                    ax.plot(idx, list(node_mapping.values()).index(y), node_shape, color=node_color,
                         markeredgecolor=marker_edge_color, markersize=node_size, markeredgewidth=marker_edge_width, **kwargs)
            idx += 0.5
        if isinstance(h, TemporalHypergraph):
            ax.plot([idx, idx], [-0.5, max_node], color=time_separation_line_color,
                    linewidth=time_separation_line_width, **kwargs)
            idx_timestamp += 1
            idx += 0.5

    if isinstance(h, TemporalHypergraph):
        idx -= 0.5

    #Initiatiate the grid for the axes
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_xticks([])
    ax.set_xlim([-0.5, idx])
    ax.set_yticks(range(len(h.get_nodes())))
    ax.set_yticklabels(h.get_nodes())
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
