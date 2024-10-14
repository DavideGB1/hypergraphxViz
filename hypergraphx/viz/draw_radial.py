from math import cos, sin
from typing import Optional

import matplotlib
import numpy as np
from matplotlib.widgets import Slider

from hypergraphx import Hypergraph
from matplotlib import pyplot as plt

from hypergraphx.viz.__support import __check_edge_intersection


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

def draw_radial_layout(
    h: Hypergraph,
    cardinality: int = -1,
    k: int = 1.0,
    draw_labels:bool = True,
    figsize: tuple[float,float] = (10,10),
    dpi: int = 300,
    ax: Optional[plt.Axes] = None,
    node_shape: str = "o",
    node_color: str = "#0000FF",
    node_size: int = 5,
    marker_color: str = "#FF0000",
    marker_size: int = 5,
    edge_color: str = "#000000",
    font_size: int = 12,
    font_spacing_multiplier: float = 1.5,
    **kwargs) -> None:
    """
    Draws a Radial representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
       The hypergraph to be projected.
    cardinality: int, optional
        Only the hyperedges with this cardinality will be drawn. -1 means that all edges will be drawn.
    k : float, optional
        Scale for the Radius value.
    draw_labels : bool
        Decide if the labels should be drawn.
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
    marker_color : str, optional
        HEX value for the node markers along the hyperedges.
    marker_size : int, optional
        The size of the node markers along the hyperedges.
    edge_color : str, optional
        HEX value for the edges color.
    font_size : int, optional
        The size of the font.
    font_spacing_multiplier : float, optional
        Value used to place the labels in a circle different from the inner one. 0 means that the labels position is
        the inner circle position.
    kwargs : dict.
        Keyword arguments to be passed to the various MathPlotLib function.
    Returns
    -------
    """
    if ax is None:
        plt.figure(figsize=figsize, dpi = dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()
    hypergraph = Hypergraph()
    if cardinality != -1:
        for node in h.get_nodes():
            hypergraph.add_node(node)
        for edge in h.get_edges():
            if len(edge)==cardinality:
                hypergraph.add_edge(edge)
    else:
        hypergraph = h


    #Calculate the radius and the necessary alpha value
    radius = (hypergraph.num_nodes()*k) / (2*np.pi)
    alpha = (2*np.pi)/hypergraph.num_nodes()

    nodes_mapping = hypergraph.get_mapping()
    sector_list , binary_edges = __radial_edge_placemente_calculation(hypergraph)
    pos = __calculate_node_position(h,alpha,radius)
    #Draw the binary edges in the inner circle
    for edge in binary_edges:
        pos_node_1 = pos[edge[0]]
        pos_node_2 = pos[edge[1]]
        x = [pos_node_1[0], pos_node_2[0]]
        y = [pos_node_1[1], pos_node_2[1]]
        ax.plot(x, y, color=edge_color, **kwargs)


    #Draw the nodes with their own label in the inner circle
    node_depth = 1
    for node in hypergraph.get_nodes():
        value_x = pos[node][0]
        value_y = pos[node][1]
        ax.plot(value_x, value_y, node_shape, color=node_color, markersize=node_size, **kwargs)
        if draw_labels:
            ax.text(value_x *font_spacing_multiplier, value_y*font_spacing_multiplier, node, fontsize=font_size, **kwargs)
        node_depth += 1

    sector_depth = font_spacing_multiplier
    if draw_labels:
        sector_depth+=1
    #Draw the various sectors' circles
    for sector in sector_list:
        sector = sorted(sector)
        #For each edge draw the corresponding arch
        for edge in sector:
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
            ax.plot(x, y, color=edge_color, **kwargs)

            #Place the nodes along the arch
            for node in edge:
                value_x = pos[node][0]*sector_depth
                value_y = pos[node][1]*sector_depth
                ax.plot(value_x, value_y, node_shape, color=marker_color, markersize=marker_size, **kwargs)

        sector_depth += 0.25

    plt.axis('off')
    ax.axis('off')
    ax.set_aspect('equal')
    ax.autoscale(enable = True, axis = 'both')


def draw_radial_interactive(
    h: Hypergraph,
    k: int = 1.0,
    draw_labels: bool = True,
    ax: Optional[plt.Axes] = None,
    node_shape: str = "o",
    node_color: str = "#0000FF",
    node_size: int = 5,
    marker_color: str = "#FF0000",
    marker_size: int = 5,
    edge_color: str = "#000000",
    font_size: int = 12,
    font_spacing_multiplier: float = 1.5,
    **kwargs) -> Slider:
    """
    Draws an interactive radial representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
       The hypergraph to be projected.
    k : float, optional
        Scale for the Radius value.
    draw_labels : bool
        Decide if the labels should be drawn.
    ax : plt.Axes, optional
        Axis if the user wants to specify an image.
    node_shape : str, optional
        The shape of the nodes in the image. Use standard MathPlotLib values.
    node_color : str, optional
        HEX value for the nodes color.
    node_size : int, optional
        The size of the nodes in the image.
    marker_color : str, optional
        HEX value for the node markers along the hyperedges.
    marker_size : int, optional
        The size of the node markers along the hyperedges.
    edge_color : str, optional
        HEX value for the edges color.
    font_size : int, optional
        The size of the font.
    font_spacing_multiplier : float, optional
        Value used to place the labels in a circle different from the inner one. 0 means that the labels position is
        the inner circle position.
    kwargs : dict.
        Keyword arguments to be passed to the various MathPlotLib function.
    Returns
    slider : Slider
        A reference to the slider. It must be collected and saved or the interactive representation will not work.
    -------
    """
    matplotlib.use('TkAgg')

    max_edge = 0
    for edge in h.get_edges():
        if len(edge)>max_edge:
            max_edge = len(edge)
    fig, ax = plt.subplots()
    draw_radial_layout(h, cardinality= 2, ax=ax)
    fig.subplots_adjust(bottom=0.25)
    # Make a horizontal slider to control the frequency.
    ax_slider = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    slider = Slider(
        ax=ax_slider,
        label='Cardinality',
        valmin=2,
        valmax=max_edge,
        valinit=2,
        valstep=1
    )
    def update(val):
        ax.cla()
        draw_radial_layout(h,cardinality=int(slider.val),ax=ax, k = k, draw_labels=draw_labels,node_shape=node_shape,node_color=node_color,
                           node_size=node_size,marker_size=marker_size,edge_color=edge_color,marker_color=marker_color,font_size=font_size,font_spacing_multiplier=font_spacing_multiplier,**kwargs)
        fig.canvas.draw()

    slider.on_changed(update)

    return slider