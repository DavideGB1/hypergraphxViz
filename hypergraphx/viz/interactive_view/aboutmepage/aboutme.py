from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize


class AboutMePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_icon = QIcon("logo.png")
        self.icon_label = QLabel(self)
        self.pixmap = self.logo_icon.pixmap(QSize(1000, 300))
        self.icon_label.setPixmap(self.pixmap)
        self.icon_label.setStyleSheet("""
                                    background-color: white;
                                    border: 1px solid #cccccc;
                                    border-radius: 15px;     
                                    padding: 10px;           
                                    color: black;
        """)

        self.layout = QVBoxLayout(self)
        self.version_label = QLabel(parent=self)
        self.version_label.setTextFormat(Qt.RichText)
        self.version_label.setText("<b>Version:</b> 0.0.1")
        self.version_label.setFont(QFont("Arial", 20))
        self.version_label.setStyleSheet("""
                            background-color: white;
                            border: 1px solid #cccccc;
                            border-radius: 15px;     
                            padding: 10px;           
                            color: black;
        """)

        self.author_label = QLabel(parent=self)
        self.author_label.setOpenExternalLinks(True)
        self.author_label.setTextFormat(Qt.RichText)
        self.author_label.setText("<b>Author:</b> <a href=\"http://www.google.com\">Davide Colosimo</a>")
        self.author_label.setFont(QFont("Arial", 20))
        self.author_label.setStyleSheet("""
                    background-color: white;
                    border: 1px solid #cccccc;
                    border-radius: 15px;     
                    padding: 10px;           
                    color: black;
        """)

        self.github_label = QLabel(parent=self)
        self.github_label.setOpenExternalLinks(True)
        self.github_label.setTextFormat(Qt.RichText)
        self.github_label.setText("<b>GitHub Repository:</b> <a href=\"http://www.google.com\">Hypergraphx</a>")
        self.github_label.setFont(QFont("Arial", 20))
        self.github_label.setStyleSheet("""
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 15px;     
            padding: 10px;           
            color: black;
        """)

        self.credits_label = QLabel(parent=self)
        self.credits_label.setOpenExternalLinks(True)
        self.credits_label.setTextFormat(Qt.RichText)
        self.credits_label.setText("<b>Credits:</b> ")
        self.credits_label.setFont(QFont("Arial", 20))
        self.credits_label.setStyleSheet("""
            background-color: white;
            border: 1px solid #cccccc;
            border-radius: 15px;     
            padding: 10px;           
            color: black;
        """)

        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.version_label)
        self.layout.addWidget(self.author_label)
        self.layout.addWidget(self.github_label)
        self.layout.addWidget(self.credits_label)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)
        self.setStyleSheet("""
            background-color: white;
            QLabel {
                border-radius: 5px;
            }
        """)
