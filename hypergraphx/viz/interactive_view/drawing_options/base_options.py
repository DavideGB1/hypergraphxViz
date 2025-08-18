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

        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(container_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        self.scroll_content_widget = QWidget()
        scroll_area.setWidget(self.scroll_content_widget)
        self.scroll_content_widget.setObjectName("GraphicOptionsContent")


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
