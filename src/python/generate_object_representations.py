"""
This is a file to read in output from standard input and connect work being done in parallel to simulate and visualize games.


Notes:
    - result = sim.simulate_task_with_input(simulator.get_task(0), action, stride = 1)[0]
    This would be to get the call to get the user ball information from the action
"""

import json

# reads in a file with a json object in it and prints it out
def read_json_file(fp):
    with open(fp) as f:
        lines = f.read()
        simulations_json = json.loads(lines) # removes the ' at the beginning and end
    return simulations_json

# takes the json of a single task, action simulation
def get_collisions(initial_scene_objects, simulation_json, window):
    collision_steps = [] # list of steps that have a begin/ end collision
    steps_of_interest = set() # set of all step frame numbers we care about
    step_objects = [] # list of all step objects we care about

    # loop through all the steps
    all_steps = simulation_json['steps']
    for step in all_steps:
        if 'collisions' in step:
            collision_steps.append(step['step']) 
    
    # at this point collision_steps has all the desired frames, now we need to add the window to all
    for collision_step in collision_steps:
        for shift in range(-window, window + 1):
            curr_step = collision_step + shift
            if curr_step not in steps_of_interest:
                steps_of_interest.add(collision_step + shift)
                step_objects.append(all_steps[curr_step])

    return step_objects

def print_steps(initial_scene_objects, steps_list):
    # if there is a collision
    for step in steps_list:

        # print like a collision
        if 'collisions' in step:
            for collision in step['collisions']:
                # print(collision)
                object_1 = collision['1']
                object_2 = collision['2']

                # TODO: improve this
                # replace object with user input
                object_1_description = initial_scene_objects[object_2['id']].get_short_description() if object_1['type'] == 0 else initial_scene_objects[-1].get_short_description()
                object_2_description = initial_scene_objects[object_2['id']].get_short_description() if object_2['type'] == 0 else initial_scene_objects[-1].get_short_description()

                print(f"Step {step['step']} a collision {collision['kind']} at ({object_1['x']}, {object_1['y']}) between ", end='')
                print(f"the {object_1_description} going at vector ({object_1['x_vel']}, {object_1['y_vel']}) and ", end='')
                print(f"the {object_2_description} going at vector ({object_2['x_vel']}, {object_2['y_vel']})")
        else:
            for obj in step['list']:
                obj_description = initial_scene_objects[obj['id']].get_short_description() if obj['type'] == 0 else initial_scene_objects[-1].get_short_description()
                print(f"Step {step['step']} at ({obj['x']}, {obj['y']}) ", end='')
                print(f"the {obj_description} is going at vector ({obj['x_vel']}, {obj['y_vel']})")

def generate_excel(initial_scene_objects, simulation_json):
    print("Hello")