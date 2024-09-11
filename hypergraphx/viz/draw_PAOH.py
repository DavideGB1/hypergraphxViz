import matplotlib.pyplot as plt
import networkx as nx

from hypergraphx import Hypergraph
from hypergraphx.representations.projections import (
    bipartite_projection,
    clique_projection,
)


def draw_PAOH(h: Hypergraph):
    """
    Draws a PAOH representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    Returns
    -------
    """

    plt.figure(constrained_layout=True, figsize=(h.num_edges(), h.num_nodes() / 2))
    nodes_mapping = h.get_mapping()

    column_list = PAOH_edge_placemente_calculation(h)
    idx = 0
    for column_set in column_list:
        for edge in column_set:
            edge = tuple(sorted(edge))
            first_node = edge[0]
            last_node = edge[len(edge) - 1]
            plt.plot([idx, idx], [nodes_mapping.transform([first_node])[0], nodes_mapping.transform([last_node])[0]], color='black')
            for y in edge:
                plt.plot(idx, nodes_mapping.transform([y])[0], 'o', color='white', markeredgecolor='black', markersize=10, markeredgewidth=3)
        idx+=1

    plt.xticks(range(0, len(column_list)), [])
    plt.ylabel('Nodes')
    plt.yticks(range(0, h.num_nodes()), nodes_mapping.classes_)
    ax = plt.gca()
    ax.set_xticks([x - 0.5 for x in range(0, len(column_list))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(0, h.num_nodes())], minor=True)
    plt.grid(which="minor", ls="--", lw=1)
    plt.show()

def PAOH_edge_placemente_calculation(h: Hypergraph):
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

    for edge in h.get_edges():
        for column_set in column_list:
            for edge_in_column in column_set:
                set1 = set(edge)
                set2 = set(edge_in_column)
                if len(set1.intersection(set2)) != 0:
                    good_column_set = False
            if good_column_set:
                column_found = True
                column_set.add(edge)
                break
            else:
                good_column_set = True

        if not column_found:
            column_list.append(set())
            column_list[len(column_list) - 1].add(edge)

        column_found = False
        good_column_set = True

    return column_list