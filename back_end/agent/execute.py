from time import sleep
from back_end.useful_functions import get_completion

# Get the direction from position1 to position2
def direction(position1, position2):
    if position1[0] == position2[0]:
        if position1[1] == position2[1] + 1:
            return "O"
        else:
            return "E"
    elif position1[1] == position2[1]:
        if position1[0] == position2[0]+1:
            return "S"
        else:
            return "N"
    else:
        return None

# Choose a place from provided places to performe the task
def get_place(task, places):
    file = open("prompts/get_place.txt", "r")
    prompt = file.read()
    file.close()
    prompt.replace("#places#", places).replace("#task#", task)
    message = [
        {"role": "user", "content": prompt}
    ]
    return get_completion(message)

# move the agent by one step in the direction
def move(agent, direction, environment):
    map = environment.map
    
    event = agent.name + " is walking"
    map.remove_event(event, agent.position)
    map.case_details[agent.position[0], agent.position[1]]["agents"].remove(agent)
    
    if direction == "N":
        agent.position = (agent.position[0]+1, agent.position[1])
    elif direction == "S":
        agent.position = (agent.position[0]-1, agent.position[1])
    elif direction == "E":
        agent.position = (agent.position[0], agent.position[1]+1)
    else:
        agent.position = (agent.position[0],agent.position[1]-1)
    
    map.case_details[agent.position[0], agent.position[1]]["agents"].add(agent)
    map.add_event(event, agent.position)
    
    environment.add_configuration_to_the_queue([event, direction])

    #map.activate_perceive(agent.position)

# Move the agent from its current position to the destination            
def move_agent_to(agent, destination, environment, step=1):
    
    path = map.find_path(agent.position, destination)
    
    while len(path) > 0:
        agent_direction = direction(agent.position, path.pop())
        move(agent, agent_direction, environment)

# Execute the task in the building:hall
def execute_sub_task(agent, start, end, destination_localisation, task, environment):
    
    map = environment.map
    current_localisation = map.get_localisation(agent)
    
    if current_localisation == destination_localisation:
        map.remove_event(agent.current_event, agent.position)
        map.add_event([task, start, end], agent.position)
        environment.add_configuration_to_the_queue([task, start, end, 'STAY'])
        
    else:
        destinations = map.get_coordinates(destination_localisation)
        
        for x, y in destinations:
            if map.grid_roads[x, y] != 0:
                x1 = x
                y1 = y
                break
        
        move_agent_to(agent, (x1, y1), environment)
        
        agent.add_event([task, start, end], (x1, y1))
        event = agent.name + " is walking"
        
        map.remove_event(event, agent.position)
        #map.activate_perceive((x1,y1))
