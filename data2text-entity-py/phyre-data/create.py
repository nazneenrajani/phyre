import json
import pdb
import codecs
import inflect
import pandas
import re
import argparse

from pathlib import Path
from tqdm import tqdm
from nltk import word_tokenize
from collections import defaultdict, Counter

from phyre.mturk.create_phyre_mturk import read_annotation_sentence_csv, read_annotation_salient_event_csv

parser = argparse.ArgumentParser(
    description="Create dataset for data2text generation",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument('--mode', type=str,
                    help="list, either 'train', or 'dev', or 'test'")
parser.add_argument('--description_type', type=str,
                    help="dataset is aligned to initial_state_description or simulation_description")
args = parser.parse_args()

EXP_NAME = "phyre"
MODE = args.mode
DESCRIPTION_TYPE = args.description_type

FILTERED_DATA_DIR = f"{EXP_NAME}/filtered_jsons"
INITIAL_DATA_DIR = f"{EXP_NAME}/initial_jsons"
IDS_FILE = f"../../data/split/task_ids_{MODE}_annotation.txt"
SENTENCE_ANNOTATION_DIR = f"../../data/annotation/{DESCRIPTION_TYPE}"
EVENT_ANNOTATION_DIR = f"../../data/annotation/salient_event"

SRC_FILE = f"{EXP_NAME}/{DESCRIPTION_TYPE}/src_{MODE}.txt" # src file input
TGT_FILE = f"{EXP_NAME}/{DESCRIPTION_TYPE}/tgt_{MODE}.txt"  # tgt file

PAD_WORD = '<blank>'
UNK_WORD = '<unk>'
UNK = 0
BOS_WORD = '<s>'
EOS_WORD = '</s>'

RECORD_DELIM = " "
DELIM = u"￨"
NUM_PATT = re.compile('([+-]?\d+(?:\.\d+)?)')

# ORACLE_IE_OUTPUT = f"roto_train-beam5_gens.h5-tuples.txt"  # oracle content plan obtained from IE tool
# INTER_CONTENT_PLAN = f"{EXP_NAME}/inter/train_content_plan.txt"  # intermediate content plan input to second stage
# CONTENT_PLAN_OUT = f"{EXP_NAME}/train_content_plan.txt"  # content plan output of first stage

INFLECT = inflect.engine()

# taking object as the entity [value|color_type(entity)|feat|COLLISION]
init_keys = [
    # information about current entity
    "OBJ_COLOR",
    "OBJ_TYPE",
    "OBJ_STATE",  # dynamic or static

    # information about the object
    "X",
    "Y",
    "ANGLE",
    "LENGTH",
    "WIDTH",
    "BASE_LENGTH",
    "RADIUS",
]
collision_keys = [
    # information about current entity
    "OBJ_COLOR",
    "OBJ_TYPE",

    # information about the beginning of the collision
    "X",
    "Y",
    "X_VEL",
    "Y_VEL",
    "ANGLE",

    # information about the collision itself
    "COLLISION_OBJ_COLOR",
    "COLLISION_OBJ_TYPE",
    "COLLISION_OBJ_X",
    "COLLISION_OBJ_Y",
    "COLLISION_OBJ_X_VEL",
    "COLLISION_OBJ_Y_VEL",
    "COLLISION_OBJ_ANGLE",

    # meta information about collision
    "KIND",
    "SOLVED_STATE",
    "STEP",
]


def to_int(matchobj):
    num = int(round(float(matchobj.group(0)),0)) # rounds to nearest integer
    return str(num)


def get_list_entities(step_dict):
    entities = []
    dynamic_obj_records = step_dict["list"]
    counter_name = Counter()
    for dynamic_obj_record in dynamic_obj_records:
        entity_name = dynamic_obj_record["color"].lower() + "_" + "".join(dynamic_obj_record["type"].lower().split())
        entity = {
            "name": entity_name + "_" + str(counter_name[entity_name]),
            "color": dynamic_obj_record["color"],
            "type": dynamic_obj_record["type"],
        }
        counter_name[entity_name] += 1
        entities.append(entity)
    return entities


def get_init_entities(init_dict):
    entities = []
    obj_records = init_dict["objects"]
    counter_name = Counter()
    for obj_record in obj_records:
        entity_name = obj_record["color"].lower() + "_" + "".join(obj_record["type"].lower().split())
        entity = {
            "object_id": obj_record["object_id"],
            "name": entity_name + "_" + str(counter_name[entity_name]),
            "color": obj_record["color"],
            "type": obj_record["type"],
        }
        counter_name[entity_name] += 1
        entities.append(entity)
    return entities


def create_record(value, entity_name, record_type, index):
    record = []
    record.append(value)
    record.append(entity_name)
    record.append(record_type)
    record.append(index)
    return record


def find_collision_dict(entity, step_dicts):
    for step_dict in step_dicts:
        for collision_dict in step_dict["collisions"]:
            if entity["color"] == collision_dict["1"]["color"] and entity["type"] == collision_dict["1"]["type"]:
                return collision_dict, "1"
            if entity["color"] == collision_dict["2"]["color"] and entity["type"] == collision_dict["2"]["type"]:
                return collision_dict, "2"
    return None, None


def get_ids(ids_file):
    with open(ids_file, 'r') as f:
        ids = f.readlines()
        ids = [id.strip() for id in ids]
        return ids


def get_data(ids, sentence_annotation_dir, event_annotation_dir):

    src_instances = []
    tgt_summaries = []
    for id in tqdm(ids):
        # get template, task and annotations
        template, task = id.split(':')
        event_annotation_file = f"{event_annotation_dir}/{template}-{task}.txt"
        sentence_annotation_file = f"{sentence_annotation_dir}/{template}-{task}.txt"
        events_annotation = open(event_annotation_file).readlines()
        sentences_annotation = open(sentence_annotation_file).readlines()

        # get src instance
        events = [event.strip() for event in events_annotation]
        initial_json_file = f"{INITIAL_DATA_DIR}/{template}/{task}.json"
        filtered_json_file = f"{FILTERED_DATA_DIR}/{template}/{task}_list.json"
        if len(events) == 0:
            print(f"{initial_json_file}: 0 salient events")
            continue
        src_instance = get_src_instance(initial_json_file, filtered_json_file, events)

        # get tgt_summary
        sentence = sentences_annotation[0].strip()
        tgt_summary = get_summary(id, sentence)

        # append
        src_instances.append(src_instance)
        tgt_summaries.append(tgt_summary)

    return src_instances, tgt_summaries


def get_src_instance(initial_json_file, filtered_json_file, events):
    with codecs.open(initial_json_file, "r", "utf-8") as initial_f, codecs.open(filtered_json_file, "r", "utf-8") as filtered_f:
        initial_state = json.load(initial_f)
        assert(len(initial_state) == 1)
        initial_state = initial_state[0]
        steps = json.load(filtered_f)
        entity_records = {}

        # init_keys
        entities = get_init_entities(initial_state)
        for i, entity in enumerate(entities):
            object_dict = initial_state["objects"][i]
            assert(object_dict["object_id"] == entity["object_id"])
            entity_records[entity["name"]] = []
            entry = {}
            entry["OBJ_COLOR"] = entity["color"].lower()
            entry["OBJ_TYPE"] = entity["type"].lower().replace(" ", "_")
            entry["OBJ_STATE"] = object_dict["state"].lower()
            entry["X"] = str(int(object_dict["x"]))
            entry["Y"] = str(int(object_dict["y"]))
            entry["ANGLE"] = str(int(object_dict["angle"])) if object_dict["angle"] else PAD_WORD
            entry["LENGTH"] = str(int(object_dict["length"])) if object_dict["length"] else PAD_WORD
            entry["WIDTH"] = str(int(object_dict["width"])) if object_dict["width"] else PAD_WORD
            entry["BASE_LENGTH"] = str(int(object_dict["base_length"])) if object_dict["base_length"] else PAD_WORD
            entry["RADIUS"] = str(int(object_dict["radius"])) if object_dict["radius"] else PAD_WORD
            for i, record_type in enumerate(init_keys):
                entity_records[entity["name"]].append(DELIM.join(create_record(
                    entry[record_type],
                    entity["name"],
                    record_type,
                    "INITIAL_STATE",
                )))

        # collision_keys
        count_significant = defaultdict(int)
        if DESCRIPTION_TYPE == "simulation_description":
            record_len_start = sum([len(record) for entity, record in entity_records.items()])
            entities = get_list_entities(steps[0])
            for entity in entities:
                for idx, step_dict in enumerate(steps):
                    if str(step_dict["step"]) not in events:
                        continue
                    count_significant[idx] += 1
                    collision_dict, collision_id = find_collision_dict(entity, [step_dict])
                    if collision_dict:
                        entry = {}
                        entry["OBJ_COLOR"] = entity["color"].lower()
                        entry["OBJ_TYPE"] = entity["type"].lower().replace(" ", "_")
                        entry["X"] = str(int(collision_dict[collision_id]["x"]))
                        entry["Y"] = str(int(collision_dict[collision_id]["y"]))
                        entry["X_VEL"] = str(int(collision_dict[collision_id]["x_vel"]))
                        entry["Y_VEL"] = str(int(collision_dict[collision_id]["y_vel"]))
                        entry["ANGLE"] = str(int(collision_dict[collision_id]["angle"]))
                        other_collision_id = "1" if collision_id == "2" else "2"
                        entry["COLLISION_OBJ_COLOR"] = collision_dict[other_collision_id]["color"].lower()
                        entry["COLLISION_OBJ_TYPE"] = collision_dict[other_collision_id]["type"].lower().replace(" ", "_")
                        entry["COLLISION_OBJ_X"] = str(int(collision_dict[other_collision_id]["x"]))
                        entry["COLLISION_OBJ_Y"] = str(int(collision_dict[other_collision_id]["y"]))
                        entry["COLLISION_OBJ_X_VEL"] = str(int(collision_dict[other_collision_id]["x_vel"]))
                        entry["COLLISION_OBJ_Y_VEL"] = str(int(collision_dict[other_collision_id]["y_vel"]))
                        entry["COLLISION_OBJ_ANGLE"] = str(int(collision_dict[other_collision_id]["angle"]))
                        entry["KIND"] = collision_dict["kind"]
                        entry["SOLVED_STATE"] = str(step_dict["solved_state"]).lower()
                        entry["STEP"] = str(step_dict["step"])
                        for i, record_type in enumerate(collision_keys):
                            entity_records[entity["name"]].append(DELIM.join(create_record(
                                entry[record_type],
                                entity["name"],
                                record_type,
                                "COLLISION",
                            )))
            if sum([len(record) for entity, record in entity_records.items()]) <= record_len_start:
                assert(len(events) == 1)
                print(f"{initial_json_file}: only 1 salient event that is last frame not in json")
            # if len([v for k, v in count_significant.items() if v != 0]) != len(events):
            #     print(f"num_significant does not match: {initial_json_file}")

        # append records
        records = []
        for entity, record in entity_records.items():
            records.extend(record)

        src_instance = " ".join(records)
        return src_instance


# def get_src_instances(INPUT_DIR, salient_events):
#     src_instances = []
#     input_dir_path = Path(INPUT_DIR)
#     template_dirs = sorted([f for f in input_dir_path.iterdir() if f.is_dir()])
#     df = pandas.read_csv(SPLIT_FILE, usecols=["taskId"])
#     ids = list(df["taskId"])
#     final_ids = []
#     for template in tqdm(template_dirs):
#         tasks = [f for f in template.iterdir()]
#         # print(f"{template.stem}: {len(tasks)}")
#         for task in tasks:
#             template_stem = template.stem
#             task_stem = task.stem[:-5]
#             print(template_stem)
#             print(task_stem)
#             import pdb; pdb.set_trace()
#             events = salient_events[template_stem][task_stem]["import_labels"]
#             id = f"{template_stem}:{task_stem}"
#             # print(id)
#             if id in ids:
#                 src_instance = get_src_instance(task, events)
#                 src_instances.append(src_instance)
#                 final_ids.append(id)
#
#     return src_instances, final_ids

"""
from https://github.com/harvardnlp/boxscore-data/blob/master/scripts/preproc.py
"""
def get_summary(id, sentence):
    # remove all newlines
    summary = sentence.replace(u'\xa0', ' ')
    summary = summary.replace('\\n', ' ').replace('\r', ' ')
    summary = summary.replace('|', '')
    summary = summary.replace('{', '')
    summary = summary.replace('}', '')
    summary = summary.strip()
    summary = re.sub("<[^>]*>", " ", summary)
    # replace all numbers wih rounded integers
    summary = NUM_PATT.sub(to_int, summary)
    tokes = word_tokenize(summary)
    new_tokes = []
    for toke in tokes:
        if '.' in toke and len(toke) != 1:
            for new_toke in toke.split('.'):
                new_tokes.append(new_toke)
                new_tokes.append('.')
            del new_tokes[-1]
        else:
            new_tokes.append(toke)
    tokes = filter(None, new_tokes)
    # replace hyphens
    newtokes = []
    [newtokes.append(toke) if toke[0].isupper() or '-' not in toke
      else newtokes.extend(toke.replace('-', " - ").split()) for toke in tokes]
    if summary == '':
        print(f"{id}: empty summary sentence")
    # assert(summary != '')
    return newtokes


# def get_summaries(ids, annotation_file):
#     summaries = []
#     skips = []
#     annotations = read_annotation_sentence_csv([annotation_file])
#     for i, id in enumerate(ids):
#         template, task = id.split(':')
#         summary = get_summary(annotations, template, task)
#         if summary is None:
#             skips.append(i)
#         summaries.append(summary)
#     return summaries, skips


def write_tgt_file(summaries):
    summary_file = open(TGT_FILE,'w')
    for i, summary in enumerate(summaries):
        summary_file.write(" ".join(summary))
        summary_file.write("\n")
    summary_file.close()


def write_src_file(src_instances):
    src_file = open(SRC_FILE, 'w')
    for i, src_instance in enumerate(src_instances):
        src_file.write(src_instance)
        src_file.write("\n")
    src_file.close()


def write_ids_file(ids, skips):
    ids_file = open(IDS_FILE, 'w')
    for i, id in enumerate(ids):
        ids_file.write(id)
        ids_file.write("\n")
    ids_file.close()


if __name__ == "__main__":
    print(EXP_NAME, MODE, DESCRIPTION_TYPE)
    ids = get_ids(IDS_FILE)
    src_instances, tgt_summaries = get_data(ids, SENTENCE_ANNOTATION_DIR, EVENT_ANNOTATION_DIR)
    write_src_file(src_instances)
    write_tgt_file(tgt_summaries)
    print()

    # annotations = read_annotation_sentence_csv([SENTENCE_ANNOTATION_FILE])
    # import pdb; pdb.set_trace()
    # for skip in skips:
    #     id = final_ids[skip]
    #     template, task = id.split(':')
    #     print(f"skipping: {id}")
    #     print(annotations[template][task])
    #     print()
