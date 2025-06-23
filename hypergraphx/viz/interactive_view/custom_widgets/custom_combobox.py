from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QWidget

from hypergraphx.viz.interactive_view.graphic_options.graphic_enum import GraphicOptionsName


class ComboBoxCustomWindget(QWidget):
    """
        Class ComboBoxCustomWindget

        A custom PyQt widget that combines a QLabel and a QComboBox. The widget is used
        to display a label and a combo box with selectable options. Upon changes in the
        combo box selection, the widget emits a signal with the updated status.

        Attributes
        ----------
        update_status : pyqtSignal
            Signal emitted when the combo box selection is changed. Emits a dictionary
            containing the updated key-value pair.

        Parameters
        ----------
        name : str
            The unique identifier or key associated with the custom widget.
        value : str
            The initial selected value in the combo box.
        translation_dictionary : dict
            A dictionary containing the mapping between keys and their translated
            strings to be displayed in the combo box.

        Methods
        -------
        comboBox_selection()
            Captures the current selected text from the combo box, determines its
            corresponding key in the given translation dictionary, and emits the
            `update_status` signal with the updated key-value pair.
    """
    update_status = pyqtSignal(dict)
    def __init__(self,name, value, translation_dictionary, parent = None):
        super(ComboBoxCustomWindget, self).__init__(parent)

        self.name = name
        self.translation_dictionary = translation_dictionary
        self.key_list = list(translation_dictionary.keys())
        self.val_list = list(translation_dictionary.values())

        self.hbox = QHBoxLayout()
        self.label = QLabel(GraphicOptionsName[name].value, parent=self)
        self.hbox.addWidget(self.label)

        self.combobox = QComboBox(parent=self)
        self.combobox.addItems(translation_dictionary.values())
        self.combobox.setCurrentText(translation_dictionary[value])
        self.combobox.currentTextChanged.connect(self.on_selection_changed)

        self.hbox.addWidget(self.combobox)
        self.setLayout(self.hbox)

    def on_selection_changed(self, current_text):
        """This is the slot that handles the change."""
        try:
            position = self.val_list.index(current_text)
            key = self.key_list[position]
            self.update_status.emit({self.name: key})
        except ValueError:
            pass