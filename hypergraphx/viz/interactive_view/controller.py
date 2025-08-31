from enum import Enum

import hypergraphx
from PyQt5.QtCore import QObject, pyqtSignal

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.generation import random_hypergraph
from hypergraphx.generation.random import random_uniform_hypergraph
from hypergraphx.readwrite import save_hypergraph
from hypergraphx.utils.cc import connected_components
from hypergraphx.viz.interactive_view.drawing_view.drawing_thread import PlotWorker


class HypergraphType(Enum):
    NORMAL=1
    DIRECTED = 2
    TEMPORAL = 3

class Controller(QObject):
    updated_hypergraph = pyqtSignal(dict)
    finished_drawing = pyqtSignal(int)
    # constructor
    def __init__(self, hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph):
        super().__init__()
        self.hypergraph_type = ""
        self.showed_hypergraph = None
        self.actual_hypergraph = None
        self.thread = None
        self.change_hypergraph(hypergraph)
        self.cc = connected_components(self.actual_hypergraph)

    def add_edge(self, values):
        try:
            if isinstance(self.actual_hypergraph, TemporalHypergraph):
                self.actual_hypergraph.add_edge(
                    values["edge_data"],
                    values["time"],
                    values["weight"],
                    values["metadata"]
                )
            else:
                self.actual_hypergraph.add_edge(
                    values["edge_data"],
                    values["weight"],
                    values["metadata"]
                )
            self.update_hypergraph()
        except Exception as e:
            raise Exception

    def add_node(self, values):
        try:
            self.actual_hypergraph.add_node(eval(values["name"]), values["metadata"])
            self.update_hypergraph()
        except Exception as e:
            raise Exception

    def remove_nodes(self, node_list):
        node_list = list(set(node_list))
        for node in node_list:
            try:
                self.actual_hypergraph.remove_node(node, True)
            except KeyError:
                self.actual_hypergraph.remove_node(int(node), True)
            except Exception:
                raise Exception
        self.cc = connected_components(self.actual_hypergraph)
        self.update_hypergraph()

    def remove_edges(self, edge_list):
        edge_list = list(set(edge_list))
        for edge in edge_list:
            if isinstance(self.actual_hypergraph, Hypergraph):
                self.actual_hypergraph.remove_edge(edge)
            elif isinstance(self.actual_hypergraph, DirectedHypergraph):
                self.actual_hypergraph.remove_edge(edge)
            elif isinstance(self.actual_hypergraph, TemporalHypergraph):
                edge = edge[0]
                time = edge[1]
                self.actual_hypergraph.remove_edge(edge, time)
        self.cc = connected_components(self.actual_hypergraph)
        self.update_hypergraph()

    def generate_random_hypergraph(self, values):
        try:
            self.actual_hypergraph = random_hypergraph(
                num_nodes=int(values["num_nodes"]),
                num_edges_by_size=values["edges_by_size"]
            )
            self.update_hypergraph()
        except Exception as e:
            raise Exception

    def random_uniform_graph(self, values):
        try:
            self.actual_hypergraph = random_uniform_hypergraph(
                int(values["num_nodes"]),
                int(values["edge_size"]),
                int(values["num_edges"])
            )
            self.update_hypergraph()
        except Exception as e:
            raise Exception

    def load_from_file(self, file_path):
        try:
            if file_path.endswith(".hif.json"):
                self.change_hypergraph(hypergraphx.readwrite.load_hif(file_path))
            else:
                self.change_hypergraph(hypergraphx.readwrite.load_hypergraph(file_path))
        except Exception as e:
            raise Exception

    def save_to_file(self, file_path):
        try:
            if file_path.endswith(".hgx"):
                save_hypergraph(self.showed_hypergraph, file_path, binary=True)
                self.update_hypergraph()
            elif file_path.endswith(".json"):
                save_hypergraph(self.showed_hypergraph, file_path, binary=False)
                self.update_hypergraph()
        except Exception:
            raise Exception

    def modify_edge_weight(self, edge, weight, time = None):
        match self.hypergraph_type:
            case HypergraphType.TEMPORAL:
                self.actual_hypergraph.set_weight(edge, time, weight)
            case _:
                self.actual_hypergraph.set_weight(edge, weight)
        self.update_hypergraph()

    def modify_edge_time(self, edge, old_time,time):
        weight = 0
        if self.actual_hypergraph.is_weighted():
            weight = self.actual_hypergraph.get_weight(edge, old_time)
        metadata = self.actual_hypergraph.get_edge_metadata(edge, old_time)
        self.actual_hypergraph.remove_edge(edge, old_time)
        if self.actual_hypergraph.is_weighted():
            self.actual_hypergraph.add_edge(edge, time, weight, metadata)
        else:
            self.actual_hypergraph.add_edge(edge, time, metadata=metadata)
        self.update_hypergraph()

    def update_selected_ccs(self, selected_cc_list):
        self.showed_hypergraph = Hypergraph()
        for cc in selected_cc_list:
            cc_hg: Hypergraph = self.actual_hypergraph.subhypergraph(cc)
            weights = None
            if self.actual_hypergraph.is_weighted():
                weights = cc_hg.get_weights()
            self.showed_hypergraph.add_edges(cc_hg.get_edges(), weights, cc_hg.get_all_edges_metadata())
        self.update_hypergraph(updated_ccs=True)

    def change_hypergraph(self, hypergraph):
        self.actual_hypergraph = hypergraph
        self.showed_hypergraph = hypergraph
        if isinstance(hypergraph, TemporalHypergraph):
            self.hypergraph_type = HypergraphType.TEMPORAL
        elif isinstance(hypergraph, DirectedHypergraph):
            self.hypergraph_type = HypergraphType.DIRECTED
        else:
            self.hypergraph_type = HypergraphType.NORMAL
            self.cc = connected_components(self.actual_hypergraph)
        self.update_hypergraph()

    def get_hypergraph(self):
        return self.showed_hypergraph

    def plot_graph(self, input_values):
        if self.thread and self.thread.isRunning():
            self.thread.cancel()
            self.thread.quit()
        curr_function = input_values["curr_function"]
        community_model = input_values["community_model"]
        community_algorithm = input_values["community_algorithm"]
        community_options_dict = input_values["community_options_dict"]
        aggregation_options = input_values["aggregation_options"]
        if self.thread and self.thread.isRunning():
            self.thread.cancel()
            self.thread.quit()
        self.thread = PlotWorker(
            curr_function,
            self.showed_hypergraph,
            input_values["dictionary"],
            community_model,
            community_algorithm,
            community_options_dict,
            input_values["use_last"],
            aggregation_options
        )
        self.thread.progress.connect(self.calculated_positions)
        self.thread.start()

    def calculated_positions(self, value_list):
        self.drawing_result = value_list
        self.finished_drawing.emit(0)

    def update_hypergraph(self, updated_ccs = False):
        self.updated_hypergraph.emit({"hypergraph": self.showed_hypergraph, "updated_ccs": updated_ccs})