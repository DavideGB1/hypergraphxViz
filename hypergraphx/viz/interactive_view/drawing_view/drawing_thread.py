import multiprocessing

from PyQt5.QtCore import QThread, pyqtSignal

from hypergraphx import TemporalHypergraph
from hypergraphx.communities.hy_mmsbm.model import HyMMSBM
from hypergraphx.communities.hy_sc.model import HySC
from hypergraphx.communities.hypergraph_mt.model import HypergraphMT
from hypergraphx.measures.degree import degree_sequence
from hypergraphx.measures.s_centralities import s_betweenness_nodes_averaged, s_betweenness_nodes
from hypergraphx.utils import normalize_array
from hypergraphx.viz.draw_PAOH import calculate_paoh_layout
from hypergraphx.viz.draw_projections import _compute_extra_node_drawing_data, _compute_bipartite_drawing_data, \
    _compute_clique_drawing_data
from hypergraphx.viz.draw_radial import _compute_radial_layout
from hypergraphx.viz.draw_sets import _compute_set_layout
from hypergraphx.viz.simplification_methods.agglomerative_simplification import agglomerative_simplification
from hypergraphx.viz.simplification_methods.polygonal_symplification import polygonal_simplification, unstrangle_edges


def create_figure(draw_function, hypergraph, dictionary):
    # Support
    def normalize_centrality(centrality):
        """
        Normalizes the centrality scores stored in the `self.centrality` dictionary
        by dividing each centrality value by the mean centrality value. This ensures
        that the centrality values are relative to the mean and scaled proportionally.

        Returns
        -------
        None
            The method updates the `self.centrality` dictionary in place.
        """
        if centrality is None:
            return None
        mean = sum(centrality.values()) / len(centrality)
        for k, v in centrality.items():
            centrality[k] = v / mean
        return centrality

    centrality = None
    match dictionary["centrality"]:
        case "No Centrality":
            pass
        case "Degree Centrality":
            centrality = degree_sequence(hypergraph)
        case "Betweenness Centrality":
            if isinstance(hypergraph, TemporalHypergraph):
                centrality = s_betweenness_nodes_averaged(hypergraph)
            else:
                centrality = s_betweenness_nodes(hypergraph)
            for k in centrality.keys():
                centrality[k] *= 2
                centrality[k] += 0.5
        case "Adjacency Factor (t=1)":
            centrality = hypergraph.adjacency_factor(t=1)
        case "Adjacency Factor (t=2)":
            centrality = hypergraph.adjacency_factor(t=2)
    centrality = normalize_centrality(centrality)
    output = dict()
    if draw_function == "PAOH":
        result = calculate_paoh_layout(
            h=hypergraph,
            u=dictionary["community_model"],
            k=dictionary["community_options_dict"]["number_communities"],
            cardinality=dictionary["slider_value"],
            x_heaviest=dictionary["heaviest_edges_value"],
            space_optimization=dictionary["algorithm_options_dict"]["space_optimization"],
            sort_nodes_by=dictionary["algorithm_options_dict"]["sort_nodes_by"],
            sorting_mapping = centrality,
        )
        centrality = None
        output[0] = result
        n_times = 1
    else:
        hypergraphs = dict()
        if isinstance(hypergraph, TemporalHypergraph):
            hypergraphs = hypergraph.subhypergraph()
        else:
            hypergraphs[0] = hypergraph
        n_times = len(hypergraphs)
        for time, hypergraph in hypergraphs.items():
            if draw_function == "Sets":
                result = _compute_set_layout(
                    hypergraph= hypergraph,
                    u=dictionary["community_model"],
                    k=dictionary["community_options_dict"]["number_communities"],
                    weight_positioning = dictionary["weight_positioning"],
                    cardinality=dictionary["slider_value"],
                    x_heaviest=dictionary["heaviest_edges_value"],
                    iterations=dictionary["algorithm_options_dict"]["iterations"],
                    pos=None,
                    rounded_polygon = dictionary["algorithm_options_dict"]["rounded_polygon"],
                    hyperedge_color_by_order = None,
                    hyperedge_facecolor_by_order  = None,
                    hyperedge_alpha = dictionary["extra_attributes"]["hyperedge_alpha"],
                    scale = dictionary["algorithm_options_dict"]["scale_factor"],
                    rounding_radius_size = dictionary["extra_attributes"]["rounding_radius_factor"],
                    polygon_expansion_factor = dictionary["extra_attributes"]["polygon_expansion_factor"],
                )
            elif draw_function == "PAOH":
                result = calculate_paoh_layout(
                    h=hypergraph,
                    u=dictionary["community_model"],
                    k=dictionary["community_options_dict"]["number_communities"],
                    cardinality=dictionary["slider_value"],
                    x_heaviest=dictionary["heaviest_edges_value"],
                    space_optimization=dictionary["algorithm_options_dict"]["space_optimization"],
                    sort_nodes_by=dictionary["algorithm_options_dict"]["sort_nodes_by"],
                    sorting_mapping = centrality,
                )
                centrality = None
            elif draw_function == "Radial":
                result = _compute_radial_layout(
                    h=hypergraph,
                    u=dictionary["community_model"],
                    k=dictionary["community_options_dict"]["number_communities"],
                    cardinality=dictionary["slider_value"],
                    x_heaviest=dictionary["heaviest_edges_value"],
                    radius_scale_factor=dictionary["extra_attributes"]["radius_scale_factor"],
                )
            elif draw_function == "Extra-Node":
                result = _compute_extra_node_drawing_data(
                    h=hypergraph,
                    cardinality=dictionary["slider_value"],
                    x_heaviest=dictionary["heaviest_edges_value"],
                    ignore_binary_relations=dictionary["algorithm_options_dict"]["ignore_binary_relations"],
                    weight_positioning=dictionary["weight_positioning"],
                    respect_planarity=dictionary["algorithm_options_dict"]["respect_planarity"],
                    iterations=dictionary["algorithm_options_dict"]["iterations"],
                    pos=None,
                    u=dictionary["community_model"],
                    k=dictionary["community_options_dict"]["number_communities"],
                    draw_edge_graph=False
                )
            elif draw_function == "Bipartite":
                result = _compute_bipartite_drawing_data(
                    h=hypergraph,
                    u=dictionary["community_model"],
                    k=dictionary["community_options_dict"]["number_communities"],
                    pos = None,
                    cardinality=dictionary["slider_value"],
                    x_heaviest=dictionary["heaviest_edges_value"],
                    align=dictionary["algorithm_options_dict"]["align"],
                )
            elif draw_function == "Clique":
                result = _compute_clique_drawing_data(
                    h=hypergraph,
                    cardinality=dictionary["slider_value"],
                    x_heaviest=dictionary["heaviest_edges_value"],
                    iterations=dictionary["algorithm_options_dict"]["iterations"],
                    pos=None,
                    weight_positioning = dictionary["weight_positioning"],
                    u=dictionary["community_model"],
                    k=dictionary["community_options_dict"]["number_communities"],
                )
            output[time] = result
    return [output,centrality, n_times]

