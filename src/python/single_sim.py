import phyre
import thrift
import json
import os
from phyre import simulator as sim
from phyre import visualize_tasks as viz
from phyre import SimulationStatus

# make the output dir
OUTPUT_DIR = "testing/"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# pick which task
tasks = ["00006:003"]
eval_setup = 'ball_within_template'
action_tier = phyre.eval_setup_to_action_tier(eval_setup)
simulator = phyre.initialize_simulator(tasks, action_tier)
task_index = 0
task_id = simulator.task_ids[task_index]

print("Task being simulated:", task_id)

# search for an action that solves this
actions = simulator.build_discrete_action_space(max_actions = 10000)
for action in actions:
    status, _ = simulator.simulate_single(task_index, action, need_images=False)
    if status == SimulationStatus.SOLVED:
        print("Solution found:", action)
        actual_action = action # for output later
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
        
        print("CSV created at:", fp)

        break