from typing import Optional

import networkx as nx

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.representations import bipartite_projection
from hypergraphx.viz.__support import __ignore_unused_args
from hypergraphx.viz.layout_calculation.__layout_data import BipartiteLayoutData


@__ignore_unused_args
def _compute_bipartite_drawing_data(
        hypergraph: Hypergraph | DirectedHypergraph,
        align: str,
        pos: Optional[dict] = None,
) -> BipartiteLayoutData:
    """Computes the necessary data for drawing the bipartite projection."""
    g, id_to_obj = bipartite_projection(hypergraph)

    if pos is None:
        pos = nx.bipartite_layout(
            g, nodes=[n for n, d in g.nodes(data=True) if d['bipartite'] == 0], align=align
        )

    result = BipartiteLayoutData(
        hypergraph=hypergraph,
        graph=g,
        pos=pos,
        id_to_obj=id_to_obj
    )
    return result
