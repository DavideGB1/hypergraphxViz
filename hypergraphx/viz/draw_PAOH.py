from typing import Optional

import matplotlib.pyplot as plt
from hypergraphx import Hypergraph
from hypergraphx.viz.__support import __check_edge_intersection


def draw_PAOH(
    h: Hypergraph,
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
    **kwargs) -> None:
    """
    Draws a PAOH representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
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
    kwargs : dict.
        Keyword arguments to be passed to the various MathPlotLib function.
    Returns
    -------
    """
    nodes_mapping = h.get_mapping()
    #Get the edged position
    column_list = __PAOH_edge_placemente_calculation(h)
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    idx = 0
    #Draw each column
    for column_set in column_list:
        column_set = sorted(column_set)
        #Plo each column in the relative position
        for edge in column_set:
            edge = tuple(sorted(edge))
            first_node = edge[0]
            last_node = edge[len(edge) - 1]
            ax.plot([idx, idx], [nodes_mapping.transform([first_node])[0], nodes_mapping.transform([last_node])[0]],
                     color=edge_color, linewidth = edge_width, **kwargs)
            for y in edge:
                ax.plot(idx, nodes_mapping.transform([y])[0], node_shape, color=node_color,
                         markeredgecolor=marker_edge_color, markersize=node_size, markeredgewidth=marker_edge_width, **kwargs)
        idx += 1

    #Initiatiate the grid for the plot
    plt.ylabel('Nodes')
    plt.xticks(range(0, len(column_list)), [])
    plt.yticks(range(0, h.num_nodes()), nodes_mapping.classes_)
    plt.grid(which="minor", ls="--", lw=1)

    #Initiatiate the grid for the axes
    ax.set_ylabel('Nodes')
    ax.set_xticks([x - 0.5 for x in range(0, len(column_list) + 1)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(0, h.num_nodes())], minor=True)
    ax.grid(which="minor", ls="--", lw=1)



def __PAOH_edge_placemente_calculation(h: Hypergraph)  -> list:
    """
    Calculate how to place the edges in order to optimize space in the grid.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
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
    for edge in h.get_edges():
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