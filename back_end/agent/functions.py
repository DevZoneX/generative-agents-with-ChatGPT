import json
from back_end.useful_functions import get_completion, retrieve_episodic
import time


def search(agent_name, lock):
    '''
    return the name of the agent that has seen given agent_name
    '''
    lock.acquire()
    try :
        with open('back_end/memory/agent_detected.json', 'r') as file:
            info = json.load(file)
            file.close()
    finally:
        lock.release()
    for name in info:
        if agent_name in info[name]:
            return name
    return None


def calculate_direction(position1, position2):
    '''
    INPUT:  

    position1
    position2

    OUTPUT: 

    direction: "DOWN" / "UP" / "RIGHT" / "LEFT"
    '''
    if position1[0] == position2[0]:
        if position1[1] == position2[1] + 1:
            return "LEFT"
        else:
            return "RIGHT"
    elif position1[1] == position2[1]:
        if position1[0] == position2[0]+1:
            return "UP"
        else:
            return "DOWN"
    else:
        return None


def hear_discussion(agent, agent_asking_me, environment, lock):
    lock.acquire()
    try:
        with open('back_end/memory/discussion_state.json', 'r') as file:
            info = json.load(file)
            file.close()
    finally:
        lock.release()

    state = info[agent_asking_me]

    # Time to wait
    ref_time_to_wait = time.time()
    if state[0] == "WAITING":
        while True:
            lock.acquire()
            try:
                with open('back_end/memory/discussion_state.json', 'r') as file:
                    info = json.load(file)
                    file.close()
            finally:
                lock.release()

            state = info[agent_asking_me]
            if state[0] != "WAITING" or state[0] == "Ignore":
                break
            time.sleep(0.3)
            
        time_to_wait = time.time() - ref_time_to_wait
        environment.add_configuration_to_the_queue(agent.name, [
            f'{agent.name} is talking with {agent_asking_me}', time_to_wait*environment.front_back_ratio, 'STAY'])

    if state[0] == "TALKING":
        time_of_discussion = state[1]
        environment.add_configuration_to_the_queue(agent.name, [
            f'{agent.name} is talking with {agent_asking_me}', time_of_discussion*environment.front_back_ratio, 'STAY'])
        time.sleep(time_of_discussion)


