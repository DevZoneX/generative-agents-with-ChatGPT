import networkx as nx
from useful_functions import get_similarity
import matplotlib.pyplot as plt
import json
from epis_mem_slice import EpisodicMemorySlice
from API_gabriel import get_completion

class EpisodicMemoryGraph:
    def __init__(self):
        self.episodic_memory_graph = nx.Graph()

    # Add nodes
    def add_connected_node(self, node):
        # get all nodes
        nodes = list(self.episodic_memory_graph.nodes())
        
        #add node
        self.episodic_memory_graph.add_node(node)
        
        # add edges
        for neighbor in nodes:
            txt1 = node.context
            txt2 = neighbor.context
            weight = get_similarity(txt1, txt2)
            if weight > 0.1:
                self.episodic_memory_graph.add_edge(node, neighbor, weight=weight)
    
    def get_nodes(self):
        return self.episodic_memory_graph.nodes()
    
    def display(self):
        pos = nx.spring_layout(self.episodic_memory_graph)
        labels = {node: node.context for node in self.episodic_memory_graph.nodes()}

        nx.draw(self.episodic_memory_graph, pos, with_labels=True, labels=labels)
        edge_labels = nx.get_edge_attributes(self.episodic_memory_graph, "weight")
        nx.draw_networkx_edge_labels(self.episodic_memory_graph, pos, edge_labels=edge_labels)

        plt.show()
    
    def think(self,node,agent): #-take all the events linked to it in the episodic memory -add the personality and emotions of the agent -use the fonction get_completion with the prompt prompt : -What 5 high-level insights can you infer from the above statements? adding the fact that the response must be a JSON file : a key in form of "Node_ID" and (localisation thinking, start time thought, end time = None, a sentence that describes the thought) as the corresponding value  -adding the thought to the graph, linked to events used to generate it (maybe not be all of them)
        presentation = agent.info+agent.emotion+agent.personality
        neighbors = list(self.episodic_memory_graph.neighbors(node))
        contexts_of_neighbors = [neighbor.context for neighbor in neighbors]
        prompt_thought= f"""You are an individual with a profile defined by the information in the text delimited by double backticks ''{presentation}''. What 5 high-level insights can you infer from the following statements delimited by triple backticks ? '''{contexts_of_neighbors}'''. Tasks should be represented as a JSON file with a key in form of "Thought_numberOfThought" and the list containing: the sentence that describes the thought. The response must be only the JSON text."""
        message_thought = [ {'role':'system',
        'content': prompt_thought},
        ]
        thoughts= get_completion(message_thought, model="gpt-3.5-turbo", max_tokens=500, temperature=0).get('content', '')
        thoughts = json.loads(thoughts)
        for thought in thoughts:
            print(thought)
            self.add_connected_node(EpisodicMemorySlice(timsestep=node.timestep,context=thought)) #could be upgraded ()
        return thoughts
    
    
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