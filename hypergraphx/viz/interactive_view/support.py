import ast

from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtWidgets import QLayout, QSizePolicy

from hypergraphx import Hypergraph, DirectedHypergraph, TemporalHypergraph


def clear_layout(layout: QLayout):
    """
    Function to clear a QLayout
    Parameters
    ----------
    layout: QLayout
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

def str_to_dict(string: str):
    """
    Converts a colon-separated string into a dictionary where each key-value pair is split by commas.

    Parameters
    ----------
    string : str
        A string containing key-value pairs separated by colons (:) and individual pairs separated by commas (,).

    Returns
    -------
    dict
        A dictionary where keys and values are converted to integers or floats if possible.
    """
    dict = {}
    values = string.split(",")
    for pair in values:
        try:
            k, v = pair.split(":")
            k = str_to_int_or_float(k.strip())
            v = str_to_int_or_float(v.strip())
            dict[k] = v
        except ValueError:
            pass
    return dict

def str_to_tuple(string: str):
    """
    Converts a string representation of a tuple into an actual tuple of integers or floats.

    Parameters
    ----------
    string : str
        A string representing a tuple, e.g., "(1, 2.5, 'text')".

    Returns
    -------
    tuple
        A tuple containing converted integers or floats.
    """
    try:
        # Usa ast.literal_eval per valutare la stringa in modo sicuro
        result = ast.literal_eval(string)
        if not isinstance(result, tuple):
            result = (result,)
        processed_elements = []
        for item in result:
            if isinstance(item, (int, float)):
                processed_elements.append(item)
            elif isinstance(item, str):
                try:
                    processed_elements.append(float(item))
                except ValueError:
                    try:
                        processed_elements.append(int(item))
                    except ValueError:
                        processed_elements.append(item)
            else:
                processed_elements.append(item)

        return tuple(processed_elements)

    except (ValueError, SyntaxError) as e:
        print(f"Errore nella conversione della stringa in tupla: {e}")
        return ()

def str_to_int_or_float(string):
    """
    Converts a string to an integer or a float.

    Attempts to interpret the given string as an integer. If unsuccessful,
    the function will try to interpret it as a float. If neither conversion
    is possible, it raises a ValueError.

    Parameters
    ----------
    string : str
        The string to be converted into an integer or float.

    Returns
    -------
    int or float
        The converted value of the string as an integer or float.

    Raises
    ------
    ValueError
        If the string cannot be converted to either an integer or a float.
    """
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string

def numerical_hypergraph(hypergraph: Hypergraph|DirectedHypergraph|TemporalHypergraph):
    """
    Checks if any node in the given hypergraph has a numeric string representation.

    Parameters
    ----------
    hypergraph : Hypergraph or DirectedHypergraph or TemporalHypergraph
        The input hypergraph whose nodes will be checked.

    Returns
    -------
    bool
        True if at least one node in the hypergraph has a numeric string representation, otherwise False.
    """
    for node in hypergraph.get_nodes():
        if str(node).isnumeric():
            return True

    return False

def create_canvas_with_toolbar(figure):
    canvas = FigureCanvas(figure)
    canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    toolbar = NavigationToolbar(canvas)
    home_icon = QIcon("icons/home.svg")
    toolbar._actions['home'].setIcon(home_icon)
    back_icon = QIcon("icons/left.svg")
    toolbar._actions['back'].setIcon(back_icon)
    forward_icon = QIcon("icons/right.svg")
    toolbar._actions['forward'].setIcon(forward_icon)
    pan_icon = QIcon("icons/move.svg")
    toolbar._actions['pan'].setIcon(pan_icon)
    zoom_icon = QIcon("icons/zoom.svg")
    toolbar._actions['zoom'].setIcon(zoom_icon)
    configure_subplots_icon = QIcon("icons/options.svg")
    toolbar._actions['configure_subplots'].setIcon(configure_subplots_icon)
    edit_parameters_icon = QIcon("icons/settings.svg")
    toolbar._actions['edit_parameters'].setIcon(edit_parameters_icon)
    save_icon = QIcon("icons/save.svg")
    toolbar._actions['save_figure'].setIcon(save_icon)
    return canvas, toolbar

def generate_key(dictionary):
    keys_label = []
    keys = []
    idx = 1
    for edge in dictionary.keys():
        keys.append(idx)
        idx += 1
        keys_label.append(str(edge))
    return keys_label, keys