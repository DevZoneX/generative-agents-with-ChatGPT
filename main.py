from agent import Agent
from environment import Environment
from multiprocessing import Process
import time

def main():
    
    # Initial set up
    env = Environment(min_equivalent_seconds=2)
    agent = Agent(id='agent1', position=(2,2), localisations=["Jon's bed room", "Jon's kitchen", "Jon's bathroom", "Jon's office in Orange", "Gym"])
    initial_plan = agent.create_initial_plan()
    
    # Create sub tasks for task_1 and execute them
    sub_plan_1 = agent.create_sub_plan(1)
    
    task_1 = initial_plan[f'task_{1}']
    print(f'---------- Executing task {1}: {task_1[0]}, {task_1[1]}, {task_1[2]} ---------- \n')

    # Execute sub tasks for task_1
    for j in range(1, len(sub_plan_1)+1):
        key = f'sub_task_{j}'
        print(f'---------- Executing sub task {j}: {sub_plan_1[key][0]}, {sub_plan_1[key][1]}, {sub_plan_1[key][2]}, {sub_plan_1[key][3]}---------- \n')
        #agent.execute_sub_task(start = sub_plan_1[key][0], end = sub_plan_1[key][1], localisation = sub_plan_1[key][2], task = sub_plan_1[key][3], environment = env)
    time.sleep(20)
    
    # Create sub tasks for the rest of the tasks
    def create_all_sub_tasks():
        for i in range(2, 3):
            # Create sub tasks for task_i and return them
            sub_plan_i = agent.create_sub_plan(i)

            task_i = initial_plan[f'task_{i}']
            print(f'---------- Executing task {i}: {task_i[0]}, {task_i[1]}, {task_i[2]} ---------- \n')

            # Execute sub tasks for task_i
            for j in range(1, len(sub_plan_i)+1):
                key = f'sub_task_{j}'
                print(f'---------- Executing sub task {j}: {sub_plan_i[key][0]}, {sub_plan_i[key][1]}, {sub_plan_i[key][2]}, {sub_plan_i[key][3]}---------- \n')
                #agent.execute_sub_task(start = sub_plan_i[key][0], end = sub_plan_i[key][1], localisation = sub_plan_i[key][2], task =sub_plan_i[key][3], map=env.map)
            time.sleep(20)
    
    # Run the environment
    def run_enviroment():
        print('---------- Running the environment ---------- \n')
    
    # Start the simulation on two different processes running in parallel
    process1 = Process(target=create_all_sub_tasks)
    process2 = Process(target=run_enviroment)

    process1.start()
    process2.start()

    process1.join()
    process2.join()

if __name__ == "__main__":
    main()