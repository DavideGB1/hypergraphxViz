import math
from math import cos, sin
from typing import Optional
import numpy as np
from matplotlib import pyplot as plt
from sympy.printing.pretty.pretty_symbology import line_width

from __support import __check_edge_intersection, __filter_hypergraph, __ignore_unused_args, \
    __support_to_normal_hypergraph, _get_node_community, _draw_node_community, _get_community_info
from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.readwrite import load_hypergraph
from hypergraphx.viz.__graphic_options import GraphicOptions


def __radial_edge_placemente_calculation(h: Hypergraph) -> (list,list):
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
    #For each edge decide in which sector place them
    for edge in h.get_edges():
        if len(edge)!=2:
            for sector_set in sector_list:
                #We check if there are intersections in the current sector that we are exploring
                for edge_in_column in sector_set:
                    set1 = set(edge_in_column)
                    set2 = set(edge)
                    if __check_edge_intersection(set1, set2):
                        good_sector_set = False
                #If the sector has been found we stop
                if good_sector_set:
                    sector_found = True
                    sector_set.add(edge)
                    break
                else:
                    good_sector_set = True
        else:
            #No sector if the relationship is binary
            binary_edges.append(edge)
            sector_found = True
        if not sector_found:
            #If no sector has been found we simply add a new one
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

