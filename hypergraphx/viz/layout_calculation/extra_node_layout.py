from typing import Optional
import networkx as nx
from matplotlib import pyplot as plt
from networkx import planar_layout, is_planar, DiGraph
from hypergraphx import Hypergraph
from hypergraphx.representations import bipartite_projection
from hypergraphx.viz.__support import __ignore_unused_args
from hypergraphx.viz.layout_calculation.__layout_data import ExtraNodeLayoutData


def _hyperedges_relations_detection(h: Hypergraph, obj_to_id: dict) -> dict:
    """Calculate the number of common nodes between pairs of hyperedges."""
    hyperedges_relations = {}
    edges = list(h.get_edges())

    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            edge1, edge2 = edges[i], edges[j]
            if len(edge1) > 2 and len(edge2) > 2:
                id1, id2 = obj_to_id[edge1], obj_to_id[edge2]
                if id1 != id2:
                    common_nodes = len(set(edge1).intersection(set(edge2)))
                    if common_nodes > 0:
                        pair = tuple(sorted((id1, id2)))
                        hyperedges_relations.setdefault(pair, 0)
                        hyperedges_relations[pair] += common_nodes

    return hyperedges_relations


def _edges_graph_creation(
        hyperedges_relations: dict, edgeList: list, drawing: bool = False
) -> dict:
    """Create a graph using the relations between hyperedges."""
    edges_graph = nx.Graph()
    edges_graph.add_nodes_from(edgeList)

    for edge_pair, weight in hyperedges_relations.items():
        edges_graph.add_edge(edge_pair[0], edge_pair[1], weight=weight)

    if is_planar(edges_graph):
        posEdges = nx.planar_layout(edges_graph)
    else:
        pos = nx.spectral_layout(edges_graph)
        toImprovePos = nx.kamada_kawai_layout(edges_graph, pos=pos)
        posEdges = nx.spring_layout(edges_graph, k=0.5, pos=toImprovePos, weight="weight")

    if drawing:
        plt.figure(figsize=(12, 12))
        nx.draw_networkx(edges_graph, pos=posEdges, with_labels=True)
        plt.title("Hyperedge Relation Graph")
        plt.show()

    return posEdges


@__ignore_unused_args
def _compute_extra_node_drawing_data(
        hypergraph: Hypergraph,
        ignore_binary_relations: bool,
        weight_positioning: int,
        respect_planarity: bool,
        iterations: int,
        pos: Optional[dict] = None,
        draw_edge_graph: bool = False,
) -> ExtraNodeLayoutData:
    """Computes the necessary data for drawing the extra-node projection."""
    g, x, obj_to_id = bipartite_projection(hypergraph, mode="extra_node", return_obj_to_id = True)

    if ignore_binary_relations:
        binary_edges = [
            x for x in g.edges()
            if not (str(x[0]).startswith('E') or str(x[1]).startswith('E'))
        ]
        g.remove_edges_from(binary_edges)
        g.remove_nodes_from(list(nx.isolates(g)))

    if hypergraph.is_weighted():
        for u_node, v_node, data in g.edges(data=True):
            if weight_positioning == 0:
                data['weight'] = 1
            elif weight_positioning == 2:
                data['weight'] = 1 / data['weight']

    clone_g = None
    if isinstance(g, DiGraph):
        clone_g = g
        g = g.to_undirected()

    if pos is None:
        if is_planar(g) and respect_planarity:
            pos = planar_layout(g)
        else:
            edgeList = [x for x in g.nodes() if str(x).startswith('E')]
            hyperedges_relations = _hyperedges_relations_detection(hypergraph, obj_to_id)
            posEdges = _edges_graph_creation(hyperedges_relations, edgeList, drawing=draw_edge_graph)
            if len(posEdges) > 0:
                pos = nx.spring_layout(
                    G=g, pos=posEdges, iterations=iterations, weight="weight", fixed=edgeList
                )
            else:
                pos = nx.spring_layout(G=g, iterations=iterations, weight="weight")

    if clone_g is not None:
        g = clone_g
    result = ExtraNodeLayoutData(
        hypergraph=hypergraph,
        graph=g,
        pos=pos,
    )
    return result