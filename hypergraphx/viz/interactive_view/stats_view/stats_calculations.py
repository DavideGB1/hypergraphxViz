import numpy as np
import pandas as pd

from hypergraphx import TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness_averaged, s_closeness_averaged, \
    s_betweenness_nodes_averaged, s_betweenness, s_closeness, s_closeness_nodes, \
    s_betweenness_nodes, s_closenness_nodes_averaged
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.interactive_view.support import generate_key
import seaborn as sns

from hypergraphx.viz.plt_degree_distribution_for_order import compute_binned_degree_distributions, \
    draw_degree_distribution_plot


# Motifs
def motifs_calculations(hypergraph):
    motifs_3 = compute_motifs(hypergraph, order=3)
    motifs3_profile = [i[1] for i in motifs_3['norm_delta']]
    return motifs3_profile


#Adjacency
def adjacency_calculations_pool(hypergraph):
    adj_matrix = None
    if isinstance(hypergraph, TemporalHypergraph):
        adj_matrix, mapping = hypergraph.annealed_adjacency_matrix(return_mapping=True)
    else:
        adj_matrix, mapping = hypergraph.adjacency_matrix(return_mapping=True)

    return [adj_matrix, mapping]

#Centrality
def calculate_centrality_pool(hypergraph):

    is_temporal = isinstance(hypergraph, TemporalHypergraph)

    betweenness_func_edge = s_betweenness_averaged if is_temporal else s_betweenness
    closeness_func_edge = s_closeness_averaged if is_temporal else s_closeness
    betweenness_func_node = s_betweenness_nodes_averaged if is_temporal else s_betweenness_nodes
    closeness_func_node = s_closenness_nodes_averaged if is_temporal else s_closeness_nodes

    edge_betweenness = betweenness_func_edge(hypergraph)
    edge_closeness = closeness_func_edge(hypergraph)
    node_betweenness = betweenness_func_node(hypergraph)
    node_closeness = closeness_func_node(hypergraph)


    all_edge_ids = set(edge_betweenness.keys()).union(edge_closeness.keys())
    edges_values = []
    for edge_id in all_edge_ids:
        b_value = edge_betweenness.get(edge_id, None)
        c_value = edge_closeness.get(edge_id, None)
        edges_values.append((edge_id, b_value, c_value))

    all_node_ids = set(node_betweenness.keys()).union(node_closeness.keys())
    nodes_values = []
    for node_id in all_node_ids:
        b_value = node_betweenness.get(node_id, None)
        c_value = node_closeness.get(node_id, None)
        nodes_values.append((node_id, b_value, c_value))

    return [nodes_values, edges_values]

def draw_centrality(axes, values_list, **kwargs):
    df = pd.DataFrame(values_list[1], columns=['Node', 'Betweenness', 'Closeness'])
    df = df.sort_values(by='Node').reset_index(drop=True)

    df_rounded = df.round(4)
    df_for_table = df_rounded.fillna('N/A').astype(str)

    cell_text = df_for_table.values.tolist()
    col_labels = df_for_table.columns.tolist()

    table = axes[0].table(
        cellText=cell_text,
        colLabels=col_labels,
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)

    for i, key in enumerate(cell_text):
        bg_color = '#FFFFFF' if i % 2 == 0 else '#f1f1f2'
        for j in range(len(col_labels)):
            table[(i + 1, j)].set_facecolor(bg_color)

    for i in range(len(col_labels)):
        table[(0, i)].set_facecolor("#40466e")
        table[(0, i)].get_text().set_color('white')
        table[(0, i)].get_text().set_weight('bold')

    df = pd.DataFrame(values_list[0], columns=['Edges', 'Betweenness', 'Closeness'])
    df = df.sort_values(by='Edges').reset_index(drop=True)

    df_rounded = df.round(4)
    df_for_table = df_rounded.fillna('N/A').astype(str)

    cell_text = df_for_table.values.tolist()
    col_labels = df_for_table.columns.tolist()

    table = axes[1].table(
        cellText=cell_text,
        colLabels=col_labels,
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)

    for i, key in enumerate(cell_text):
        bg_color = '#FFFFFF' if i % 2 == 0 else '#f1f1f2'
        for j in range(len(col_labels)):
            table[(i + 1, j)].set_facecolor(bg_color)

    for i in range(len(col_labels)):
        table[(0, i)].set_facecolor("#40466e")
        table[(0, i)].get_text().set_color('white')
        table[(0, i)].get_text().set_weight('bold')


# Degree
def degree_calculations(hypergraph):
    degree_distribution = hypergraph.degree_distribution()
    return [degree_distribution]

# Weight
def calculate_weight_distribution(hypergraph):
    weight_distribution = {}
    for weight in hypergraph.get_weights():
        if weight not in weight_distribution:
            weight_distribution[weight] = 0
        weight_distribution[weight] += 1
    return [weight_distribution]
