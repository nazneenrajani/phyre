import json
import pdb
import codecs
import inflect
import pandas
import re

from pathlib import Path
from tqdm import tqdm
from nltk import word_tokenize

from phyre.mturk.create_phyre_mturk import read_annotation_sentence_csv, read_annotation_salient_event_csv

EXP_NAME = "phyre"
MODE = "test"

IDS_FILE = f"{EXP_NAME}/data/task_ids_{MODE}_annotation.txt"
SENTENCE_ANNOTATION_FILE = f"{EXP_NAME}/mturk/sentence_annotation_csv/{MODE}_mturk_annotation_sentence.csv"
EVENT_ANNOTATION_FILE = f"{EXP_NAME}/mturk/salient_event_annotation_csv/{MODE}_mturk_annotation_salient_event.csv"

SRC_FILE = f"{EXP_NAME}/src_{MODE}.txt" # src file input
TGT_FILE = f"{EXP_NAME}/tgt_{MODE}.txt"  # tgt file

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

salient_events_dict, _ = read_annotation_salient_event_csv([EVENT_ANNOTATION_FILE])
sentences_dict = read_annotation_sentence_csv([SENTENCE_ANNOTATION_FILE])

id = "00000:061"
template, task = id.split(':')
import pdb; pdb.set_trace()
