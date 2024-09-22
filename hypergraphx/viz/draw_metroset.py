import itertools
import math
import sys
from math import trunc
import random
from typing import Union, Optional

import numpy
import numpy as np
from PIL.ImageChops import offset
from fa2_modified import ForceAtlas2
from hypergraphx import Hypergraph
from hypergraphx.readwrite import load_hypergraph
from hypergraphx.representations.projections import clique_projection
from hypergraphx.viz import draw_clique, draw_hypergraph
from hypergraphx.viz.draw_hypergraph import Object
from networkx import subgraph, kamada_kawai_layout
from networkx.algorithms.approximation import simulated_annealing_tsp, greedy_tsp
from numpy.ma.core import floor
from scipy.linalg import sqrtm
from scipy.signal import square
from setuptools.wheel import unpack


sys.path.append("..")

import networkx as nx
import matplotlib.pyplot as plt


import numpy as np
import scipy as sp
import networkx as nx
import numba
import math


def chivers_rodgers(Graph, Paths, layout, edgeLength: int = 100):
    n = len(Graph.nodes())

    ind = []
    adj = nx.adjacency_matrix(Graph)
    adj = adj.todense()

    pos = np.zeros((n, 2))
    degree = np.zeros(n)

    #### Read Position of the graph nodes
    for i, node in enumerate(Graph.nodes()):
        pos[i, 0] = layout[node][0]
        pos[i, 1] = layout[node][1]

        degree[i] = Graph.degree[node]

    shortestPathsIter = dict(nx.shortest_path_length(Graph))
    shortestPaths = np.zeros((n, n))

    for i, node in enumerate(Graph.nodes()):
        for j, node2 in enumerate(Graph.nodes()):
            try:
                shortestPaths[i, j] = shortestPathsIter[node][node2]
            except KeyError:
                pass

    k = shortestPaths.max()

    ####  do algorithm
    # pos = slow(pos, adj, n)
    pos = phase2(pos, adj, n, edgeLength, degree)
    pos = phase3(pos, adj, n, edgeLength, degree)

    for i, idx in enumerate(ind):
        node = Graph.nodes[idx]["data"]

        node.X = pos[i, 0]
        node.Y = pos[i, 1]

    for i, node in enumerate(Graph.nodes()):
        layout[node][0]  = pos[i, 0]
        layout[node][1] = pos[i, 1]

        degree[i] = Graph.degree[node]

    return layout
    # postProcessing(Graph)


def postProcessing(Graph):
    processed = set()
    paths = []

    for node in Graph.nodes():

        if node in processed:
            continue

        if Graph.degree(node) == 1:

            path = []
            node1 = node

            while True:
                neighbours = Graph.neighbors(node1)
                path.append(node1)

                if Graph.degree(node1) <= 2:

                    for node2 in neighbours:
                        if node1 != node2 and not node2 in path:
                            node1 = node2
                            continue
                else:
                    break

            path.reverse()
            for n in path:
                data = Graph.nodes[n]["data"]
                print(data.Label)

            print(path, '\n')

            processed.add(node)

            if len(path) < 3:
                continue

            segments = []
            segment = []

            v1 = Graph.nodes[segments[0]]["data"]
            v2 = Graph.nodes[segments[1]]["data"]

            dX = node2.X - node1.X
            dY = node2.Y - node1.Y

            angle1 = np.arctan2(-dY, dX) * 180 / math.pi
            if angle1 < 0:
                angle1 = 360 + angle1

            segment.add(segments[0])
            segment.add(segments[1])

            for n2 in path[2:]:
                v3 = Graph.nodes[n2]["data"]

                dX = node2.X - node1.X
                dY = node2.Y - node1.Y

                angle2 = np.arctan2(-dY, dX) * 180 / math.pi
                if angle2 < 0:
                    angle2 = 360 + angle2

                if abs(angle1 - angle2) > 22.5:
                    segment.add(n2)
                    segments.add(segment)
                    segment = []
                    segment.add(n2)
                else:
                    segment.add(n2)

                angle1 = angle2
                v1 = v2
                v2 = v3

            for s in segments:
                for n in s:
                    data = Graph.nodes[n]["data"]
                    print(data.Label)
                print("\n")


