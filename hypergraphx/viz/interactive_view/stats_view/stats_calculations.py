import numpy as np
import pandas as pd

from hypergraphx import TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness_averaged, s_closeness_averaged, \
    s_closeness_nodes_averaged, s_betweenness_nodes_averaged, s_betweenness, s_closeness, s_closeness_nodes, \
    s_betweenness_nodes
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


def draw_adjacency(axes, values_list, **kwargs):
    df = pd.DataFrame(values_list[1].todense(), index=values_list[0][1], columns=values_list[0][1])
    sns.heatmap(data = df, ax=axes[1], annot = True, **kwargs)
    axes[1].set_title("Adjacency Matrix")
    axes[1].set_yticks(np.arange(len(values_list[0][1]))+ 0.5)
    axes[1].set_yticklabels(values_list[0][1], rotation=0, va='center')

    axes[1].set_xticks(np.arange(len(values_list[0][1]))+ 0.5)
    axes[1].set_xticklabels(values_list[0][1], rotation=0, ha='center')

    sns.regplot(
        data=values_list[2],
        x='Betweenness Centrality',
        y='Adjacency Factor (t=1)',
        scatter_kws={'s': 100},
        ax=axes[2]
    )
    axes[2].set_title("Adjacency Factor (t=1) - Node Centrality Correlation")
    sns.barplot(x=list(values_list[0][1]), y=list(values_list[0][0].values()), color='skyblue', ax=axes[0],
                label='Adjacency Factor (t=1) Values')
    axes[0].set_title("Adjacency Factor (t=1) Distribution")



#Adjacency
def adjacency_calculations_pool(hypergraph):
    results = []
    adj_factor_matrix = hypergraph.adjacency_factor(1)
    adj_factor_keys_label, adj_factor_label = generate_key(adj_factor_matrix)
    results.append([adj_factor_matrix, adj_factor_keys_label, adj_factor_label])
    adj_matrix = None
    if isinstance(hypergraph, TemporalHypergraph):
        adj_matrix = hypergraph.annealed_adjacency_matrix()
    else:
        adj_matrix = hypergraph.adjacency_matrix()
    results.append(adj_matrix)

    centrality = None
    if isinstance(hypergraph, TemporalHypergraph):
        centrality = s_betweenness_nodes_averaged(hypergraph)
    else:
        centrality = s_betweenness_nodes(hypergraph)
    data_list = []
    for node in centrality:
        degree = centrality[node]
        adj_factor = adj_factor_matrix.get(node, None)
        if adj_factor is not None:
            data_list.append((node, degree, adj_factor))

    df_adj_degree = pd.DataFrame(data_list, columns=['Node', 'Betweenness Centrality', 'Adjacency Factor (t=1)'])
    results.append(df_adj_degree)
    return results

#Centrality
def calculate_centrality_pool(hypergraph):

    is_temporal = isinstance(hypergraph, TemporalHypergraph)

    betweenness_func_edge = s_betweenness_averaged if is_temporal else s_betweenness
    closeness_func_edge = s_closeness_averaged if is_temporal else s_closeness
    betweenness_func_node = s_betweenness_nodes_averaged if is_temporal else s_betweenness_nodes
    closeness_func_node = s_closeness_nodes_averaged if is_temporal else s_closeness_nodes

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
    ddo = compute_binned_degree_distributions(hypergraph)
    sizes = dict()
    for edge in hypergraph.get_edges():
        if len(edge) not in sizes.keys():
            sizes[len(edge)] = 0
        sizes[len(edge)] += 1
    return [degree_distribution, ddo]

def draw_degree(axes, value_list, **kwargs):

    df = pd.DataFrame(list(value_list[0].items()), columns=['Degree', 'Frequency'])

    sns.barplot(x='Degree', y='Frequency', data=df, hue = 'Degree', legend=False, ax = axes[0])

    axes[0].set_title('Node Degree Distribution', fontsize=16)
    axes[0].set_xlabel('Degree', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)

    for p in axes[0].patches:
        axes[0].annotate(f'{int(p.get_height())}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center',
                    xytext=(0, 9),
                    textcoords='offset points')

    draw_degree_distribution_plot(value_list[1],ax = axes[1])

# Weight
def calculate_weight_distribution(hypergraph):
    weight_distribution = {}
    value_list = []
    for weight in hypergraph.get_weights():
        if weight not in weight_distribution:
            weight_distribution[weight] = 0
            value_list.append(len(value_list))
        weight_distribution[weight] += 1
    return [weight_distribution, value_list]

def draw_weight(axes, value_list, **kwargs):
    axes[0].set_xlabel('Weights')
    axes[0].set_title('Weights Frequency')
    sns.barplot(x=list(value_list[0].keys()), y=list(value_list[0].values()), color='skyblue', ax=axes[0], label='Weight Frequency')

    weights_list = [weight for weight, count in value_list[0].items() for _ in range(count)]
    axes[1].set_xlabel('Weights')
    axes[1].set_title('Weights Distribution')
    sns.histplot(data=weights_list, kde=True, stat="density", bins=20, ax = axes[1])

#Similarity
def draw_similarity(ax, data):
    matrix, mapping = data
    labels = sorted(mapping.keys())
    df = pd.DataFrame(matrix, index=labels, columns=labels)
    sns.heatmap(data = df, ax=ax, annot = True)
    ax.set_yticks(np.arange(len(labels))+ 0.5)
    ax.set_yticklabels(labels, rotation=0, va='center')

    ax.set_xticks(np.arange(len(labels))+ 0.5)
    ax.set_xticklabels(labels, rotation=0, ha='center')
    ax.set_title(f'Jaccard Similarity Matrix', fontsize=16)

