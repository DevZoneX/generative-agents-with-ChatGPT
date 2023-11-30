import json
from back_end.agent.plan import create_initial_plan, create_sub_plan
from back_end.agent.functions import get_info, add_event_to_sensory_memory
from back_end.agent.execute import execute_sub_task 

class Agent:
    def __init__(self, id, current_event = None, position=(2,2)):
        self.id = id
        self.file_path = f'back_end/memory/{id}/'
        self.name = self.get_info()['name']
        self.position = position
        self.sensory_memory = []
        self.seen = set()

        # The current event the agent is executing
        self.current_event = current_event
        
        # Possible localisations of the agent
        self.localisations = []

    # Get identity info from memory to create initial plan
    def get_info(self):
        return get_info(self)
    
    # Get the localisations where the agent can be
    def get_localisations(self):
        return self.localisations
    
    # Create initial plan and save it in memory
    def create_initial_plan(self):
        return create_initial_plan(self.get_info(), self.file_path)
    
    # Create sub plan for task_i and save it in memory
    def create_sub_plan(self, i):
        return create_sub_plan(i, self.file_path, self.get_localisations())
    
    # add event to the sensory memory
    def add_event_to_sensory_memory(self, event, pos):
        add_event_to_sensory_memory(self, event, pos)
    
    # Clear the seen set
    def clear_seen(self):
        self.seen = set()

    # Clear the sensory memory
    def clear_memory(self):
        self.sensory_memory = []

    # Execute sub task
    def execute_sub_task(self, start, end, localisation, task, environment):
        execute_sub_task(self, start, end, localisation, task, environment)
    
    # Get information about the environment
    def perceive(self):
        events = map.nearby(self)
        for event in events:
            self.add_event_to_sensory_memory(event[0],event[1])
    
    # Squeeze the relevant information from the information perceived
    def retreive(self):
        pass