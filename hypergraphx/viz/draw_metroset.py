import random
import sys
from typing import Optional

from matplotlib import pyplot as plt
from networkx import subgraph, kamada_kawai_layout
from hypergraphx import Hypergraph
from hypergraphx.viz.__chivers_rodgers import chivers_rodgers
from hypergraphx.viz.__support import __draw_line, __distance, __calculate_incidence

sys.path.append("..")
import networkx as nx
import math

def __compress_nodes(
        h: Hypergraph,
        only_in_one_edge: list,
        edge_mapping: dict) -> dict:
    """
    Compress the hypergraph nodes in order to optimize the calculations.
    Parameters
    ----------
        h : Hypergraph
            The starting Hypergraph
        only_in_one_edge : list
            A list of all the nodes that are only in one hyperedge.
        edge_mapping : dict
            A mapping for each hyperedge.
    Returns
    -------
         compressed_nodes : list
            The new compressed nodes' list.
    """
    # Identify similar nodes and compress them in one big node
    compressed_nodes = dict()
    for node in h.get_nodes():
        if node not in only_in_one_edge:
            incident_edges = sorted([edge_mapping[edge] for edge in h.get_incident_edges(node)])
            incident_edges = tuple(incident_edges)
            if incident_edges not in compressed_nodes.keys():
                compressed_nodes[incident_edges] = node
            else:
                x = compressed_nodes[incident_edges]
                compressed_nodes[incident_edges] = list()
                if type(x) is list:
                    compressed_nodes[incident_edges] += x
                else:
                    compressed_nodes[incident_edges].append(x)
                compressed_nodes[incident_edges].append(node)

    return compressed_nodes


def __compress_edges(
        h: Hypergraph,
        only_in_one_edge: list,
        compressed_nodes: list) -> [list, dict]:
    """
    Compress the hypergraph edges in order to optimize the calculations.
    Parameters
    ----------
       h : Hypergraph
           The starting Hypergraph
       only_in_one_edge : list
           A list of all the nodes that are only in one hyperedge.
       compressed_nodes : list
              A list with the compressed nodes.
    Returns
    -------
         compressed_edges : list
            A list with the compressed nodes.
         edge_to_compressed_edge : dict
            A mapping from the original edges to the compressed ones.
    """
    edge_to_compressed_edge = dict()
    compressed_edges = list()
    for edge in h.get_edges():
        edge_clone = set(edge)
        compressed_edge = tuple()
        for node in only_in_one_edge:
            edge_clone = edge_clone.difference({node})
        for compressed_node in compressed_nodes:
            edge = set(sorted(edge))
            if type(compressed_node) is list:
                compressed_node = set(sorted(compressed_node))
            else:
                compressed_node = {compressed_node}
            if compressed_node.issubset(edge) and len(edge.intersection(compressed_node)) > 1:
                compressed_edge += (tuple(sorted(compressed_node)),)
                for value in compressed_node:
                    edge_clone.remove(value)

        if len(edge_clone) > 0:
            compressed_edge += tuple(edge_clone)
        if len(compressed_edge) > 1:
            compressed_edges.append(compressed_edge)
            edge_to_compressed_edge[tuple(edge)] = compressed_edge

    return compressed_edges, edge_to_compressed_edge


def __compress_hypergraph(h: Hypergraph) -> [nx.Graph, dict, list]:
    """
    Compress the hypergraph in order to optimize the calculations.
    Parameters
    ----------
        h : Hypergraph
            The starting Hypergraph
    Returns
    -------
        compressed_graph : nx.Graph
            The compressed graph.
        one_edge_to_edge : dict
            A mapping used to retrieve the original edge of the nodes present in only one hyperedge.
        only_in_one_edge : list
            A list of all the nodes that are only in one hyperedge.
    """
    # Identify Nodes that are only in one hyperedge
    one_edge_to_edge = dict()
    only_in_one_edge = list()
    for node in h.get_nodes():
        if h.degree(node) == 1:
            only_in_one_edge.append(node)
            one_edge_to_edge[node] = h.get_incident_edges(node)[0]

    edge_mapping = dict()
    idx = 0
    for edge in h.get_edges():
        edge_mapping[edge] = idx
        idx += 1

    compressed_nodes = __compress_nodes(h, only_in_one_edge, edge_mapping)

    # Add compressed nodes to the support graph
    compressed_graph = nx.Graph()
    for compressed_node in compressed_nodes:
        if type(compressed_node) is not list:
            compressed_graph.add_node(compressed_node)
        else:
            compressed_graph.add_node(tuple(compressed_node))

    return compressed_graph, one_edge_to_edge, only_in_one_edge


