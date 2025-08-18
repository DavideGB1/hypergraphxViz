from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout


class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("LoadingScreen")

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.bar_layout = QVBoxLayout()

        label = QLabel("Loading...", self)
        label.setObjectName("LoadingLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_bar = QProgressBar(self)
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(0)

        self.bar_layout.addStretch()
        self.bar_layout.addWidget(label)
        self.bar_layout.addWidget(progress_bar)
        self.bar_layout.addStretch()
        self.bar_widget = QWidget(parent=self)
        self.bar_widget.setLayout(self.bar_layout)
        self.bar_widget.setFixedSize(500, 200)
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addStretch()
        self.h_layout = QHBoxLayout()
        self.h_layout.addStretch()
        self.h_layout.addWidget(self.bar_widget)
        self.h_layout.addStretch()
        self.container_layout.addLayout(self.h_layout)
        self.container_layout.addStretch()
        self.setLayout(self.container_layout)