from dataclasses import dataclass, field
from typing import Any

import matplotlib
import numpy as np
import seaborn as sns
import colorcet as cc


# ─────────────────────────────────────────
# BASE
# ─────────────────────────────────────────
@dataclass
class HypergraphLayoutData:
    """Campi comuni a tutti i layout."""
    hypergraph: Any
    is_directed: bool = False
    is_temporal: bool = False
    edge_directed_mapping: dict = field(default_factory=dict)


# ─────────────────────────────────────────
# SOTTOCLASSI
# ─────────────────────────────────────────
@dataclass
class PAOHLayoutData(HypergraphLayoutData):
    node_mapping: dict = field(default_factory=dict)
    timestamps_layout: list = field(default_factory=list)
    timestamp_mapping: dict = field(default_factory=dict)
    final_idx_width: float = 0.0


@dataclass
class RadialLayoutData(HypergraphLayoutData):
    pos: dict = field(default_factory=dict)
    radius: float = 0.0
    alpha: float = 0.0
    nodes_mapping: Any = None
    sector_list: list = field(default_factory=list)
    binary_edges: list = field(default_factory=list)


@dataclass
class ProjectionLayoutData(HypergraphLayoutData):
    """Base comune per bipartite, clique ed extra-node (tutti usano un grafo NX e pos)."""
    pos: dict = field(default_factory=dict)
    graph: Any = None


@dataclass
class BipartiteLayoutData(ProjectionLayoutData):
    id_to_obj: dict = field(default_factory=dict)


@dataclass
class CliqueLayoutData(ProjectionLayoutData):
    pass


@dataclass
class ExtraNodeLayoutData(ProjectionLayoutData):
    pass

@dataclass
class SetLayoutData(ProjectionLayoutData):
    dummy_nodes: set = field(default_factory=set)
    hyperedges_to_draw: list = field(default_factory=list)
    edge_labels_info: Any = None

class CommunityData:
    node_community_mapping: dict
    def __init__(
            self,
            hypergraph: Any,
            u,
            community_number
    ):
        self.node_community_mapping = dict()

        _, mappingID2Name = hypergraph.binary_incidence_matrix(return_mapping=True)
        mappingName2ID = {n: i for i, n in mappingID2Name.items()}
        cmap = sns.color_palette(cc.glasbey, n_colors=community_number)
        colors = {k: matplotlib.colors.to_hex(cmap[k], keep_alpha=False) for k in np.arange(community_number)}
        for node in hypergraph.get_nodes():
            threshold = 0.1
            id = mappingName2ID[node]
            valid_groups = np.where(u[id] > threshold)[0]
            wedge_sizes = u[id][valid_groups]
            wedge_colors = [colors[k] for k in valid_groups]
            self.node_community_mapping[node] = (wedge_sizes, wedge_colors)
