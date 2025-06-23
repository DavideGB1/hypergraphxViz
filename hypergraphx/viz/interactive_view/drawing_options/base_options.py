from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QScrollArea


class BaseOptionsWidget(QWidget):
    """
    Base class for options widgets.
    It manages layout, change signals, and data submission logic,
    leaving subclasses to create specific widgets and define how to collect options.
    """
    modified_options = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet(
            """
                QCheckBox {
                    spacing: 10px;
                    color: #333;
                    font-size: 13px;
                    /* Aggiungiamo un po' di spazio sotto per l'ombra */
                    padding-bottom: 3px; 
                }

                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 5px;
                }

                QCheckBox::indicator:unchecked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #F5F5F5, stop: 1 #E0E0E0);
                    border: 1px solid #BDBDBD;
                    border-bottom: 2px solid #B0B0B0; 
                }

                QCheckBox::indicator:unchecked:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #FFFFFF, stop: 1 #E8E8E8);
                    border-color: #9E9E9E;
                }

                QCheckBox::indicator:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #4A89DC, stop: 1 #3A79CB);
                    border: 1px solid #3A79CB;
                    margin-top: 2px;
                }

                QCheckBox::indicator:checked:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5D9CEC, stop: 1 #4A89DC); /* Gradiente più chiaro al hover */
                }

                QCheckBox::check-mark {
                    subcontrol-origin: indicator;
                    subcontrol-position: center center;
                    image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'><path fill='white' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>);
                }

                QCheckBox::indicator:disabled {
                    background: #E0E0E0;
                    border: 1px solid #C0C0C0;
                    border-bottom: 2px solid #BDBDBD;
                }

                QCheckBox::check-mark:disabled {
                    image: none;
                }
            """
        )

        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(container_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        self.scroll_content_widget = QWidget()
        scroll_area.setWidget(self.scroll_content_widget)
        self.scroll_content_widget.setObjectName("GraphicOptionsContent")
        self.scroll_content_widget.setStyleSheet("""
                            QWidget#GraphicOptionsContent {
                                background-color: white;
                                border: 1px solid #dcdcdc; /* Il nostro solito colore per i bordi */
                                border-radius: 5px;
                                border-top-left-radius: 0px;
                            }
                        """)

        self.main_layout = QVBoxLayout(self.scroll_content_widget)
        self.main_layout.setContentsMargins(9, 9, 9, 9)
        self.main_layout.setSpacing(10)
        container_layout.addWidget(scroll_area)
        self._setup_widgets()
        self.main_layout.addStretch()

    def _setup_widgets(self):
        """
        Virtual method that subclasses must implement to create and add their specific widgets.
        """
        raise NotImplementedError("Subclasses must implement _setup_widgets()")

    def get_options(self):
        """
        Virtual method that subclasses must implement
        to return a dictionary with their options status.
        """
        raise NotImplementedError("Subclasses must implement get_options()")

    def send_data(self):
        """
        Gets options using get_options() and emits the signal.
        This method is connected to the change signal of the widgets.
        """
        options = self.get_options()
        self.modified_options.emit(options)
