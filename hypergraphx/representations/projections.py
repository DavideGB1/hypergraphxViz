import networkx as nx
from hypergraphx import Hypergraph, DirectedHypergraph
from hypergraphx.measures.edge_similarity import intersection, jaccard_similarity


def bipartite_projection(
        h: Hypergraph | DirectedHypergraph,
        *,
        mode: str = "bipartite",  # "bipartite" o "extra_node"
        node_order=None,
        edge_order=None,
        return_obj_to_id: bool = False,
):
    """
    Returns a bipartite or extra-node graph representation of the hypergraph.

    Parameters
    ----------
    h : Hypergraph | DirectedHypergraph
        The hypergraph to be projected.
    mode : str, optional (keyword-only)
        Projection mode:
        - "bipartite": All hyperedges become extra nodes (traditional bipartite)
        - "extra_node": Only hyperedges of order ≥3 become extra nodes, binary edges remain as edges
    node_order : list, optional (keyword-only)
        Explicit node iteration order to make the node-id mapping deterministic.
        If None, uses `h.get_nodes()` order.
    edge_order : list, optional (keyword-only)
        Explicit edge iteration order to make the edge-id mapping deterministic.
        If None, uses `h.get_edges()` order.
    return_obj_to_id : bool, optional (keyword-only)
        If True, also return the reverse mapping `obj_to_id`.

    Returns
    -------
    tuple
        `(g, id_to_obj)` where:
        - `g` is a `networkx.Graph` (or DiGraph for DirectedHypergraph)
        - `id_to_obj` maps node ids to original objects

        If `return_obj_to_id=True`, returns `(g, id_to_obj, obj_to_id)`.

    Raises
    ------
    ValueError
        If mode is not "bipartite" or "extra_node".

    Notes
    -----
    This function is deterministic given `node_order` and `edge_order`.

    Examples
    --------
    >>> h = Hypergraph()
    >>> h.add_edges([(1, 2), (1, 2, 3)])

    >>> # Bipartite mode: all edges become nodes
    >>> g_bip, _ = bipartite_projection(h, mode="bipartite")
    >>> g_bip.nodes()
    # ['N0', 'N1', 'N2', 'E0', 'E1']

    >>> # Extra-node mode: binary edges stay as edges
    >>> g_ext, _ = bipartite_projection(h, mode="extra_node")
    >>> g_ext.nodes()
    # [1, 2, 3, 'E0']
    >>> g_ext.edges()
    # [(1, 2), (1, 'E0'), (2, 'E0'), (3, 'E0')]
    """
    if mode not in {"bipartite", "extra_node"}:
        raise ValueError(f"mode must be 'bipartite' or 'extra_node', got '{mode}'")

    g = nx.Graph()
    id_to_obj = {}
    obj_to_id = {}
    idx = 0

    # Detect if directed
    isDirected = isinstance(h, DirectedHypergraph)
    if isDirected:
        g = g.to_directed()

    # Add nodes
    nodes = h.get_nodes() if node_order is None else list(node_order)

    if mode == "bipartite":
        # Bipartite mode: nodes get "N" prefix
        for node in nodes:
            id_to_obj["N" + str(idx)] = node
            obj_to_id[node] = "N" + str(idx)
            g.add_node(obj_to_id[node], bipartite=0)
            idx += 1
    else:  # extra_node mode
        # Extra-node mode: nodes keep original IDs
        for node in nodes:
            id_to_obj[node] = node
            obj_to_id[node] = node
            g.add_node(node, is_edge="node")

    # Add edges
    idx = 0
    edges = h.get_edges() if edge_order is None else list(edge_order)

    for edge in edges:
        original_edge = edge

        # Normalize edge representation
        if isDirected:
            compressed_edge = []
            for node in edge[0]:
                compressed_edge.append(node)
            for node in edge[1]:
                compressed_edge.append(node)
            edge_key = tuple(compressed_edge)
        else:
            edge_key = tuple(sorted(edge))

        # Get weight if weighted
        weight = 1
        if h.is_weighted():
            weight = h.get_weight(original_edge)

        # EXTRA-NODE MODE: binary edges become direct edges
        if mode == "extra_node" and len(edge_key) == 2:
            g.add_edge(edge_key[0], edge_key[1], weight=weight)

        # BIPARTITE MODE or higher-order edges: create extra node
        else:
            edge_id = "E" + str(idx)
            obj_to_id[edge_key] = edge_id
            id_to_obj[edge_id] = edge_key

            if mode == "bipartite":
                g.add_node(edge_id, bipartite=1, weight=weight)
            else:  # extra_node
                g.add_node(edge_id, weight=weight, is_edge="edge")

            # Connect edge node to its constituent nodes
            if isDirected:
                for node in original_edge[0]:
                    g.add_edge(obj_to_id[node], edge_id, weight=weight)
                for node in original_edge[1]:
                    g.add_edge(edge_id, obj_to_id[node], weight=weight)
            else:
                for node in original_edge:
                    g.add_edge(obj_to_id[node], edge_id, weight=weight)

            idx += 1

    if return_obj_to_id:
        return g, id_to_obj, obj_to_id
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
                g.add_edge(edge[i], edge[j])

    return g