@numba.jit(nopython=True)
def phase2(pos, adj, n, k, degree):
    k = 50
    # k = 1 / n
    minMaxFactor = 0
    factor = max(degree) - 2

    if factor == 0:
        factor = 1

    degree[degree < 2] = 2
    degree = 1.0 * k + minMaxFactor * k * (degree - 2) / factor

    energyDiff = 100.0

    alpha = 50
    iterations = 600

    i = 0

    posNew = np.zeros((n, 2))

    t = alpha
    dt = (t / iterations)

    temp = np.ones(n) * 0.5
    velocityAngle = np.zeros(n)
    factor = 1
    df = factor / iterations

    while i <= iterations:

        # force = np.zeros((n, 2))
        velocity = np.zeros((n, 2))
        velocityM = np.zeros((n, 2))

        for idx1 in range(n):
            # print(idx1)
            for idx2 in range(idx1, n):

                if idx1 == idx2:
                    continue

                pos1 = pos[idx1, :]
                pos2 = pos[idx2, :]

                k1 = degree[idx1]
                k2 = degree[idx2]

                delta = pos1 - pos2
                dist = np.sqrt(delta.dot(delta))

                if dist <= 0.0001:
                    dist = 0.0001

                delta = delta / dist

                if adj[idx1, idx2]:
                    k = (k1 + k2) / 2

                    force = ((0.1 * dist))
                    if force > alpha:
                        force = alpha

                    velocity[idx1] = velocity[idx1] - delta * force
                    velocity[idx2] = velocity[idx2] + delta * force

                    center = (pos1 + pos2) / 2
                    centerToNode = pos1 - center

                    theta = np.arctan2(delta[1], delta[0])
                    # print(theta * 180 / math.pi)

                    isNeg = 1
                    if theta < 0:
                        theta = abs(theta)
                        isNeg = -1

                    theta = np.fmod(theta, math.pi / 4.0)  # Rotate to nearest resolution

                    if theta < math.pi / 8.0:
                        theta = -theta
                    else:
                        theta = math.pi / 4.0 - theta

                    # if isNeg:
                    #    theta = -theta
                    theta = theta * isNeg

                    # print(theta * 180 / math.pi)

                    rotPos = np.zeros((2))
                    rotPos[0] = center[0] + centerToNode[0] * math.cos(theta) - centerToNode[1] * math.sin(theta)
                    rotPos[1] = center[1] + centerToNode[0] * math.sin(theta) + centerToNode[1] * math.cos(theta)

                    vecToNew = rotPos - pos1
                    length = np.sqrt(vecToNew.dot(vecToNew))

                    if length <= 0.0:
                        length = 1

                    vecToNew = vecToNew / length

                    force = length / 2
                    if force > alpha:
                        force = alpha

                    velocityM[idx1] = velocityM[idx1] + vecToNew * force
                    velocityM[idx2] = velocityM[idx2] - vecToNew * force

                    # print(force)
                    # print(vecToNew)

                    force = 0.01 * (k - dist)
                    if force > alpha:
                        force = alpha

                    velocityM[idx1] = velocityM[idx1] + delta * force
                    velocityM[idx2] = velocityM[idx2] - delta * force

                force = ((5000) / (dist ** 2))
                if force > alpha:
                    force = alpha

                velocity[idx1] = velocity[idx1] + delta * force
                velocity[idx2] = velocity[idx2] - delta * force

            # print(velocity[idx1])
            # print(velocityM[idx1])

            v = velocity[idx1] * factor + velocityM[idx1] * (1 - factor)
            angle = np.arctan2(v[1], v[0])
            if angle < 0:
                angle += 2 * math.pi

            d1 = abs(angle - velocityAngle[idx1])
            d2 = 2 * math.pi - d1
            diff = d1 if d1 < d2 else d2;

            if diff <= math.pi / 8:
                temp[idx1] += 0.1
            elif diff >= 3 * math.pi / 8:
                temp[idx1] -= 0.1

            if temp[idx1] < 0.1:
                temp[idx1] = 0.1
            elif temp[idx1] > 1.0:
                temp[idx1] = 1.0

            velocityAngle[idx1] = angle

            posNew[idx1] = pos[idx1] + velocity[idx1] * temp[idx1] * factor + velocityM[idx1] * temp[idx1] * factor

        d = pos - posNew
        dd = np.sum(np.abs(d) ** 2, axis=-1) ** (1. / 2)
        for idx1 in range(n):
            pos[idx1] = posNew[idx1]

        energyDiff = max(dd)
        factor -= df
        i = i + 1

    print(energyDiff)
    print(i)

    return pos