def run_community_detection(hypergraph, algorithm, community_options):
    """
    Worker function to perform community detection in a separate process.

    Args:
        hypergraph: The Hypergraph object.
        algorithm: The name of the community detection algorithm
                   ('HySC', 'HypergraphMT', 'Hy-MMSBM', or 'None').
        community_options: Dictionary of options for the algorithm.

    Returns:
        The community model (e.g., membership matrix) or None.
    """
    if algorithm == "Hypergraph Spectral Clustering":
        model = HySC(
            seed=community_options["seed"],
            n_realizations=community_options["realizations"]
        )
        community_model = model.fit(
            hypergraph,
            K=community_options["number_communities"],
            weighted_L=False
        )
    elif algorithm == "Hypergraph-MT":
        model = HypergraphMT(
            n_realizations=community_options["realizations"],
            max_iter=community_options["max_iterations"],
            check_convergence_every=community_options["check_convergence_every"],
            verbose=False
        )
        u, _, _ = model.fit(
            hypergraph,
            K=community_options["number_communities"],
            seed=community_options["seed"],
            normalizeU=community_options["normalizeU"],
            baseline_r0=community_options["baseline_r0"],
        )
        community_model = normalize_array(u, axis=1)
    elif algorithm == "Hy-MMSBM":
        best_model = None
        best_loglik = float("-inf")
        for j in range(community_options["realizations"]):
            model = HyMMSBM(
                K=community_options["number_communities"],
                assortative=community_options["assortative"]
            )
            model.fit(
                hypergraph,
                n_iter=community_options["max_iterations"],
            )

            log_lik = model.log_likelihood(hypergraph)
            if log_lik > best_loglik:
                best_model = model
                best_loglik = log_lik

        community_model = normalize_array(best_model.u, axis=1)
    elif algorithm == "None":
        community_model = None
    else:
        raise ValueError(f"Unknown community detection algorithm: {algorithm}")
    return community_model

class PlotWorker(QThread):
    progress = pyqtSignal(list)

    def __init__(self, draw_function, hypergraph, input_dictionary, model, community_algorithm, community_options, use_last, aggregation_options, parent=None):
        super(PlotWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.draw_function = draw_function
        self.input_dictionary = input_dictionary
        self.model = model
        self.use_last = use_last
        self.community_algorithm = community_algorithm
        self.community_options = community_options
        self.aggregation_options = aggregation_options
        self._is_cancelled = False

    def run(self):
        try:
            if self._is_cancelled:
                return
            if self.aggregation_options["use_simplification"]:
                if self.aggregation_options["use_polygonal_simplification"]:
                    self.hypergraph = polygonal_simplification(self.hypergraph)
                self.hypergraph = agglomerative_simplification(self.hypergraph, self.aggregation_options["aggregation_threshold"])
                if self.aggregation_options["use_polygonal_simplification"] and self.draw_function == "Sets":
                    self.hypergraph = unstrangle_edges(self.hypergraph)

            if not self.use_last:
                with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
                    self.model = pool.apply(run_community_detection,
                                            args=(self.hypergraph, self.community_algorithm, self.community_options))

                self.input_dictionary["community_model"] = self.model
            else:
                self.model = self.input_dictionary["community_model"]

            if self._is_cancelled:
                return

            with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
                results = pool.apply(create_figure, args=(self.draw_function, self.hypergraph, self.input_dictionary))

            if self._is_cancelled:
                return

            results.append(self.model)
            self.progress.emit(results)
        except Exception as e:
            print(f"Error in PlotWorker: {e}")

    def cancel(self):
        """Request thread cancellation."""
        self._is_cancelled = True