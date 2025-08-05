import matplotlib.pyplot as plt
import networkx as nx

from hypergraphx import Hypergraph
from hypergraphx.representations.projections import (
    bipartite_projection,
    clique_projection,
)

def draw_bipartite_old(h: Hypergraph, pos=None, ax=None, align="vertical", **kwargs):
    """
    Draws a bipartite graph representation of the hypergraph.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    align : str.
        The alignment of the nodes. Can be 'vertical' or 'horizontal'.

    Returns
    -------
    ax : matplotlib.axes.Axes.
        The axes the graph was drawn on.
    """
    g, id_to_obj = bipartite_projection(h)

    if pos is None:
        pos = nx.bipartite_layout(
            g, nodes=[n for n, d in g.nodes(data=True) if d["bipartite"] == 0]
        )

    if ax is None:
        ax = plt.gca()

    nx.draw_networkx(g, pos=pos, ax=ax, **kwargs)
    return ax

h = Hypergraph([(6,7,8,9),(7,8,15),(8,9,14),(3,6),(1,2,3),(4,5,6),(5,24,25),(23,24,25),(24,26),(23,27)])
draw_bipartite_old(h)
plt.savefig("bipartite_old.svg")
plt.show()