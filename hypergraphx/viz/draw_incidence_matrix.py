import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from hypergraphx import Hypergraph, TemporalHypergraph


def plot_incidence_matrix(hypergraph, weighted= False,  title = None, ax = None, figsize: tuple = (12, 7), cmap= None, **kwargs):
    if ax is None:
        plt.figure(figsize=figsize)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    matrix = None
    mapping = None
    if isinstance(hypergraph, Hypergraph):
        matrix, mapping = hypergraph.incidence_matrix(return_mapping=True)
    elif isinstance(hypergraph, TemporalHypergraph):
        matrix, mapping = hypergraph.annealed_adjacency_matrix(return_mapping=True)
    if matrix is None:
        raise ValueError("Matrix is None. Hypergraph type not supported.")
    if not weighted and hypergraph.is_weighted():
        pass
    df = pd.DataFrame(matrix.todense())
    if not weighted and hypergraph.is_weighted():
        df = df.applymap(lambda x: 0 if x == 0 else 1)
    sns.heatmap(data=df, ax=ax, annot=True, cbar=False, cmap=cmap, vmin=0, vmax=1)

    xlabels = [f"E{i}" for i in range(hypergraph.num_edges())]
    ax.set_xlabel("HyperEdges", **kwargs)
    ax.set_xticklabels(xlabels, **kwargs)

    ax.set_yticks(np.arange(len(mapping.values()))+ 0.5)
    ax.set_yticklabels(mapping.values(), **kwargs)
    ax.set_ylabel("Nodes", **kwargs)
    if title is None:
        title = "Incidence Matrix"
        if hypergraph.is_weighted() and weighted:
            title = "Weighted " + title
        if isinstance(hypergraph, TemporalHypergraph):
            title = "Annealed " + title
    ax.set_title(title, **kwargs)