import networkx as nx
from back_end.useful_functions import get_completion, get_embedding, get_similarity
# import matplotlib.pyplot as plt
import json


class EpisodicMemoryGraph:
    def __init__(self):
        self.episodic_memory_graph = nx.Graph()

    # Add a node (an event) to the graph and connect it to the existing nodes
    def add_connected_node(self, node):
        # Get all nodes that are already in the graph
        nodes = list(self.episodic_memory_graph.nodes())

        # Add the new node to the graph
        self.episodic_memory_graph.add_node(node)

        # Load or create the embeddings dictionary
        file_path = 'back_end/long_term_memory/embeddings.json'
        try:
            with open(file_path, 'r') as file:
                existing_data = json.load(file)
        except:
            existing_data = {}

        # Get the embedding for the new node
        if node not in existing_data:
            embedding2 = get_embedding(node)
            existing_data[node] = embedding2.tolist()

            # Update the embeddings file with the new node
            with open(file_path, 'w') as file:
                json.dump(existing_data, file, indent=4)

        # Add edges between the new node and existing nodes
        for neighbor in nodes:
            if neighbor != node:

                # Get the embeddings of the two nodes
                embedding1 = existing_data.get(neighbor)

                # Get the similarity between the two embeddings
                if embedding1 is not None:
                    weight = get_similarity(
                        embedding1, existing_data[node][0])[0]

                    # Add an edge if the similarity is high enough
                    if weight > 0.15:
                        self.episodic_memory_graph.add_edge(
                            node, neighbor, weight=weight)

    '''def display(self):
        pos = nx.spring_layout(self.episodic_memory_graph)
        labels = {node: node for node in self.episodic_memory_graph.nodes()}

        nx.draw(self.episodic_memory_graph, pos, with_labels=True, labels=labels)
        edge_labels = nx.get_edge_attributes(self.episodic_memory_graph, "weight")
        nx.draw_networkx_edge_labels(self.episodic_memory_graph, pos, edge_labels=edge_labels)

        plt.show()'''

    def print_graph(self):
        '''
        Print the graph of the long term memory in the terminal to visualize it
        '''

        print("-- The graph of long terme memory: --")
        for edge, weight in nx.get_edge_attributes(self.episodic_memory_graph, "weight").items():
            print(f"<>{edge[0]}<----{weight}---->{edge[1]}")
        print("\n")


''' 
# Create instances of EpisodicMemory
episodic_memory_node1 = EpisodicMemory('2023', 'cafe', 'happy', 'drinking coffee')
episodic_memory_node2 = EpisodicMemory('2022', 'house', 'scary', 'watching a horror movie')
episodic_memory_node3 = EpisodicMemory('2021', 'park', 'relaxed', 'picnic in the park')
episodic_memory_node4 = EpisodicMemory('2020', 'beach', 'fun', 'building sandcastles')

# Add these instances as connected nodes
add_connected_node(episodic_memory_node1)
add_connected_node(episodic_memory_node2)
add_connected_node(episodic_memory_node3)
add_connected_node(episodic_memory_node4)


# Display the graph
pos = nx.spring_layout(episodic_memory_graph)
labels = {node: node.context for node in episodic_memory_graph.nodes()}

nx.draw(episodic_memory_graph, pos, with_labels=True, labels=labels)
edge_labels = nx.get_edge_attributes(episodic_memory_graph, "weight")
nx.draw_networkx_edge_labels(episodic_memory_graph, pos, edge_labels=edge_labels)

plt.show()
'''
