import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import mpld3
import streamlit as st
import streamlit.components.v1 as components
from collections import defaultdict
class IMPNode:
    MAX_NEIGHBORS = 4

    def __init__(self, center):
        self.center = center
        self.my_neighbors = set()

    def get_center(self):
        return self.center

    def add_neighbor(self, neighbor):
        if self == neighbor or neighbor in self.my_neighbors or not self.accept_neighbors() or not neighbor.accept_neighbors():
            return False
        self.my_neighbors.add(neighbor)
        neighbor.my_neighbors.add(self)
        return True

    def is_neighbor(self, node):
        return node in self.my_neighbors

    def accept_neighbors(self):
        return len(self.my_neighbors) < IMPNode.MAX_NEIGHBORS

class Network:
    def __init__(self, dimension):
        self.dimension = dimension
        self.nodes = set()

    def create_and_link_nodes(self, nb_nodes):
        self.nodes.clear()
        node_positions = defaultdict(bool)

        while len(self.nodes) < nb_nodes:
            x = random.randint(0, self.dimension[0])
            y = random.randint(0, self.dimension[1])
            point = (x, y)
            if not node_positions[point]:
                node = IMPNode(point)
                self.nodes.add(node)
                node_positions[point] = True

        for node1 in self.nodes:
            for node2 in self.nodes:
                if self.get_nb_jumps(node1, node2, 0, set()) == 0:
                    node1.add_neighbor(node2)

        for node1 in self.nodes:
            for node2 in self.nodes:
                if self.get_nb_jumps(node1, node2, 0, set()) > 1:
                    node1.add_neighbor(node2)

    def get_nodes(self):
        return self.nodes
        
    def draw(self, icon_path):
        G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.get_center())
            for neighbor in node.my_neighbors:
                G.add_edge(node.get_center(), neighbor.get_center())
        random_seed = random.randint(0, 9999999)
        pos = nx.spring_layout(G, seed=random_seed)

        fig, ax = plt.subplots(figsize=(7, 8))

        # Dessine d'abord le graphe et ses arêtes
        nx.draw(G, pos, with_labels=False, ax=ax, width=3.0, alpha=0.8)

        # Dessine ensuite les icônes par-dessus
        for n in pos:
            x, y = pos[n]
            img = mpimg.imread(icon_path)  # Charge l'icône
            ax.imshow(img, extent=(x-0.05, x+0.05, y-0.05, y+0.05), zorder=2)  # Ajustez la taille et la position ici
        
        # Ajustez les limites de l'axe ici si nécessaire
        ax.set_xlim([min(x for x, y in pos.values()) - 0.1, max(x for x, y in pos.values()) + 0.1])
        ax.set_ylim([min(y for x, y in pos.values()) - 0.1, max(y for x, y in pos.values()) + 0.1])

        # Vous pouvez également utiliser ax.margins() pour ajouter une marge autour du graphe
        # ax.margins(0.1)
        plt.show()
        return fig

    def get_nb_jumps(self, node1, node2, nb_jumps, checked):
        if node1.is_neighbor(node2):
            return nb_jumps + 1

        checked.add(node1)
        min_jumps = float('inf')

        for n in node1.my_neighbors:
            if n not in checked:
                current = self.get_nb_jumps(n, node2, nb_jumps + 1, checked)
                if current > 0:
                    min_jumps = min(current, min_jumps)

        return 0 if min_jumps == float('inf') else min_jumps
    
    def calculate_diameter(self):
        G = nx.Graph()
        for node in self.nodes:
            for neighbor in node.my_neighbors:
                G.add_edge(node.get_center(), neighbor.get_center())

        diameter = nx.diameter(G)
        return diameter

# Dimensions de l'espace du réseau
dimension = (500,500)

# Fonction principale de l'application Streamlit
def main():
    st.title("Générateur de graphe réseau optimisé")

    # Création du formulaire
    st.sidebar.header("Nombre de noeuds :", divider='rainbow')
    with st.sidebar.form("network_config"):
        random_nodes = st.checkbox("Cocher pour un nombre aléatoire (3-30)")
        if random_nodes:
            nb_nodes = random.randint(3, 30)
            st.write(f"Nombre de noeuds actuel (aléatoire): {nb_nodes}")
        else:
            st.divider()
            nb_nodes = st.slider("Choix du nombre de noeuds (3-30) :", 3, 30, 15)
        submit_button = st.form_submit_button(label="Générer Réseau")

    # Si le bouton est cliqué
    if submit_button:
        # Création du réseau avec le nombre de nœuds spécifié
        network = Network(dimension)
        network.create_and_link_nodes(nb_nodes)

        # Calcul du diamètre
        diameter = network.calculate_diameter()

        # Affichage du graphique et du diamètre
        st.header("Représentation graphique du réseau :")
        st.caption(f'Avec :blue[{nb_nodes}] noeuds réseau, ayant chacun maximum :blue[{IMPNode.MAX_NEIGHBORS}] liaisons')
        fig = network.draw('Router_symbol.png')  # Obtient le graphique Matplotlib
        fig_html = mpld3.fig_to_html(fig)  # Convertit le graphique en HTML interactif
        components.html(fig_html, height=810 )

        st.info(f"Le diamètre de ce réseau est: {diameter}",icon='ℹ️')

if __name__ == "__main__":
    main()
