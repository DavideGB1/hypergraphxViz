from matplotlib import pyplot as plt

from hypergraphx import Hypergraph
from hypergraphx.viz.draw_sets import draw_sets


def polygonal_simplification(
        hypergraph: Hypergraph,
        show_progress: bool = False,
        print_log: bool = False
) -> Hypergraph:
    edge2_adj3, edge3_adj2, strangled_edges = find_nonplanar_structures(hypergraph)
    iteration = 0
    index = max(enumerate(hypergraph.get_nodes(),start=1))[0]
    # Fix edge2_adj3
    while len(edge2_adj3) > 0 or len(edge3_adj2) > 0:
        edges = hypergraph.get_edges()
        nodes = hypergraph.get_nodes()
        for problem in edge2_adj3:
            edge1, edge2 = set(problem[0]), set(problem[1])
            intersection = edge1.intersection(edge2)
            hypergraph.remove_edge(edge1)
            hypergraph.remove_edge(edge2)
            new_edge1 = [x for x in edge1 if x not in intersection]
            new_edge1.append(str(intersection))
            try:
                hypergraph.add_edge(tuple(new_edge1))
            except TypeError:
                print(f"Error with {new_edge1}")
                break
            new_edge2 = [x for x in edge2 if x not in intersection]
            new_edge2.append(str(intersection))
            hypergraph.add_edge(tuple(new_edge2))
        if print_log:
            print(f"Solve edge2_adj3 in iteration: {iteration}")
        for problem in edge3_adj2:
            edge1, edge2, edge3 = set(problem[0]), set(problem[1]), set(problem[2])
            intersection = edge1.intersection(edge2.intersection(edge3))
            to_remove = []
            for edge in edges:
                for node in edge:
                    if node in intersection:
                        to_remove.append(edge)
                        break
            new_edges = []
            for edge in to_remove:
                new_edge = list()
                for node in edge:
                    if node not in intersection:
                        new_edge.append(node)
                new_edge.append(index)
                new_edges.append(tuple(new_edge))
            for edge in to_remove:
                edges.remove(edge)
            for edge in new_edges:
                edges.append(edge)

            for node in intersection:
                try:
                    nodes.remove(node)
                except ValueError:
                    pass
            index += 1
        if print_log:
            print(f"Solve edge3_adj2 in iteration: {iteration}")

        hypergraph = Hypergraph()
        hypergraph.add_edges(edges)
        hypergraph.add_nodes(nodes)
        edge2_adj3, edge3_adj2, strangled_edges = find_nonplanar_structures(hypergraph)
        if show_progress:
            draw_sets(hypergraph, rounded_polygon=False, polygon_expansion_factor=0)
            plt.show()
        if print_log:
            print(f"Iteration number: {iteration}")
            print("edge2_adj3:")
            print(edge2_adj3)
            print("edge3_adj2:")
            print(edge3_adj2)
            print("strangled_edges:")
            print(strangled_edges)
        iteration += 1
        if iteration > 9:
            break
    return hypergraph

def find_nonplanar_structures(h:Hypergraph):
    strangled_edges = list()
    strangled_edges_fake = []
    for edge1 in h.get_edges():
        for edge2 in h.get_edges():
            if edge1 != edge2 and len(edge1) > 2 and len(edge2)>2:
                e1 = set(edge1)
                e2 = set(edge2)
                if e1.issubset(e2):
                    val = tuple(sorted((sorted(edge1), sorted(edge2))))
                    if val not in strangled_edges_fake:
                        strangled_edges.append(e1)
                        strangled_edges_fake.append(val)
    edge2_adj3 = list()
    edge3_adj2 = list()
    for edge1 in h.get_edges():
        for edge2 in h.get_edges():
            if edge1 != edge2 :
                e1 = set(edge1)
                e2 = set(edge2)
                if len(e1.intersection(e2))==3:
                    val = tuple(sorted((sorted(edge1), sorted(edge2))))
                    if val not in edge2_adj3 and val not in strangled_edges_fake:
                        edge2_adj3.append(val)
            for edge3 in h.get_edges():
                if edge1 != edge2 and edge2 != edge3 and edge3 != edge1:
                    e1 = set(edge1)
                    e2 = set(edge2)
                    e3 = set(edge3)
                    if len(e1.intersection(e2.intersection(e3)))==2:
                        val = tuple(sorted((sorted(edge1), sorted(edge2),sorted(edge3))))
                        if val not in edge3_adj2:
                            edge3_adj2.append(val)
    return edge2_adj3, edge3_adj2, strangled_edges

def unstrangle_edges(
        hypergraph: Hypergraph
)-> (Hypergraph,list):
    _, _, strangled_edges = find_nonplanar_structures(hypergraph)
    dummy = -1
    edges = hypergraph.get_edges()
    strangled_edges_fake = []
    for edge1 in hypergraph.get_edges():
        for edge2 in hypergraph.get_edges():
            if edge1 != edge2 and len(edge1) > 2 and len(edge2) > 2:
                e1 = set(edge1)
                e2 = set(edge2)
                if e1.issubset(e2):
                    val = tuple(sorted((sorted(edge1), sorted(edge2))))
                    if val not in strangled_edges_fake:
                        strangled_edges.append(e1)
                        strangled_edges_fake.append(val)
    dummy_nodes = []
    for problem in strangled_edges:
        edge = list(problem)
        edge.append(dummy)
        problem = tuple(sorted(problem))
        try:
            edges.remove(problem)
            edges.append(tuple(edge))
            dummy_nodes.append(dummy)
            dummy -= 1
        except ValueError:
            pass

    nodes = hypergraph.get_nodes()
    hypergraph = Hypergraph()
    hypergraph.add_edges(edges)
    hypergraph.add_nodes(nodes)

    return hypergraph, dummy_nodes