from cmath import cos, sin

import networkx as nx
import numpy as np
from fontTools.merge import layoutPreMerge
from hypergraphx import Hypergraph
from hypergraphx.readwrite import load_hypergraph
from matplotlib import pyplot as plt
from networkx import spring_layout, is_planar, circular_layout, draw_networkx


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

    for edge in h.get_edges():
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

        if not sector_found:
            sector_list.append(set())
            sector_list[len(sector_list) - 1].add(edge)

        sector_found = False
        good_sector_set = True

    return sector_list

def check_edge_intersection(set1, set2):
    """
    Check if two sets overlaps.
    Parameters
    ----------
        set1 : Set.
        set2 : Set.
    Returns
    -------
        res : Bool
    """
    set1 = sorted(set1)
    set2 = sorted(set2)
    res = False
    for x in set2:
        if set1[0] <= x <= set1[-1]:
            res = True
            break

    return res

def draw_radial_layout(h: Hypergraph):
    R = 1
    angle_step = 2 * np.pi/h.num_nodes()
    node_depth = 1
    nodes_mapping = h.get_mapping()
    alpha = 2*np.pi/h.num_nodes()

    sector_list = radial_edge_placemente_calculation(h)
    plt.figure(constrained_layout=True, figsize=((len(sector_list)+7), (len(sector_list)+7)))

    sector_depth = 2
    for sector in sector_list:
        sector = sorted(sector)
        for edge in sector:
            if len(edge) == 2:
                x = [cos(alpha*nodes_mapping.transform([edge[0]]))*R, cos(alpha*nodes_mapping.transform([edge[1]]))*R]
                y = [sin(alpha*nodes_mapping.transform([edge[0]]))*R, sin(alpha*nodes_mapping.transform([edge[1]]))*R]
                plt.plot(x, y, color='black')
            else:
                edge = sorted(edge)
                theta = np.linspace(alpha*nodes_mapping.transform([edge[0]]), alpha*nodes_mapping.transform([edge[-1]]), 100)
                x = R*sector_depth * np.cos(theta)
                y = R*sector_depth * np.sin(theta)
                plt.plot(x, y, color='black')

                for node in edge:
                    plt.plot(cos(alpha*nodes_mapping.transform([node])[0])*sector_depth*R,
                             sin(alpha*nodes_mapping.transform([node])[0])*sector_depth*R, 'o', color='red', markersize=5)

        sector_depth += 0.5

    node_depth = 1
    for node in h.get_nodes():
        plt.plot(cos(alpha*nodes_mapping.transform([node])[0])*R, sin(alpha*nodes_mapping.transform([node])[0])*R, 'o', color='blue', markersize=5)
        node_depth += 1

    sector_depth -= 1
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set(xlim=(-R*sector_depth, R*sector_depth), ylim=(-R*sector_depth, R*sector_depth))
    plt.show()


H = Hypergraph([(1,2,3,4),(3,4,5,6),(1,2,3),(4,5), (10,11,12,13,14,15,16,17,18,19), (1,2,3,7,8,9,10,11)])
draw_radial_layout(H)

