import multiprocessing

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from matplotlib.figure import Figure

from hypergraphx.viz.interactive_view.custom_widgets.loading_screen import LoadingScreen
from hypergraphx.viz.interactive_view.stats_view.stats_calculations import motifs_calculations
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
        if isinstance(self.drawing_params['axes'], tuple):
            self.axes = self.figure.subplots(*self.drawing_params['axes'])
        else:
            self.axes = self.figure.subplots(1, 1)
        if not self.drawing_function == plot_motifs:
            self.drawing_function(self.axes, data, **self.drawing_params.get('extra_params', {}))
        else:
            plot_motifs(data, None, self.axes)
        self.figure.subplots_adjust(wspace=self.drawing_params.get('wspace', 0.5), hspace=self.drawing_params.get('hspace', 0.5))
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
        if not self.drawing_function == plot_motifs:
            self.drawing_function(self.axes, data, **self.drawing_params.get('extra_params', {}))
        else:
            plot_motifs(data, None, self.axes)
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
        self.hypergraph = hypergraph

class StatsWorker(QThread):
    progress = pyqtSignal(list)
    def __init__(self, hypergraph, function, parent=None):
        super(StatsWorker, self).__init__(parent)
        self.hypergraph = hypergraph
        self.function = function
    def run(self):
        with multiprocessing.Pool(processes=1, maxtasksperchild=1) as pool:
            result = pool.apply(self.function, args=(self.hypergraph, ))
            self.progress.emit(result)