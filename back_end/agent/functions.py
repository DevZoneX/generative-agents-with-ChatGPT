import json

# Get identity information from memory to create initial plan
def get_info(agent):
    '''
    input: agent
    output: a dictionnary containing identity info i.e name, age, personality, life style, profile. 
    '''
    try:
        with open(agent.file_path + 'identity.json', 'r') as file:
            existing_data = json.load(file)
            file.close()
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    return existing_data[agent.id]

# Add event to the sensory memory
def add_event_to_sensory_memory(agent, event, pos):
    n = len(agent.sensory_memory)
    distance = abs(agent.position[0] - pos[0]) + abs(agent.position[1] - pos[1])
    if event not in agent.seen:
        if n == 0:
            agent.sensory_memory.append([event, distance])
        else:
            for i in range(n):
                if distance <= agent.sensory_memory[i][1]:
                    agent.sensory_memory.insert(i,[event,distance])
                    break
    agent.seen.add(event)