def __calculate_similarity_matrix(
        node_list: list,
        edge_list: list) -> dict:
    """
    Create the similarity matrix for the node placement calculations.
    Parameters
    ----------
        node_list: list
        edge_list: list
    Returns
    -------
        similarity_matrix : dict
            Matrix with the similarity between nodes.
    """
    similarity_matrix = dict()
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2:
                if type(node1) is list:
                    node1 = tuple(node1)
                if type(node2) is list:
                    node2 = tuple(node2)
                incident_edges1 = __calculate_incidence(node1, edge_list)
                incident_edges2 = __calculate_incidence(node2, edge_list)
                similarity = len(incident_edges1.intersection(incident_edges2))
                similarity_matrix[(node1, node2)] = similarity
    return similarity_matrix


def __similarity_graph(
        g: nx.Graph,
        edge_list: list,
        similarity_matrix: dict) -> nx.Graph:
    """
    Create the similarity matrix for the node placement calculations.
    Parameters
    ----------
        g : nx.Graph
            Starting graph.
        edge_list : list
        similarity_matrix : dict
            Matrix with the similarity between nodes.
    Returns
    -------
        g : nx.Graph
            New graph with the similarity between nodes as edge weight.
    """
    for edge in edge_list:
        for i in range(len(edge) - 1):
            for j in range(i + 1, len(edge)):
                if similarity_matrix[(edge[i], edge[j])] != 0:
                    similarity_weight = 1 / similarity_matrix[(edge[i], edge[j])]
                else:
                    similarity_weight = 2
                g.add_edge(edge[i], edge[j], weight=similarity_weight)
    return g

def __calculate_compressed_paths(
        g: nx.Graph,
        edge_list: list) -> [dict,list]:
    """
    Decide how to place the nodes inside the compressed paths.
    Parameters
    ----------
        g : nx.Graph
            Starting graph.
        edge_list : list
    Returns
    -------
        edge_to_path : dict
            Mapping from edge to path.
        paths : list
            A list with the new ordered paths.
    """
    edge_to_path = dict()
    paths = list()
    for edge in edge_list:
        edge_graph = subgraph(g, edge)
        method = lambda G, weight: nx.approximation.simulated_annealing_tsp(edge_graph,
            list(edge_graph) + [next(iter(edge_graph))], weight=weight, temp=5000)
        path = nx.approximation.traveling_salesman_problem(edge_graph, method=method, cycle=False)
        paths.append(path)
        edge_to_path[edge] = path

    return edge_to_path, paths

def __unpack_paths(paths: list) -> list:
    """
    Decide how to place the nodes inside the compressed paths.
    Parameters
    ----------
        paths : list
            A list of compressed paths.
    Returns
    -------
        paths : list
            The list of unpacked paths.
    """
    for path in paths:
        for node in path:
            if type(node) is tuple:
                index = path.index(node)
                path.pop(index)
                for x in node:
                    path.insert(index, x)
                    index += 1

    return paths

def __add_only_in_one_edge(
        paths: list,
        node_list: list,
        edge_to_path: dict,
        edge_to_new_edge: dict,
        one_edge_to_edge: dict) -> list:
    """
    Add back the nodes present in only one hyperedge.
    Parameters
    ----------
        paths : list
            A list of  paths.
        node_list : list
            The list with the nodes to add.
        edge_to_path : dict
            Mapping used to determine the paths that are present in the edges.
        edge_to_new_edge : dict
            Mapping from compressed edges to normal edges.
        one_edge_to_edge : dict
            A mapping used to retrieve the original edge of the nodes present in only one hyperedge.
    Returns
    -------
        paths : list
            The paths' list with the new nodes.
    """
    for node in node_list:
        try:
            current_path = edge_to_path[edge_to_new_edge[one_edge_to_edge[node]]]
            current_path.append(node)
            index = paths.index(edge_to_path[edge_to_new_edge[one_edge_to_edge[node]]])
            paths.pop(index)
            paths.insert(index, current_path)
        except KeyError:
            if list(one_edge_to_edge[node]) not in paths:
                paths.append(list(one_edge_to_edge[node]))
    return paths


