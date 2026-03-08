from matplotlib import pyplot as plt


class Node:
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.up_left = None
        self.up_right = None
        self.down_left = None
        self.down_right = None

    def __repr__(self):
        return f"Node({self.value})"


class DynamicDoubleLinkedMatrix:
    def __init__(self):
        self.nodes = {}
        self.origin = None
    def get_node_position(self, node_value):
        for (pos, node) in self.nodes.items():
            if node.value == node_value:
                return pos
        return None
    def get_node(self, r, c):
        """Restituisce il nodo alle coordinate (r, c) se esiste."""
        return self.nodes.get((r, c))
    def has_node(self, r, c):
        """Restituisce il nodo alle coordinate (r, c) se esiste."""
        return self.nodes.get((r, c)) is not None

    def insert_node(self, r, c, value):
        """
        Crea e inserisce un nuovo nodo alle coordinate (r, c).
        Gestisce i collegamenti con i nodi vicini esistenti.
        """
        if (r, c) in self.nodes:
            # Il nodo esiste già, aggiorniamo il suo valore
            self.nodes[(r, c)].value = value
            return self.nodes[(r, c)]

        new_node = Node(value, r, c)
        self.nodes[(r, c)] = new_node

        if self.origin is None:
            self.origin = new_node

        # Up
        neighbor = self.get_node(r - 1, c)
        if neighbor:
            new_node.up = neighbor
            neighbor.down = new_node

        # Down
        neighbor = self.get_node(r + 1, c)
        if neighbor:
            new_node.down = neighbor
            neighbor.up = new_node

        # Left
        neighbor = self.get_node(r, c - 1)
        if neighbor:
            new_node.left = neighbor
            neighbor.right = new_node

        # Right
        neighbor = self.get_node(r, c + 1)
        if neighbor:
            new_node.right = neighbor
            neighbor.left = new_node

        # Up-Left
        neighbor = self.get_node(r - 1, c - 1)
        if neighbor:
            new_node.up_left = neighbor
            neighbor.down_right = new_node

        # Up-Right
        neighbor = self.get_node(r - 1, c + 1)
        if neighbor:
            new_node.up_right = neighbor
            neighbor.down_left = new_node

        # Down-Left
        neighbor = self.get_node(r + 1, c - 1)
        if neighbor:
            new_node.down_left = neighbor
            neighbor.up_right = new_node

        # Down-Right
        neighbor = self.get_node(r + 1, c + 1)
        if neighbor:
            new_node.down_right = neighbor
            neighbor.up_left = new_node

        return new_node

    def print_connections(self, r, c):
        """Stampa le connessioni per un nodo specifico."""
        node = self.get_node(r, c)
        if not node:
            print(f"Node at ({r}, {c}) does not exist.")
            return

        print(f"Connections for Node at ({r}, {c}) with value {node.value}:")
        print(f"  Up: {node.up.value if node.up else None}")
        print(f"  Down: {node.down.value if node.down else None}")
        print(f"  Left: {node.left.value if node.left else None}")
        print(f"  Right: {node.right.value if node.right else None}")
        print(f"  Up-Left: {node.up_left.value if node.up_left else None}")
        print(f"  Up-Right: {node.up_right.value if node.up_right else None}")
        print(f"  Down-Left: {node.down_left.value if node.down_left else None}")
        print(f"  Down-Right: {node.down_right.value if node.down_right else None}")

    def draw_matrix(self, ax):
        """Disegna la matrice usando matplotlib."""
        if not self.nodes:
            print("The matrix is empty.")
            return

        # Disegna i nodi e i loro valori
        for (r, c), node in self.nodes.items():
            ax.scatter(c, r, s=200, c='lightblue', zorder=2)  # zorder per assicurarsi che i punti siano sopra le linee
            ax.text(c, r, str(node.value), ha='center', va='center', fontsize=12, zorder=3)

        # Configura il grafico
        ax.set_title("Double Linked Matrix Visualization")
        ax.set_xlabel("Colonna")
        ax.set_ylabel("Riga")
        ax.grid(True)
        ax.set_aspect('equal', adjustable='box')