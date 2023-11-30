from back_end.useful_functions import get_completion
import json

# create initial plan for the agent
def create_initial_plan(info, file_path):
    '''
    input: information from agent identity and the file path where the plan will be saved
    output: initial plan in the form of json and return it
    '''
    file = open('back_end/prompts/initial_plan.txt', 'r')
    prompt_initial_plan = file.read().replace('#info#', str(info))
    file.close()
    message = [ 
        {'role':'system',
        'content': prompt_initial_plan},
    ]
    plan = get_completion(message, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
    
    plan = json.loads(plan)
    with open(file_path + 'plan.json', 'w') as file:
        json.dump(plan, file)
        file.close()
        
    return plan

# create sub plan for task_i
def create_sub_plan(i, file_path, localisations):
    '''
    input: the task i for which the sub plan will be created, the file path where the plan will be saved, the localisations of the agent
    output: create sub plan in the form of json and save it in memory and return it
    '''
    
    task = f"task_{i}"

    with open(file_path + 'plan.json', 'r') as file:
        existing_data = json.load(file)
        file.close()
    
    task_i = existing_data[task]
    
    file = open('back_end/prompts/sub_plan.txt', 'r')
    prompt_sub_plan = file.read().replace('#start_time#', task_i[0]).replace('#end_time#', task_i[1]).replace('#task#', task_i[2]).replace('#localisations#', str(localisations))
    file.close()
    message = [
        {'role':'system',
        'content': prompt_sub_plan},
    ]
    plan = get_completion(message, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
    
    plan = json.loads(plan)
    
    existing_data[task].append(plan)
    with open(file_path + 'plan.json', 'w') as file:
        json.dump(existing_data, file)
        file.close()
    
    return plan

# Get details of task_i
def get_task(path, task):
    try:
        with open(path + 'plan.json', 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    return existing_data[task]