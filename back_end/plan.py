from back_end.useful_functions import get_completion
import json

# create initial plan response
def create_initial_plan(info):
    file = open('back_end/prompts/initial_plan.txt', 'r')
    prompt_initial_plan = file.read().replace('#info#', str(info))
    file.close()
    message = [ 
        {'role':'system',
        'content': prompt_initial_plan},
    ]
    plan = get_completion(message, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
    return json.loads(plan)

# create sub plan response
def create_sub_plan(start_time, end_time, localisations, task):
    file = open('back_end/prompts/sub_plan.txt', 'r')
    prompt_sub_plan = file.read().replace('#start_time#', start_time).replace('#end_time#', end_time).replace('#task#', task).replace('#localisations#', localisations)
    file.close()
    message = [
        {'role':'system',
        'content': prompt_sub_plan},
    ]
    plan = get_completion(message, model="gpt-3.5-turbo", max_tokens=500, temperature=0)
    return json.loads(plan)

# Get details of task_i
def get_task(path, task):
    try:
        with open(path + 'plan.json', 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}
    return existing_data[task]