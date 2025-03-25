import math

import networkx as nx
import numba
import numpy as np


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



    return pos