def __to_complete_path_graph(paths: list) -> nx.Graph:
    """
    Creates a completed graph using the paths.
    Parameters
    ----------
        paths : list
            A list of  paths.
    Returns
    -------
        g : nx.Graph
            The new complete graph.
    """
    g = nx.Graph()
    for edge in paths:
        for i in range(len(edge) - 1):
            for j in range(i + 1, len(edge)):
                g.add_edge(edge[i], edge[j])
    return g


def __calculate_distances(
        node_list: list,
        similarity_matrix: dict,
        layout: dict) -> dict:
    """
    Modify the similarity matrix adding the euclidean distance factors.
    Parameters
    ----------
        node_list : list
            The list with all the nodes.
        similarity_matrix : dict
            The matrix to edit.
        layout : dict
            Position of all the nodes in the 2D plane.
    Returns
    -------
        similarity_matrix : dict
            The new similarity matrix.
    """
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2:
                euclidean_distance = __distance(layout, node1, node2)
                similarity = similarity_matrix[node1, node2]
                try:
                    similarity = 1 / similarity
                except ZeroDivisionError:
                    similarity = 2
                value = math.sqrt(similarity * euclidean_distance)
                similarity_matrix[node1, node2] = value
    return similarity_matrix


def __calculate_paths(
        paths: list,
        layout: dict) -> [nx.Graph, list]:
    """
    Rearrange the nodes in the paths in order to improve the layout.
    Parameters
    ----------
        paths : list
            A list of  paths.
        layout : dict
            Position of all the nodes in the 2D plane.
    Returns
    -------
        refined : nx.Graph
            The new refined graph.
        new_paths : list
            A list with the new paths.
    """
    new_paths = list()
    entire_copy = __to_complete_path_graph(paths)
    similarity_matrix = __calculate_similarity_matrix(entire_copy.nodes(), entire_copy.edges())
    similarity_matrix = __calculate_distances(entire_copy.nodes(), similarity_matrix, layout)
    entire_copy = __similarity_graph(entire_copy, paths, similarity_matrix)
    for path in paths:
        edge_graph = subgraph(entire_copy, path)
        method = lambda G, weight: nx.approximation.simulated_annealing_tsp(edge_graph, "greedy",
            weight=weight, temp=5000)
        new_path = nx.approximation.traveling_salesman_problem(edge_graph, method=method, cycle=False)
        new_paths.append(new_path)

    refined = nx.Graph()
    for path in new_paths:
        for i in range(len(path) - 1):
            refined.add_edge(path[i], path[i + 1])

    return refined, new_paths


def __calculate_new_paths(
        paths: list,
        layout: dict,
        iterations: int = 10) -> [nx.Graph, list]:
    """
    Rearrange the nodes in the paths in order to improve the layout.
    Parameters
    ----------
        paths : list
            A list of  paths.
        layout : dict
            Position of all the nodes in the 2D plane.
        iterations : int
            Number of iterations.
    Returns
    -------
        refined : nx.Graph
            The new refined graph.
        paths : list
            A list with the new paths.
    """
    refined = nx.Graph()
    for i in range(iterations):
        refined, new_paths = __calculate_paths(paths, layout)
        if new_paths != paths:
            paths = new_paths
        else:
            break
    return refined, paths


def __calculate_palette(paths: list) -> list:
    """
    Create a palette with a color for each path.
    Parameters
    ----------
        paths : list
            A list of  paths.
    Returns
    -------
        palette : list
            A list of colors.
    """
    palette = list()
    while len(palette) < len(paths):
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        if color not in palette:
            palette.append(color)
    return palette


