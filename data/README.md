# GRAVITY


This directory contains data set for GRAVITY.

goal.txt
 - goal in sentences for 25 templates.

split/
 - task_ids_[train|dev|test].txt contain split of template:task ids for 2500 tasks.
 - task_ids_[train|dev|test]_annotation.txt contain split of template:task ids for annotated tasks.

raw_outputs/
  - contains every output step for every simulation for 25 templates.

no_solution.txt
 - contains template:task ids for tasks that we do not find a solution for.

solution_csv_json_imgs/
 - each template/task/ contains filtered_list.csv filtered_list.json initial.csv initial.json imgs/ for this task.
 - initial.csv initial.json have object attributes for initial state.
 - filtered_list.csv filtered_list.json have attributes for all collisions.
 - imgs/ have screenshots for all collisions, and a gif for all screenshots. step.txt shows the step number of collisions.

annotation/
 - salient_event/ contains time steps of important collisions for [template]-[task].txt.
 - initial_state_description/ contains descriptions of initial state for [template]-[task].txt
 - simulation_description/ contains descriptions of simulation for [template]-[task].txt