def launch_discussion(agent, other_agents, environment, lock):
    '''
    INTPUT:  agent, orther_agents, environment
    OUTPUT: outperform the process that the agent discuss with the other agents
    '''
    # Add the agents that I have seen
    lock.acquire()
    try:
        with open('back_end/memory/agent_detected.json', 'r') as file:
            info = json.load(file)
            file.close()
    finally:
        lock.release()
    info[agent.name] = [a.name for a in other_agents]
    
    lock.acquire()
    try:
        with open('back_end/memory/agent_detected.json', 'w') as file:
            json.dump(info, file, indent=4)
            file.close()
    finally:
        lock.release()

    # Update the state of the discussion
    lock.acquire()
    try:
        with open('back_end/memory/discussion_state.json', 'r') as file:
            info = json.load(file)
            file.close()
        info[agent.name] = ["WAITING", 0]
        with open('back_end/memory/discussion_state.json', 'w') as file:
            json.dump(info, file, indent=4)
            file.close()
    finally:
        lock.release()

    # Reference time to wait
    ref_time_to_wait = time.time()

    interact_answer = interact(agent, [other_agents[0]], lock)
    print(f'interact_answer: {interact_answer}')

    if interact_answer != 'NO':

        other_agent = environment.map.agents[interact_answer]
        disc_time = agent.get_discussion(other_agent, lock)

        # Add the waiting time to the configuration queue
        time_to_wait = time.time() - ref_time_to_wait
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is talking with {interact_answer}', time_to_wait*environment.front_back_ratio, 'STAY'])

        # Update the current event of the agent
        cur_event = agent.change_current_event(f'{agent.name},talking with {interact_answer}')
        environment.map.add_event(cur_event, agent)

        lock.acquire()
        try:
            # Update the state of the discussion
            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            info[agent.name] = ["TALKING", disc_time]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()
        finally:
            lock.release()

        # Add the discussion to the configuration queue
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is talking with {interact_answer}', disc_time*environment.front_back_ratio, 'STAY'])

        # Wait for the duration of the discussion
        time.sleep(disc_time)
        
        lock.acquire()
        try:    
            # discussion is over
            with open('back_end/memory/agent_detected.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/agent_detected.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()

            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()
        finally:
            lock.release()

        '''# Add the discussion to the sensory memory of the agent
        summarize_discussion = summarize_discussion(
            discussion, agent.name, other_agent.name)
        agent.sensory_memory.add(summarize_discussion)'''

    else:
        lock.acquire()
        try:    
            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            info[agent.name] = ["Ignore", 0]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()

            # discussion is over
            with open('back_end/memory/agent_detected.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/agent_detected.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()

            with open('back_end/memory/discussion_state.json', 'r') as file:
                info = json.load(file)
                file.close()
            del info[agent.name]
            with open('back_end/memory/discussion_state.json', 'w') as file:
                json.dump(info, file, indent=4)
                file.close()
        finally:
            lock.release()

        # Add the waiting time to the configuration queue
        time_to_wait = time.time() - ref_time_to_wait
        environment.add_configuration_to_the_queue(agent.name, [
                                                   f'{agent.name} is talking with {other_agents[0]}', time_to_wait*environment.front_back_ratio, 'STAY'])


def get_current_event(agent_name, lock):
    '''
    INTPUT: agent_name
    OUTPUT: the current event of the agent
    '''
    lock.acquire()
    try:
        with open('back_end/memory/current_event.json', 'r') as file:
            data = json.load(file)
            file.close()
            current_event = data[agent_name]
    finally:
        lock.release()
    return current_event


def change_current_event(agent_name, event, lock):
    '''
    Change the current event of the agent in the memory
    '''
    lock.acquire()
    try:
        with open('back_end/memory/current_event.json', 'r') as file:
            data = json.load(file)
            file.close()
        data[agent_name] = event
        with open('back_end/memory/current_event.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()
    finally:
        lock.release()
    return event


def get_identity():
    '''
    INTPUT: agent
    OUTPUT: a dictionnary containing identity info i.e name, age, personality, life style, profile ...
    '''
    try:
        with open('back_end/memory/identity.json', 'r') as file:
            existing_data = json.load(file)
            file.close()
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    return existing_data


def get_relationship(agent_file_path, agent_name, other_agent_name):
    '''
    INTPUT: agent, other_agent_name
    OUTPUT: the relationship between the agent and the other_agent for example "Husband"
    '''
    relationship_explanation = f"What is following is an array of size 4, describing the relationship from the point of view of {agent_name} where each element corresponds, in order, to the following characteristics: dominance, appreciation, solidarity, familiarity with values ranging from 0 to 10 : "

    try:
        with open(agent_file_path + 'relationship.json', 'r') as file:
            data = json.load(file)
            file.close()
    except (FileNotFoundError, json.JSONDecodeError):
        print('relationship.json not found')
        data = {}

    return relationship_explanation+str(data[other_agent_name]["relationship"])+". "+str(data[other_agent_name]["description"])


def perceive(agent, map):
    '''
    add events to the sensory memory when discovering the environment or when some agent
    activated the perceive function and return the agents nearby
    '''

    # Get the events nearby the agent and eventually the discussion
    events_nearby = map.get_events_nearby(agent.name, agent.position)
    events_nearby = [
        f'{event.split(",")[0]} is {event.split(",")[1]}' for event in events_nearby]

    for event in events_nearby:
        agent.sensory_memory.add(event)

    agents_nearby = map.get_agents_nearby(agent.name, agent.position)

    return agents_nearby


def get_plan_status(agent, lock):
    '''
    OUTPUT a list of all tasks already performed and a list of tasks to be done in the future.
    '''
    sub_tasks_already_done = []
    rest_of_plan = []
    with open(agent.file_path + 'plan.json', 'r') as file:
        plan = json.load(file)

    current_event_found = False

    for task in plan:
        if len(task) >= 4:
            sub_tasks = task[3]
            for sub_task_value in sub_tasks:
                sub_task_description = sub_task_value[3]

                if f"{agent.name},{sub_task_description}" == get_current_event(agent.name, lock):
                    current_event_found = True
                    sub_tasks_already_done.append(sub_task_description)
                elif current_event_found:
                    rest_of_plan.append(sub_task_description)
                else:
                    sub_tasks_already_done.append(sub_task_description)
        else:
            if len(task) > 2:
                rest_of_plan.append(task[2])

    return sub_tasks_already_done, rest_of_plan


def filter_sensory_memory(agent, events, env, discussions, lock):
    '''
    INTPUT: agent, sensory_memory
    OUTPUT: a list of events that are relevant to the agent
    '''

    if discussions != None:
        pass

    sub_tasks_already_done, rest_of_plan = get_plan_status(agent, lock)

    # Get the importance of each event in the sensory memory
    file = open('back_end/prompts/sensory_memory.txt', 'r')
    prompt_filter = file.read().replace('#identity#', str(agent.get_info())).replace('#sub_tasks#', str(
        sub_tasks_already_done)).replace('#events#', str(events)).replace('#rest_of_plan#', str(rest_of_plan))
    file.close()

    prompt_filter = prompt_filter.split("###")

    message = [
        {'role': 'system',
         'content': prompt_filter[0]},
        {'role': 'user',
         'content': prompt_filter[1]},
    ]

    events_importance = get_completion(message, max_tokens=500, temperature=0)

    events_importance = eval(events_importance)

    # add the events that have an importance greater than the threshold to the long term memory
    threshold = 4

    for i in range(len(events)):
        if events_importance[i] > threshold:
            node = events[i]
            # agent.long_term_memory.add_connected_node(node)
            agent.add_episodic(node, env.get_time_back_end(),
                               events_importance[i])

    # Print the graph of the long term memory in the terminal
    # agent.long_term_memory.print_graph(agent.name)


def get_info_agent(agent_name):
    try:
        with open('back_end/memory/identity.json', 'r') as file:
            data = json.load(file)
            info = data[agent_name]
    except FileNotFoundError:
        print(f"file identity cannot be found")
        info = None
    return info


def interact(agent, other_agents, lock):
    '''
    INTPUT: agent, other_agents
    OUTPUT:
        No or name of the orther agent that the agent should interact with 
    '''

    other_agents_info = [[other_agent.name, agent.get_relationship(other_agent.name), get_current_event(
        other_agent.name, lock)] for other_agent in other_agents]

    file = open('back_end/prompts/interact.txt', 'r')
    prompt_interact = file.read().replace('#task_of_the_agent#', get_current_event(
        agent.name, lock).split(',')[1]).replace('#other_agents_info#', str(other_agents_info))
    file.close()

    prompt_interact = prompt_interact.split("###")

    message = [
        {'role': 'system',
         'content': prompt_interact[0]},
        {'role': 'user',
         'content': prompt_interact[1]},
    ]

    answer = get_completion(message)

    return answer


def get_discussion(agent, other_agent, lock):
    '''
    INTPUT: agent, other_agent_name
    OUTPUT: the discussion between the agent and the other_agent
    '''
    sub_tasks_already_done_1, rest_of_plan_1 = get_plan_status(agent, lock)
    sub_tasks_already_done_2, rest_of_plan_2 = get_plan_status(other_agent, lock)

    file = open('back_end/prompts/discussion.txt', 'r')
    prompt_interact = file.read().replace(
        '#agent_name_1#', str(agent.name)).replace(
        '#agent_name_2#', str(other_agent.name)).replace(
        '#relationship_1_to_2#', str(agent.get_relationship(other_agent.name))).replace(
        '#relationship_2_to_1#', str(get_relationship(other_agent.file_path, other_agent.name, agent.name))).replace(
        '#important_1#', str(agent.retrieve_episodic(get_current_event(agent.name, lock).split(',')[1], 4)[0][0])).replace(
        '#important_2#', str(other_agent.retrieve_episodic(get_current_event(other_agent.name, lock).split(',')[1], 4)[0][0])).replace(
        '#sub_tasks_already_done_1#', str(sub_tasks_already_done_1)).replace(
        '#sub_tasks_already_done_2#', str(sub_tasks_already_done_2)).replace(
        '#rest_of_plan_1#', str(rest_of_plan_1)).replace(
        '#rest_of_plan_2#', str(rest_of_plan_2))
    file.close()

    prompt_interact = prompt_interact.split("###")

    message = [
        {'role': 'system',
         'content': prompt_interact[0]},
        {'role': 'user',
         'content': prompt_interact[1]},
    ]
    discussion = get_completion(message)

    lock.acquire()
    try:
        with open('back_end/memory/discussion.json', 'r') as file:
            data = json.load(file)
            file.close()

        data[agent.name]["current_discussion"] = discussion
        data[agent.name]["discussion_history"].append(discussion)
        data[other_agent.name]["current_discussion"] = discussion
        data[other_agent.name]["discussion_history"].append(discussion)

        with open('back_end/memory/discussion.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()
    finally:
        lock.release()

    summarize_discussion(discussion, agent.name, other_agent.name)

    disc_time = len(discussion)*0.01
    return disc_time


def think(agent, event):  # -take all the events linked to it in the episodic memory -add the personality and emotions of the agent -use the fonction get_completion with the prompt prompt : -What 5 high-level insights can you infer from the above statements? adding the fact that the response must be a JSON file : a key in form of "Node_ID" and (localisation thinking, start time thought, end time = None, a sentence that describes the thought) as the corresponding value  -adding the thought to the graph, linked to events used to generate it (maybe not be all of them)
    identity = get_identity()[agent.name]
    identity.pop('initial_position', None)

    neighbors = retrieve_episodic(agent, event)
    contexts_of_neighbors = [neighbor[0] for neighbor in neighbors]
    with open('back_end/memory/identity.json', 'r') as file:
        data = json.load(file)
    names = data.keys()

    names_here = [word for word in event if word in names]

    file = open('back_end/prompts/think.txt', 'r')
    prompt_thought = file.read().replace(
        '#agent_name#', agent.name).replace(
        '#info#', str(identity)).replace(
        '#event#', event).replace(
        '#related_events#', str(contexts_of_neighbors)).replace(
        '#personality#', agent.print_personality()).replace(
        '#emotions#', agent.print_emotions())

    prompt_thought = prompt_thought.replace("{", "").replace(
        "}", "").replace("'", "").replace("[", "").replace("]", "")

    if len(names_here) == 0:
        prompt_thought = prompt_thought.replace(
            "They have a complex relationship with #other_agent_name#, marked by #relationship#.", " ")
    else:
        prompt_thought = prompt_thought.replace(
            '#other_agent_name#', str([name for name in names_here])).replace(
            'relationship', str([agent.get_relationship(name) for name in names_here]))  # relationship#.","They have a complex relationship with #other_agent_name#, marked by #relationship#.")

    file.close()

    print(len(names_here))

    print(prompt_thought)

    prompt_thought = prompt_thought.split("###")

    message = [
        {'role': 'system',
         'content': prompt_thought[0]},
        {'role': 'user',
         'content': prompt_thought[1]},
    ]

    thought = get_completion(message)

    agent.sensory_memory.add(thought)

    print(f"{agent.name} thought: {thought}")

    return thought


def delete(agent_name):
    '''
    clean discussion.json, agent_detected.json, current_event.json, discussion_state.json, current_emotion.json
    '''

    # Discussion
    with open('back_end/memory/discussion.json', 'r') as file:
        data = json.load(file)

    data[agent_name]["discussion_history"] = []
    data[agent_name]["current_discussion"] = ""
    data[agent_name]["summary"] = ""

    with open('back_end/memory/discussion.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Agent detected
    data = {}
    with open('back_end/memory/agent_detected.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Current event
    with open('back_end/memory/current_event.json', 'r') as file:
        data = json.load(file)
    data[agent_name] = f"{agent_name},None"

    with open('back_end/memory/current_event.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Discussion state
    data = {}
    with open('back_end/memory/discussion_state.json', 'w') as file:
        json.dump(data, file, indent=4)

    # Current emotion
    with open('back_end/memory/current_emotion.json', 'r') as file:
        data = json.load(file)

    data[agent_name]["current_state"] = []

    with open('back_end/memory/current_emotion.json', 'w') as file:
        json.dump(data, file, indent=4)


def summarize_discussion(discussion, agent_name, other_agent_name):
    '''
    INTPUT: discussion
    OUTPUT: the summary of the discussion
    '''
    file = open('back_end/prompts/summarize_discussion.txt', 'r')
    prompt_summarize = file.read().replace('#discussion#', str(discussion)).replace(
        '#agent_name#', str(agent_name)).replace('#other_agent_name#', str(other_agent_name))
    file.close()

    prompt_summarize = prompt_summarize.split("###")

    message = [
        {'role': 'system',
         'content': prompt_summarize[0]},
        {'role': 'user',
         'content': prompt_summarize[1]},
    ]

    summary = get_completion(message)

    try:
        with open('back_end/memory/discussion.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"file discussion cannot be found")
        return

    data[agent_name]["summary"] = summary
    data[other_agent_name]["summary"] = summary

    with open('back_end/memory/discussion.json', 'w') as file:
        json.dump(data, file, indent=4)

    return summary