@numba.jit(nopython=True)
def phase3(pos, adj, n, k, degree):
    # k = 1 / n
    minMaxFactor = 0
    factor = max(degree) - 2

    if factor == 0:
        factor = 1

    degree[degree < 2] = 2
    degree = 1.0 * k + minMaxFactor * k * (degree - 2) / factor

    energyDiff = 100.0

    alpha = 50

    iterations = 400
    i = 0

    posNew = np.zeros((n, 2))

    temp = np.ones(n) * 0.5
    velocityAngle = np.zeros(n)
    factor = 1
    df = factor / iterations

    while i <= iterations:

        # force = np.zeros((n, 2))
        velocity = np.zeros((n, 2))
        velocityM = np.zeros((n, 2))

        for idx1 in range(n):
            # print(idx1)
            for idx2 in range(idx1, n):

                if idx1 == idx2:
                    continue

                pos1 = pos[idx1, :]
                pos2 = pos[idx2, :]

                k1 = degree[idx1]
                k2 = degree[idx2]

                # print(delta)
                delta = pos1 - pos2
                dist = np.sqrt(delta.dot(delta))

                if dist <= 0.0001:
                    dist = 0.0001

                delta = delta / dist

                if adj[idx1, idx2]:
                    k = (k1 + k2) / 2

                    center = (pos1 + pos2) / 2
                    centerToNode = pos1 - center

                    theta = np.arctan2(delta[1], delta[0])

                    isNeg = 1
                    if theta < 0:
                        theta = abs(theta)
                        isNeg = -1

                    theta = np.fmod(theta, math.pi / 4.0)  # Rotate to nearest resolution

                    if theta < math.pi / 8.0:
                        theta = -theta
                    else:
                        theta = math.pi / 4.0 - theta

                    theta = theta * isNeg

                    rotPos = np.zeros((2))
                    rotPos[0] = center[0] + centerToNode[0] * math.cos(theta) - centerToNode[1] * math.sin(theta)
                    rotPos[1] = center[1] + centerToNode[0] * math.sin(theta) + centerToNode[1] * math.cos(theta)

                    vecToNew = rotPos - pos1
                    length = np.sqrt(vecToNew.dot(vecToNew))
                    if length == 0:
                        length = 0.0001
                    vecToNew = vecToNew / length

                    force = length / 2
                    if force > alpha:
                        force = alpha

                    velocityM[idx1] = velocityM[idx1] + vecToNew * force
                    velocityM[idx2] = velocityM[idx2] - vecToNew * force

                    force = 0.01 * (k - dist)
                    if force > alpha:
                        force = alpha

                    velocityM[idx1] = velocityM[idx1] + delta * force
                    velocityM[idx2] = velocityM[idx2] - delta * force

            v = velocityM[idx1]
            angle = np.arctan2(v[1], v[0])
            if angle < 0:
                angle += 2 * math.pi

            d1 = abs(angle - velocityAngle[idx1])
            d2 = 2 * math.pi - d1
            diff = d1 if d1 < d2 else d2;

            if diff <= math.pi / 8:
                temp[idx1] += 0.1
            elif diff >= 3 * math.pi / 8:
                temp[idx1] -= 0.1

            if temp[idx1] < 0.1:
                temp[idx1] = 0.1
            elif temp[idx1] > 1.0:
                temp[idx1] = 1.0

            velocityAngle[idx1] = angle

            posNew[idx1] = pos[idx1] + velocityM[idx1] * temp[idx1]

        d = pos - posNew
        dd = np.sum(np.abs(d) ** 2, axis=-1) ** (1. / 2)
        for idx1 in range(n):
            pos[idx1] = posNew[idx1]

        energyDiff = max(dd)
        factor -= df
        i = i + 1

    # print(energyDiff)
    print(i)

    return pos




