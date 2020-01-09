import json
import csv
from copy import deepcopy

#json_str = '[{"step": 0, "b1_x": 100, "solved": False}, {"step": 1, "b1_x": 70, "solved": False}, {"step": 2, "b1_x": 0, "solved": True}]'
#obj = json.loads(json_str)
#obj = [{"step": 0, "b1_x": 100, "solved": False}, {"step": 1, "b1_x": 70, "solved": False}, {"step": 2, "b1_x": 0, "solved": True}]
f = open("list_of_steps.txt", "r")
obj = json.loads(f.read())
new = []

key_names = ["step"] + ["is_list"] + list(obj[0]["list"][0].keys()) + ["is_collision"]
for step in obj:
    if "collisions" in step:
        key_names += ["kind"]
        collision_keys = list(step["collisions"][0]["1"].keys())
        keys1 = [key + '_1' for key in collision_keys]
        keys2 = [key + '_2' for key in collision_keys]
        key_names += keys1 + keys2 # + ["force"]
        break

base_dict = {key: 0 for key in key_names}


for step in obj:
    tmp = {}
    for lists in step["list"]:
        tmp = deepcopy(base_dict)
        tmp["is_list"] = 1
        tmp["step"] = step["step"]
        for key in lists:
            tmp[key] = lists[key]
        new.append(tmp)
    if "collisions" in step:
        # force_index = 0
        for collision in step["collisions"]:
            tmp = deepcopy(base_dict)
            tmp["step"] = step["step"]
            tmp["is_collision"] = 1
            tmp["kind"] = collision["kind"]
            for key in collision["1"]:
                new_key = key + "_1"
                tmp[new_key] = collision["1"][key]
            for key in collision["2"]:
                tmp[key + "_2"] = collision["2"][key]
            #if collision["kind"] == "begin":
            #    tmp["force"] = step["forces"][force_index]
            #    force_index += 1
            new.append(tmp)

f = open("csv_out.csv", "w")
output = csv.writer(f)
output.writerow(key_names)
for row in new:
    output.writerow(row.values())

f.close()
