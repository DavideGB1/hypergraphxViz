from hypergraphx import DirectedHypergraph, TemporalHypergraph, Hypergraph
from hypergraphx.viz.__support import __ignore_unused_args, __check_edge_intersection, __support_to_normal_hypergraph
from hypergraphx.viz.layout_calculation.__layout_data import PAOHLayoutData

def __PAOH_edge_placement_calculation(l: list) -> list:
    column_found = False
    column_list = list()
    column_list.append(set())
    for edge in l:
        for column_set in column_list:
            good_column_set = all(
                not __check_edge_intersection(set(edge_in_column), set(edge)) for edge_in_column in column_set)
            if good_column_set:
                column_found = True
                column_set.add(edge)
                break
        if not column_found:
            column_list.append({edge})
        column_found = False
    return [list(s) for s in column_list]

@__ignore_unused_args
def calculate_paoh_layout(
        hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph,
        space_optimization: bool = False,
        sort_nodes_by: bool = False,
        sorting_mapping: dict = None,
) -> PAOHLayoutData:
    """
    Calculates all the necessary data and layout for a PAOH plot without drawing.
    This function is designed to be run in a separate process to avoid blocking the GUI.
    Returns
    -------
    dict
        A dictionary containing all the pre-calculated data needed for drawing.
    """

    def get_edge_mapping_sorter(tup):
        max_value = 0
        for item in tup:
            # Get the degree from the mapping
            item_degree = sorting_mapping[item]
            if item_degree > max_value:
                max_value = item_degree
        return (max_value, tuple(sorted(tup)))

    if sort_nodes_by and space_optimization:
        raise ValueError("It's not possible to sort nodes and optimize space at the same time.")

    if sort_nodes_by and sorting_mapping is None:
        raise ValueError("A Sorting Mapping must be provided is the nodes are going to be sorted")


    # Get the list of nodes from the filtered hypergraph
    nodes = hypergraph.get_nodes()
    # Sort the nodes based on the specified criteria
    if sort_nodes_by:
        sorted_node_list = sorted(nodes, key=lambda node: (sorting_mapping.get(node, 0), node))
    else:
        sorted_node_list = sorted(nodes)

    # Create Node Mapping from the sorted list
    node_mapping = {node: i for i, node in enumerate(sorted_node_list)}


    # Manage Directed Hypergraphs
    isDirected = isinstance(hypergraph, DirectedHypergraph)

    edge_directed_mapping = {}
    if isDirected:
        hypergraph, edge_directed_mapping = __support_to_normal_hypergraph(hypergraph)

    # Manage Temporal Hypergraphs
    isTemporal = isinstance(hypergraph, TemporalHypergraph)

    timestamp_mapping = {}
    timestamps_layout = []

    if isTemporal:
        for edge in hypergraph.get_edges():
            if edge[0] not in timestamp_mapping:
                timestamp_mapping[edge[0]] = []
            timestamp_mapping[edge[0]].append(edge[1])

        sorted_timestamps = sorted(timestamp_mapping.keys())
        for ts_key in sorted_timestamps:
            edge_set = timestamp_mapping[ts_key]
            if space_optimization:
                timestamps_layout.append(__PAOH_edge_placement_calculation(edge_set))
            else:
                if sort_nodes_by:
                    edge_set = sorted(edge_set, key=get_edge_mapping_sorter, reverse=True)
                timestamps_layout.append([[edge] for edge in edge_set])
    else:
        edges = hypergraph.get_edges()
        if space_optimization:
            column_list = __PAOH_edge_placement_calculation(edges)
        else:
            if sort_nodes_by:
                edges = sorted(edges, key=get_edge_mapping_sorter, reverse=True)
            column_list = [[edge] for edge in edges]
        timestamps_layout.append(column_list)

    # Get plot width
    final_idx = 0
    for timestamp_group in timestamps_layout:
        for _ in timestamp_group:
            final_idx += 0.5
        if isTemporal:
            final_idx += 0.5
    if isTemporal:
        final_idx -= 0.5

    # Return the needed datas
    result = PAOHLayoutData(
        hypergraph=hypergraph,
        edge_directed_mapping=edge_directed_mapping,
        is_directed=isDirected,
        is_temporal=isTemporal,
        node_mapping=node_mapping,
        timestamps_layout=timestamps_layout,
        timestamp_mapping=timestamp_mapping,
        final_idx_width=final_idx,
    )

    return result