def condense_hypergraph(h: Hypergraph):
    compressed_hypergraph = Hypergraph

    one_edge_to_edge = dict()
    only_in_one_edge = list()
    for node in h.get_nodes():
        if h.degree(node) == 1:
            only_in_one_edge.append(node)
            one_edge_to_edge[node] = h.get_incident_edges(node)[0]


    edge_mapping = dict()
    idx = 0;
    for edge in h.get_edges():
        edge_mapping[edge] = idx
        idx += 1

    compressed_nodes = dict()
    for node in h.get_nodes():
        if node not in only_in_one_edge:
            incident_edges = sorted([edge_mapping[edge] for edge in h.get_incident_edges(node)])
            incident_edges = tuple(incident_edges)
            if incident_edges not in compressed_nodes.keys():
                compressed_nodes[incident_edges] = node
            else:
                x = compressed_nodes[incident_edges]
                compressed_nodes[incident_edges] = list()
                if type(x) is list:
                    compressed_nodes[incident_edges] += x
                else:
                    compressed_nodes[incident_edges].append(x)
                compressed_nodes[incident_edges].append(node)

    g = nx.Graph()

    for compressed_node in compressed_nodes.values():
        if type(compressed_node) is not list:
            g.add_node(compressed_node)
        else:
            g.add_node(tuple(compressed_node))

    edge_to_new_edge = dict()
    new_edges = list()
    for edge in h.get_edges():
        edge_clone = set(edge)
        new_edge = tuple()
        for node in only_in_one_edge:
            edge_clone = edge_clone.difference({node})
        for compressed_node in compressed_nodes.values():
            edge = set(sorted(edge))
            if type(compressed_node) is list:
                compressed_node = set(sorted(compressed_node))
            else:
                compressed_node = {compressed_node}
            if compressed_node.issubset(edge) and len(edge.intersection(compressed_node)) > 1:
                new_edge += (tuple(sorted(compressed_node)),)
                for value in compressed_node:
                    edge_clone.remove(value)

        if len(edge_clone) > 0:
            new_edge += tuple(edge_clone)
        if len(new_edge) > 1:
            new_edges.append(new_edge)
            edge_to_new_edge[tuple(edge)] = new_edge

    similarity = dict()
    for node1 in compressed_nodes.values():
        for node2 in compressed_nodes.values():
            if node1 != node2:
                if type(node1) is list:
                    node1 = tuple(node1)
                if type(node2) is list:
                    node2 = tuple(node2)
                incident_edges1 = calculate_incidence(node1, new_edges)
                incident_edges2 = calculate_incidence(node2, new_edges)
                similarity12 = len(incident_edges1.intersection(incident_edges2))
                similarity[(node1, node2)] = similarity12


    for edge in new_edges:
        for i in range(len(edge) - 1):
            for j in range(i + 1, len(edge)):
                if similarity[(edge[i], edge[j])] != 0:
                    similarity_weight = 1/similarity[(edge[i], edge[j])]
                else:
                    similarity_weight = 2
                g.add_edge(edge[i], edge[j], weight=similarity_weight)

    edge_to_path = dict()
    paths = list()
    for edge in new_edges:
        edge_graph = subgraph(g, edge)
        method = lambda G, weight: nx.approximation.simulated_annealing_tsp(edge_graph, list(edge_graph)+[next(iter(edge_graph))], weight=weight, temp=5000)
        path = nx.approximation.traveling_salesman_problem(edge_graph, method=method, cycle=False)
        paths.append(path)
        edge_to_path[edge] = path

    to_remove_node = list()
    to_add_edge = list()
    for node in g.nodes():
        if type(node) is tuple:
            to_remove_node.append(node)
            neighbors = g.neighbors(node)
            unpacked_node = [x for x in node]
            x = 1

            incident_edges = g.edges(node)
            for edge in incident_edges:
                new_edge = set(edge)
                new_edge.remove(node)
                for x in unpacked_node:
                    new_edge.add(x)
                    to_add_edge.append(tuple(new_edge))
                    new_edge.remove(x)



    for node in to_remove_node:
        g.remove_node(node)
    for edge in to_add_edge:
        g.add_edge(edge[0], edge[1])
    for path in paths:
        for node in path:
            if type(node) is tuple:
                index = path.index(node)
                path.pop(index)
                for x in node:
                    path.insert(index, x)
                    index += 1

    for node in only_in_one_edge:
        try:
            current_path = edge_to_path[edge_to_new_edge[one_edge_to_edge[node]]]
            current_path.append(node)
            index = paths.index(edge_to_path[edge_to_new_edge[one_edge_to_edge[node]]])
            paths.pop(index)
            paths.insert(index, current_path)
        except KeyError:
            if list(one_edge_to_edge[node]) not in paths:
                paths.append(list(one_edge_to_edge[node]))

    new_support = nx.Graph()
    for path in paths:
        for i in range(len(path) - 1):
            new_support.add_edge(path[i], path[i + 1])


    initial_layout = kamada_kawai_layout(new_support)

    new_support = nx.Graph()
    for edge in paths:
        for i in range(len(edge) - 1):
            for j in range(i + 1, len(edge)):
                new_support.add_edge(edge[i], edge[j])
    new_paths = list()
    for i in range(10):
        entire_copy = new_support.copy()
        for edge in paths:
            for i in range(len(edge) - 1):
                for j in range(i + 1, len(edge)):
                    entire_copy.add_edge(edge[i], edge[j])
        for node1 in entire_copy.nodes():
            for node2 in entire_copy.nodes():
                if node1 != node2:
                    incident_edges1 = calculate_incidence(node1, paths)
                    incident_edges2 = calculate_incidence(node2, paths)
                    similarity12 = len(incident_edges1.intersection(incident_edges2))
                    euclidean_distance = distance(initial_layout, node1, node2)
                    try:
                        similarity12 = 1/similarity12
                    except ZeroDivisionError:
                        similarity12 = 2
                    value = math.sqrt(similarity12*euclidean_distance)
                    if entire_copy.has_edge(node1, node2):
                        entire_copy[node1][node2]["weight"] = value

        for path in paths:
            edge_graph = subgraph(entire_copy, path)
            method = lambda G, weight: nx.approximation.simulated_annealing_tsp(edge_graph, "greedy", weight=weight, temp=5000)
            new_path = nx.approximation.traveling_salesman_problem(edge_graph, method=method, cycle=False)
            new_paths.append(new_path)

        refined = nx.Graph()
        for path in new_paths:
            for i in range(len(path) - 1):
                refined.add_edge(path[i], path[i + 1])

        initial_layout = kamada_kawai_layout(refined, pos = initial_layout)
        if new_paths != paths:
            paths = new_paths.copy()
        else:
            break
        new_paths.clear()
        new_support = refined.copy()

    initial_layout = chivers_rodgers(new_support, paths, initial_layout)
    paths_in_edge = dict()
    idx = 0
    for path in paths:
        for i in range(len(path) - 1):
            key = (path[i], path[i + 1])
            key = tuple(sorted(key))
            try:
                prev = paths_in_edge[key]
            except KeyError:
                prev = []
            paths_in_edge[key] = list()
            paths_in_edge[key] += prev
            paths_in_edge[key] += [idx]

        idx += 1


    palette = list()
    while len(palette) < len(paths):
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        if color not in palette:
            palette.append(color)

    passo_edge = dict()
    for edge in new_support.edges():
        key = (edge[0], edge[1])
        key = tuple(sorted(key))
        lines_in_edge = len(paths_in_edge[key])
        if lines_in_edge % 2 != 0:
            passo = lines_in_edge - 1
            passo /= 2
        else:
            passo = lines_in_edge / 2
        passo_edge[key] = passo

    idx = 0
    for path in paths:
        for i in range(len(path) - 1):
            key = (path[i], path[i + 1])
            key = tuple(sorted(key))
            passo = passo_edge[key]
            draw_line(initial_layout, palette, path, i, idx, passo)
            passo_edge[key] -= 1

        idx += 1

    labels = dict((n, n) for n in new_support.nodes())
    nx.draw_networkx_nodes(new_support, initial_layout,)
    nx.draw_networkx_labels(new_support, pos=initial_layout, labels=labels)


    return h