@__ignore_unused_args
def draw_radial_layout(
    h: Hypergraph | DirectedHypergraph,
    u = None,
    cardinality: tuple[int,int]|int = -1,
    x_heaviest: float = 1.0,
    draw_labels:bool = True,
    radius_scale_factor: float = 1.0,
    font_spacing_factor: float = 1.5,
    ax: Optional[plt.Axes] = None,
    figsize: tuple[float,float] = (10,10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = None,
    **kwargs) -> None:
    """
    Draws a Radial representation of the hypergraph.
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
    Returns
    -------
    """
    if ax is None:
        plt.figure(figsize=figsize, dpi = dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()
    if graphicOptions is None:
        graphicOptions = GraphicOptions(is_PAOH=True)
    isDirected = False
    hypergraph = __filter_hypergraph(h, cardinality, x_heaviest)
    if isinstance(hypergraph, DirectedHypergraph):
        hypergraph, edge_directed_mapping = __support_to_normal_hypergraph(hypergraph)
        isDirected = True
    graphicOptions.check_if_options_are_valid(hypergraph)

    #Remove isolated Nodes
    isolated_nodes = [node for node in  hypergraph.get_nodes() if hypergraph.degree(node) == 0]
    hypergraph.remove_nodes(isolated_nodes)
    #Calculate the radius and the necessary alpha value
    radius = (hypergraph.num_nodes() * radius_scale_factor) / (2 * np.pi)
    alpha = (2*np.pi)/hypergraph.num_nodes()

    nodes_mapping = hypergraph.get_mapping()
    sector_list , binary_edges = __radial_edge_placemente_calculation(hypergraph)
    pos = __calculate_node_position(hypergraph,alpha,radius)
    #Draw the binary edges in the inner circle
    for edge in binary_edges:
        pos_node_1 = pos[edge[0]]
        pos_node_2 = pos[edge[1]]
        x = [pos_node_1[0], pos_node_2[0]]
        y = [pos_node_1[1], pos_node_2[1]]
        ax.plot(x, y, color=graphicOptions.edge_color[edge],linewidth =graphicOptions.edge_size[edge],zorder = -1, **kwargs)
        if hypergraph.is_weighted():
            ax.text((pos_node_1[0]+pos_node_2[0])/2, (pos_node_1[1]+pos_node_2[1])/2, str(hypergraph.get_weight(edge)))


    #Draw the nodes with their own label in the inner circle
    max_x = -math.inf
    min_x = math.inf
    max_y = -math.inf
    min_y = math.inf
    node_depth = 1
    if u is not None:
        mapping, col = _get_community_info(hypergraph)

    for node in hypergraph.get_nodes():
        value_x = pos[node][0]
        value_y = pos[node][1]
        max_x = max(max_x, value_x)
        min_x = min(min_x, value_x)
        max_y = max(max_y, value_y)
        min_y = min(min_y, value_y)
        ax.plot(value_x, value_y, graphicOptions.node_shape[node], color=graphicOptions.node_color[node],
                markersize=graphicOptions.node_size[node]/30,
                markeredgecolor=graphicOptions.node_facecolor[node],zorder = -1, **kwargs)
        if draw_labels:
            ax.text(value_x * font_spacing_factor, value_y * font_spacing_factor, node,
                    fontsize=graphicOptions.label_size, color=graphicOptions.label_color, **kwargs)
            max_x = max(max_x, value_x * font_spacing_factor)
            min_x = min(min_x, value_x * font_spacing_factor)
            max_y = max(max_y, value_y * font_spacing_factor)
            min_y = min(min_y, value_y * font_spacing_factor)
        node_depth += 1
    sector_depth = font_spacing_factor
    if draw_labels:
        sector_depth+=1
    #Draw the various sectors' circles
    for sector in sector_list:
        sector = sorted(sector)
        #For each edge draw the corresponding arch
        for edge in sector:
            original_edge = edge
            #Calculate points needed to plot the arch
            edge = sorted(edge)
            start_node = nodes_mapping.transform([edge[0]])[0]
            end_node = nodes_mapping.transform([edge[-1]])[0]
            theta = np.linspace(alpha * start_node, alpha * end_node, 100)
            x = list()
            y = list()
            for angle in theta:
                value_x = round(cos(angle),5)*radius*sector_depth
                value_y = round(sin(angle), 5)*radius*sector_depth
                x.append(value_x)
                y.append(value_y)
            ax.plot(x, y, color=graphicOptions.edge_color[original_edge],linewidth = graphicOptions.edge_size[original_edge],zorder = -1, **kwargs)

            #Place the nodes along the arch
            for node in edge:
                value_x = pos[node][0]*sector_depth
                value_y = pos[node][1]*sector_depth
                max_x = max(max_x, value_x)
                min_x = min(min_x, value_x)
                max_y = max(max_y, value_y)
                min_y = min(min_y, value_y)
                if isDirected:
                    true_edge = edge_directed_mapping[original_edge]
                    edge_metadata = hypergraph.get_edge_metadata(original_edge)
                    if edge_metadata != "I/O":
                        in_edge_color = graphicOptions.in_edge_color
                        out_edge_color = graphicOptions.out_edge_color
                    else:
                        in_edge_color = graphicOptions.default_node_color
                        out_edge_color = graphicOptions.default_node_color
                    if node in true_edge[0]:
                        ax.plot(value_x, value_y, marker=graphicOptions.node_shape[node],
                                color=in_edge_color, markeredgecolor=graphicOptions.node_facecolor[node],
                                markersize=graphicOptions.node_size[node]/30 , **kwargs)
                    else:
                        ax.plot(value_x, value_y, marker=graphicOptions.node_shape[node],
                                color=out_edge_color, markeredgecolor=graphicOptions.node_facecolor[node],
                                markersize=graphicOptions.node_size[node]/30 , **kwargs)
                else:
                    if u is None:
                        ax.plot(value_x, value_y, graphicOptions.edge_shape[node], color=graphicOptions.edge_node_color[node],
                            markersize=graphicOptions.node_size[node]/30,markeredgecolor=graphicOptions.node_facecolor[node], **kwargs)
                    else:
                        wedge_sizes, wedge_colors = _get_node_community(mapping, node, u, col, 0.1)
                        _draw_node_community(ax, node, center=(value_x, value_y), radius=graphicOptions.node_size[node]/2100, wedge_sizes=wedge_sizes,
                                             wedge_colors=wedge_colors, graphicOptions=graphicOptions)

            if hypergraph.is_weighted():
                start_node = nodes_mapping.transform([edge[-1]])[0]
                end_node = start_node+1
                theta = np.linspace(alpha * start_node, alpha * end_node, 50)

                value_x = round(cos(theta[12]), 5) * radius * sector_depth
                value_y = round(sin(theta[12]), 5) * radius * sector_depth
                len_x = round(cos(theta[1]), 5) * radius * sector_depth
                len_y = round(sin(theta[1]), 5) * radius * sector_depth
                ax.annotate('', xy=(len_x, len_y), xytext = (value_x, value_y),arrowprops=dict(arrowstyle='->'))
                value_x = round(cos(theta[15]), 5) * radius * sector_depth
                value_y = round(sin(theta[15]), 5) * radius * sector_depth

                ax.text(value_x,value_y,str(hypergraph.get_weight(edge)), horizontalalignment='center', verticalalignment='center',
                        fontsize = graphicOptions.weight_size)


        sector_depth += 0.35
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    max_x = max(max_x, abs(min_x))
    max_y = max(max_y, abs(min_y))
    ax.set_xlim([-max_x-1,max_x+1])
    ax.set_ylim([-max_y-1,max_y+1])
    ax.axis("off")
    plt.axis("off")