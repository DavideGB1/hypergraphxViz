import math

from matplotlib import pyplot as plt

from hypergraphx import TemporalHypergraph

temporal = TemporalHypergraph()
temporal.add_edge((1, 2, 3), 1)
temporal.add_edge((4, 5, 6), 1)
temporal.add_edge((6, 7, 8, 9), 1)
temporal.add_edge((1, 2), 2)
temporal.add_edge((4, 5, 6, 3), 2)
temporal.add_edge((6, 7, 8, 9, 1), 2)
temporal.add_edge((1, 2, 5), 3)
temporal.add_edge((4, 5, 6, 3), 3)
temporal.add_edge((6, 7, 8), 3)
temporal.add_edge((1, 2), 6)
temporal.add_edge((1, 2), 7)

def find_intervals(timeline: list):
    timeline = sorted(timeline)
    new_timeline = []
    first_check = True
    timeline_integer_part = dict()
    for number in timeline:
        k = math.floor(number)
        if k not in timeline_integer_part.keys():
            timeline_integer_part[k] = list()
        timeline_integer_part[k].append(number)
    for number_class in timeline_integer_part.values():
        if first_check:
            new_timeline.append(min(number_class))
            first_check = False
        else:
            new_timeline.append(max(number_class))
    timeline = new_timeline
    res = []
    starting_element = timeline[0]
    prev_element = timeline[0]
    for element in timeline:
        if prev_element == element:
            pass
        else:
            if math.floor(element) != math.floor(prev_element)+1:
                res.append((starting_element, prev_element))
                starting_element = element
            prev_element = element
    if (starting_element, prev_element) not in res:
        res.append((starting_element, prev_element))
    return res

def draw_timeline(h: TemporalHypergraph, ax = None, figsize: tuple = (12, 7)):
    if ax is None:
        plt.figure(figsize=figsize)
        plt.subplot(1, 1, 1)
        ax = plt.gca()


    actual_edge_time = dict()
    edges_by_time = dict()
    for values in h.get_edges():
        edge = 0
        time = 0
        if len(values) == 3:
            time, edge, _ = values
        else:
            time, edge = values
        if time not in edges_by_time.keys():
            edges_by_time[time] = list()
        edges_by_time[time].append(edge)
        actual_edge_time[(edge, time)] = time

    for time in edges_by_time.keys():
        edge_list = edges_by_time[time]
        if len(edge_list) > 1:
            for i in range(len(edge_list)-1):
                edge1 = set(sorted(edge_list[i]))
                edge2 = set(sorted(edge_list[i+1]))
                if len(edge1.intersection(edge2)) > 0:
                    actual_edge_time[(edge_list[i+1], time)] = actual_edge_time[(edge_list[i], time)]+0.1

    nodes_timeline = dict()
    for node in h.get_nodes():
        nodes_timeline[node] = set()
    for (edge, actual_time), actual_time in actual_edge_time.items():
        for node in edge:
            nodes_timeline[node].add(actual_time)

    for node, timeline in nodes_timeline.items():
        list_timeline = list(timeline)
        intervals = find_intervals(list_timeline)
        for start, end in intervals:
            if start == end:
                ax.plot(start, node, "bo")
            else:
                ax.plot([start, end], [node, node], color="k")

    for (edge, time), actual_time in actual_edge_time.items():
        for i in range(len(edge)-1):
            ax.plot([actual_time, actual_time], [edge[i]-0.1,edge[i+1]+0.1], color = "b", lw=6, solid_capstyle='round')
        for node in edge:
            ax.plot(actual_time, node, marker = 'o', color='r')

    node_list = h.get_nodes()
    ax.set_yticks(node_list)
    ax.set_xlabel("Epochs")
    ax.set_ylabel("Nodes")
draw_timeline(temporal)
plt.show()