def set_projection(h: Hypergraph) -> [nx.Graph,list]:
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
        g.add_node(node,is_edge = "node")

    idx = 0
    #Manage Hyperedges
    for edge in h.get_edges():
        #Manage binary relations
        if len(edge) == 2:
            weight = 1
            if h.is_weighted():
                weight = h.get_weight(edge)
            g.add_edge(edge[0], edge[1], weight=weight)
        #Any other type of relation
        else:
            obj_to_id[tuple(edge)] = 'E' + str(idx)
            id_to_obj['E' + str(idx)] = edge
            weight = 1
            if h.is_weighted():
                weight = h.get_weight(edge)
            g.add_node(obj_to_id[tuple(edge)], weight=weight, is_edge = "edge")
            for node in edge:
                g.add_edge(node, obj_to_id[tuple(edge)], weight=weight)
            for i in range(len(edge) - 1):
                    if h.is_weighted():
                        g.add_edge(edge[i], edge[i+1], weight=h.get_weight(edge))
                    else:
                        g.add_edge(edge[i], edge[i+1])
            if h.is_weighted():
                g.add_edge(edge[-1], edge[0], weight=h.get_weight(edge))
            else:
                g.add_edge(edge[-1], edge[0])
        idx += 1
    return g, obj_to_id


def line_graph(
    h: Hypergraph,
    distance="intersection",
    s=1,
    weighted=False,
    *,
    edge_order=None,
):
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
    edge_order : list, optional (keyword-only)
        Explicit edge iteration order to make the returned `id_to_edge` mapping deterministic.
        If None, uses `h.get_edges()` order.

    Returns
    -------
    tuple
        `(g, id_to_edge)` where:
        - `g` is a `networkx.Graph` whose nodes are edge-ids `0..m-1`
        - `id_to_edge` maps those ids back to hyperedges

    Notes
    -----
    Computing the line graph can be very expensive for large hypergraphs.
    This function is deterministic given `edge_order`. Without it, edge-id assignment
    depends on the insertion/iteration order of `h`.

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

    edges = h.get_edges() if edge_order is None else list(edge_order)
    nodes = h.get_nodes()
    adj = {}

    for node in nodes:
        adj[node] = h.get_incident_edges(node)

    edge_to_id = {}
    id_to_edge = {}
    cont = 0
    for e in edges:
        edge_key = h._normalize_edge(e)
        edge_to_id[edge_key] = cont
        id_to_edge[cont] = edge_key
        cont += 1

    g = nx.Graph()
    g.add_nodes_from([i for i in range(len(h))])

    vis = {}

    for n in adj:
        for i in range(len(adj[n]) - 1):
            for j in range(i + 1, len(adj[n])):
                id_i = edge_to_id[adj[n][i]]
                id_j = edge_to_id[adj[n][j]]
                k = frozenset((id_i, id_j))
                e_i = set(adj[n][i])
                e_j = set(adj[n][j])
                if k not in vis:
                    w = _distance(e_i, e_j)
                    if w >= s:
                        if weighted:
                            g.add_edge(id_i, id_j, weight=w)
                        else:
                            g.add_edge(id_i, id_j, weight=1)
                    vis[k] = True
    return g, id_to_edge


def directed_line_graph(
    h: DirectedHypergraph,
    distance="intersection",
    s=1,
    weighted=False,
    *,
    edge_order=None,
):
    """
    Returns a line graph of the directed hypergraph.

    Parameters
    ----------
    h : DirectedHypergraph
        The directed hypergraph to be projected.
    distance : str
        The distance function to be used. Can be 'intersection' or 'jaccard'.
    s : float
        The threshold for the distance function.
    weighted : bool
        Whether the line graph should be weighted or not.
    edge_order : list, optional (keyword-only)
        Explicit edge iteration order to make the returned `id_to_edge` mapping deterministic.
        If None, uses `h.get_edges()` order.

    Returns
    -------
    tuple
        `(g, id_to_edge)` where:
        - `g` is a `networkx.DiGraph` whose nodes are edge-ids `0..m-1`
        - `id_to_edge` maps those ids back to directed hyperedges

    Notes
    -----
    Computing the line graph can be very expensive for large hypergraphs.
    This function is deterministic given `edge_order`. Without it, edge-id assignment
    depends on the insertion/iteration order of `h`.

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

    edges = h.get_edges() if edge_order is None else list(edge_order)
    edge_to_id = {}
    id_to_edge = {}
    cont = 0
    for e in edges:
        edge_to_id[e] = cont
        id_to_edge[cont] = e
        cont += 1

    g = nx.DiGraph()
    g.add_nodes_from([i for i in range(len(h))])

    for edge1 in edges:
        for edge2 in edges:
            if edge1 != edge2:
                source = set(edge1[1])
                target = set(edge2[0])
                w = _distance(source, target)
                if w >= s:
                    if weighted:
                        g.add_edge(edge_to_id[edge1], edge_to_id[edge2], weight=w)
                    else:
                        g.add_edge(edge_to_id[edge1], edge_to_id[edge2])

    return g, id_to_edge
