import time
import numpy as np
from back_end.useful_functions import get_duration

class Map:
    def __init__(self, width = 10, length = 10, buildings=dict()):
        self.width = width
        self.length = length
        self.case_details = np.array([[{"events": set(), "agents": set(), "building": None, "halls": None, "objects": None} for i in range(10)] for j in range (10)], dtype=dict)
        self.grid_roads = np.array([[0 for i in range(10)] for j in range(10)])
        self.buildings = buildings

        # Coordinates of each place
        self.coordinates = dict()
        for i in range(self.width):
            for j in range(self.length):
                building = self.case_details[i,j]["building"]
                hall = self.case_details[i,j]["halls"]
                object = self.case_details[i,j]["objects"]
                if building != None:
                    if building not in self.coordinates:
                        self.coordinates[building] = {(i,j)}
                    else :
                        self.coordinates[building].add((i,j))
                    if hall != None:
                        if building+":"+hall not in self.coordinates:
                            self.coordinates[building+":"+hall] = {(i,j)}
                        else :
                            self.coordinates[building+":"+hall].add((i,j))
                        if object != None:
                            if building+":"+hall+":"+object not in self.coordinates:
                                self.coordinates[building+":"+hall+":"+object] = {(i,j)}
                            else :
                                self.coordinates[building+":"+hall+":"+object].add((i,j))
    
    # Get case details
    def get_case_details(self, x, y):
        return self.case_details[x][y]
    
    # Get the localisation of the agent
    def get_localisation(self, agent):
        x = agent.position[0]
        y = agent.position[1]
        localisation = self.case_details[x, y]["building"]
        if self.case_details[x, y]["halls"] != None:
            localisation += ":" + self.case_details[x, y]["halls"]
        return localisation
    
    # Get the coordinates of each place
    def get_coordinates(self, key):
        return self.coordinates[key]
    
    # Get the path from start to destination
    def find_path(self, start, destination):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        def heuristic(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return abs(x1 - x2) + abs(y1 - y2)

        def astar(grid_roads, start, end):
            stack = [start]
            origin = {}
            g_score = {point: float('inf') for row in grid_roads for point in row}
            g_score[start] = 0
            f_score = {point: float('inf') for row in grid_roads for point in row}
            f_score[start] = heuristic(start, end)

            while stack:
                current = min(stack, key=lambda p: f_score[p])

                if current == end:
                    path = []
                    while current in origin:
                        path.append(current)
                        current = origin[current]
                    return path

                stack.remove(current)

                for direction in directions:
                    x, y = current
                    neighbor = (x + direction[0], y + direction[1])

                    if (
                        0 <= neighbor[0] < len(grid_roads) and
                        0 <= neighbor[1] < len(grid_roads[0]) and
                        grid_roads[neighbor[0]][neighbor[1]] == 0
                    ):
                        tentative_g_score = g_score[current] + 1

                        if tentative_g_score < g_score.get(neighbor, float('inf')):
                            origin[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)

                            if neighbor not in stack:
                                stack.append(neighbor)

            return None

        return astar(self.grid_roads, start, destination)

    # Get the events nearby the agent
    def nearby(self, agent):
        x = agent.position[0]
        y = agent.position[1]
        agent_building = self.case_details[x, y]["building"]
        events = []
        radius = 5

        for i in range(x - radius, x + radius + 1):
            for j in range(y - radius, y + radius + 1):
                if 0 <= i < self.length and 0 <= j < self.width:
                    if self.case_details[i, j]["building"] == agent_building:
                            for event in self.case_details[i, j]["events"]:
                                events.append([event, (i, j)])
        return events
    
    # Add event to the map
    def add_event(self, event, position):
        x = position[0]
        y = position[1]
        self.case_details[x,y]["events"].add(event)
    
    # Remove event from the map
    def remove_event(self, event, position):
        x = position[0]
        y = position[1]
        if event in self.case_details[x,y]["events"]:
            self.case_details[x,y]["events"].remove(event)

    # Commend agent to perceive the environment
    def activate_perceive(self, position):
        x = position[0]
        y = position[1]
        for i in range(x-5, x+6):
            if 0 <= i < self.length:
                for j in range(y-5, y+6):
                    if 0 <= j < self.width:
                        for agent in self.case_details[i,j]["agents"]:
                            agent.perceive()

class Environment:
    def __init__(self, start_env_time=time.time(), min_equivalent_seconds=1):
        self.map = Map()
        self.start_env_time = start_env_time
        self.min_equivalent_seconds = min_equivalent_seconds
        self.queue_of_configurations = []
        
    def get_time(self):
        return time.time() - self.start_env_time
    
    def get_min_equivalent_seconds(self):
        return self.min_equivalent_seconds
    
    def get_duration_equivalent(self, start, end):
        return get_duration(start, end) * self.min_equivalent_seconds
    
    def add_configuration_to_the_queue(self, configuration):
        self.queue_of_configurations.append(configuration)
    
    def pop_configuration_from_the_queue(self):
        return self.queue_of_configurations.pop(0)