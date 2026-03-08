from math import cos, sin

import numpy as np

from hypergraphx import DirectedHypergraph, Hypergraph
from hypergraphx.viz.__support import __support_to_normal_hypergraph, __check_edge_intersection
from hypergraphx.viz.layout_calculation.__layout_data import RadialLayoutData


def __radial_edge_placement_calculation(h: Hypergraph) -> (list, list):
    """
    Calculate how to place the edges in order to optimize space in the grid.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    Returns
    -------
    sector_list : List of Set of Edges
        The sectors' list. Each sector contain various edges
    """
    sector_found = False
    good_sector_set = True
    sector_list = list()
    sector_list.append(set())
    binary_edges = list()
    # For each edge decide in which sector place them
    for edge in h.get_edges():
        if len(edge) != 2:
            for sector_set in sector_list:
                # We check if there are intersections in the current sector that we are exploring
                for edge_in_column in sector_set:
                    set1 = set(edge_in_column)
                    set2 = set(edge)
                    if __check_edge_intersection(set1, set2):
                        good_sector_set = False
                # If the sector has been found we stop
                if good_sector_set:
                    sector_found = True
                    sector_set.add(edge)
                    break
                else:
                    good_sector_set = True
        else:
            # No sector if the relationship is binary
            binary_edges.append(edge)
            sector_found = True
        if not sector_found:
            # If no sector has been found we simply add a new one
            sector_list.append(set())
            sector_list[len(sector_list) - 1].add(edge)

        sector_found = False
        good_sector_set = True

    return sector_list, binary_edges


def __calculate_node_position(h: Hypergraph, alpha: float, radius: float) -> dict:
    """
    Calculate the position of each node in the image.
    Parameters
    ----------
    h : Hypergraph.
        The hypergraph to be projected.
    alpha : float
        Starting angle position needed for the edge placement.
    radius : float
        Radius of the inner circle.
    Returns
    -------
    pos : Dictionary
        Dictionary with the position of each node
    """
    pos = dict()
    for node in sorted(h.get_nodes()):
        nodes_mapping = h.get_mapping()
        value_x = cos(alpha * nodes_mapping.transform([node])[0]) * radius
        value_x = round(value_x, 2)
        value_y = sin(alpha * nodes_mapping.transform([node])[0]) * radius
        value_y = round(value_y, 2)
        pos[node] = (value_x, value_y)

    return pos


def _compute_radial_layout(
        hypergraph: Hypergraph | DirectedHypergraph,
        radius_scale_factor,
) -> RadialLayoutData:
    """
    Performs all calculations for the radial layout without drawing.
    This includes filtering, positioning, sector allocation, and data preparation.
    """
    is_directed = False
    edge_directed_mapping = None
    if isinstance(hypergraph, DirectedHypergraph):
        hypergraph, edge_directed_mapping = __support_to_normal_hypergraph(hypergraph)
        is_directed = True

    # Remove isolated nodes
    isolated_nodes = [node for node in hypergraph.get_nodes() if hypergraph.degree(node) == 0]
    hypergraph.remove_nodes(isolated_nodes)

    # Calculate core layout parameters
    num_nodes = hypergraph.num_nodes()
    if num_nodes == 0:
        return RadialLayoutData(hypergraph)  # Handle empty graph case

    radius = (num_nodes * radius_scale_factor) / (2 * np.pi)
    alpha = (2 * np.pi) / num_nodes

    # Perform calculations
    nodes_mapping = hypergraph.get_mapping()
    pos = __calculate_node_position(hypergraph, alpha, radius)
    sector_list, binary_edges = __radial_edge_placement_calculation(hypergraph)


    return RadialLayoutData(
        hypergraph=hypergraph,
        is_directed=is_directed,
        edge_directed_mapping=edge_directed_mapping,
        pos=pos,
        radius=radius,
        sector_list=sector_list,
        binary_edges=binary_edges,
        alpha=alpha,
        nodes_mapping=nodes_mapping,
    )