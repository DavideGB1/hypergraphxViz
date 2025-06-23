from hypergraphx import TemporalHypergraph
from hypergraphx.measures.s_centralities import s_betweenness_averaged, s_closeness_averaged, \
    s_closenness_nodes_averaged, s_betweenness_nodes_averaged, s_betweenness, s_closeness, s_closeness_nodes, \
    s_betweenness_nodes
from hypergraphx.motifs import compute_motifs
from hypergraphx.viz.interactive_view.support import generate_key


# Motifs
def motifs_calculations(hypergraph):
    motifs_3 = compute_motifs(hypergraph, order=3)
    motifs3_profile = [i[1] for i in motifs_3['norm_delta']]
    return motifs3_profile


def draw_adjacency(axes, values_list, **kwargs):
    draw_bar(axes[0], values_list[0], "Nodes", "Adjacency Factor (t=0)")
    draw_bar(axes[1], values_list[1], "Nodes", "Adjacency Factor (t=1)")

#Adjacency
def adjacency_calculations_pool(hypergraph):
    results = []
    for t in [0,1]:
        adj_factor = hypergraph.adjacency_factor(t)
        adj_factor_keys_label, adj_factor_label = generate_key(adj_factor)
        results.append([adj_factor, adj_factor_keys_label, adj_factor_label])
    return results

#Centrality
def calculate_centrality_pool(hypergraph):
    functions = [
        s_betweenness_averaged if isinstance(hypergraph, TemporalHypergraph) else s_betweenness,
        s_closeness_averaged if isinstance(hypergraph, TemporalHypergraph) else s_closeness,
        s_betweenness_nodes_averaged if isinstance(hypergraph, TemporalHypergraph) else s_betweenness_nodes,
        s_closenness_nodes_averaged if isinstance(hypergraph, TemporalHypergraph) else s_closeness_nodes,
    ]
    results = []
    for func in functions:
        result = func(hypergraph)
        keys_label, keys = generate_key(result)
        results.append((result, keys_label, keys))
    return results

def draw_centrality(axes, values_list, **kwargs):
    draw_bar(axes[0, 0], values_list[0], 'Edges', 'Edges Betweenness Centrality')
    draw_bar(axes[0, 1], values_list[1], 'Edges', 'Edges Closeness Centrality')
    draw_bar(axes[1, 0], values_list[2], 'Nodes', 'Nodes Betweenness Centrality')
    draw_bar(axes[1, 1], values_list[3], 'Nodes', 'Nodes Closeness Centrality')

# Degree
def degree_calculations(hypergraph):
    degree_distribution = hypergraph.degree_distribution()
    sizes = dict()
    for edge in hypergraph.get_edges():
        if len(edge) not in sizes.keys():
            sizes[len(edge)] = 0
        sizes[len(edge)] += 1
    return [degree_distribution, sizes]

def draw_degree(axes, value_list, **kwargs):
    draw_bar(axes[0], value_list[0], "Degrees", "Degree Distribution")
    draw_bar(axes[1], value_list[1], "Sizes", "Size Distribution")

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
    weights = value_list[0]
    positions = value_list[1]
    axes.bar(positions, weights.values())
    axes.set_xlabel('Weights')
    axes.set_title('Weights Distribution')
    axes.set_xticks(positions, list(weights.keys()))
    axes.set_ylim(0, max(weights.values()) + 1)
    axes.set_yticks(range(1, max(weights.values()) + 1))



#Drawing
def draw_bar(ax, values, label, title, y_ticks_increment=1):
    dict_values = values if isinstance(values, dict) else values[0]
    labels = values[1] if isinstance(values, tuple) else dict_values.keys()

    ax.bar(labels, dict_values.values())
    ax.set_xlabel(label)
    ax.set_ylabel('Values')
    ax.set_title(title)
    try:
        ax.set_xticks(list(dict_values.keys()))
        max_value = max(dict_values.values())
        ax.set_yticks(range(1, max_value + y_ticks_increment))
        ax.set_ylim(0, max_value + y_ticks_increment)

    except Exception:
        pass