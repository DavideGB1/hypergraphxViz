import pandas as pd
from matplotlib import pyplot as plt

from hypergraphx import Hypergraph
from hypergraphx.filters import filter_hypergraph
from hypergraphx.readwrite import load_hypergraph
from hypergraphx.viz.__support import __filter_hypergraph
from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_sets import draw_sets
from matplotlib import pyplot as plt

from hypergraphx.readwrite import load_hif
from hypergraphx.utils.cc import largest_component
from hypergraphx.viz.draw_PAOH import draw_PAOH
from hypergraphx.viz.draw_projections import draw_clique, draw_extra_node
from hypergraphx.viz.draw_radial import draw_radial_layout
from hypergraphx.viz.draw_sets import draw_sets

hypergraph = load_hypergraph("/home/davide/Downloads/antonio.json")
cc = largest_component(hypergraph)
#h = hypergraph.subhypergraph(cc)
h = Hypergraph([(6,7,8,9),(7,8,15),(8,9,14),(3,6),(1,2,3),(4,5,6),(4,5,12,16,17),(17,18,2),(1,4,10,11,12),(10,11,13),(5,6,17,18),(4,12,16,17),(16,17,20),(17,19,20,22),(18,19,21),(16,17,18,19,21),(19,22),(19,23,24,25),(23,24,25),(24,26),(23,27)])
#h = load_hypergraph("/home/davide/PycharmProjects/hypergraphxViz/test_data/hs/hs_one_class.json")
#h = __filter_hypergraph(h, (3,h.max_size()), 1)
#h = Hypergraph([(1,2,3,4,5),(3,4,5,6,7,8),(7,2,1)])
draw_sets(h, rounding_radius_size=0)
plt.show()
import matplotlib.pyplot as plt
import numpy as np

def disegna_heatmap(matrice, titolo="Heatmap", etichette_x=None, etichette_y=None, cmap="viridis"):
    plt.imshow(matrice, cmap=cmap, aspect='auto')
    plt.colorbar(label='Valore')
    for i in range(matrice.shape[0]):
        for j in range(matrice.shape[1]):
            if matrice[i, j] > 0:
                text = plt.text(j, i, f"{matrice[i, j]:.2f}",
                           ha="center", va="center", color="w", fontsize = 5)
    if titolo:
        plt.title(titolo)
    if etichette_x is not None:
        plt.xticks(np.arange(len(etichette_x)), etichette_x)
    if etichette_y is not None:
        plt.yticks(np.arange(len(etichette_y)), etichette_y)
    plt.xlabel("Nodes")
    plt.ylabel("Nodes")
    plt.tight_layout()
    plt.show()

def jaccard_matrix(h: Hypergraph):
    dictionary = dict()
    for node1 in sorted(h.get_nodes()):
        for node2 in sorted(h.get_nodes()):
            if node1 != node2:
                if node1 in [19,20,21] and node2 in [19,20,21]:
                    pass
                e_1 = set(h.get_incident_edges(node1))
                e_2 = set(h.get_incident_edges(node2))
                index = len(e_1.intersection(e_2))/len(e_1.union(e_2))
                dictionary[(node1, node2)] = index
    matrice = np.full((h.num_nodes(),h.num_nodes()), np.nan)
    mapping = h.get_mapping()

    for (x, y), valore in dictionary.items():
        try:
            matrice[x,y] = valore
        except (IndexError, ValueError, TypeError):
            raise ValueError("Le chiavi del dizionario non corrispondono a indici validi per la matrice.")

    return matrice, dictionary
#disegna_heatmap(jaccard_matrix(h),titolo = "Jaccard Similarity",etichette_x=sorted(h.get_nodes()), etichette_y=sorted(h.get_nodes()))

def trova_strutture_problematiche(h:Hypergraph):
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

