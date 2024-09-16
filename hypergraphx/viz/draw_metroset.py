import sys

from fa2_modified import ForceAtlas2
from hypergraphx import Hypergraph
from hypergraphx.readwrite import load_hypergraph
from hypergraphx.viz import draw_clique

sys.path.append("..")

import networkx as nx
import matplotlib.pyplot as plt

def condense_hypergraph(h: Hypergraph):
    compressed_hypergraph = Hypergraph
    adjiacency = h.incidence_matrix().indptr
    only_in_one_edge = list()
    for x in range(h.num_nodes()):
        if adjiacency[x+1]-adjiacency[x] == 1:
            only_in_one_edge.append(x)

    edge_mapping = dict()
    idx = 0;
    for edge in h.get_edges():
        edge_mapping[edge] = idx
        idx += 1


    compressed_nodes = dict()
    for node in h.get_nodes():
        incident_edges = sorted([edge_mapping[edge] for edge in h.get_incident_edges(node)])
        incident_edges = tuple(incident_edges)
        if incident_edges not in compressed_nodes:
            compressed_nodes[incident_edges] = list()
            compressed_nodes[incident_edges].append(node)
        else:
            compressed_nodes[incident_edges].append(node)

    g = nx.Graph()

    for compressed_node in compressed_nodes.values():
        if len(tuple(compressed_node)) > 1:
            g.add_node(tuple(compressed_node))
        else:
            g.add_node(compressed_node[0])

    new_edges = list()

    for edge in h.get_edges():
        edge_clone = set(edge)
        new_edge = tuple()
        for compressed_node in compressed_nodes.values():
            edge = set(sorted(edge))
            compressed_node = set(sorted(compressed_node))
            if compressed_node.issubset(edge) and len(edge.intersection(compressed_node)) > 1:
                new_edge += (tuple(sorted(compressed_node)),)
                for value in compressed_node:
                    edge_clone.remove(value)

        if len(edge_clone) > 0:
            new_edge += tuple(edge_clone)
        new_edges.append(new_edge)

    for edge in new_edges:
        for i in range(len(edge) - 1):
            for j in range(i + 1, len(edge)):
                g.add_edge(edge[i], edge[j])

    nx.draw(g, with_labels=True)
    plt.show()
    return h

def draw_metroset(h: Hypergraph):
    condensed_h = condense_hypergraph(h)



h = Hypergraph([(1,2,3,9),(1,2,4),(5,6,7), (5,6,7,8), (1,2,5)])
draw_metroset(h)