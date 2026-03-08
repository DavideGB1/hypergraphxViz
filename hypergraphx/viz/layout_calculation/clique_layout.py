from math import sqrt
from typing import Optional
import networkx as nx
from hypergraphx import Hypergraph
from hypergraphx.representations import clique_projection
from hypergraphx.viz.layout_calculation.__layout_data import CliqueLayoutData


def _compute_clique_drawing_data(
        hypergraph: Hypergraph,
        iterations: int,
        pos: Optional[dict] = None
) -> CliqueLayoutData:
    """Computes the necessary data for drawing the clique projection."""
    g = clique_projection(hypergraph)

    for u_node, v_node, data in g.edges(data=True):
        data['weight'] = 1

    if pos is None:
        pos = nx.kamada_kawai_layout(G=g, pos=pos, weight="weight")
        pos = nx.spring_layout(
            G=g,
            pos=pos,
            iterations=iterations,
            weight="weight",
            k=1/sqrt(g.number_of_nodes())
        )

    result = CliqueLayoutData(
        hypergraph=hypergraph,
        graph=g,
        pos=pos,
    )
    return result