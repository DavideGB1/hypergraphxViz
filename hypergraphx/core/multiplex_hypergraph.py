from hypergraphx import Hypergraph


class MultiplexHypergraph:

    def __init__(self, edge_list=None, edge_layer=None, hypergraph_metadata=None, weighted=False, weights=None, edge_metadata=None):
        if hypergraph_metadata is None:
            self.hypergraph_metadata = {}
        else:
            self.hypergraph_metadata = hypergraph_metadata
        self.node_metadata = {}
        self.edge_metadata = {}
        self._weighted = weighted
        self._weights = {}
        self.hypergraph_metadata['weighted'] = weighted
        self._edge_list = {}
        self.reverse_edge_list = {}
        self.next_edge_id = 0
        self.existing_layers = set()

        if edge_list is not None:
                self.add_edges(edge_list, edge_layer=edge_layer, weights=weights, metadata=edge_metadata)

    def get_edge_metadata(self, edge, layer):
        k = (tuple(sorted(edge)), layer)
        if k not in self._edge_list:
            raise ValueError("Edge {} not in hypergraph.".format(edge))
        return self.edge_metadata[self._edge_list[k]]

    def is_weighted(self):
        return self._weighted

    def get_edge_list(self):
        return self._edge_list

    def set_edge_list(self, edge_list):
        self._edge_list = edge_list

    def get_existing_layers(self):
        return self.existing_layers

    def set_existing_layers(self, existing_layers):
        self.existing_layers = existing_layers
    
    def get_nodes(self, metadata=False):
        if metadata:
            return self.node_metadata
        else:
            return list(self.node_metadata.keys())


    def add_node(self, node, metadata=None):
        """
        Add a node to the hypergraph. If the node is already in the hypergraph, nothing happens.

        Parameters
        ----------
        node : object
            The node to add.

        Returns
        -------
        None
        """
        if node not in self.node_metadata:
            if metadata is not None:
                self.node_metadata[node] = metadata
            else:
                self.node_metadata[node] = {}

    def add_nodes(self, node_list: list, node_metadata=None):
        """
        Add a list of nodes to the hypergraph.

        Parameters
        ----------
        node_list : list
            The list of nodes to add.

        Returns
        -------
        None
        """
        for node in node_list:
            try:
                self.add_node(node, node_metadata[node] if node_metadata is not None else None)
            except KeyError:
                raise ValueError("The metadata dictionary must contain an entry for each node in the node list.")


    def add_edges(self, edge_list, edge_layer, weights=None, metadata=None):
        """Add a list of hyperedges to the hypergraph. If a hyperedge is already in the hypergraph, its weight is updated.

        Parameters
        ----------
        edge_list : list
            The list of hyperedges to add.

        edge_layer : list
            The list of layers to which the hyperedges belong.

        weights : list, optional
            The list of weights of the hyperedges. If the hypergraph is weighted, this must be provided.

        metadata : list, optional
            The list of metadata of the hyperedges.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the hypergraph is weighted and no weights are provided or if the hypergraph is not weighted and weights are provided.

        """
        if weights is not None and not self._weighted:
            print(
                "Warning: weights are provided but the hypergraph is not weighted. The hypergraph will be weighted."
            )
            self._weighted = True

        if self._weighted and weights is not None:
            if len(set(edge_list)) != len(list(edge_list)):
                raise ValueError(
                    "If weights are provided, the edge list must not contain repeated edges."
                )
            if len(list(edge_list)) != len(list(weights)):
                raise ValueError("The number of edges and weights must be the same.")

        i = 0
        if edge_list is not None:
            for edge in edge_list:
                self.add_edge(
                    edge,
                    edge_layer[i],
                    weight=weights[i]
                    if self._weighted and weights is not None
                    else None,
                    metadata=metadata[i] if metadata is not None else None,
                )
                i += 1

    def add_edge(self, edge, layer, weight=None, metadata=None):
        """Add a hyperedge to the hypergraph. If the hyperedge is already in the hypergraph, its weight is updated.

        Parameters
        ----------
        edge : tuple
            The hyperedge to add.
        layer : str
            The layer to which the hyperedge belongs.
        weight : float, optional
            The weight of the hyperedge. If the hypergraph is weighted, this must be provided.
        metadata : dict, optional
            The metadata of the hyperedge.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the hypergraph is weighted and no weight is provided or if the hypergraph is not weighted and a weight is provided.
        """
        if self._weighted and weight is None:
            weight = 1
        if not self._weighted and weight is not None and weight != 1:
            raise ValueError("If the hypergraph is not weighted, weight can be 1 or None.")
        
        self.existing_layers.add(layer)

        edge = tuple(sorted(edge))
        k = (edge, layer)
        order = len(edge) - 1

        if k not in self._edge_list:
            e_id = self.next_edge_id
            self.reverse_edge_list[e_id] = k
            self._edge_list[k] = e_id
            self.next_edge_id += 1

        e_id = self._edge_list[k]

        if metadata is None:
            metadata = {}

        self.edge_metadata[e_id] = metadata

        if weight is None:
            if edge in self._edge_list and self._weighted:
                self._weights[e_id] += 1
            else:
                self._weights[e_id] = 1
        else:
            self._weights[e_id] = weight

        for node in edge:
            self.add_node(node)

    def get_edges(self, metadata=False):
        if metadata:
            return {self.reverse_edge_list[k]: self.edge_metadata[k] for k in self.edge_metadata.keys() }
        else:
            return list(self._edge_list.keys())

    def get_weight(self, edge, layer):
        k = (tuple(sorted(edge)), layer)
        try:
            return self._weights[self._edge_list[k]]
        except KeyError:
            raise ValueError("The edge is not in the hypergraph.")
        

    def set_dataset_metadata(self, metadata):
        self.hypergraph_metadata['multiplex_metadata'] = metadata

    def get_dataset_metadata(self):
        return self.hypergraph_metadata['multiplex_metadata']

    def set_layer_metadata(self, layer_name, metadata):
        if layer_name not in self.hypergraph_metadata:
            self.hypergraph_metadata[layer_name] = {}
        self.hypergraph_metadata[layer_name] = metadata

    def get_layer_metadata(self, layer_name):
        return self.hypergraph_metadata[layer_name]

    def get_hypergraph_metadata(self):
        return self.hypergraph_metadata

    def set_hypergraph_metadata(self, metadata):
        self.hypergraph_metadata = metadata

    def aggregated_hypergraph(self):
        h = Hypergraph(weighted=self._weighted, hypergraph_metadata=self.hypergraph_metadata)
        for node in self.get_nodes():
            h.add_node(node, metadata=self.node_metadata[node])
        for edge in self.get_edges():
            _edge, layer = edge
            h.add_edge(_edge, weight=self.get_weight(_edge, layer), metadata=self.get_edge_metadata(_edge, layer))
        return h