edge2_adj3, edge3_adj2, strangled_edges = trova_strutture_problematiche(h)
iteration = 0
index = 10000
dummy = -1
#Fix edge2_adj3
while len(edge2_adj3) > 0 or len(edge3_adj2) > 0:
    edges = h.get_edges()
    nodes = h.get_nodes()
    #for problem in edge2_adj3:
        #edge1, edge2 = set(problem[0]), set(problem[1])
        #intersection = edge1.intersection(edge2)
        #h.remove_edge(edge1)
        #h.remove_edge(edge2)
        #new_edge1 = [x for x in edge1 if x not in intersection]
        #new_edge1.append(str(intersection))
        #try:
         #   h.add_edge(tuple(new_edge1))
        #except TypeError:
        #    print(f"Errore con {new_edge1}")
       #     break
      #  new_edge2 = [x for x in edge2 if x not in intersection]
     #   new_edge2.append(str(intersection))
    #    h.add_edge(tuple(new_edge2))
    print(f"Solve edge2_adj3 in iteration: {iteration}",)
    for problem in edge3_adj2:
        if index == 1171:
            print("Sono io il merdo")
        to_remove_nodes = list()
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
        index+=1
    print(f"Solve edge3_adj2 in iteration: {iteration}",)
    strangled_edges = list()

    h = Hypergraph()
    h.add_edges(edges)
    h.add_nodes(nodes)
    draw_sets(h, rounded_polygon=False, poligon_expansion_factor = 0)
    plt.show()
    edge2_adj3, edge3_adj2, strangled_edges = trova_strutture_problematiche(h)
    print(f"Iteration number: {iteration}")
    print("edge2_adj3:")
    print(edge2_adj3)
    print("edge3_adj2:")
    print(edge3_adj2)
    print("strangled_edges:")
    print(strangled_edges)
    iteration+=1
    if iteration > 9:
        break

nodes_normalized = {node: idx for idx, node in enumerate(h.get_nodes())}
h_normalized = Hypergraph()
for edge in h.get_edges():
    new_edge = list()
    for node in edge:
        new_edge.append(nodes_normalized[node])
    h_normalized.add_edge(tuple(new_edge))
print(h.get_incident_edges(19))
print(h.get_incident_edges(20))
print(h.get_incident_edges(21))
matrice, matrice_dictionary = jaccard_matrix(h_normalized)
threshold = 0.9
idx = 100000
to_compress=list()
flag = False
for (x,y), val in matrice_dictionary.items():
    if val > threshold:
        for comp in to_compress:
            if x in comp:
                flag = True
                if y not in comp:
                    comp.append(y)
            elif y in comp:
                if x not in comp:
                    comp.append(x)
                flag = True
        if not flag:
            to_compress.append([x,y])
        flag = False
new_edges = []
flag = False
compressed_nodes = {tuple(node): idx+100000 for idx, node in enumerate(to_compress)}

for edge in h_normalized.get_edges():
    to_add = list()
    new_edge = list(edge)
    for nodes in to_compress:
        for node in nodes:
            if node in edge:
                new_edge.remove(node)
                to_add.append(compressed_nodes[tuple(nodes)])
    if len(to_add) > 0:
        for node in to_add:
            if node not in new_edge:
                new_edge.append(node)
    if new_edge not in new_edges:
        new_edges.append(new_edge)
h = Hypergraph()
h.add_edges(new_edges)
draw_sets(h, rounded_polygon=False, poligon_expansion_factor = 0, dummy_nodes = [])
plt.show()

dummy = -1
edges = h.get_edges()
strangled_edges_fake = []
for edge1 in h.get_edges():
    for edge2 in h.get_edges():
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
        dummy-=1
    except ValueError:
        pass

h = Hypergraph()
nodes = h.get_nodes()
h.add_edges(edges)
h.add_nodes(nodes)
draw_sets(h, rounded_polygon=False, poligon_expansion_factor = 0, dummy_nodes = dummy_nodes)
plt.show()

disegna_heatmap(matrice,titolo = "Jaccard Similarity",etichette_x=nodes_normalized.keys(), etichette_y=nodes_normalized.keys())