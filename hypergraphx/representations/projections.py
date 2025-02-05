import networkx as nx

from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.measures.edge_similarity import intersection, jaccard_similarity


def bipartite_projection(h: Hypergraph):
    """
    Returns a bipartite graph representation of the hypergraph.

    Parameters
    ----------
    h : Hypergraph
        The hypergraph to be projected.

    Returns
    -------
    networkx.Graph
        The bipartite graph representation of the hypergraph.

    """
    g = nx.Graph()
    id_to_obj = {}
    obj_to_id = {}
    idx = 0

    for node in h.get_nodes():
        id_to_obj["N" + str(idx)] = node
        obj_to_id[node] = "N" + str(idx)
        idx += 1
        g.add_node(obj_to_id[node], bipartite=0)

    idx = 0

    for edge in h.get_edges():
        edge = tuple(sorted(edge))
        obj_to_id[edge] = "E" + str(idx)
        id_to_obj["E" + str(idx)] = edge
        idx += 1
        if h.is_weighted():
            g.add_node(obj_to_id[edge], bipartite=1,weight=h.get_weight(edge))
        else:
            g.add_node(obj_to_id[edge], bipartite=1)

        for node in edge:
                g.add_edge(obj_to_id[edge], obj_to_id[node])

    return g, id_to_obj


def clique_projection(h: Hypergraph, keep_isolated=False):
    """
    Returns a clique projection of the hypergraph.

    Parameters
    ----------
    h : Hypergraph
        The hypergraph to be projected.
    keep_isolated : bool
        Whether to keep isolated nodes or not.

    Returns
    -------
    networkx.Graph
        The clique projection of the hypergraph.

    Notes
    -----
    Computing the clique projection can be very expensive for large hypergraphs.

    Example
    -------
    >>> import networkx as nx
    >>> import hypergraphx as hgx
    >>> from hypergraphx.representations.projections import clique_projection
    >>>
    >>> h = hgx.Hypergraph()
    >>> h.add_nodes([1, 2, 3, 4, 5])
    >>> h.add_edges([(1, 2), (1, 2, 3), (3, 4, 5)])
    >>> g = clique_projection(h)
    >>> g.edges()
    EdgeView([(1, 2), (1, 3), (2,3), (3, 4), (3, 5), (4, 5)])
    """
    g = nx.Graph()

    if keep_isolated:
        for node in h.get_nodes():
            g.add_node(node)

    for edge in h.get_edges():
        for i in range(len(edge) - 1):
            for j in range(i + 1, len(edge)):
                if h.is_weighted():
                    g.add_edge(edge[i], edge[j],weight = h.get_weight(edge) )
                else:
                    g.add_edge(edge[i], edge[j])

    return g


def line_graph(h: Hypergraph, distance="intersection", s=1, weighted=False):
    """
    Returns a line graph of the hypergraph.

    Parameters
    ----------
    h : Hypergraph
        The hypergraph to be projected.
    distance : str
        The distance function to be used. Can be 'intersection' or 'jaccard'.
    s : float
        The threshold for the distance function.
    weighted : bool
        Whether the line graph should be weighted or not.

    Returns
    -------
    networkx.Graph
        The line graph of the hypergraph.

    Notes
    -----
    Computing the line graph can be very expensive for large hypergraphs.

    Example
    -------
    >>> import networkx as nx
    >>> import hypergraphx as hgx
    >>> from hypergraphx.representations.projections import line_graph
    >>>
    >>> h = hgx.Hypergraph()
    >>> h.add_nodes([1, 2, 3, 4, 5])
    >>> h.add_edges([(1, 2), (1, 2, 3), (3, 4, 5)])
    >>> g, idx = line_graph(h)
    >>> g.edges()
    EdgeView([(0, 1), (1, 2)])
    """

    def _distance(a, b):
        if distance == "intersection":
            return intersection(a, b)
        if distance == "jaccard":
            return jaccard_similarity(a, b)

    edges = h.get_edges()
    nodes = h.get_nodes()
    adj = {}

    for node in nodes:
        adj[node] = h.get_incident_edges(node)

    edge_to_id = {}
    id_to_edge = {}
    cont = 0
    for e in edges:
        e = tuple(sorted(e))
        edge_to_id[e] = cont
        id_to_edge[cont] = e
        cont += 1

    g = nx.Graph()
    g.add_nodes_from([i for i in range(len(h))])

    vis = {}

    for n in adj:
        for i in range(len(adj[n]) - 1):
            for j in range(i + 1, len(adj[n])):
                k = tuple(sorted((edge_to_id[adj[n][i]], edge_to_id[adj[n][j]])))
                e_i = set(adj[n][i])
                e_j = set(adj[n][j])
                if k not in vis:
                    w = _distance(e_i, e_j)
                    if w >= s:
                        if weighted:
                            g.add_edge(
                                edge_to_id[adj[n][i]], edge_to_id[adj[n][j]], weight=w
                            )
                        else:
                            g.add_edge(
                                edge_to_id[adj[n][i]], edge_to_id[adj[n][j]], weight=1
                            )
                    vis[k] = True
    return g, id_to_edge

def extra_node_projection(h: Hypergraph|DirectedHypergraph) -> [nx.Graph,list]:
    """
    Returns a graph representation of the hypergraph using the extra-node projection method.
    Parameters
    ----------
    h : Hypergraph
        The hypergraph to be projected.
    Returns
    -------
    networkx.Graph
        The graph representation of the hypergraph.
    """
    g = nx.Graph()
    id_to_obj = {}
    obj_to_id = {}
    idx = 0

    #Add normal nodes
    for node in h.get_nodes():
        id_to_obj[idx] = node
        obj_to_id[node] = idx
        idx += 1
        g.add_node(node)

    idx = 0
    binary_edges = list()
    isDirected = False
    if isinstance(h, DirectedHypergraph):
        g = g.to_directed()
        isDirected = True
    #Manage Hyperedges
    for edge in h.get_edges():
        original_edge = edge
        if isDirected:
            compressed_edge = []
            for node in edge[0]:
                compressed_edge.append(node)
            for node in edge[1]:
                compressed_edge.append(node)
            edge = compressed_edge
        else:
            edge = tuple(sorted(edge))
        #Manage binary relations
        if len(edge) == 2:
            weight = 1
            if h.is_weighted():
                weight = h.get_weight(edge)
            binary_edges.append((edge[0], edge[1], weight))
        #Any other type of relation
        else:
            obj_to_id[tuple(edge)] = 'E' + str(idx)
            id_to_obj['E' + str(idx)] = edge
            weight = 1
            if h.is_weighted():
                weight = h.get_weight(original_edge)
            g.add_node(obj_to_id[tuple(edge)], weight=weight)
            if isDirected:
                for node in original_edge[0]:
                    g.add_edge(node,obj_to_id[tuple(edge)], weight=weight)
                for node in original_edge[1]:
                    g.add_edge(obj_to_id[tuple(edge)],node, weight=weight)
            else:
                for node in original_edge:
                    g.add_edge(node,obj_to_id[tuple(edge)], weight=weight)
        idx += 1

    return g, binary_edges, isDirected

