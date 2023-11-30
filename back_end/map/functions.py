import json
import numpy as np

# Get path from start to destination
def find_path(start, destination, grid_roads):
    '''
    A* algorithm: it returns the path from start to destination both included. 0 represents a road and 1 represents a wall
    input: start, destination, grid_roads
    output: A list of coordinates from start to destination both included
    '''
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    def heuristic(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        return abs(x1 - x2) + abs(y1 - y2)

    def astar(grid_roads, start, end):
        stack = [start]
        origin = {}
        g_score = {(x, y): float('inf') for x in range(len(grid_roads)) for y in range(len(grid_roads[0]))}
        g_score[start] = 0
        f_score = {(x, y): float('inf') for x in range(len(grid_roads)) for y in range(len(grid_roads[0]))}
        f_score[start] = heuristic(start, end)

        while stack:
            current = min(stack, key=lambda p: f_score[p])

            if current == end:
                path = []
                while current in origin:
                    path.append(current)
                    current = origin[current]
                return path[::-1]  # Reversed to get the correct path order

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

    return astar(grid_roads, start, destination)

# Get the events nearby the agent
def nearby(map, agent, radius=5):
    '''
    Get the events nearby the agent in a block of radius
    input: map, agent, radius
    output: a list of events
    '''
    x = agent.position[0]
    y = agent.position[1]
    agent_building = map.case_details[x, y]["building"]
    events = []

    for i in range(x - radius, x + radius + 1):
        for j in range(y - radius, y + radius + 1):
            if 0 <= i < map.length and 0 <= j < map.width:
                if map.case_details[i, j]["building"] == agent_building:
                        for event in map.case_details[i, j]["events"]:
                            events.append([event, (i, j)])
    return events

# Get the localisation of the agent
def get_localisation(map, agent):
    '''
    Get the localisation of the agent
    input: map, agent
    output: localisation in the form of building:hall:object
    '''
    x = agent.position[0]
    y = agent.position[1]
    localisation = map.case_details[x, y]["building"]
    if map.case_details[x, y]["hall"] != None:
        localisation += ":" + map.case_details[x, y]["hall"]
        if map.case_details[x, y]["object"] != None:
            localisation += ":" + map.case_details[x, y]["object"]
    return localisation

# Prepare on process the map
def prepare_map(map_file="back_end/map/map.json"):
    '''
    Prepare the map: Generate the case_details, map_dict, coordinates and grid_roads
    input: map_file
    output:
        case_details: a 2D array of dictionaries, each dictionary contains the details of a case
        map_dict: a dictionary of dictionaries, each dictionary contains the objects in a hall
            example: {"building":{"hall_1":{"object_1","object_2"},"hall_2":{"object_3"}}}
        coordinates: a dictionary of sets, each set contains the coordinates of a place
        grid_roads: a 2D array of integers, each integer represents 1 if the case is a road and 0 otherwise
    '''
    
    with open(map_file) as json_file:
        data = json.load(json_file)
        json_file.close()

    height, width, tilewidth = data["height"], data["width"], data["tilewidth"]

    # initialize the details of each case
    case_details = np.array([[{"building":None,"events":set(),"agents":set(),"hall":None,"object":None} for i in range(width)] for j in range (height)],dtype=dict)
    
    # map to dict : building -> hall -> object
    # example: {"building":{"hall_1":{"object_1","object_2"},"hall_2":{"object_3"}}}
    map_dict = dict()
    
    layers = data["layers"]
    
    # get the grid_roads
    grid_roads = layers[0]["data"]
    
    # convert pixels to cases
    def get_cases(x, y, width, height): 
        xmin=int(x/tilewidth)
        ymin=int(y/tilewidth)
        xmax=int((x+width)/tilewidth)
        ymax=int((y+height)/tilewidth)
        cases = set()
        for i in range(xmin,xmax+1):
            for j in range(ymin,ymax+1):
                cases.add((j,i))
        return cases
    
    # update the case details with the places and objects from the json file 
    for layer in layers:
        layer_name = layer["name"]
        if layer_name in ["places","objets with reactions"]:
            places = layer["objects"]
            for place in places:
                x=place["x"]
                y=place["y"]
                width_=place["width"]
                height_=place["height"]
                name = place["name"]
                cases = get_cases(x, y, width_, height_)
                if layer_name == "places":
                    for case in cases:
                        case_details[case[0],case[1]]["building"]= name
                        case_details[case[0],case[1]]["hall"]= name
                elif layer_name == "objets with reactions":
                    for case in cases:
                        case_details[case[0],case[1]]["object"] = name

    # update the building dict
    for i in range(height):
        for j in range(width):
            building = case_details[i,j]["building"]
            hall = case_details[i,j]["hall"]
            object = case_details[i,j]["object"]
            if building is not None:
                if building not in map_dict.keys():
                    map_dict[building] = dict()
                if hall not in map_dict[building].keys():
                    map_dict[building][hall] = set()
                if object is not None:
                    map_dict[building][hall].add(object)

    # Coordinates of each place
    coordinates = dict()
    for i in range(width):
        for j in range(height):
            building = case_details[i,j]["building"]
            hall = case_details[i,j]["hall"]
            object = case_details[i,j]["object"]
            if building != None:
                if building not in coordinates:
                    coordinates[building] = {(i,j)}
                else :
                    coordinates[building].add((i,j))
                if hall != None:
                    if building+":"+hall not in coordinates:
                        coordinates[building+":"+hall] = {(i,j)}
                    else :
                        coordinates[building+":"+hall].add((i,j))
                    if object != None:
                        if building+":"+hall+":"+object not in coordinates:
                            coordinates[building+":"+hall+":"+object] = {(i,j)}
                        else :
                            coordinates[building+":"+hall+":"+object].add((i,j))
    
    return case_details, map_dict, coordinates, grid_roads

case_details, map_dict, coordinates, grid_roads = prepare_map()
'''
for i in range(20):
    for j in range(20):
        print(case_details[i,j])
'''