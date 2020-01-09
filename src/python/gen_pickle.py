import phyre
import pickle

eval_setup = 'ball_within_template'

# IMPORTANT: If you want to reduce the size of the pickle, you should alter tasks list
with open("task_ids.txt", "r") as f:
    tasks = f.read().split('\n')
action_tier = phyre.eval_setup_to_action_tier(eval_setup)

# Create the simulator from the tasks and tier.
simulator = phyre.initialize_simulator(tasks, action_tier)

with open("all.pickle", "wb") as w:
    pickle.dump(simulator, w)