def __draw_metrograph(
        g: nx.Graph,
        paths: list,
        layout: dict,
        ax: plt.Axes,
        palette: list = None,
        draw_labels: bool = True,
        node_size: int = 300,
        node_color: str = "#1f48b4",
        node_shape: str = "o") -> None:
    """
    Draw the graph as a metro map.
    Parameters
    ----------
        g : nx.Graph
           The graph to draw.
        paths : list
            A list of  paths.
        layout : dict
            Position of all the nodes in the 2D plane.
        ax : plt.Axes
            Axis if the user wants to specify an image.
        palette : list
            A list of colors.
        draw_labels : bool
            Decide if labels should be drawn.
        node_size : int
            Size of the nodes.
        node_color : str
            HEX value that determines the color of the nodes.
        node_shape : str
            Use standard networkx shapes.
    Returns
    -------
    """
    paths_in_edge = dict()
    idx = 0
    for path in paths:
        for i in range(len(path) - 1):
            key = (path[i], path[i + 1])
            key = tuple(sorted(key))
            try:
                prev = paths_in_edge[key]
            except KeyError:
                prev = []
            paths_in_edge[key] = list()
            paths_in_edge[key] += prev
            paths_in_edge[key] += [idx]

        idx += 1
    if palette is None:
        palette = __calculate_palette(paths)
    else:
        if len(palette) != len(paths):
            raise Exception("There are more hyperedges than colors in the palette")

    passo_edge = dict()
    for edge in g.edges():
        key = (edge[0], edge[1])
        key = tuple(sorted(key))
        try:
            lines_in_edge = len(paths_in_edge[key])
            if lines_in_edge % 2 != 0:
                passo = lines_in_edge - 1
                passo /= 2
            else:
                passo = lines_in_edge / 2
            passo_edge[key] = passo
        except KeyError:
            pass


    idx = 0
    for path in paths:
        for i in range(len(path) - 1):
            key = (path[i], path[i + 1])
            key = tuple(sorted(key))
            try:
                passo = passo_edge[key]
                __draw_line(layout, palette, path, i, idx, passo, ax = ax)
                passo_edge[key] -= 1
            except KeyError:
                pass

        idx += 1

    nx.draw_networkx_nodes(g, layout, ax = ax, node_size = node_size, node_shape=node_shape, node_color = node_color)
    if draw_labels:
        labels = dict((n, n) for n in g.nodes())
        nx.draw_networkx_labels(g, pos=layout, labels=labels, ax = ax)


def draw_metroset(
        h: Hypergraph,
        iterations: int = 10,
        figsize: tuple[float, float] = (10, 10),
        dpi: int = 300,
        ax: Optional[plt.Axes] = None,
        palette: list = None,
        edge_lenght: int = 300,
        draw_labels: bool = True,
        node_size: int = 300,
        node_color: str = "#1f48b4",
        node_shape: str = "o") -> None:
    """
    Draw the hypergraph using the MetroSet pipeline.
    Parameters
    ----------
        h : Hypergraph
           The hypergraph to draw.
        iterations : int
            Number of iterations for the optimization algorithm.
        figsize : tuple, optional
            Tuple of float used to specify the image size. Used only if ax is None.
        dpi : int, optional
            The dpi for the figsize. Used only if ax is None.
        ax : plt.Axes, optional
            Axis if the user wants to specify an image.
        edge_lenght : int
            Ideal lenght for the metro edges.
        palette : list
            A list of colors.
        draw_labels : bool
            Decide if labels should be drawn.
        node_size : int
            Size of the nodes.
        node_color : str
            HEX value that determines the color of the nodes.
        node_shape : str
            Use standard networkx shapes.
    Returns
    -------
    """
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()
    compressed_graph, one_edge_to_edge, only_in_one_edge = __compress_hypergraph(h)
    compressed_edges, edge_to_new_edge = __compress_edges(h, only_in_one_edge, list(compressed_graph.nodes()))
    for edge in compressed_edges:
        for i in range(len(edge) - 1):
            compressed_graph.add_edge(edge[i], edge[i+1])
    similarity_matrix = __calculate_similarity_matrix(list(compressed_graph.nodes()), compressed_edges)
    compressed_graph = __similarity_graph(compressed_graph, compressed_edges, similarity_matrix)
    edge_to_path, paths = __calculate_compressed_paths(compressed_graph, compressed_edges)
    paths = __unpack_paths(paths)
    paths = __add_only_in_one_edge(paths, only_in_one_edge, edge_to_path, edge_to_new_edge, one_edge_to_edge)
    path_graph = __to_complete_path_graph(paths)
    initial_layout = kamada_kawai_layout(path_graph)
    refined_graph, paths = __calculate_new_paths(paths, initial_layout, iterations)
    initial_layout = chivers_rodgers(refined_graph, paths, initial_layout, edgeLength=edge_lenght)
    __draw_metrograph(refined_graph, paths, initial_layout, draw_labels = draw_labels, node_size = node_size,
                      node_color = node_color, node_shape = node_shape, palette = palette, ax = ax)