import phyre
import pickle
from phyre import simulator as sim
from phyre import SimulationStatus
import matplotlib.pyplot as plt
import os
import multiprocessing


# Function used for multiprocessing
save_dir = ""
def plot(image):
    fig = plt.figure()
    data, i = image
    plt.imshow(data)
    fig.savefig(save_dir + '/' + str(i))
    plt.close(fig)


# Pickle object with all the tasks
with open("all.pickle", "rb") as f:
    simulator = pickle.load(f)

step_size = 25  # Tests 4 tasks per template
solutions_per_task = 3  # Generates output for 3 solutions per task

# Generate action space (not guaranteed a solution for every task if we lower it to 1000, but it would run
# noticeably faster
actions = simulator.build_discrete_action_space(max_actions=10000)
print("[", end="")
for i in range(0, 2500, step_size):
    print("{", end="")
    task_index = i
    task_id = simulator.task_ids[task_index]
    print('"task_id": "' + task_id + '", ', end="")

    # Directory to save the scene images
    save_dir = task_id.replace(':', '.')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    solutions = 0

    # Brute force actions until a solution is found
    for action in actions:
        status, images = simulator.simulate_single(task_index, action, need_images=False)
        if status == SimulationStatus.SOLVED:
            sim.set_print(True)
            print('"action": ' + str(action).replace(' ', ', ') + ', ', end="")
            print('"initial": [', end="", flush=True)
            status, images = simulator.simulate_single(task_index, action, stride=1, need_images=True)
            print("]}", end="")

            ims = [phyre.vis.observations_to_float_rgb(image) for image in images]

            # NOTE: Could possibly speed up image generation, but it is very intensive
            #       If you want to use this, replace the loop below with these three lines
            # ims_proc = zip(ims, range(len(ims)))
            # pool = multiprocessing.Pool()
            # pool.map(plot, ims_proc)

            for i in range(len(ims)):
                plt.imshow(ims[i])
                plt.savefig(save_dir + "/" + str(i))
                plt.cla()

            sim.set_print(False)

            solutions += 1
            if solutions == solutions_per_task:
                break

print("]")
