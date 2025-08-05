from hypergraphx.viz.interactive_view.graphic_options.base_graphic_options import BaseGraphicOptionsWidget


def get_base_options(weighted=False):
    """Returns the graphical options common to nearly all layouts."""
    options = [
        "node_size", "node_shape", "node_color", "node_facecolor",
        "edge_size", "edge_color"
    ]
    if weighted:
        options.append("weight_size")
    return options

def get_label_options():
    """Returns the common options for labels."""
    return ["label_size", "label_color"]

def get_edge_node_options():
    """Returns common options for hyperedge nodes."""
    return ["edge_shape", "edge_node_color"]

def get_PAOH_options(weighted=False, hypergraph_type: str = "normal"):
    """PAOH Layout Options."""
    options = get_base_options(weighted)
    if hypergraph_type == "temporal":
        options.extend(["time_font_size", "time_separation_line_color", "time_separation_line_size"])
    if hypergraph_type == "directed":
        options.extend(["in_edge_color", "out_edge_color"])
    options.extend(["axis_labels_size", "nodes_name_size"])

    return options

def get_Clique_options():
    """Clique Layout Options."""
    options = get_base_options()
    options.extend(get_label_options())
    return options

def get_Radial_options(weighted=False, hypergraph_type: str = "normal"):
    """Radial Layout Options."""
    options = get_base_options(weighted)
    options.extend(get_label_options())
    options.extend(get_edge_node_options())
    if hypergraph_type == "directed":
        options.extend(["in_edge_color", "out_edge_color"])
    options.extend(["radius_scale_factor", "font_spacing_factor"])
    return options

def get_ExtraNode_options(weighted=False):
    """Extra-Node Layout Options."""
    options = get_base_options(weighted)
    options.extend(get_label_options())
    options.extend(get_edge_node_options())
    return options

def get_Bipartite_options(weighted=False):
    """Bipartite Layout Options (equal to Extra-Node)."""
    return get_ExtraNode_options(weighted)

def get_Sets_options(weighted=False):
    """Sets Layout Options."""
    options = get_base_options(weighted)
    options.extend(get_label_options())
    options.extend([
        "hyperedge_alpha", "rounding_radius_factor",
        "polygon_expansion_factor"
    ])
    return options

class PAOHGraphicOptionsWidget(BaseGraphicOptionsWidget):
    def _setup_widgets(self):
        options = get_PAOH_options(self.weighted, self.hypergraph_type)
        self._create_and_add_widgets(options)

class RadialGraphicOptionsWidget(BaseGraphicOptionsWidget):
    def _setup_widgets(self):
        options = get_Radial_options(self.weighted, self.hypergraph_type)
        self._create_and_add_widgets(options)

class CliqueGraphicOptionsWidget(BaseGraphicOptionsWidget):
    def _setup_widgets(self):
        options = get_Clique_options()
        self._create_and_add_widgets(options)

class ExtraNodeGraphicOptionsWidget(BaseGraphicOptionsWidget):
    def _setup_widgets(self):
        options = get_ExtraNode_options(self.weighted)
        self._create_and_add_widgets(options)

class BipartiteGraphicOptionsWidget(BaseGraphicOptionsWidget):
    def _setup_widgets(self):
        options = get_Bipartite_options(self.weighted)
        self._create_and_add_widgets(options)

class SetsGraphicOptionsWidget(BaseGraphicOptionsWidget):
    def _setup_widgets(self):
        options = get_Sets_options(self.weighted)
        self._create_and_add_widgets(options)

GRAPHIC_WIDGET_MAP = {
    "PAOH": PAOHGraphicOptionsWidget,
    "Radial": RadialGraphicOptionsWidget,
    "Clique": CliqueGraphicOptionsWidget,
    "Extra-Node": ExtraNodeGraphicOptionsWidget,
    "Bipartite": BipartiteGraphicOptionsWidget,
    "Sets": SetsGraphicOptionsWidget,
}
def create_graphic_options_widget(layout_type: str, graphic_options, extra_attributes=None, weighted=False, hypergraph_type: str = "normal", parent=None):
    """
    Factory function per creare il widget di opzioni grafiche corretto.

    Args:
        layout_type (str): Il tipo di layout (es. "paoh", "radial").
        graphic_options (GraphicOptions): L'oggetto con le opzioni grafiche.
        extra_attributes (dict, optional): Attributi extra.
        parent (QWidget, optional): Il widget genitore.

    Returns:
        BaseGraphicOptionsWidget or None: L'istanza del widget creato o None se il tipo non è valido.
    """
    widget_class = GRAPHIC_WIDGET_MAP.get(layout_type)
    if widget_class:
        return widget_class(graphic_options, extra_attributes, weighted, hypergraph_type, parent)

    print(f"Alert: No Option Widget found for type '{layout_type}'")
    return None