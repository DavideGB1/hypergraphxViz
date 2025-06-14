import math
import random
from typing import Optional

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx import kamada_kawai_layout, spring_layout
from scipy.spatial import ConvexHull

from hypergraphx import Hypergraph
from hypergraphx.readwrite import load_hypergraph
from hypergraphx.representations.projections import clique_projection, extra_node_projection
from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.__support import __ignore_unused_args, __filter_hypergraph, _get_node_community, \
    _draw_node_community, _get_community_info, draw_networkx_edge_labels_clone


def _draw_hyperedge_set(
        points: list[tuple[float, float,float,float]],
        radius: Optional[float] = 0.1,
        hyperedge_alpha: Optional[float] = 0.8,
        border_color: Optional[str] = "FFBC79",
        face_color: Optional[str] = "FFBC79",
        ax: Optional[plt.Axes] = None ) -> None:
    """
    Support function used to draw each hyperedge as a polygon with rounded corners.
    Parameters
    ----------
    points: list[tuple[float, float,float,float]]
        Vertexes of the polygon saved two times.
    radius: float, optional
        Used to scale the rounding of the corners.
    hyperedge_alpha: float, optional
        Alpha value of the polygon surface.
    border_color: str, optional
        Color of the polygon border.
    face_color: str, optional
        Color of the polygon surface.
    ax: plt.Axes, optional
        The axes to draw the set on.
    """
    lenPoints = len(points)
    vertexes_x = []
    vertexes_y = []
    for i in range(lenPoints):
        #Find the pivot vertex and the adjacent ones
        p1 = points[i]
        p = points[(i + 1)%lenPoints]
        p2 = points[(i + 2)%lenPoints]
        #Create the vectors that describe the corner
        v1 = __vector(p,p1)
        v2 = __vector(p,p2)
        #Calculate the various angles
        sinA = v1.nx*v2.ny - (v1.ny*v2.nx)
        sinA90 = v1.nx*v2.nx -(v1.ny*(-v2.ny))
        angle = math.asin(max(-1, min(1, sinA)))
        #Checks used to determine how to draw the rounded corner
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
        #Calculate the correct distance of the points
        halfAngle = angle/2
        try:
            lenOut = abs(math.cos(halfAngle) * radius / math.sin(halfAngle))
        except ZeroDivisionError:
            lenOut = abs(math.cos(halfAngle) * radius / 0.01)
        if lenOut > min(v1.length / 2, v2.length / 2):
            lenOut = min(v1.length / 2, v2.length / 2)
            cRadius = abs(lenOut * math.sin(halfAngle) / math.cos(halfAngle))
        else:
            cRadius = radius
        #Caulculate the arc center
        o = (
            p[0] + v2.nx * lenOut-v2.ny * cRadius * radDirection,
            p[1] + v2.ny * lenOut+v2.nx * cRadius * radDirection
        )
        #Calculate start and ending angle
        start_angle = v1.ang + (np.pi / 2 * radDirection)
        end_angle = v2.ang - (np.pi / 2 * radDirection)
        #Modify the angles so we draw the correct arc
        if end_angle < 0 and radDirection != -1:
            end_angle += 2 * np.pi
        if not drawDirection:
            tmp =  start_angle + 2 * np.pi
            if start_angle < 0 and tmp < end_angle:
                start_angle = tmp
        elif end_angle < start_angle and radDirection != -1:
            end_angle += 2 * np.pi
        #Calculate some angles for the arch
        theta = np.linspace(start_angle, end_angle, 100)
        point_angle = math.atan2(p[2],p[3])
        #Determine if the center is inside or outside the arc
        in_arc= True
        if point_angle < 0:
            point_angle += 2 * np.pi
        if not start_angle <= point_angle <= end_angle:
            in_arc = False
        if (p[2]**2 + p[3]**2) > radius * radius:
            in_arc = False
        if not in_arc and not magic:
            o = (p[2],p[3])
        #Calculate the actual points
        x = o[0] + cRadius * np.cos(theta)
        y = o[1] + cRadius * np.sin(theta)
        vertexes_x.extend(x)
        vertexes_y.extend(y)

    #Create and draw the polygon
    polygon = plt.Polygon(np.column_stack([vertexes_x, vertexes_y]), closed=True, fill=True, alpha=hyperedge_alpha)
    polygon.set_facecolor(face_color)
    polygon.set_edgecolor(border_color)
    ax.add_patch(polygon)

class __vector:
    """
    Support class for the set drawing
    """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.x = p2[0] - p1[0]
        self.y = p2[1] - p1[1]
        self.length = math.sqrt((self.x**2)+(self.y**2))
        self.nx = self.x / self.length
        self.ny = self.y / self.length
        self.ang = math.atan2(self.ny, self.nx)

