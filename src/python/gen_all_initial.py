from phyre import SimulationStatus
from phyre import visualize_tasks as viz
from phyre import simulator as sim
import pickle
import json
import os

# setup output dir
OUTPUT_DIR = "output/"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# read in pickle
with open("all.pickle", "rb") as f:
    simulator = pickle.load(f)

# initialize actions
actions = simulator.build_discrete_action_space(max_actions = 10000)
step_size = 1
solutions_per_task = 1

for i in range(0, 2500, step_size):
    # simulate the task
    task_index = i
    task_id = simulator.task_ids[task_index]
    solutions = 0

    # Simulate every action
    for action in actions:
        status, images = simulator.simulate_single(task_index, action, need_images = False)
        
        # for every solving action
        if status == SimulationStatus.SOLVED:
            actual_action = action
            action, is_valid = simulator.get_user_input(action)
            result, user_input = sim.simulate_task_with_input(simulator.get_task(task_index), action, stride=1)

            # get the initial scene
            initial_scene = result.sceneList[0]
            initial_scene_objects = viz.create_list_of_objects(initial_scene)

            # add user input
            viz.add_user_ball(initial_scene_objects, user_input)

            # generate json format
            initial_json = viz.initial_json(task_id, actual_action, initial_scene_objects)
            initial_json = json.loads(initial_json.replace("'", '"'))

            # convert json to csv
            fp = OUTPUT_DIR + task_id.replace(':', '.') + ".csv"
            viz.initial_csv(initial_json, fp)

            # increment solution count
            solutions += 1
            if solutions == solutions_per_task:
                break

