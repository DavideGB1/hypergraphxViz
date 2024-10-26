class Options():
    def __init__(self):
        self.lineEditColor_dict = dict()
        self.lineEdit_dict = dict()
        self.combobox_dict = dict()
        self.spinbox_dict = dict()
        self.set_default_radial()
    def clear(self):
        self.lineEditColor_dict = dict()
        self.lineEdit_dict = dict()
        self.combobox_dict = dict()
        self.spinbox_dict = dict()
    def set_default_PAOH(self):
        self.clear()
        self.lineEditColor_dict["Node Color"] = "#FFFFFF"
        self.lineEditColor_dict["Edge Color"] = "#000000"
        self.lineEditColor_dict["Marker Edge Color"] = "#000000"
        self.lineEditColor_dict["Time Separation Line Color"] = "#000000"
        self.combobox_dict["Node Shape"] = "o"
        self.spinbox_dict["Node Size"] = 10
        self.spinbox_dict["Edge Width"] = 2
        self.spinbox_dict["Marker Edge Width"] = 3
        self.spinbox_dict["Time Font Size"] = 18
        self.spinbox_dict["Time Separation Line Width"] = 4
    def set_default_radial(self):
        self.clear()
        self.lineEditColor_dict["Node Color"] = "#0000FF"
        self.lineEditColor_dict["Edge Color"] = "#000000"
        self.lineEditColor_dict["Marker Color"] = "#FF0000"
        self.combobox_dict["Node Shape"] = "o"
        self.spinbox_dict["Node Size"] = 5
        self.spinbox_dict["Marker Size"] = 5
        self.spinbox_dict["Font Size"] = 12
    def set_default_clique_expasion_bipartite(self):
        self.clear()
        self.lineEditColor_dict["Node Color"] = "#1f78b4"
        self.lineEditColor_dict["Edge Color"] = "#000000"
        self.combobox_dict["Node Shape"] = "o"
        self.spinbox_dict["Node Size"] = 300
        self.spinbox_dict["Edge Width"] = 2
    def set_default_extra_node(self):
        self.clear()
        self.lineEditColor_dict["Node Color"] = "#1f78b4"
        self.lineEditColor_dict["Edge Color"] = "#000000"
        self.lineEditColor_dict["Edge Node Color"] = "#8a0303"
        self.combobox_dict["Node Shape"] = "o"
        self.combobox_dict["Edge Node Shape"] = "p"
        self.spinbox_dict["Node Size"] = 300
        self.spinbox_dict["Edge Width"] = 2
    def set_default_metroset(self):
        self.clear()
        self.lineEditColor_dict["Node Color"] = "#1f78b4"
        self.combobox_dict["Node Shape"] = "o"
        self.spinbox_dict["Node Size"] = 300
        self.spinbox_dict["Edge Lenght"] = 300
    def get_node_color(self):
        try:
            return self.lineEditColor_dict["Node Color"]
        except KeyError:
            return None
    def get_edge_color(self):
        try:
            return self.lineEditColor_dict["Edge Color"]
        except KeyError:
            return None
    def get_marker_edge_color(self):
        try:
            return self.lineEditColor_dict["Marker Edge Color"]
        except KeyError:
            return None
    def get_time_separation_line_color(self):
        try:
            return self.lineEditColor_dict["Time Separation Line Color"]
        except KeyError:
            return None
    def get_edge_node_color(self):
        try:
            return self.lineEditColor_dict["Edge Node Color"]
        except KeyError:
            return None
    def get_marker_color(self):
        try:
            return self.lineEditColor_dict["Marker Color"]
        except KeyError:
            return None
    def get_node_shape(self):
        try:
            return self.combobox_dict["Node Shape"]
        except KeyError:
            return None
    def get_edge_node_shape(self):
        try:
            return self.combobox_dict["Edge Node Shape"]
        except KeyError:
            return None
    def get_edge_width(self):
        try:
            return self.spinbox_dict["Edge Width"]
        except KeyError:
            return None
    def get_marker_edge_width(self):
        try:
            return self.spinbox_dict["Marker Edge  Width"]
        except KeyError:
            return None
    def get_time_font_size(self):
        try:
            return self.spinbox_dict["Time Font Size"]
        except KeyError:
            return None
    def get_time_separation_line_width(self):
        try:
            return self.spinbox_dict["Time Separation Line Width"]
        except KeyError:
            return None
    def get_marker_size(self):
        try:
            return self.spinbox_dict["Marker Size"]
        except KeyError:
            return None
    def get_font_size(self):
        try:
            return self.spinbox_dict["Font Size"]
        except KeyError:
            return None
    def get_edge_lenght(self):
        try:
            return self.spinbox_dict["Edge Lenght"]
        except KeyError:
            return None
    def get_node_size(self):
        try:
            return self.spinbox_dict["Node Size"]
        except KeyError:
            return None