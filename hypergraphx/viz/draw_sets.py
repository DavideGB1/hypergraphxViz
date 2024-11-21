import math
import random
from typing import Optional, Union
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx import kamada_kawai_layout
from hypergraphx import Hypergraph
from hypergraphx.representations.projections import clique_projection
from hypergraphx.viz.__support import ignore_unused_args, filter_hypergraph


def draw_second(points, radius,hyperedge_alpha, color, facecolor, ax = None):
    lenPoints = len(points)
    vertexes_x = []
    vertexes_y = []
    for i in range(lenPoints):
        p1 = points[i]
        p = points[(i + 1)%lenPoints]
        p2 = points[(i + 2)%lenPoints]
        v1 = vector(p,p1)
        v2 = vector(p,p2)
        sinA = v1.nx*v2.ny - (v1.ny*v2.nx)
        sinA90 = v1.nx*v2.nx -(v1.ny*(-v2.ny))
        angle = math.asin(max(-1, min(1, sinA)))
        radDirection = 1
        drawDirection = False
        magic = False
        if sinA90 < 0:
            if angle < 0:
                angle = np.pi + angle
            else:
                angle = np.pi - angle
                radDirection = -1
                drawDirection = True
                magic = True
        else:
            if angle > 0:
                radDirection = -1
            else:
                drawDirection = True

        halfAngle = angle/2
        lenOut = abs(math.cos(halfAngle) * radius / math.sin(halfAngle))
        if lenOut > min(v1.length / 2, v2.length / 2):
            lenOut = min(v1.length / 2, v2.length / 2)
            cRadius = abs(lenOut * math.sin(halfAngle) / math.cos(halfAngle))
        else:
            cRadius = radius
        ox = p[0] + v2.nx * lenOut
        oy = p[1] + v2.ny * lenOut
        ox += -v2.ny * cRadius * radDirection
        oy += v2.nx * cRadius * radDirection
        start_angle = v1.ang + (np.pi / 2 * radDirection)
        end_angle = v2.ang - (np.pi / 2 * radDirection)
        if end_angle < 0 and radDirection != -1:
            end_angle += 2 * np.pi
        if not drawDirection:
            tmp =  start_angle + 2 * np.pi
            if start_angle < 0 and tmp < end_angle:
                start_angle = tmp
        elif end_angle < start_angle and radDirection != -1:
            end_angle += 2 * np.pi

        theta = np.linspace(start_angle, end_angle, 100)

        point_angle = math.atan2(p[2],p[3])
        in_arch= True
        if point_angle < 0:
            point_angle += 2 * np.pi
        if not start_angle <= point_angle <= end_angle:
            in_arch = False
        if (p[2]**2 + p[3]**2) > radius * radius:
            in_arch = False
        if not in_arch and not magic:
            ox = p[2]
            oy = p[3]

        x = ox + cRadius * np.cos(theta)
        y = oy + cRadius * np.sin(theta)

        vertexes_x.extend(x)
        vertexes_y.extend(y)

    polygon = plt.Polygon(np.column_stack([vertexes_x, vertexes_y]), closed=True, fill=True, alpha=hyperedge_alpha)
    polygon.set_facecolor(facecolor)
    polygon.set_edgecolor(color)
    ax.add_patch(polygon)

class vector():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.x = p2[0] - p1[0]
        self.y = p2[1] - p1[1]
        self.length = math.sqrt((self.x**2)+(self.y**2))
        self.nx = self.x / self.length
        self.ny = self.y / self.length
        self.ang = math.atan2(self.ny, self.nx)


