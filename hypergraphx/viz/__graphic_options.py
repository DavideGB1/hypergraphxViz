from typing import Optional
from networkx import Graph, DiGraph
from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
import re

class GraphicOptions:
    """
    Support class used to store the common options among the visualization functions.
    ...
    Attributes
    ----------
    is_PAOH : bool, optional
        Default value used to change the base node size if we are working with PAOHvis.
    node_shape : str | dict, optional
        Defines the shape of each node. It's possible to specify a shape for each node using a dictionary.
        Specification is as matplotlib.scatter marker.
    edge_shape: str | dict, optional
        Defines the shape of each edge node (the nodes that represent edges). It's possible to specify a shape for
        each node using a dictionary.Specification is as matplotlib.scatter marker.
    node_color: str | dict, optional
        HEX color for the node border. It's possible to specify a color for each node using a dictionary.
    node_facecolor: str | dict, optional
        HEX color for the node. It's possible to specify a color for each node using a dictionary.
    label_color: str, optional
        HEX color for the labels.
    in_edge_color: str, optional
        HEX color for the in-edge nodes in Directed Hypergraphs.
    out_edge_color: str, optional
        HEX color for the out-edge nodes in Directed Hypergraphs.
    edge_node_color: str | dict, optional
        HEX color for the edge nodes. It's possible to specify a color for each edge node using a dictionary.
    edge_color: str | dict, optional
        HEX color for the edges. It's possible to specify a color for each edge using a dictionary.
    edge_size: float | dict, optional
        Size for the edges. It's possible to specify a size for each edge using a dictionary.
    label_size: int, optional
        Size of the label font.
    node_size: int | dict, optional
        Size for the nodes. It's possible to specify a size for each node using a dictionary.
    default_attributes: Set of optional default values that can be modified. When a dictionary is provided for an attribute
        and such dictionary doesn't cover all possible nodes/edges/etc, the default value is will be used.
    Methods
    -------
    send_data():
        Sends the modified options to the main menu.
    add_color_picker(name, value, in_extra = False):
        Adds a color picker option to the main layout.
    add_combobox(name, value):
        Adds a ComboBox option to the main layout.
    add_spinbox(name, value, decimals = False, in_extra = False):
        Adds a SpinBox option to the main layout.
    """
    def __init__(
            self,
            is_PAOH: bool = False,
            node_shape: Optional[str | dict] = "o",
            edge_shape: Optional[str | dict] = 'p',
            node_color: Optional[str | dict] = "#1f78b4",
            node_facecolor: Optional[str | dict] = "#000000",
            label_color: Optional[str] = "#000000",
            in_edge_color: Optional[str] = "#00ff00",
            out_edge_color: Optional[str] = "#ff0000",
            edge_node_color: Optional[str | dict] = '#8a0303',
            edge_color: Optional[str | dict] = "#000000",
            edge_size: Optional[float | dict] = 2.0,
            label_size: Optional[int] = 15,
            node_size: Optional[int | dict] = None,
            weight_size: Optional[int] = 20,
            default_node_shape: Optional[str] = "o",
            default_node_color: Optional[str] = "#1f78b4",
            default_node_facecolor: Optional[str] = "#000000",
            default_edge_size: Optional[float] = 2.0,
            default_edge_color: Optional[str] = "#000000",
            default_edge_node_color: Optional[str] = '#8a0303',
            default_edge_shape: Optional[str] = "p",
            default_label_size: Optional[int] = 15,
            default_label_color: Optional[str] = "#000000",
            default_node_size: Optional[int] = 10,
            default_weight_size: Optional[int] = 20,
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
        self.default_weight_size = default_weight_size

        self.node_shape = node_shape
        self.node_color = node_color
        self.node_facecolor = node_facecolor
        self.edge_size = edge_size
        self.edge_color = edge_color
        self.edge_node_color = edge_node_color
        self.edge_shape = edge_shape
        self.label_size = label_size
        self.label_color = label_color
        self.weight_size = weight_size
        #Checks if all the colors have a valid HEX value
        hex_color_regex = r"^#[0-9a-fA-F]{6}$"
        for attr, value in vars(self).items():
            if "color" in str(attr):
                if not isinstance(value, str) or not re.match(hex_color_regex, value):
                    raise ValueError(
                        "Attribute " + str(attr) + " has invalid color " + str(value)
                    )
        self.centrality = None

    def check_if_options_are_valid(self, anygraph: Graph|Hypergraph|TemporalHypergraph|DirectedHypergraph) -> None:
        """
        Generate a dictionary for each parameter and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        anygraph: Graph | Hypergraph | TemporalHypergraph | DirectedHypergraph
        """
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

    def create_shape_dict(self, node_list: list) -> None:
        """
        Generate a dictionary for the node shape and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        node_list: list
        """
        if type(self.node_shape) == str:
            self.node_shape = {n: self.node_shape for n in node_list}
        elif type(self.node_shape) == dict:
            for node in node_list:
                if node not in self.node_shape:
                    self.node_shape[node] = self.default_node_shape

    def create_color_dict(self, node_list: list) -> None:
        """
        Generate a dictionary for the node color and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        node_list: list
        """
        if type(self.node_color) == str:
            self.node_color = {n: self.node_color for n in node_list}
        elif type(self.node_color) == dict:
            for node in node_list:
                if node not in self.node_color:
                    self.node_color[node] = self.default_node_color

    def create_facecolor_dict(self, node_list: list) -> None:
        """
        Generate a dictionary for the node facecolor and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        node_list: list
        """
        if type(self.node_facecolor) == str:
            self.node_facecolor = {n: self.node_facecolor for n in node_list}
        elif type(self.node_facecolor) == dict:
            for node in node_list:
                if node not in self.node_facecolor:
                    self.node_facecolor[node] = self.default_node_facecolor

    def create_size_dict(self, node_list: list) -> None:
        """
        Generate a dictionary for the node size and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        node_list: list
        """
        if type(self.node_size) == dict:
            for node in node_list:
                if node not in self.node_size:
                    self.node_size[node] = self.default_node_size
        else:
            self.node_size = {n: int(self.node_size) for n in node_list}
        if self.centrality is not None:
            if type(self.node_size) == dict:
                for k, v in self.node_size.items():
                    val = 1
                    try:
                        val = self.centrality[k]
                    except KeyError:
                        pass
                    self.node_size[k] = v * val

    def create_edgewidth_dict(self, edges_list: list) -> None:
        """
        Generate a dictionary for the edge size and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        edges_list: list
        """
        if type(self.edge_size) == float:
            self.edge_size = {n: self.edge_size for n in edges_list}
        elif type(self.edge_size) == dict:
            for edge in edges_list:
                if edge not in self.edge_size:
                    self.edge_size[edge] = self.default_edge_size

    def create_edgecolor_dict(self, edges_list: list) -> None:
        """
        Generate a dictionary for the edge color and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        edges_list: list
        """
        if type(self.edge_color) == str:
            self.edge_color = {n: self.edge_color for n in edges_list}
        elif type(self.edge_color) == dict:
            for edge in edges_list:
                if edge not in self.edge_color:
                    self.edge_color[edge] = self.default_edge_color

    def create_edgeshape_dict(self, node_list: list) -> None:
        """
        Generate a dictionary for the edge node shape and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        node_list: list
        """
        edge_list = [x for x in node_list if str(x).startswith('E')]
        if not edge_list:
            edge_list = node_list
        if type(self.edge_shape) == str:
            self.edge_shape = {n: self.edge_shape for n in edge_list}
        elif type(self.edge_shape) == dict:
            for edge in edge_list:
                if edge not in self.edge_shape:
                    self.edge_shape[edge] = self.default_edge_shape

    def create_edgenodecolor_dict(self, node_list: list) -> None:
        """
        Generate a dictionary for the edge node color and checks if such dictionary is complete. If not fills the missing entries.
        Parameters
        ----------
        node_list: list
        """
        edge_list = [x for x in node_list if str(x).startswith('E')]
        if not edge_list:
            edge_list = node_list
        if type(self.edge_node_color) == str:
            self.edge_node_color = {n: self.edge_node_color for n in edge_list}
        elif type(self.edge_node_color) == dict:
            for edge in edge_list:
                if edge not in self.edge_node_color:
                    self.edge_node_color[edge] = self.default_edge_node_color

    def add_centrality_factor_dict(self, centrality: dict):
        self.centrality = centrality