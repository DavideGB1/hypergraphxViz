from typing import Optional, Any, Dict

from PyQt5 import QtGui
import pyqtgraph as pg

from hypergraphx.viz.__graphic_options import GraphicOptions
from hypergraphx.viz.interactive_view.pyqtgraph_functions.support import _draw_single_node_pyqt, _draw_community_nodes


def draw_paoh_pyqtgraph(
        data: Dict[str, Any],
        widget: Optional[pg.GraphicsLayoutWidget] = None,
        graphicOptions: Optional[GraphicOptions] = None,
        y_label: str = "Nodes",
        x_label: str = "Edges",
        axis_labels_size: int = 16,
        nodes_name_size: int = 12,
        **kwargs
) -> pg.GraphicsLayoutWidget:
    """
    Disegna un PAOH plot usando PyQtGraph partendo dai dati calcolati da calculate_paoh_layout.

    Parameters
    ----------
    data : Dict[str, Any]
        Output della funzione calculate_paoh_layout
    widget : pg.GraphicsLayoutWidget, optional
        Widget esistente su cui disegnare. Se None, ne crea uno nuovo.
    graphicOptions : GraphicOptions, optional
        Opzioni grafiche per personalizzare il plot
    y_label : str
        Label dell'asse Y
    x_label : str
        Label dell'asse X
    axis_labels_size : int
        Dimensione font delle label degli assi
    nodes_name_size : int
        Dimensione font dei nomi dei nodi

    Returns
    -------
    pg.GraphicsLayoutWidget
        Il widget contenente il plot disegnato
    """

    # Unpack the data
    hypergraph = data["hypergraph"]
    node_mapping = data["node_mapping"]
    isDirected = data["isDirected"]
    isTemporal = data["isTemporal"]
    isWeighted = data["isWeighted"]
    timestamps_layout = data["timestamps_layout"]
    timestamp_mapping = data["timestamp_mapping"]
    edge_directed_mapping = data["edge_directed_mapping"]
    u = data["u"]
    community_mapping = data["community_mapping"]
    community_colors = data["community_colors"]
    final_idx_width = data["final_idx_width"]

    # Get and Validate the Graphic Options
    if graphicOptions is None:
        graphicOptions = GraphicOptions()
    graphicOptions.check_if_options_are_valid(hypergraph)

    # Crea o usa widget esistente
    if widget is None:
        widget = pg.GraphicsLayoutWidget()
        widget.resize(1000, 800)

    # Crea il plot
    plot = widget.addPlot()
    plot.setLabel('left', y_label, **{'font-size': f'{axis_labels_size}pt'})
    plot.setLabel('bottom', x_label, **{'font-size': f'{axis_labels_size}pt'})
    plot.showGrid(x=False, y=True, alpha=0.3)

    # Prepara i dati per i nodi
    sorted_nodes = sorted(node_mapping.keys(), key=lambda n: node_mapping[n])
    max_node_y = len(sorted_nodes) - 0.5

    # Configura l'asse Y con i nomi dei nodi
    y_ticks = [(node_mapping[node], str(node)) for node in sorted_nodes]
    plot.getAxis('left').setTicks([y_ticks])
    plot.getAxis('left').setStyle(tickFont=QtGui.QFont('Arial', nodes_name_size))

    # Nascondi i tick dell'asse X
    plot.getAxis('bottom').setTicks([])

    # Imposta i limiti degli assi
    plot.setXRange(-0.5, final_idx_width, padding=0)
    plot.setYRange(-0.5, len(sorted_nodes) - 0.5, padding=0)

    idx = 0
    idx_timestamp = 0
    max_timestamp = len(timestamps_layout) - 1

    # Main drawing cycle
    for timestamp_group in timestamps_layout:
        if isTemporal:
            ts_key = sorted(timestamp_mapping.keys())[idx_timestamp]
            # Aggiungi label del timestamp
            text = pg.TextItem(f"Epoch: {ts_key}", anchor=(0, 1), color=(0,0,0))
            text.setPos(idx - 0.45, max_node_y + 0.15)
            text.setFont(QtGui.QFont('Arial', graphicOptions.time_font_size))
            text.setZValue(100)
            plot.addItem(text)

        for column_set in timestamp_group:
            for edge in sorted(column_set):
                original_edge = (ts_key, edge) if isTemporal else edge

                # Calcola le coordinate Y
                first_node, last_node = min(edge), max(edge, key=lambda n: node_mapping[n])
                y1 = node_mapping[min(edge, key=lambda n: node_mapping[n])]
                y2 = node_mapping[last_node]

                # Disegna la linea dell'edge
                edge_color = graphicOptions.edge_color.get(original_edge, 'k')
                edge_width = graphicOptions.edge_size.get(original_edge, 2)

                # Converti colore matplotlib in formato PyQtGraph
                pen = pg.mkPen(color=edge_color, width=edge_width)

                line = pg.PlotDataItem([idx, idx], [y1, y2], pen=pen)
                plot.addItem(line)

                # Aggiungi il peso se presente
                if isWeighted:
                    weight_val = hypergraph.get_weight(edge, ts_key) if isTemporal else hypergraph.get_weight(edge)
                    weight_text = pg.TextItem(str(weight_val), anchor=(0.5, 0), color = (0,0,0))
                    weight_text.setPos(idx, y2 + 1)
                    weight_text.setFont(QtGui.QFont('Arial', graphicOptions.weight_size))
                    weight_text.setZValue(100)
                    plot.addItem(weight_text)

                # Disegna i nodi sull'edge
                if isDirected:
                    true_edge_in, true_edge_out = edge_directed_mapping[original_edge]
                    in_color = graphicOptions.in_edge_color
                    out_color = graphicOptions.out_edge_color

                    # Nodi in ingresso
                    for node in true_edge_in:
                        _draw_single_node_pyqt(
                            plot, idx, node_mapping[node],
                            node, graphicOptions,
                            node_color=in_color
                        )

                    # Nodi in uscita
                    for node in true_edge_out:
                        _draw_single_node_pyqt(
                            plot, idx, node_mapping[node],
                            node, graphicOptions,
                            node_color=out_color
                        )
                else:
                    # Nodi normali
                    for node in edge:
                        _draw_single_node_pyqt(
                            plot, idx, node_mapping[node],
                            node, graphicOptions
                        )

            idx += 0.5

        # Disegna le community se presenti
        if u is not None:
            for node in hypergraph.get_nodes():
                from hypergraphx.viz.__support import _get_node_community
                wedge_sizes, wedge_colors = _get_node_community(
                    community_mapping, node, u, community_colors, 0.1
                )
                _draw_community_nodes(
                    plot,
                    pos=(-0.35, node_mapping[node]),
                    data = wedge_sizes, wedge_colors = wedge_colors,
                    node = node, graphicOptions = graphicOptions,

                )

        # Disegna la linea di separazione temporale
        if isTemporal and idx_timestamp != max_timestamp:
            sep_pen = pg.mkPen(color=graphicOptions.time_separation_line_color, width=graphicOptions.time_separation_line_size)
            sep_line = pg.PlotDataItem([idx, idx], [-0.5, max_node_y], pen=sep_pen)
            plot.addItem(sep_line)
            idx_timestamp += 1
            idx += 0.5

    return widget