@__ignore_unused_args
def draw_sets(
    hypergraph: Hypergraph,
    u = None,
    k = 0,
    weight_positioning = 0,
    cardinality: tuple[int, int] | int = -1,
    x_heaviest: float = 1.0,
    draw_labels: bool = True,
    rounded_polygon: bool = True,
    hyperedge_color_by_order: Optional[dict] = None,
    hyperedge_facecolor_by_order: Optional[dict] = None,
    hyperedge_alpha: float | dict = 0.8,
    scale: int = 1,
    iterations: int = 1000,
    rounding_radius_size: float = 0.1,
    polygon_expansion_factor: float = 1.8,
    pos: Optional[dict] = None,
    ax: Optional[plt.Axes] = None,
    figsize: tuple[float, float] = (10, 10),
    dpi: int = 300,
    graphicOptions: Optional[GraphicOptions] = None,
    dummy_nodes = [],
    **kwargs) -> dict:
    """
    Draws a set projection of the hypergraph.
    Parameters
    ----------
    hypergraph: Hypergraph.
        The hypergraph to be projected.
    cardinality: tuple[int,int]|int. optional
        Allows you to filter hyperedges so that only those with the default cardinality are visible.
        If it is a tuple, hyperedges with cardinality included in the tuple values will be displayed.
        If -1, all the hyperedges will be visible.
    x_heaviest: float, optional
        Allows you to filter the hyperedges so that only the heaviest x's are shown.
    draw_labels : bool
        Decide if the labels should be drawn.
    rounded_polygon: bool
        Decide if the polygon should be rounded and expanded.
    hyperedge_color_by_order: dict, optional
        Used to determine the border color of each hyperedge using its order.
    hyperedge_facecolor_by_order: dict, optional
        Used to determine the color of each hyperedge using its order.
    hyperedge_alpha: dict | float, optional
        It's used to specify the alpha gradient of each hyperedge polygon. Each hyperedge can have its own alpha.
    scale: int, optional
        Used to influence the distance between nodes
    rounding_radius_size: float, optional
        Radius for the rounded corners of the polygons.
    polygon_expansion_factor: float, optional
        Scale factor for the polygon expansion.
    pos : dict.
        A dictionary with nodes as keys and positions as values.
    ax : matplotlib.axes.Axes.
        The axes to draw the graph on.
    figsize : tuple, optional
        Tuple of float used to specify the image size. Used only if ax is None.
    dpi : int, optional
        The dpi for the figsize. Used only if ax is None.
    graphicOptions: Optional[GraphicOptions].
        Object used to store all the common graphical settings among the representation methods.
    kwargs : dict.
        Keyword arguments to be passed to networkx.draw_networkx.
    """
    # Initialize figure.
    if ax is None:
        plt.figure(figsize=figsize, dpi=dpi)
        plt.subplot(1, 1, 1)
        ax = plt.gca()

    #Filter the Hypergraph nodes and edges
    hypergraph = __filter_hypergraph(hypergraph, cardinality, x_heaviest)
    try:
        for node in hypergraph.isolated_nodes():
            hypergraph.remove_node(node)
    except AttributeError:
        pass

    if graphicOptions is None:
        graphicOptions = GraphicOptions()
    # Extract node positions based on the hypergraph clique projection.
    if pos is None:
        g, _ = extra_node_projection(hypergraph)
        if hypergraph.is_weighted():
            for edge in g.edges():
                weight = g.get_edge_data(edge[0], edge[1])['weight']
                match weight_positioning:
                    case 0:
                        g[edge[0]][edge[1]]['weight'] = 1
                    case 1:
                        pass
                    case 2:
                        g[edge[0]][edge[1]]['weight'] = 1 / weight
        first_pos = kamada_kawai_layout(g, scale=scale)
        if first_pos != {}:
            pos = spring_layout(g,pos=first_pos, iterations=iterations, k = 15)
        else:
            pos = spring_layout(g, iterations=iterations, k = 15)


    # Set color hyperedges of size > 2 (order > 1).
    if hyperedge_color_by_order is None:
        hyperedge_color_by_order = {2: "#FCB07E", 3: "#048BA8", 4: "#99C24D", 5: "#BC2C1A", 6: "#2F1847"}
    if hyperedge_facecolor_by_order is None:
        hyperedge_facecolor_by_order = {2: "#FCB07E", 3: "#048BA8", 4: "#99C24D", 5: "#BC2C1A", 6: "#2F1847"}

    # Extract edges (hyperedges of size=2/order=1).
    edges = hypergraph.get_edges(order=1)

    # Initialize empty graph with the nodes and the pairwise interactions of the hypergraph.
    G = nx.Graph()
    for node in hypergraph.get_nodes():
        G.add_node(node)
    for e in edges:
        weight = hypergraph.get_weight(e)
        match weight_positioning:
            case 0:
                weight = 1
            case 1:
                pass
            case 2:
                weight = 1/weight
        G.add_edge(e[0], e[1], weight = weight, original_weight = hypergraph.get_weight(e))

    #Ensure that all the nodes and binary edges have the graphical attributes specified
    graphicOptions.check_if_options_are_valid(G)

    #Add the labels to the nodes if necessary
    if draw_labels:
        nx.draw_networkx_labels(
            G,
            pos,
            labels  = dict((n, n) for n in G.nodes() if n not in dummy_nodes),
            font_size=graphicOptions.label_size,
            font_color=graphicOptions.label_color,
            **kwargs
        )
    #Ensure that all the hyperedges have an alpha
    if type(hyperedge_alpha) == float:
        hyperedge_alpha = {edge: hyperedge_alpha for edge in hypergraph.get_edges()}
    elif type(hyperedge_alpha) == dict:
        for edge in hypergraph.get_edges():
            if edge not in hyperedge_alpha:
                hyperedge_alpha[edge] = 0.8

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


            #Calculate Order and use it to select a color
            order = len(hye) - 1
            has_dummy = False
            for node in hye:
                if node in dummy_nodes:
                    has_dummy = True
            if has_dummy:
                order-=1
            if order not in hyperedge_color_by_order.keys():
                std_color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                hyperedge_color_by_order[order] = std_color
            if order not in hyperedge_facecolor_by_order.keys():
                std_face_color = "#" + "%06x" % random.randint(0, 0xFFFFFF)
                hyperedge_facecolor_by_order[order] = std_face_color
            color = hyperedge_color_by_order[order]
            facecolor = hyperedge_facecolor_by_order[order]
            if rounded_polygon:
                #Draw the hyperedge with the polygon rounding algoritm
                points = [
                    (x_c + polygon_expansion_factor * (x - x_c), y_c + polygon_expansion_factor * (y - y_c), a, b) for x, y, a, b in points
                ]
                if len(points) >= 5:
                    points_dict = {(a,b) :(c,d) for (a,b,c,d) in points}
                    points_2d = [(a,b) for a,b,c,d in points]
                    hull = ConvexHull(points_2d)
                    hull_points = [ (hull.points[x][0],hull.points[x][1]) for x in hull.vertices]
                    points = [(a,b,points_dict[(a,b)][0],points_dict[(a,b)][1]) for a,b in hull_points]
                _draw_hyperedge_set(points, rounding_radius_size, hyperedge_alpha[hye], color, facecolor, ax)
            else:
                #Draw the hyperedge as a normal polygon with the vertexes in the points
                x = [x[0] for x in points]
                y = [y[1] for y in points]
                polygon = plt.Polygon(np.column_stack([x,y]), closed=True, fill=True,
                                      alpha=hyperedge_alpha[hye])
                polygon.set_facecolor(facecolor)
                polygon.set_edgecolor(color)
                ax.add_patch(polygon)
            if hypergraph.is_weighted():
                ax.text(x_c, y_c, str(hypergraph.get_weight(hye)), fontsize = graphicOptions.weight_size)


    #Draws Binary Edges
    for edge in G.edges():
        nx.draw_networkx_edges(G, pos, edgelist=[edge], width=graphicOptions.edge_size[edge],
                               edge_color=graphicOptions.edge_color[edge], ax=ax, **kwargs)
    if hypergraph.is_weighted():
        labels = nx.get_edge_attributes(G, 'original_weight')
        pos_higher = {}
        y_off = 0.075
        for k, v in pos.items():
            pos_higher[k] = (v[0], v[1] + y_off)
        draw_networkx_edge_labels_clone(G, pos_higher, edge_labels=labels, bbox={'alpha': 0, 'pad': 1}, verticalalignment="top")

    # Draw the Nodes
    if u is not None:
        mapping, col = _get_community_info(hypergraph,k)

    for node in G.nodes():
        if node not in dummy_nodes:
            if u is None:
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    nodelist=[node],
                    node_size=graphicOptions.node_size[node],
                    node_shape=graphicOptions.node_shape[node],
                    node_color=graphicOptions.node_color[node],
                    edgecolors=graphicOptions.node_facecolor[node],
                    ax=ax,
                    **kwargs
                )
            else:
                wedge_sizes, wedge_colors = _get_node_community(mapping,node, u, col,0.1)
                _draw_node_community(ax, node, pos[node], wedge_sizes, wedge_colors, graphicOptions, **kwargs)

    ax.axis("equal")
    ax.axis("off")
    plt.axis("equal")
    plt.axis("off")
    plt.tight_layout()
    return pos