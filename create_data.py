import os
import random
import csv
import shutil

random.seed(0)

def create_split():
  tasks = {}
  templates = []

  with open('task_ids.txt') as f:
    for line in f:
      template,task = line.strip().split(':')
      print(template,task)
      if template not in tasks:
        tasks[template] = []
        templates.append(template)
      tasks[template].append(task)

  train_tasks = []
  dev_tasks = []
  test_tasks = []
  for template in templates:
    random.shuffle(tasks[template])
    for task in tasks[template][:80]:
      train_tasks.append('{}:{}'.format(template, task))
    for task in tasks[template][80:90]:
      dev_tasks.append('{}:{}'.format(template, task))
    for task in tasks[template][90:]:
      test_tasks.append('{}:{}'.format(template, task))

  with open('task_ids_train.txt', 'w') as f:
    for task_id in train_tasks:
      f.write('{}\n'.format(task_id))

  with open('task_ids_dev.txt', 'w') as f:
    for task_id in dev_tasks:
      f.write('{}\n'.format(task_id))

  with open('task_ids_test.txt', 'w') as f:
    for task_id in test_tasks:
      f.write('{}\n'.format(task_id))


def create_split_annotation():
  train_tasks = []
  with open('data_split/train_mturk.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
      task_id = row['taskId']
      train_tasks.append(task_id)
  with open('data/task_ids_train_annotation.txt', 'w') as f:
    for task_id in train_tasks:
      f.write('{}\n'.format(task_id))

  dev_tasks = []
  with open('data_split/dev_mturk.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
      task_id = row['taskId']
      dev_tasks.append(task_id)
  with open('data/task_ids_dev_annotation.txt', 'w') as f:
    for task_id in dev_tasks:
      f.write('{}\n'.format(task_id))

  test_tasks = []
  with open('data_split/test_mturk.csv', 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
      task_id = row['taskId']
      test_tasks.append(task_id)
  with open('data/task_ids_test_annotation.txt', 'w') as f:
    for task_id in test_tasks:
      f.write('{}\n'.format(task_id))


def create_data():
  tasks = {}
  templates = []

  with open('task_ids.txt') as f:
    for line in f:
      template,task = line.strip().split(':')
      print(template,task)
      template = int(template)
      task = int(task)
      if template not in tasks:
        tasks[template] = []
        templates.append(template)
      tasks[template].append(task)

  num_objects = []
  num_frames = []
  num_collisions = []

  for template in templates:
    template_path = "data/solution_csv_json_imgs/{:05d}".format(template)
    # if os.path.isdir(template_path):
    #   shutil.rmtree(template_path)
    # os.mkdir(template_path)
    for task in tasks[template]:
      task_path = "data/solution_csv_json_imgs/{:05d}/{:03d}".format(template,task)
      # if os.path.isdir(task_path):
      #   shutil.rmtree(task_path)
      # os.mkdir(task_path)
      try:
        # filtered_list.json
        src_file = os.path.join('/home/lily/jw2499/phyre/data', 'filtered_jsons', "{:05d}/{:03d}_list.json".format(template,task))
        dst_file = os.path.join(task_path, 'filtered_list.json')
        # shutil.copyfile(src_file, dst_file)
        # print(src_file)
        # print(dst_file)

        # filtered_list.csv
        src_file = os.path.join('/home/lily/jw2499/phyre/data', 'filtered_csvs', "{:05d}/{:03d}_list.csv".format(template,task))
        dst_file = os.path.join(task_path, 'filtered_list.csv')
        # shutil.copyfile(src_file, dst_file)
        # print(src_file)
        # print(dst_file)

        # initial.json
        src_file = os.path.join('/home/lily/jw2499/phyre/data', 'initial_jsons', "{:05d}/{:03d}.json".format(template,task))
        dst_file = os.path.join(task_path, 'initial.json')
        # shutil.copyfile(src_file, dst_file)
        # print(src_file)
        # print(dst_file)

        # initial.csv
        src_file = os.path.join('/home/lily/jw2499/phyre/data', 'initial_csvs', "{:05d}/{:03d}.csv".format(template,task))
        dst_file = os.path.join(task_path, 'initial.csv')
        # shutil.copyfile(src_file, dst_file)
        # print(src_file)
        # print(dst_file)
        with open(src_file) as f:
          lines = f.readlines()
          num_objects.append(len(lines) - 1)

        # imgs/
        src = os.path.join('/home/lily/jw2499/phyre/data', 'imgs', "{:05d}/{:03d}/".format(template,task))
        dst = os.path.join(task_path, 'imgs/')
        # shutil.copytree(src, dst)
        # print(src)
        # print(dst)
        with open(os.path.join(src, 'step.txt')) as f:
          lines = f.readlines()
          num_frame = int(lines[-1].split('.')[0])
          num_frames.append(num_frame)
          num_collision = len(lines) - 1
          num_collisions.append(num_collision)
        
      except Exception as e:
        print("{:05d}:{:03d}".format(template,task))

  print('num_objects', len(num_objects), sum(num_objects)/float(len(num_objects)))
  print('num_frames', len(num_frames), sum(num_frames)/float(len(num_frames)))
  print('num_collisions', len(num_collisions), sum(num_collisions)/float(len(num_collisions)))

if __name__ == "__main__":
  # create_split_annotation()
  # create_data()
  # create_annotation_data()
