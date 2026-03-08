import multiprocessing
from PyQt5 import QtWidgets, QtGui
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,QLabel
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import pyqtgraph as pg

from hypergraphx.measures.node_similarity import jaccard_similarity_matrix
from hypergraphx.viz.interactive_view.custom_widgets.loading_screen import LoadingScreen
from hypergraphx.viz.interactive_view.stats_view.stats_calculations import motifs_calculations, \
    calculate_centrality_pool, degree_calculations, calculate_weight_distribution, adjacency_calculations_pool
from hypergraphx.viz.interactive_view.support import create_canvas_with_toolbar
from hypergraphx.viz.plot_motifs import plot_motifs

class GenericGraphWidget(QWidget):
    def __init__(self, hypergraph, drawing_function, drawing_params, title, parent=None):
        super(GenericGraphWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.drawing_function = drawing_function
        self.drawing_params = drawing_params
        self.title = title
        self.figure = Figure()
        self.axes = None
        self.thread = None
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.canvas, self.toolbar = create_canvas_with_toolbar(self.figure)
        self.toolbar.setParent(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, data):
        self.figure.clf()
        if 'layout' in self.drawing_params:
            layout_type = self.drawing_params['layout']
            if layout_type == '2_plus_1':
                gs = GridSpec(2, 2, figure=self.figure)
                ax1 = self.figure.add_subplot(gs[0, 0])
                ax2 = self.figure.add_subplot(gs[0, 1])
                ax3 = self.figure.add_subplot(gs[1, :])
                self.axes = [ax1, ax2, ax3]
        elif isinstance(self.drawing_params['axes'], tuple):
            self.axes = self.figure.subplots(*self.drawing_params['axes'])
        else:
            self.axes = self.figure.subplots(1, 1)
        if not self.drawing_function == plot_motifs:
            self.drawing_function(self.axes, data, **self.drawing_params.get('extra_params', {}))
        else:
            plot_motifs(data, None, self.axes)
        self.figure.subplots_adjust(wspace=self.drawing_params.get('wspace', 0.5), hspace=self.drawing_params.get('hspace', 0.5))
        self.figure.tight_layout()
        self.canvas.draw()
        self.loading_container.setVisible(False)
        self.canvas.setVisible(True)
        self.toolbar.setVisible(True)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.canvas.setVisible(False)
        self.toolbar.setVisible(False)
        self.loading_container.setVisible(True)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, self.drawing_params['calculation_function'])
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

