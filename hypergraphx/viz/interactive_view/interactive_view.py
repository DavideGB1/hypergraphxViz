import ctypes
import multiprocessing
import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.viz.interactive_view.aboutmepage.aboutme import AboutMePage
from hypergraphx.viz.interactive_view.controller import Controller
from hypergraphx.viz.interactive_view.editing_view.modify_hypergraph_menu import ModifyHypergraphMenu
from hypergraphx.viz.interactive_view.drawing_view.drawing_view import HypergraphDrawingWidget
from hypergraphx.viz.interactive_view.stats_view.stats_view import HypergraphStatsWidget

QSS_FILE = "stylesheet.qss"

class MainView(QWidget):

    # constructor
    def __init__(self, hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph):
        super().__init__()
        self.controller = Controller(hypergraph)
        self.setWindowTitle("HypergraphX Visualizer")
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(script_dir + os.path.sep + 'logo_cropped.png'))
        if "win" in sys.platform and "darwin" not in sys.platform:
            myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.central_tab = QTabWidget(parent=self)
        self.central_tab.setObjectName("MainTab")
        self.central_tab.setDocumentMode(True)
        self.drawing_tab = HypergraphDrawingWidget(controller=self.controller, parent=self.central_tab)
        visualization_icon = QIcon("icons/hypergraph.svg")
        self.central_tab.addTab(self.drawing_tab, visualization_icon, "Visualization")
        self.stats_tab = HypergraphStatsWidget(controller=self.controller, parent=self.central_tab)
        statistics_icon = QIcon("icons/stats.svg")
        self.central_tab.addTab(self.stats_tab, statistics_icon, "Statistics")
        self.modify_hypergraph_tab = ModifyHypergraphMenu(controller=self.controller, parent=self.central_tab )
        editing_icon = QIcon("icons/edit.svg")
        self.central_tab.addTab(self.modify_hypergraph_tab, editing_icon, "Hypergraph Editing")
        self.about_me = AboutMePage(parent=self.central_tab)
        info_icon = QIcon("icons/info.svg")
        self.central_tab.addTab(self.about_me, info_icon, "About Me")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.central_tab)
        self.setLayout(self.layout)


def start_interactive_view(h: Hypergraph|TemporalHypergraph|DirectedHypergraph) -> None:
    """
    Wrapper function used to start the interactive view.
    Parameters
    ----------
    h: Hypergraph or TemporalHypergraph or DirectedHypergraph
    """
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        app = QApplication(sys.argv)
        with open(QSS_FILE, "r") as fh:
            app.setStyleSheet(fh.read())

        main = MainView(hypergraph=h)
        main.show()
        sys.exit(app.exec_())

h = Hypergraph([(1,2,3,4),(1,2,3),(1,2), (2,5,6),(5,6)])
start_interactive_view(h)
