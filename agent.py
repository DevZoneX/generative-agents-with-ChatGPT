import json
from back_end.plan import create_initial_plan, create_sub_plan
from back_end.execute import execute_sub_task 

class Agent:
    def __init__(self, id, localisations, position=(2,2)):
        self.id = id
        self.file_path = f'back_end/memory/{id}/'
        self.name = self.get_info()['name']
        self.position = position
        self.sensory_memory = []
        self.seen = set()
        self.localisations = localisations

    # Get identity info from memory to create initial plan
    def get_info(self):
        try:
            with open(self.file_path + 'identity.json', 'r') as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}
        print()

        return existing_data[self.id]
    
    # Get localisations
    def get_localisations(self):
        return self.localisations
    
    # Create initial plan and save it in memory
    def create_initial_plan(self):
        initial_plan = create_initial_plan(self.get_info())
        with open(self.file_path + 'plan.json', 'w') as file:
            json.dump(initial_plan, file)
        return initial_plan
    
    # Create sub plan for task_i and save it in memory
    def create_sub_plan(self, i):
        task = f"task_{i}"

        with open(self.file_path + 'plan.json', 'r') as file:
            existing_data = json.load(file)
        
        task_i = existing_data[task]
        sub_plan = create_sub_plan(start_time=task_i[0], end_time=task_i[1], localisations = str(self.get_localisations()), task=task_i[2])
        
        existing_data[task].append(sub_plan)
        with open(self.file_path + 'plan.json', 'w') as file:
            json.dump(existing_data, file)
        
        return sub_plan
    
    # add event to the sensory memory
    def add_event(self, event, pos):
        n = len(self.sensory_memory)
        distance = abs(self.position[0] - pos[0]) + abs(self.position[1] - pos[1])
        if event not in self.seen:
            if n == 0:
                self.sensory_memory.append([event, distance])
            else:
                for i in range(n):
                    if distance <= self.sensory_memory[i][1]:
                        self.sensory_memory.insert(i,[event,distance])
                        break
        self.seen.add(event)
    
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
            self.add_event(event[0],event[1])
    
    # Squeeze the relevant information from the information perceived
    def retreive(self):
        pass
    
    # Update the environment
    def update_env(self):
        pass