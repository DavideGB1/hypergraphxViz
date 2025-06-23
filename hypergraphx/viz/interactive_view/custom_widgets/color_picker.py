from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QBrush, QPainter, QPixmap
from PyQt5.QtWidgets import QColorDialog, QWidget, QPushButton, QHBoxLayout, QLabel


class ColorPickerCustomWidget(QWidget):
    """
    Class ColorPickerCustomWidget
    -----------------------------
    A custom widget for selecting and displaying a color.
    """
    update_status = pyqtSignal(dict)

    def __init__(self, name, value, in_extra, graphic_options, extra_attributes, parent=None):
        super(ColorPickerCustomWidget, self).__init__(parent)

        self.name = name
        self.in_extra = in_extra
        self.graphic_options = graphic_options
        self.extra_attributes = extra_attributes

        self.color_btn = QPushButton(parent=self)
        self.update_button_color(QColor(value))
        self.color_btn.clicked.connect(self.open_color_picker)
        self.color_btn.setStyleSheet(
            """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #F5F5F5, stop:1 #E0E0E0);
                    border: 1px solid #BDBDBD;
                    border-radius: 5px;
                    width: 24px;
                    height: 24px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                                stop:0 #FFFFFF, stop:1 #E8E8E8);
                    border-color: #9E9E9E;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 #E0E0E0, stop:1 #D0D0D0);
                    padding-top: 2px;
                }
            """
        )
        self.hbox = QHBoxLayout()
        label = QLabel(f"{name.replace('_', ' ').title()}:", parent=self)
        self.hbox.addWidget(label)
        self.hbox.addWidget(self.color_btn)
        self.setLayout(self.hbox)

    def update_button_color(self, color: QColor):
        size = 18
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)

        rect = QRectF(0, 0, size, size)
        radius = 4.0
        painter.drawRoundedRect(rect, radius, radius)

        painter.end()

        self.color_btn.setIcon(QIcon(pixmap))
        self.color_btn.setIconSize(pixmap.size())


    def open_color_picker(self):
        """
        Opens a dialog for choosing the color using the static method, updates the value and emits the signal.
        """
        if self.in_extra:
            current_color = QColor(self.extra_attributes[self.name])
        else:
            current_color = QColor(getattr(self.graphic_options, self.name))

        new_color = QColorDialog.getColor(current_color, self, "Choose a Color")

        if new_color.isValid():
            new_color_name = new_color.name()
            self.update_button_color(new_color)
            if self.in_extra:
                self.extra_attributes[self.name] = new_color_name
            else:
                setattr(self.graphic_options, self.name, new_color_name)
            self.update_status.emit({self.name: new_color_name})