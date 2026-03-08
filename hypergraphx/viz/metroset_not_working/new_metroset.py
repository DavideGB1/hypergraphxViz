"""import random
import time
from itertools import combinations

import networkx
import numpy as np
from matplotlib import pyplot as plt
from networkx.drawing import spectral_layout, spring_layout
from shapely import LineString, Point

from hypergraphx import Hypergraph
from hypergraphx.measures.node_similarity import jaccard_similarity_matrix
from hypergraphx.viz.metroset_not_working.double_linked_matrix import DynamicDoubleLinkedMatrix

start_time = time.time()

hypergraph = Hypergraph([(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18),(1,2,3,4,5,6),(3,4,5,7,8),(6,7,8,9,10,12),(12,13,14,17,18,19),(18,20,21)])
matrix, matrix_mapping = jaccard_similarity_matrix(hypergraph, return_mapping=True)


import math

def calc_matrix_pos(curr_matrix_pos, where):
    curr_matrix_pos_x, curr_matrix_pos_y = curr_matrix_pos
    match where:
        case 0:
            curr_matrix_pos_y += 1
        case 1:
            curr_matrix_pos_y += 1
            curr_matrix_pos_x -= 1
        case 2:
            curr_matrix_pos_y += 1
            curr_matrix_pos_x += 1
        case 3:
            curr_matrix_pos_y -= 1
        case 4:
            curr_matrix_pos_y -= 1
            curr_matrix_pos_x -= 1
        case 5:
            curr_matrix_pos_y -= 1
            curr_matrix_pos_x += 1
        case 6:
            curr_matrix_pos_x -= 1
        case 7:
            curr_matrix_pos_x += 1

    return curr_matrix_pos_x, curr_matrix_pos_y

def adjust_position(pos_node, pos_adj, curr_matrix_pos, adj_matrix, to_insert, distance = 0.25):
    x_node, y_node = pos_node
    x_adj, y_adj = pos_adj

    neighbour_position = Point(x_adj, y_adj)

    up = Point(x_node, y_node+distance)
    up_left = Point(x_node - distance, y_node + distance)
    up_right = Point(x_node + distance, y_node + distance)
    down = Point(x_node, y_node-distance)
    down_left = Point(x_node - distance, y_node - distance)
    down_right = Point(x_node + distance, y_node - distance)
    left = Point(x_node-distance, y_node)
    right = Point(x_node+distance, y_node)
    up_distance = neighbour_position.distance(up)
    up_left_distance = neighbour_position.distance(up_left)
    up_right_distance = neighbour_position.distance(up_right)
    down_distance = neighbour_position.distance(down)
    down_left_distance = neighbour_position.distance(down_left)
    down_right_distance = neighbour_position.distance(down_right)
    left_distance = neighbour_position.distance(left)
    right_distance = neighbour_position.distance(right)
    distances = [
        (up_distance, 0),
        (up_left_distance,1),
        (up_right_distance, 2),
        (down_distance, 3),
        (down_left_distance, 4),
        (down_right_distance, 5),
        (left_distance, 6),
        (right_distance, 7)
    ]
    distances = sorted( distances, key=lambda x: x[0] )
    curr_index = 0
    can_continue = False
    while not can_continue:
        min_distance, min_index = distances[curr_index]
        new_matrix_pos_x, new_matrix_pos_y = calc_matrix_pos(curr_matrix_pos, min_index)
        curr_index += 1

        if not adj_matrix.has_node(new_matrix_pos_x, new_matrix_pos_y):
            adj_matrix.insert_node(new_matrix_pos_x, new_matrix_pos_y, to_insert)
            can_continue = True

    return new_matrix_pos_x, new_matrix_pos_y

def greedy_maximum_path(graph, starting_node):
    path = [starting_node]
    path_value = 0
    node = starting_node
    next_node = starting_node
    while len(path) != graph.number_of_nodes():
        max_value = 0
        for neighbor in graph.neighbors(node):
            if neighbor not in path:
                if max_value < graph[node][neighbor]["weight"]:
                    max_value = graph[node][neighbor]["weight"]
                    next_node = neighbor
        path_value += max_value
        path.append(next_node)
        node = next_node
    return path, path_value

def order_by_similarity(nodes, matrix, matrix_mapping):
    graph = networkx.Graph()
    for node1 in nodes:
        for node2 in nodes:
            if node1 != node2:
                graph.add_edge(node1, node2, weight=matrix[matrix_mapping[node1], matrix_mapping[node2]])
    best_path = []
    best_value = 0
    for node in nodes:
        path, path_value = greedy_maximum_path(graph, node)
        if path_value > best_value:
            best_path = path
    return best_path

sorted_edges = []
g = networkx.Graph()
for edge in hypergraph.get_edges():
    sorted_edge = order_by_similarity(edge, matrix, matrix_mapping)
    sorted_edges.append(sorted_edge)
    for i in range(len(sorted_edge)-1):
        g.add_edge(sorted_edge[i], sorted_edge[i+1])


layout= spectral_layout(g)
layout = spring_layout(g, pos = layout)

new_graph = networkx.Graph()
for edge in g.edges:
    new_graph.add_edge(edge[0], edge[1], geometry=LineString([layout[edge[0]], layout[edge[1]]]))
g = new_graph
intersections = []
for e1, e2 in combinations(g.edges(data=True), 2):
    line1 = e1[-1]["geometry"]
    line2 = e2[-1]["geometry"]
    if line1.crosses(line2):
        data = (line1.intersection(line2), e1, e2)
        intersections.append(data)
        #If you only want to check if any line intersects any other
        #  your can add a break here.
for point, e1, e2 in intersections:
    nodes = [e1[0], e1[1], e2[0], e2[1]]
    distances = []
    for node in nodes:
        dot = Point(layout[node])
        distance = point.distance(dot)
        distances.append((distance, node))
    problematic_node = min(distances)[1]
    to_ignore = None
    for node in nodes:
        if node != problematic_node:
            if g.has_edge(node, problematic_node):
                g.remove_edge(node, problematic_node)
                to_ignore = node
    nodes.remove(to_ignore)
    for node in nodes:
        can_continue = False
        for val in sorted_edges:
            if node in val and problematic_node in val:
                can_continue = True
                break
        if can_continue:
            g.add_edge(node, problematic_node)
            tmp_layout = spectral_layout(g)
            tmp_layout = spring_layout(g, pos=tmp_layout)
            g.remove_edge(node, problematic_node)
            g.add_edge(node, problematic_node, geometry=LineString([tmp_layout[node], tmp_layout[problematic_node]]))
            tmp_intersert = []
            for e1, e2 in combinations(g.edges(data=True), 2):
                line1 = e1[-1]["geometry"]
                line2 = e2[-1]["geometry"]
                if line1.crosses(line2):
                    data = (line1.intersection(line2), e1, e2)
                    tmp_intersert.append(data)
            if len(tmp_intersert) == 0:
                layout = tmp_layout
                break
            else:
                g.remove_edge(node, problematic_node)

DISTANCE = 0.25

min_degree = math.inf
best_node = None
for node in g.nodes:
    if g.degree[node] < min_degree:
        min_degree = g.degree[node]
        best_node = node


visited = [best_node]
s = [best_node]
matrix = DynamicDoubleLinkedMatrix()

used_sectors = dict()
for node in g.nodes:
    neigh = sum(1 for _ in g.neighbors(node))
    if neigh <= 2:
        n_sectors = 2
    elif neigh <= 4:
        n_sectors = 4
    else:
        n_sectors = 8
    used_sectors[node] = dict()
    for i in range(n_sectors):
        used_sectors[node][i] = False

matrix_position = dict()
matrix_position[best_node] = (0,0)
matrix.insert_node(0, 0, best_node)
while len(s) != 0:
    node = s.pop()
    pos_node = layout[node].copy()
    for neighbor in g.neighbors(node):
        if neighbor not in visited:
            pos_adj = layout[neighbor].copy()
            try:
                new_matrix_pos_x, new_matrix_pos_y = adjust_position(pos_node=pos_node, pos_adj=pos_adj, curr_matrix_pos=matrix_position[node],
                                                                 adj_matrix = matrix, to_insert = neighbor)
            except ValueError:
                matrix.draw_matrix()
                print(f"Nodo è {node}, vicino è {neighbor}")
                break
            matrix_position[neighbor] = (new_matrix_pos_x, new_matrix_pos_y)
            visited.append(neighbor)
            s.append(neighbor)
colors = [ '#{:06x}'.format(random.randint(0, 16777215)) for i in range(hypergraph.num_edges()) ]
idx = 0
fig, ax = plt.subplots(figsize=(10, 8))
for edge in hypergraph.get_edges():
    for i in range(len(edge)-1):
        y1, x1 = matrix.get_node_position(edge[i])
        y2, x2 = matrix.get_node_position(edge[i+1])
        ax.plot([x1, x2], [y1, y2], color=colors[idx])
    idx += 1

matrix.draw_matrix(ax)
plt.show()
print("--- %s seconds ---" % (time.time() - start_time))"""