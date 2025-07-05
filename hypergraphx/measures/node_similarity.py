import numpy as np

from hypergraphx import Hypergraph


def jaccard_similarity_matrix(h: Hypergraph, return_mapping: bool = True):
    nodes = sorted(h.get_nodes())
    n_nodes = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    matrix = np.identity(n_nodes, dtype=float)

    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            node1 = nodes[i]
            node2 = nodes[j]

            e_1 = set(h.get_incident_edges(node1))
            e_2 = set(h.get_incident_edges(node2))

            intersection_len = len(e_1.intersection(e_2))
            union_len = len(e_1.union(e_2))

            if union_len == 0:
                similarity = 0.0
            else:
                similarity = intersection_len / union_len

            matrix[i, j] = similarity
            matrix[j, i] = similarity

    if return_mapping:
        return matrix, node_to_idx
    else:
        return matrix