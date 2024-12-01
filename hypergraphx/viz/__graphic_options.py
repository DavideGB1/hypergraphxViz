import inspect
from typing import Optional
from networkx import Graph, DiGraph
from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph


class GraphicOptions:
    """
    Support class used to store the common options amoung the visualization functions.
    """
    def __init__(
            self,
            is_PAOH: bool = False,
            node_shape: Optional[str | dict] = "o",
            edge_shape: Optional[str | dict] = 'p',
            node_color: Optional[str | dict] = "#1f78b4",
            node_facecolor: Optional[str | dict] = "black",
            label_color: Optional[str] = "black",
            in_edge_color: Optional[str] = "green",
            out_edge_color: Optional[str] = "red",
            edge_node_color: Optional[str | dict] = '#8a0303',
            edge_color: Optional[str | dict] = "#000000",
            edge_size: Optional[float | dict] = 2.0,
            label_size: Optional[int] = 10,
            node_size: Optional[int | dict] = None,
            default_node_shape: Optional[str] = "o",
            default_node_color: Optional[str] = "#1f78b4",
            default_node_facecolor: Optional[str] = "black",
            default_edge_size: Optional[float] = 2.0,
            default_edge_color: Optional[str] = "#000000",
            default_edge_node_color: Optional[str] = "@8a0303",
            default_edge_shape: Optional[str] = "p",
            default_label_size: Optional[int] = 10,
            default_label_color: Optional[str] = "black",
            default_node_size: Optional[int] = 10
    ):
        self.node_size = node_size
        self.in_edge_color = in_edge_color
        self.out_edge_color = out_edge_color
        if is_PAOH:
            self.default_node_size = default_node_size
            if self.node_size is None:
                self.node_size = 10
        else:
            self.default_node_size = default_node_size
            if self.node_size is None:
                self.node_size = 300
        self.default_node_shape = default_node_shape
        self.default_node_color = default_node_color
        self.default_node_facecolor = default_node_facecolor
        self.default_edge_size = default_edge_size
        self.default_edge_color = default_edge_color
        self.default_edge_node_color = default_edge_node_color
        self.default_edge_shape = default_edge_shape
        self.default_label_size = default_label_size
        self.default_label_color = default_label_color

        self.node_shape = node_shape
        self.node_color = node_color
        self.node_facecolor = node_facecolor
        # Ensure that all Binary Edges have a Width and Color
        self.edge_size = edge_size
        self.edge_color = edge_color
        self.edge_node_color = edge_node_color
        self.edge_shape = edge_shape
        self.label_size = label_size
        self.label_color = label_color
    def check_if_options_are_valid(self, anygraph: Graph|Hypergraph|TemporalHypergraph|DirectedHypergraph):
        node_list = []
        edges_list = []
        if isinstance(anygraph, Graph) or isinstance(anygraph, DiGraph):
            node_list = anygraph.nodes()
            edges_list = anygraph.edges()
        elif isinstance(anygraph, DirectedHypergraph):
            node_list = anygraph.get_nodes()
            edges_list = anygraph.get_edges()

        else:
            node_list = anygraph.get_nodes()
            edges_list = anygraph.get_edges()
        self.create_size_dict(node_list)
        self.create_shape_dict(node_list)
        self.create_color_dict(node_list)
        self.create_facecolor_dict(node_list)
        # Ensure that all Binary Edges have a Width and Color
        self.create_edgewidth_dict(edges_list)
        self.create_edgecolor_dict(edges_list)
        self.create_edgeshape_dict(node_list)
        self.create_edgenodecolor_dict(node_list)


    def create_shape_dict(self, node_list):
        if type(self.node_shape) == str:
            self.node_shape = {n: self.node_shape for n in node_list}
        elif type(self.node_shape) == dict:
            for node in node_list:
                if node not in self.node_shape:
                    self.node_shape[node] = self.default_node_shape

    def create_color_dict(self, node_list):
        if type(self.node_color) == str:
            self.node_color = {n: self.node_color for n in node_list}
        elif type(self.node_color) == dict:
            for node in node_list:
                if node not in self.node_color:
                    self.node_color[node] = self.default_node_color

    def create_facecolor_dict(self, node_list):
        if type(self.node_facecolor) == str:
            self.node_facecolor = {n: self.node_facecolor for n in node_list}
        elif type(self.node_facecolor) == dict:
            for node in node_list:
                if node not in self.node_facecolor:
                    self.node_facecolor[node] = self.default_node_facecolor

    def create_size_dict(self, node_list):
        if type(self.node_size) == dict:
            for node in node_list:
                if node not in self.node_size:
                    self.node_size[node] = self.default_node_size
        else:
            self.node_size = {n: int(self.node_size) for n in node_list}

    def create_edgewidth_dict(self, edges_list):
        if type(self.edge_size) == float:
            self.edge_size = {n: self.edge_size for n in edges_list}
        elif type(self.edge_size) == dict:
            for edge in edges_list:
                if edge not in self.edge_size:
                    self.edge_size[edge] = self.default_edge_size

    def create_edgecolor_dict(self, edges_list):
        if type(self.edge_color) == str:
            self.edge_color = {n: self.edge_color for n in edges_list}
        elif type(self.edge_color) == dict:
            for edge in edges_list:
                if edge not in self.edge_color:
                    self.edge_color[edge] = self.default_edge_color

    def create_edgeshape_dict(self, node_list):
        edge_list = [x for x in node_list if str(x).startswith('E')]
        if not edge_list:
            edge_list = node_list
        if type(self.edge_shape) == str:
            self.edge_shape = {n: self.edge_shape for n in edge_list}
        elif type(self.edge_shape) == dict:
            for edge in edge_list:
                if edge not in self.edge_shape:
                    self.edge_shape[edge] = self.default_edge_shape

    def create_edgenodecolor_dict(self, node_list):
        edge_list = [x for x in node_list if str(x).startswith('E')]
        if not edge_list:
            edge_list = node_list
        if type(self.edge_node_color) == str:
            self.edge_node_color = {n: self.edge_node_color for n in edge_list}
        elif type(self.edge_node_color) == dict:
            for edge in edge_list:
                if edge not in self.edge_node_color:
                    self.edge_node_color[edge] = self.default_edge_node_color