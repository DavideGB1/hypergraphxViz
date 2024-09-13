from math import cos, sin

import numpy as np
from hypergraphx import Hypergraph
from hypergraphx.readwrite import load_hypergraph
from matplotlib import pyplot as plt


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
        if not sector_found:
            sector_list.append(set())
            sector_list[len(sector_list) - 1].add(edge)

        sector_found = False
        good_sector_set = True

    return sector_list, binary_edges

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
    k = 1

    R = (h.num_nodes()*k) / (2*np.pi)
    nodes_mapping = h.get_mapping()
    alpha = (2*np.pi)/h.num_nodes()
    sector_list , binary_edges = radial_edge_placemente_calculation(h)
    plt.figure(constrained_layout=True, figsize=(100,100))


    for edge in binary_edges:
        x1 = round(cos(alpha * nodes_mapping.transform([edge[0]])), 5) * R
        x2 = round(cos(alpha * nodes_mapping.transform([edge[1]])), 5) * R
        x = [x1, x2]
        y1 = round(sin(alpha * nodes_mapping.transform([edge[0]])), 5) * R
        y2 = round(sin(alpha * nodes_mapping.transform([edge[1]])), 5) * R
        y = [y1, y2]
        plt.plot(x, y, color='black')

    sector_depth = 2.5
    for sector in sector_list:
        sector = sorted(sector)
        for edge in sector:
            edge = sorted(edge)
            theta = np.linspace(alpha*nodes_mapping.transform([edge[0]]), alpha*nodes_mapping.transform([edge[-1]]), 100)
            x = list()
            y = list()
            for angle in theta:
                x.append(round(cos(angle),5)*R*sector_depth)
                y.append(round(sin(angle), 5) * R * sector_depth)
            plt.plot(x, y, color='black')

            for node in edge:
                plt.plot(cos(alpha*nodes_mapping.transform([node])[0])*sector_depth*R,
                         sin(alpha*nodes_mapping.transform([node])[0])*sector_depth*R, 'o', color='red', markersize=5)

        sector_depth += 0.25

    node_depth = 1
    for node in h.get_nodes():
        plt.plot(cos(alpha*nodes_mapping.transform([node])[0])*R, sin(alpha*nodes_mapping.transform([node])[0])*R, 'o', color='blue', markersize=5)
        plt.text(cos(alpha*nodes_mapping.transform([node])[0])*(R*2), sin(alpha*nodes_mapping.transform([node])[0])*(R*2), node, fontsize=12)
        node_depth += 1

    sector_depth -= 1
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set(xlim=(-2-sector_depth, 2+sector_depth), ylim=(-2-sector_depth, 2+sector_depth))
    plt.show()