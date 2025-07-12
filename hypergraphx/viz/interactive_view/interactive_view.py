import ctypes
import multiprocessing
import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout

from hypergraphx import Hypergraph, TemporalHypergraph, DirectedHypergraph
from hypergraphx.viz.interactive_view.aboutmepage.aboutme import AboutMePage
from hypergraphx.viz.interactive_view.editing_view.modify_hypergraph_menu import ModifyHypergraphMenu
from hypergraphx.viz.interactive_view.drawing_view.drawing_view import HypergraphDrawingWidget
from hypergraphx.viz.interactive_view.stats_view.stats_view import HypergraphStatsWidget


class MainView(QWidget):

    # constructor
    def __init__(self, hypergraph: Hypergraph | TemporalHypergraph | DirectedHypergraph):
        super().__init__()
        self.hypergraph = hypergraph
        self.setWindowTitle("HypergraphX Visualizer")
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(script_dir + os.path.sep + 'logo_cropped.png'))
        if "win" in sys.platform and "darwin" not in sys.platform:
            myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.central_tab = QTabWidget(parent=self)
        self.central_tab.setObjectName("MainTab")
        self.central_tab.setStyleSheet("""
                    QTabWidget#OptionsTabs::pane {
                    }
                    QTabBar::tab:first {
                        margin-left: 10px;
                    }
                    QTabWidget#MainTab QTabBar::tab {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F5F5F5, stop: 1 #E0E0E0);
                        border: 1px solid #BDBDBD;
                        border-bottom: none;
                        border-top-left-radius: 6px;
                        border-top-right-radius: 6px;
                        padding: 4px 5px;
                        margin-right: 2px;
                        color: #444;
                        font-weight: bold;
                        font-size: 12px;
                        width: 150px;
                    }

                    QTabWidget#MainTab QTabBar::tab:hover:!selected {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFFFFF, stop: 1 #E8E8E8);
                    }

                    QTabWidget#MainTab QTabBar::tab:selected {
                        background-color: white;
                        color: #005A9E;
                        border-bottom-color: transparent; 
                        margin-bottom: -1px;
                        padding-bottom: 9px;
                    }

                    QTabWidget#MainTab QTabBar::tab:selected:hover {
                        background-color: white;
                    }
                    AboutMePage {
                        background-color: white;
                    }
                """)
        self.central_tab.setDocumentMode(True)
        self.drawing_tab = HypergraphDrawingWidget(hypergraph = self.hypergraph, parent=self)
        visualization_icon = QIcon("icons/hypergraph.svg")
        self.central_tab.addTab(self.drawing_tab, visualization_icon, "Visualization")
        self.stats_tab = HypergraphStatsWidget(self.hypergraph, parent=self.central_tab)
        statistics_icon = QIcon("icons/stats.svg")
        self.central_tab.addTab(self.stats_tab, statistics_icon, "Statistics")
        self.modify_hypergraph_tab = ModifyHypergraphMenu(hypergraph, parent=self.central_tab)
        self.modify_hypergraph_tab.updated_hypergraph.connect(self.update_hypergraph)
        editing_icon = QIcon("icons/edit.svg")
        self.central_tab.addTab(self.modify_hypergraph_tab, editing_icon, "Hypergraph Editing")
        self.about_me = AboutMePage(parent=self)
        info_icon = QIcon("icons/info.svg")
        self.central_tab.addTab(self.about_me, info_icon, "About Me")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.central_tab)
        self.setLayout(self.layout)

    def update_hypergraph(self, example = None, hypergraph = None):
        """
        Updates the hypergraph instance with new data and corresponding UI components.

        Parameters
        ----------
        example : dict, optional
            Dictionary containing a key "hypergraph" which holds the new hypergraph data.
        hypergraph : Hypergraph, DirectedHypergraph, or TemporalHypergraph, optional
            A new hypergraph instance to update the current hypergraph.
        """
        if example is not None:
            self.hypergraph = example["hypergraph"]
        if hypergraph is not None:
            self.hypergraph = hypergraph
        self.drawing_tab.update_hypergraph(self.hypergraph)
        self.stats_tab.update_hypergraph(self.hypergraph)

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
        app.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                padding: 2px 4px 2px 4px;
                min-width: 6em;
                background: white;
                font-size: 13px;
            }
        
            QComboBox QLineEdit {
                background: transparent;
                border: none;
                padding-left: 8px;
                color: #333;
            }
        
            QComboBox:hover {
                border-color: #5D9CEC;
            }
        
            QComboBox:on {
                border: 1px solid #4A89DC;
            }
        
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 35px;
                border-left-width: 0px;
                border-radius: 4px;
                border-radius: 4px;
            }
        
            QComboBox::drop-down:!on {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5D9CEC, stop: 1 #4A89DC);
                border: 1px solid #3A79CB;
                border-bottom: 3px solid #3A79CB;
                border-radius: 5px;
                margin: 2px;
            }
        
            QComboBox::drop-down:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6AACFF, stop: 1 #5D9CEC);
            }
        
            QComboBox::drop-down:on {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4A89DC, stop: 1 #3A79CB);
                border: 1px solid #3A79CB;
                border-bottom: 1px solid #3A79CB;
                margin: 2px;
                margin-top: 4px;
            }
        
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' fill='white'><path d='M7 10l5-5H2z'/></svg>);
                width: 14px;
                height: 14px;
            }
            
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                padding: 4px;
                font-size: 13px;
                color: #333;
                padding-left: 8px; 
            }

            QDoubleSpinBox:hover {
                border-color: #5D9CEC;
            }
            
            QDoubleSpinBox:focus {
                border-color: #4A89DC;
            }
            
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                width: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #F5F5F5, stop: 1 #E0E0E0);
                border: 1px solid #BDBDBD;
            }
            
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFFFFF, stop: 1 #E8E8E8);
            }
            
            QDoubleSpinBox::up-button:pressed, QDoubleSpinBox::down-button:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #D0D0D0);
                padding-top: 2px;
            }
            
            QDoubleSpinBox::up-button {
                subcontrol-position: top right;
                border-top-right-radius: 4px;
                border-left-width: 1px;
            }
            
            QDoubleSpinBox::down-button {
                subcontrol-position: bottom right;
                border-bottom-right-radius: 4px;
                border-left-width: 1px;
                margin-top: -1px;
            }
            
            QDoubleSpinBox::up-arrow {
                image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%23666'><path d='M5 2l4 4H1z'/></svg>);
                width: 10px;
                height: 10px;
            }
            
            QDoubleSpinBox::down-arrow {
                image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' fill='%23666'><path d='M5 8L1 4h8z'/></svg>);
                width: 10px;
                height: 10px;
            }

            QCheckBox {
                spacing: 10px;
                color: #333;
                font-size: 13px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 1px solid #BDBDBD;
                border-top-color: #A0A0A0;
                border-left-color: #A0A0A0;
            }
            
            QCheckBox::indicator:unchecked:hover {
                border-color: #5D9CEC;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5D9CEC, stop: 1 #4A89DC);
                border: 1px solid #3A79CB;
                image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24'><path fill='white' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>);
            }
            
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6AACFF, stop: 1 #5D9CEC);
            }
            
            QCheckBox::indicator:disabled {
                background-color: #E0E0E0;
                border: 1px solid #C0C0C0;
            }
        """)
        main = MainView(hypergraph=h)
        main.show()
        sys.exit(app.exec_())

h = Hypergraph([(6,7,8,9),(7,8,15),(8,9,14),(3,6),(1,2,3),(4,5,6),(4,5,12,16,17),(17,18,2),(1,4,10,11,12),(10,11,13),(5,6,17,18),(4,12,16,17),(16,17,20),(17,19,20,22),(18,19,21),(16,17,18,19,21),(19,22),(19,23,24,25),(23,24,25),(24,26),(23,27)])
start_interactive_view(h)
