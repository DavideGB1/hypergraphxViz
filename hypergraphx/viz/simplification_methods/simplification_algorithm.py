from hypergraphx import Hypergraph
from hypergraphx.viz.simplification_methods.agglomerative_simplification import agglomerative_simplification
from hypergraphx.viz.simplification_methods.polygonal_symplification import polygonal_simplification, unstrangle_edges


def simplification_algorithm(
        hypergraph: Hypergraph,
        threshold: float = 0.85,
        fix_strangled_edges: bool = False,
        show_progress: bool = False,
        print_log: bool = False
):
    hypergraph = polygonal_simplification(hypergraph, show_progress=show_progress, print_log=print_log)
    hypergraph = agglomerative_simplification(hypergraph, threshold=threshold)
    if fix_strangled_edges:
        return unstrangle_edges(hypergraph)

    return hypergraph