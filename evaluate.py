from nlgeval import compute_metrics
import os
import csv
import random

def read_task_id_list(task_id_path):
  all_task_path = []
  with open(task_id_path) as f:
    for line in f:
      template, task = line.strip().split(':')
      # print(template, task)
      task_path = (template, task)
      all_task_path.append(task_path)
  return all_task_path

def read_gpt_system_output(test_ids, csv_path):
  outputs = {}
  # print(csv_path)
  with open(csv_path, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
      task_id, sentence = row
      template, task = task_id.strip('.txt').split('-')
      task_id = (template, task)
      # print(task_id)
      outputs[task_id] = sentence

  outputs_list = []
  for test_id in test_ids:
    outputs_list.append(outputs[test_id])
  return outputs_list

def read_system_output(dev_ids, test_ids, file_path):
  outputs = []
  with open(file_path) as f:
    for line in f:
      outputs.append(line.strip())

  assert len(outputs) == len(dev_ids+test_ids)

  dev_system_output = outputs[:len(dev_ids)]
  test_system_output = outputs[len(dev_ids):]

  return dev_system_output, test_system_output

def read_annotation(task_ids, annotation_type):
  annotations = []
  for template, task in task_ids:
    if annotation_type=='simulation_description':
      annotation_file = 'data/annotation/simulation_description/{}-{}.txt'.format(template, task)
    elif annotation_type=='initial_state_description':
      annotation_file = 'data/annotation/initial_state_description/{}-{}.txt'.format(template, task)
    with open(annotation_file) as f:
      annotation = f.read().strip()
      annotations.append(annotation)
  return annotations

def compute(annotations, outputs):
  with open('ref.txt', 'w') as f:
    f.write('\n'.join(annotations))

  with open('output.txt', 'w') as f:
    f.write('\n'.join(outputs))   

  metrics_dict = compute_metrics(hypothesis='output.txt',
                                 references=['ref.txt'], no_skipthoughts=True, no_glove=True)
  print()
  return metrics_dict

if __name__ == "__main__":

  #### Read IDs
  task_id_path = 'data/split/task_ids_train_annotation.txt'
  train_ids = read_task_id_list(task_id_path)

  task_id_path = 'data/split/task_ids_dev_annotation.txt'
  dev_ids = read_task_id_list(task_id_path)

  task_id_path = 'data/split/task_ids_test_annotation.txt'
  test_ids = read_task_id_list(task_id_path)

  # cnt = 0
  # for f in os.listdir('data/annotation/initial_state_description/'):
  #   template, task = f.strip('.txt').split('-')
  #   if (template, task) not in train_ids+dev_ids+test_ids:
  #     cnt += 1
  #     os.remove(os.path.join('data/annotation/initial_state_description/', f))
  # print(cnt)
  # cnt = 0
  # for f in os.listdir('data/annotation/salient_event/'):
  #   template, task = f.strip('.txt').split('-')
  #   if (template, task) not in train_ids+dev_ids+test_ids:
  #     cnt += 1
  #     os.remove(os.path.join('data/annotation/salient_event/', f))
  # print(cnt)
  # cnt = 0
  # for f in os.listdir('data/annotation/simulation_description/'):
  #   template, task = f.strip('.txt').split('-')
  #   if (template, task) not in train_ids+dev_ids+test_ids:
  #     cnt += 1
  #     os.remove(os.path.join('data/annotation/simulation_description/', f))
  # print(cnt)

  #### Read Annotations
  dev_initial_state_description = read_annotation(dev_ids, annotation_type='initial_state_description')
  dev_simulation_description = read_annotation(dev_ids, annotation_type='simulation_description')
  
  test_initial_state_description = read_annotation(test_ids, annotation_type='initial_state_description')
  test_simulation_description = read_annotation(test_ids, annotation_type='simulation_description')

  #### Read and Eval AVG outputs
  print('Read and Eval AVG outputs')
  f = 'data2text-entity-py/phyre-data/gen/initial_state_description/phyre_lr_0.15_epoch_100/dev_test_phyre_lr_0.15_epoch_100_ppl_1.14_acc_95.61_e125.pt-beam5_gens.txt'
  dev_system_output_initial_state_description, test_system_output_initial_state_description = read_system_output(dev_ids, test_ids, f)

  f = 'data2text-entity-py/phyre-data/gen/simulation_description/phyre_lr_0.15_epoch_100/dev_test_phyre_lr_0.15_epoch_100_ppl_1.13_acc_96.13_e125.pt-beam5_gens.txt'
  dev_system_output_simulation_description, test_system_output_simulation_description = read_system_output(dev_ids, test_ids, f)

  m1 = compute(dev_initial_state_description, dev_system_output_initial_state_description)
  # print(m1)
  # exit()
  m2 = compute(dev_simulation_description, dev_system_output_simulation_description)
  m3 = compute(test_initial_state_description, test_system_output_initial_state_description)
  m4 = compute(test_simulation_description, test_system_output_simulation_description)

  #### Read and Eval BiLSTM outputs
  print('Read and Eval BiLSTM outputs')
  f = 'data2text-entity-py/phyre-data/gen/initial_state_description/phyre_lr_0.15_epoch_100_brnn/dev_test_phyre_lr_0.15_epoch_100_brnn_ppl_1.14_acc_95.67_e125.pt-beam5_gens.txt'
  dev_system_output_initial_state_description, test_system_output_initial_state_description = read_system_output(dev_ids, test_ids, f)

  f = 'data2text-entity-py/phyre-data/gen/simulation_description/phyre_lr_0.15_epoch_100_brnn/dev_test_phyre_lr_0.15_epoch_100_brnn_ppl_1.14_acc_96.07_e125.pt-beam5_gens.txt'
  dev_system_output_simulation_description, test_system_output_simulation_description = read_system_output(dev_ids, test_ids, f)

  m5 = compute(dev_initial_state_description, dev_system_output_initial_state_description)
  m6 = compute(dev_simulation_description, dev_system_output_simulation_description)
  m7 = compute(test_initial_state_description, test_system_output_initial_state_description)
  m8 = compute(test_simulation_description, test_system_output_simulation_description)

  results = [m1['Bleu_1'], m1['Bleu_2'], m1['ROUGE_L'], m1['METEOR'], m3['Bleu_1'], m3['Bleu_2'], m3['ROUGE_L'], m3['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))
  results = [m5['Bleu_1'], m5['Bleu_2'], m5['ROUGE_L'], m5['METEOR'], m7['Bleu_1'], m7['Bleu_2'], m7['ROUGE_L'], m7['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))
  results = [m2['Bleu_1'], m2['Bleu_2'], m2['ROUGE_L'], m2['METEOR'], m4['Bleu_1'], m4['Bleu_2'], m4['ROUGE_L'], m4['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))
  results = [m6['Bleu_1'], m6['Bleu_2'], m6['ROUGE_L'], m6['METEOR'], m8['Bleu_1'], m8['Bleu_2'], m8['ROUGE_L'], m8['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))


  #### Read and Eval GPT outputs
  f = 'GPT/initial_1.txt'
  test_gpt_initial_1 = read_gpt_system_output(test_ids, f)

  f = 'GPT/initial_2.txt'
  test_gpt_initial_2 = read_gpt_system_output(test_ids, f)

  f = 'GPT/simulation_1.txt'
  test_gpt_simulation_1 = read_gpt_system_output(test_ids, f)

  f = 'GPT/simulation_2.txt'
  test_gpt_simulation_2 = read_gpt_system_output(test_ids, f)

  m9 = compute(test_initial_state_description, test_gpt_initial_1)
  m10 = compute(test_initial_state_description, test_gpt_initial_2)
  m11 = compute(test_simulation_description, test_gpt_simulation_1)
  m12 = compute(test_simulation_description, test_gpt_simulation_2)

  results = [m9['Bleu_1'], m9['Bleu_2'], m9['ROUGE_L'], m9['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))

  results = [m10['Bleu_1'], m10['Bleu_2'], m10['ROUGE_L'], m10['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))

  results = [m11['Bleu_1'], m11['Bleu_2'], m11['ROUGE_L'], m11['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))

  results = [m12['Bleu_1'], m12['Bleu_2'], m12['ROUGE_L'], m12['METEOR']]
  results = ['{:.2f}'.format(100*r) for r in results]
  print(' & '.join(results))

