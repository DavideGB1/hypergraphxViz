import math
from math import cos, sin
import numpy as np
from hypergraphx import Hypergraph
from matplotlib import pyplot as plt

from hypergraphx.viz.draw_PAOH import check_edge_intersection


def radial_edge_placemente_calculation(h: Hypergraph):
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
    sector_found = False
    good_sector_set = True
    sector_list = list()
    sector_list.append(set())
    binary_edges = list()
    for edge in h.get_edges():
        if len(edge)!=2:
            for column_set in sector_list:
                for edge_in_column in column_set:
                    set1 = set(edge_in_column)
                    set2 = set(edge)
                    if check_edge_intersection(set1, set2):
                        good_sector_set = False
                if good_sector_set:
                    sector_found = True
                    column_set.add(edge)
                    break
                else:
                    good_sector_set = True
        else:
            binary_edges.append(edge)
            sector_found = True
        if not sector_found:
            sector_list.append(set())
            sector_list[len(sector_list) - 1].add(edge)

        sector_found = False
        good_sector_set = True

    return sector_list, binary_edges

def draw_radial_layout(h: Hypergraph, k = 1.0):
    """
    Draws a PAOH representation of the hypergraph.
    Parameters
    ----------
        h : Hypergraph.
            The hypergraph to be projected.
        k : float, optional
            Scale for the Radius value.
    Returns
    -------
    """

    R = (h.num_nodes()*k) / (2*np.pi)
    nodes_mapping = h.get_mapping()
    alpha = (2*np.pi)/h.num_nodes()
    sector_list , binary_edges = radial_edge_placemente_calculation(h)



    for edge in binary_edges:
        node1 = nodes_mapping.transform([edge[0]])[0]
        node2 = nodes_mapping.transform([edge[1]])[0]
        x1 = round(cos(alpha * node1), 5) * R
        x2 = round(cos(alpha * node2), 5) * R
        x = [x1, x2]
        y1 = round(sin(alpha * node1), 5) * R
        y2 = round(sin(alpha * node2), 5) * R
        y = [y1, y2]
        plt.plot(x, y, color='black')

    sector_depth = 2.5

    node_depth = 1
    for node in h.get_nodes():
        value_x = cos(alpha * nodes_mapping.transform([node])[0]) * R
        value_y = sin(alpha * nodes_mapping.transform([node])[0]) * R
        plt.plot(value_x, value_y, 'o', color='blue', markersize=5)
        plt.text(value_x *1.5, value_y*1.5, node, fontsize=12)
        node_depth += 1

    for sector in sector_list:
        sector = sorted(sector)
        for edge in sector:
            edge = sorted(edge)
            start_node = nodes_mapping.transform([edge[0]])[0]
            end_node = nodes_mapping.transform([edge[-1]])[0]
            theta = np.linspace(alpha * start_node, alpha * end_node, 100)
            x = list()
            y = list()
            for angle in theta:
                value_x = round(cos(angle),5)*R*sector_depth
                x.append(value_x)
                value_y = round(sin(angle), 5) * R * sector_depth
                y.append(round(sin(angle), 5) * R * sector_depth)
            plt.plot(x, y, color='black')

            for node in edge:
                value_x = cos(alpha*nodes_mapping.transform([node])[0])*sector_depth*R
                value_y = sin(alpha*nodes_mapping.transform([node])[0])*sector_depth*R
                plt.plot(value_x, value_y, 'o', color='red', markersize=5)

        sector_depth += 0.25
        ax = plt.gca()
        plt.axis('off')
        ax.set_aspect('equal')
        plt.autoscale(enable=True, axis='both')



    sector_depth -= 1
    plt.show()