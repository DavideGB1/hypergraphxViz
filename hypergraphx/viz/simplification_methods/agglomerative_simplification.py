
from hypergraphx import Hypergraph
from hypergraphx.measures.node_similarity import jaccard_similarity_matrix
from hypergraphx.viz.interactive_view.support import numerical_hypergraph


def agglomerative_simplification(
        hypergraph: Hypergraph,
        threshold: float = 0.85
) -> Hypergraph:
    matrix, matrix_mapping = jaccard_similarity_matrix(hypergraph, return_mapping= True)
    to_compress=list()
    flag = False
    for node1 in hypergraph.get_nodes():
        for node2 in hypergraph.get_nodes():
            if node1 != node2:
                val = matrix[matrix_mapping[node1], matrix_mapping[node2]]
                if val > threshold:
                    for comp in to_compress:
                        if node1 in comp:
                            flag = True
                            if node2 not in comp:
                                comp.append(node2)
                        elif node2 in comp:
                            if node1 not in comp:
                                comp.append(node1)
                            flag = True
                    if not flag:
                        to_compress.append([node1,node2])
                    flag = False
    new_edges = []
    max_node = max(enumerate(hypergraph.get_nodes(),start=1))[0]
    numeric = numerical_hypergraph(hypergraph)
    compressed_nodes = {tuple(node): idx if numeric else str(idx)
                        for idx, node in enumerate(to_compress, start=max_node + 1)}
    for edge in hypergraph.get_edges():
        to_add = list()
        new_edge = list(edge)
        for nodes in to_compress:
            for node in nodes:
                if node in edge:
                    new_edge.remove(node)
                    to_add.append(compressed_nodes[tuple(nodes)])
        if len(to_add) > 0:
            for node in to_add:
                if node not in new_edge:
                    new_edge.append(node)
        if new_edge not in new_edges:
            new_edges.append(new_edge)
    h = Hypergraph()
    h.add_edges(new_edges)

    return h