import random

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton


class RandomSeedButton(QPushButton):
    """
    A QPushButton that generates a random seed and emits it via a signal.

    This class defines a custom QPushButton that, when clicked, generates a random integer
    to be used as a seed and emits it using a PyQt signal. The emitted signal transmits a
    dictionary containing the generated seed.

    Attributes
    ----------
    update_status : pyqtSignal
        A signal that emits a dictionary containing the generated seed.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget of this button. Defaults to None.
    """
    update_status = pyqtSignal(dict)

    def __init__(self, parent=None):
        # Call the QPushButton constructor
        super().__init__("Random Seed", parent)
        # Connect the button's built-in clicked signal to our handler
        self.clicked.connect(self.on_button_clicked)
        # Initialize the seed when the button is created
        self.seed = random.randint(0, 100000)

    def on_button_clicked(self):
        """Slot that handles the button click."""
        self.seed = random.randint(0, 100000)
        self.update_status.emit({"seed": self.seed})

    def get_seed(self):
        """Returns the current random seed."""
        return self.seed