class MotifsWidget(QWidget):

    def __init__(self, hypergraph, parent=None):
        super().__init__(parent)
        self.hypergraph = hypergraph
        self.button = QPushButton("Calculate Motifs")
        self.button.clicked.connect(self.calculate_motifs)
        self.figure = Figure()
        self.layout = QVBoxLayout()
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.canvas, self.toolbar = create_canvas_with_toolbar(self.figure)
        self.toolbar.setParent(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.toolbar.setVisible(False)
        self.canvas.setVisible(False)
        self.loading_container.setVisible(False)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.drawing_function = plot_motifs
        self.drawing_params = {'axes': (1, 1), 'calculation_function': motifs_calculations}
        self.title = "Motifs"
        self.axes = None
        self.thread = None

    def draw_graph(self, data):
        self.figure.clf()
        if isinstance(self.drawing_params['axes'], tuple):
            self.axes = self.figure.subplots(*self.drawing_params['axes'])
        else:
            self.axes = self.figure.subplots(1, 1)

        plot_motifs(ax = self.axes, motifs = data,  save_name=None, show=False, show_motif_labels=True)
        self.figure.subplots_adjust(wspace=self.drawing_params.get('wspace', 0.5),
                                    hspace=self.drawing_params.get('hspace', 0.5))
        self.canvas.draw()
        self.loading_container.setVisible(False)
        self.toolbar.setVisible(True)
        self.canvas.setVisible(True)
        self.setLayout(self.layout)
        self.update()

    def calculate_motifs(self):
        self.button.setVisible(False)
        self.loading_container.setVisible(True)
        self.thread = StatsWorker(self.hypergraph, self.drawing_params['calculation_function'])
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

    def update_hypergraph(self, hypergraph):
        self.loading_container.setVisible(False)
        self.button.setVisible(True)
        self.toolbar.setVisible(False)
        self.canvas.setVisible(False)
        self.repaint()
        self.hypergraph = hypergraph

class CentralityWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(CentralityWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.thread = None
        self.node_tab = QTableWidget(self)
        self.node_tab.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.edge_tab = QTableWidget(self)
        self.edge_tab.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.node_tab.setAlternatingRowColors(True)
        self.edge_tab.setAlternatingRowColors(True)
        self.node_tab.verticalHeader().setVisible(False)
        self.edge_tab.verticalHeader().setVisible(False)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.node_tab)
        self.layout.addWidget(self.edge_tab)
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, data):
        self.loading_container.setVisible(False)
        nodes_values, edges_values = data[0], data[1]
        self.node_tab.clear()
        self.node_tab.setColumnCount(3)
        self.node_tab.setHorizontalHeaderLabels(['Node', 'Betweenness centrality', 'Closeness centrality'])
        self.node_tab.setRowCount(len(nodes_values))
        self.node_tab.horizontalHeader().setStretchLastSection(True)
        self.node_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for curr_index, (node, b_cent, c_cent) in enumerate(nodes_values):
            item_n = QTableWidgetItem()
            item_n.setData(Qt.EditRole, node)
            self.node_tab.setItem(curr_index, 0, item_n)

            item_b = QTableWidgetItem()
            item_b.setData(Qt.EditRole, round(b_cent, 3))
            self.node_tab.setItem(curr_index, 1, item_b)

            item_c = QTableWidgetItem()
            item_c.setData(Qt.EditRole, round(c_cent, 3))
            self.node_tab.setItem(curr_index, 2, item_c)
        self.node_tab.setSortingEnabled(True)
        header = self.node_tab.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        self.node_tab.sortByColumn(0, Qt.AscendingOrder)
        self.edge_tab.clear()
        self.edge_tab.setColumnCount(3)
        self.edge_tab.setHorizontalHeaderLabels(['Edge', 'Betweenness centrality', 'Closeness centrality'])
        self.edge_tab.setRowCount(len(edges_values))
        self.edge_tab.horizontalHeader().setStretchLastSection(True)
        self.edge_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for curr_index, (edge, b_cent, c_cent) in enumerate(edges_values):
            item_n = QTableWidgetItem()
            item_n.setData(Qt.EditRole, str(edge))
            self.edge_tab.setItem(curr_index, 0, item_n)

            item_b = QTableWidgetItem()
            item_b.setData(Qt.EditRole, round(b_cent, 3))
            self.edge_tab.setItem(curr_index, 1, item_b)

            item_c = QTableWidgetItem()
            item_c.setData(Qt.EditRole, round(c_cent, 3))
            self.edge_tab.setItem(curr_index, 2, item_c)
        self.edge_tab.setSortingEnabled(True)
        header = self.edge_tab.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        self.edge_tab.sortByColumn(0, Qt.AscendingOrder)

        self.node_tab.setVisible(True)
        self.edge_tab.setVisible(True)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.node_tab.setVisible(False)
        self.edge_tab.setVisible(False)
        self.loading_container.setVisible(True)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, calculate_centrality_pool)
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

class HeatMap(pg.GraphicsLayoutWidget):
    def __init__(self, corrMatrix, columns, max=1.0):
        super().__init__()
        pg.setConfigOption('imageAxisOrder', 'row-major')
        correlogram = pg.ImageItem()
        # create transform to center the corner element on the origin, for any assigned image:
        tr = QtGui.QTransform().translate(-0.5, -0.5)
        correlogram.setTransform(tr)
        correlogram.setImage(corrMatrix)
        plotItem = self.addPlot()  # add PlotItem to the main GraphicsLayoutWidget
        plotItem.invertY(True)  # orient y axis to run top-to-bottom
        plotItem.setDefaultPadding(0.0)  # plot without padding data range
        plotItem.addItem(correlogram)  # display correlogram
        for i in range(corrMatrix.shape[0]):
            for j in range(corrMatrix.shape[1]):
                val = corrMatrix[i, j]
                lum = val / max
                text_color = 'w' if lum < 0.5 else 'k'
                text = pg.TextItem(f"{val:.2f}", anchor=(0.5, 0.5), color=text_color)
                text.setPos(j, i)
                plotItem.addItem(text)
        # show full frame, label tick marks at top and left sides, with some extra space for labels:
        plotItem.showAxes(True, showValues=(True, True, False, False), size=20)

        # define major tick marks and labels:
        ticks = [(idx, label) for idx, label in enumerate(columns)]
        for side in ('left', 'top', 'right', 'bottom'):
            plotItem.getAxis(side).setTicks((ticks, []))  # add list of major ticks; no minor ticks
        plotItem.getAxis('bottom').setHeight(10)  # include some additional space at bottom of figure
        plotItem.getAxis('top').setHeight(40)
        plotItem.getAxis('left').setWidth(40)
        plotItem.setLabel('left', 'Nodes', units='ID')
        plotItem.setLabel('top', 'Nodes', units='ID')

        colorMap = pg.colormap.get('magma')
        bar = pg.ColorBarItem(values=(0, max), colorMap=colorMap,interactive=False)
        bar.setImageItem(correlogram, insert_in=plotItem)


class SimilarityWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(SimilarityWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.thread = None
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, similarity_matrix):
        self.loading_container.setVisible(False)
        matrix, columns = similarity_matrix[0], [str(label) for label in list(similarity_matrix[1])]
        self.title = QLabel("Jaccard Similarity Matrix")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            """
                color: black;
                font-size: 18pt;
                font-weight: bold;
            """
        )
        self.heatmap = HeatMap(matrix, columns)
        self.clear()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.heatmap)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.clear()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, jaccard_similarity_matrix)
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class AdjacencyWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(AdjacencyWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.thread = None
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, adj_matrix):
        mapping = adj_matrix[1]
        adj_matrix = adj_matrix[0]
        self.loading_container.setVisible(False)
        self.title = QLabel("Adjacency Matrix")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            """
                color: black;
                font-size: 18pt;
                font-weight: bold;
            """
        )
        labels = [str(label) for label in list(mapping.values())]
        maximum = np.max(adj_matrix)
        self.heatmap = HeatMap(adj_matrix.toarray(), labels, max=maximum)
        self.clear()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.heatmap)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.clear()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, adjacency_calculations_pool)
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class DegreeWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(DegreeWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.thread = None
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, degree_distribution: list):
        degree_distribution = degree_distribution[0]
        self.loading_container.setVisible(False)
        self.title = QLabel("Degree Distribution")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            """
                color: black;
                font-size: 18pt;
                font-weight: bold;
            """
        )
        window = pg.GraphicsLayoutWidget()
        plot_item = window.addPlot()
        real_x_values = sorted(list(degree_distribution.keys()))
        y_vals = [degree_distribution[x] for x in real_x_values]
        fake_x_indices = np.arange(len(real_x_values))
        self.bargraph = pg.BarGraphItem(x = fake_x_indices, height = y_vals, width = 0.6)
        plot_item.addItem(self.bargraph)
        ax = plot_item.getAxis('bottom')
        ticks = [(i, str(val)) for i, val in enumerate(real_x_values)]
        ax.setTicks([ticks])
        self.clear()
        self.layout.addWidget(self.title)
        self.layout.addWidget(window)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.clear()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, degree_calculations)
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class WeightWidget(QWidget):
    def __init__(self, hypergraph, parent=None):
        super(WeightWidget, self).__init__(parent)
        self.hypergraph = hypergraph
        self.thread = None
        self.layout = QVBoxLayout()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.setLayout(self.layout)
        self.update_hypergraph(self.hypergraph)

    def draw_graph(self, weight_distribution: list):
        weight_distribution = weight_distribution[0]
        self.loading_container.setVisible(False)
        self.title = QLabel("Weight Distribution")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            """
                color: black;
                font-size: 18pt;
                font-weight: bold;
            """
        )
        window = pg.GraphicsLayoutWidget()
        plot_item = window.addPlot()
        real_x_values = sorted(list(weight_distribution.keys()))
        y_vals = [weight_distribution[x] for x in real_x_values]
        fake_x_indices = np.arange(len(real_x_values))
        self.bargraph = pg.BarGraphItem(x = fake_x_indices, height = y_vals, width = 0.6)
        plot_item.addItem(self.bargraph)
        ax = plot_item.getAxis('bottom')
        ticks = [(i, str(val)) for i, val in enumerate(real_x_values)]
        ax.setTicks([ticks])
        self.clear()
        self.layout.addWidget(self.title)
        self.layout.addWidget(window)
        self.update()

    def update_hypergraph(self, hypergraph):
        self.clear()
        self.loading_container = LoadingScreen()
        self.loading_container.setParent(self)
        self.layout.addWidget(self.loading_container)
        self.hypergraph = hypergraph
        self.thread = StatsWorker(self.hypergraph, calculate_weight_distribution)
        self.thread.progress.connect(self.draw_graph)
        self.thread.start()

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class StatsWorker(QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, function, parent=None):
        super(StatsWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.function = function
    def run(self):
        with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
            result = pool.apply(self.function, args=(self.hypergraph, ))
            self.progress.emit(list(result))