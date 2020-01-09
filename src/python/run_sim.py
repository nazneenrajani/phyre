import phyre
import matplotlib.pyplot as plt


eval_setup = 'ball_cross_template'
fold_id = 2  # 0-indexed template number
train_tasks, dev_tasks, test_tasks = phyre.get_fold(eval_setup, fold_id)

tasks = dev_tasks[:2]
action_tier = phyre.eval_setup_to_action_tier(eval_setup)

# Create the simulator from the tasks and tier.
simulator = phyre.initialize_simulator(tasks, action_tier)

# Replace above code with this to reduce runtime (only has task 3:28)
# import pickle
# with open("3.28.pickle", "rb") as f:
#	simulator = pickle.load(f)

task_index = 0  # Will be task 28 if you load the pickle
task_id = simulator.task_ids[task_index]
initial_scene = simulator.initial_scenes[task_index]

# Display the initial scene
# plt.imshow(phyre.vis.observations_to_float_rgb(initial_scene))
# plt.show()

from phyre import simulator as sim
actions = simulator.build_discrete_action_space(max_actions=1000)
action = actions[20]  # Successful action for 3:28
action, is_valid = simulator.get_user_input(action)  # Phyre representation of the action

# If you want to brute force every solution until you get a success
# from phyre import SimulationStatus
# for action in actions:
# 	status = simulator.simulate_single(task_index, action, need_images=False)
# 	if status == SimulationStatus.SOLVED:

# Simulates task with the action, returning Thrift representations of intermediate images every frame
# Increase stride to decrease simulation time
result = sim.simulate_task_with_input(simulator.get_task(0), action, stride=1)

# Convert Thrift scene to array of pixels
images = [sim.scene_to_raster(scene) for scene in result.sceneList]
ims = [phyre.vis.observations_to_float_rgb(image) for image in images]

# Displays the simulation
delay = 0.0005  # Delay between frames
img = plt.imshow(ims[0])
for image in ims[1:]:
	img.set_data(image)
	plt.pause(delay)
	plt.draw()
