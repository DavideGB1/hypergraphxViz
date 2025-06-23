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
        self.bar_widget.setStyleSheet("""
/* Stile per il widget principale con ID #LoadingScreen */
#LoadingScreen {
    background-color: #4a4a4a; /* Sfondo grigio scuro */
    border: 2px solid #5a5a5a;
    border-radius: 15px; /* Angoli arrotondati */
}

/* Stile per tutte le QLabel dentro a #LoadingScreen */
#LoadingScreen QLabel {
    color: black; /* Colore del testo quasi bianco */
    font-size: 18pt;
    font-weight: bold;
}

/* Stile per la QProgressBar */
QProgressBar {
    border: 2px solid #666666;
    border-radius: 8px;
    background-color: #333333; /* Sfondo della barra (la "traccia") */
    text-align: center; /* Anche se non c'è testo, è una buona pratica */
    height: 25px; /* Aumentiamo l'altezza per un effetto più visibile */
}

/* Stile per la parte "piena" della barra (il "chunk") */
QProgressBar::chunk {
    /* Usiamo un gradiente lineare per dare un effetto 3D bombato */
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #0078d7, stop: 1 #005a9e
    );
    border-radius: 6px;
    /* Aggiungiamo un margine per creare spazio tra il chunk e il bordo della barra */
    margin: 2px; 
}
""")
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