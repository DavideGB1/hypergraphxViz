from scipy._lib._disjoint_set import DisjointSet

from hypergraphx import Hypergraph
from hypergraphx.measures.node_similarity import jaccard_similarity_matrix


def agglomerative_simplification(
        hypergraph: Hypergraph,
        threshold: float = 0.85
) -> Hypergraph:
    matrix, matrix_mapping = jaccard_similarity_matrix(hypergraph, return_mapping= True)
    sets = DisjointSet(hypergraph.get_nodes())
    for node1 in hypergraph.get_nodes():
        for node2 in hypergraph.get_nodes():
            if node1 != node2:
                val = matrix[matrix_mapping[node1], matrix_mapping[node2]]
                if val >= threshold:
                    sets.merge(node1, node2)
    new_edges = list()
    for edge in hypergraph.get_edges():
        new_edge = set()
        for node in edge:
            new_edge.add(sets[node])
        new_edges.append(tuple(new_edge))
    h = Hypergraph()
    h.add_edges(new_edges)

    return h