@ignore_unused_args
def draw_sets(
        hypergraph: Hypergraph,
        figsize: tuple = (12, 7),
        cardinality: tuple[int, int] | int = -1,
        x_heaviest: float = 1.0,
        ax: Optional[plt.Axes] = None,
        pos: Optional[dict] = None,
        edge_color: str = "lightgrey",
        hyperedge_color_by_order: Optional[dict] = None,
        hyperedge_facecolor_by_order: Optional[dict] = None,
        edge_width: float = 1.2,
        hyperedge_alpha: Union[float, np.array] = 0.8,
        node_size: Union[int, np.array] = 150,
        node_color: str | dict = "#E2E0DD",
        node_facecolor: str | dict = "black",
        node_shape: str | dict = "o",
        with_node_labels: bool = True,
        label_size: float = 10,
        label_col: str = "black",
        seed: int = 10,
        scale: int = 1,
        iterations: int = 1000,
        opt_dist: float = 1,
):
    """Visualize a hypergraph."""
    # Initialize figure.
    if ax is None:
        plt.figure(figsize=figsize)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    #Filter the Hypergraph nodes and edges
    hypergraph = filter_hypergraph(hypergraph, cardinality, x_heaviest)

    # Extract node positions based on the hypergraph clique projection.
    if pos is None:
        g = clique_projection(hypergraph)
        pos = kamada_kawai_layout(g, scale=scale)


    # Set color hyperedges of size > 2 (order > 1).
    if hyperedge_color_by_order is None:
        hyperedge_color_by_order = {2: "#FFBC79", 3: "#79BCFF", 4: "#4C9F4C"}
    if hyperedge_facecolor_by_order is None:
        hyperedge_facecolor_by_order = {2: "#FFBC79", 3: "#79BCFF", 4: "#4C9F4C"}

    # Extract edges (hyperedges of size=2/order=1).
    edges = hypergraph.get_edges(order=1)

    # Initialize empty graph with the nodes and the pairwise interactions of the hypergraph.
    G = nx.Graph()
    G.add_nodes_from(hypergraph.get_nodes())
    for e in edges:
        G.add_edge(e[0], e[1])

    #Create a list of shapes for the hypergraphs if the shape is not a dictionary
    if type(node_shape) == str:
        node_shape = {n: node_shape for n in G.nodes()}
    elif type(node_shape) == dict:
       for node in G.nodes():
           if node not in node_shape:
               node_shape[node] = "o"
    if type(node_color) == str:
        node_color = {n: node_color for n in G.nodes()}
    elif type(node_color) == dict:
        for node in G.nodes():
            if node not in node_color:
                node_color[node] = "E2E0DD"
    if type(node_facecolor) == str:
        node_facecolor = {n: node_facecolor for n in G.nodes()}
    elif type(node_facecolor) == dict:
        for node in G.nodes():
            if node not in node_facecolor:
                node_facecolor[node] = "black"
    for node in G.nodes():
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist = [node],
            node_size=node_size,
            node_shape=node_shape[node],
            node_color=node_color[node],
            edgecolors=node_facecolor[node],
            ax=ax,
        )
    if with_node_labels:
        nx.draw_networkx_labels(
            G,
            pos,
            labels  = dict((n, n) for n in G.nodes()),
            font_size=label_size,
            font_color=label_col
        )

    # Plot the hyperedges (size>2/order>1).
    for hye in list(hypergraph.get_edges()):
        if len(hye) > 2:
            points = []
            for node in hye:
                points.append((pos[node][0], pos[node][1], pos[node][0], pos[node][1]))
                # Center of mass of points.
                x_c = np.mean([x for x, y, a,b in points])
                y_c = np.mean([y for x, y, a,b in points])

            # Order points in a clockwise fashion.
            points = sorted(points, key=lambda x: np.arctan2(x[1] - y_c, x[0] - x_c))

            points = [
                (x_c + 1.8 * (x - x_c), y_c + 1.8 * (y - y_c), a, b) for x, y, a,b in points
            ]

            order = len(hye) - 1

            if order not in hyperedge_color_by_order.keys():
                std_color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                hyperedge_color_by_order[order] = std_color

            if order not in hyperedge_facecolor_by_order.keys():
                std_face_color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                hyperedge_facecolor_by_order[order] = std_face_color

            color = hyperedge_color_by_order[order]
            facecolor = hyperedge_facecolor_by_order[order]
            draw_second(points, 0.1, hyperedge_alpha, color, facecolor, ax)

    #Draws Binary Edges
    nx.draw_networkx_edges(G, pos, width=edge_width, edge_color=edge_color, ax=ax)

    ax.axis("equal")
    plt.axis("equal")

h = Hypergraph([(1,2,3),(4,5,6),(6,7,8,9),(10,11,12,1,4),(4,1),(3,6)])
draw_sets(h)
plt.show()