def draw_metroset(h: Hypergraph):
    condensed_h = condense_hypergraph(h)

def draw_line(layout, palette, path, i:int, idx: int, passo: int):
    offset = (passo * 3)
    pos = find_pos(layout, path[i], path[i+1])
    if pos == "vertical":
        plt.plot([layout[path[i]][0]+ offset, layout[path[i + 1]][0] + offset],
             [layout[path[i]][1], layout[path[i + 1]][1]], linewidth=1,
             color=palette[idx])
    elif pos == "horizontal":
        plt.plot([layout[path[i]][0], layout[path[i + 1]][0]],
                 [layout[path[i]][1] + offset, layout[path[i + 1]][1] + offset], linewidth=1,
                 color=palette[idx])
    elif pos == "oblique":
        plt.plot([layout[path[i]][0] + offset, layout[path[i + 1]][0] + offset],
                 [layout[path[i]][1] + offset, layout[path[i + 1]][1] + offset], linewidth=1,
                 color=palette[idx])

def calculate_incidence(node, edges):
    if type(node) is tuple:
        node = set(node)
    else:
        node = {node}
    incident_edges = set()
    for edge in edges:
        edge = set(edge)
        if len(edge.intersection(node)) > 0:
            incident_edges.add(tuple(edge))

    return incident_edges
def distance(layout, node1, node2):
    """
    Given a layout, return the euclidian distance between two nodes.
    """
    x1, y1 = layout[node1]
    x2, y2 = layout[node2]
    return ((x1 - x2)**2 + (y1-y2)**2)**(1/2)
def find_pos(layout, node1, node2):
    x1, y1 = layout[node1]
    x2, y2 = layout[node2]

    if trunc(x1) == trunc(x2):
        return "vertical"
    else:
        return "horizontal"

