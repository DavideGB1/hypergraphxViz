from PyQt5.QtWidgets import QLayout

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
    string = string.removeprefix("(")
    string = string.removesuffix(")")
    string = string.replace("'","")
    string = string.replace(", ",",")
    res = string.split(",")
    vals = []
    for val in res:
        try:
            vals.append(str_to_int_or_float(val))
        except ValueError:
            pass

    return tuple(vals)

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