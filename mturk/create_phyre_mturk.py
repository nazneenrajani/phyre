import os
import csv
import urllib
import urllib.request
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import collections
import random
random.seed(0)

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

def create_phyre_task_salient_event(task_id_path, csv_path, maxlen=40):
  data_dir = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs/'

  local_data_dir = '/home/lily/jw2499/phyre/data/imgs/'

  all_task_path = []
  with open(task_id_path) as f:
    for line in f:
      template, task = line.strip().split(':')
      # print(template, task)
      task_path = (template, task)
      all_task_path.append(task_path)

  all_goals = {}
  with open('../goal.txt') as f:
    for line in f:
      template, goal = line.strip().split(':')
      all_goals[template] = goal

  len_screen_urls = []

  with open(csv_path, 'w') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['taskId', 'goal']
    for i in range(maxlen+1):
      header.append('screen_url_{}'.format(i))
    for i in range(maxlen+1):
      header.append('time_step_{}'.format(i))

    csv_writer.writerow(header)
    for task_path in all_task_path:
      template, task = task_path
      task_id = '{}:{}'.format(template, task)
      # print('task_id', task_id)
      step_file = os.path.join(local_data_dir, template, task, 'step.txt')
      goal = all_goals[template]
      # read step file
      screen_urls = []
      time_steps = []
      print(step_file)
      # data = urllib.request.urlopen(step_file).read().decode("utf-8")
      data = open(step_file).read()
      for line in data.strip().split('\n'):
        if line:
          screen_url = os.path.join(data_dir, template, task, line)
          screen_urls.append(screen_url)
          time_steps.append(int(line.split('.')[0]))
      print('len', len(screen_urls))
      len_screen_urls.append(len(screen_urls))

      # if len(screen_urls) == 0:
      #   continue

      if len(screen_urls) <= 31:
        continue

      if len(screen_urls) > maxlen+1:
        continue

      num_missing = maxlen+1 - len(screen_urls)
      screen_urls = screen_urls + [screen_urls[-1]] * num_missing
      # screen_urls = screen_urls + [''] * num_missing
      time_steps = time_steps + [time_steps[-1]] * num_missing
      # time_steps = time_steps + [-1] * num_missing
      
      csv_writer.writerow([task_id, goal] + screen_urls + time_steps)

  print(len(len_screen_urls), max(len_screen_urls), min(len_screen_urls))
  num_bins = 10
  n, bins, patches = plt.hist(len_screen_urls, num_bins, facecolor='blue', alpha=0.5)
  plt.savefig('num_images.png')
  return


def read_annotation_salient_event_csv(csv_path_list, maxlen=40, write_html=False):
  salient_event_annotation = {}
  max_len = 0

  num_time_steps = []
  num_important_time_steps = []

  for csv_path in csv_path_list:
    with open(csv_path, 'r') as f:
      csv_reader = csv.DictReader(f)
      for row in csv_reader:
        # print(row)
        task_id = row['Input.taskId']
        template, task = task_id.split(':')
        if template not in salient_event_annotation:
          salient_event_annotation[template] = {}
        salient_event_annotation[template][task] = {}
        hitid = row['HITId']
        screen_url_0 = row['Input.screen_url_0']
        screen_urls = []
        time_steps = []
        import_labels = []
        for i in range(1, maxlen+1):
          screen_urls.append(row['Input.screen_url_{}'.format(i)])
          time_steps.append(row['Input.time_step_{}'.format(i)])
          import_labels.append(int(row['Answer.screen_{}_important'.format(i)]))

        salient_event_annotation[template][task]['screen_urls'] = screen_urls
        salient_event_annotation[template][task]['time_steps'] = time_steps
        salient_event_annotation[template][task]['import_labels'] = import_labels
        max_len = max(max_len, sum(import_labels)+1)
        if sum(import_labels)+1 == 26:
          print(task_id)

        num_time_step = len(set(time_steps))
        num_time_steps.append(num_time_step)
        num_important_time_steps.append(sum(import_labels[:num_time_step]))

        important_time_steps = []
        for i in range(len(import_labels)):
          if import_labels[i] == 1:
            important_time_steps.append(int(time_steps[i]))
        important_time_steps = sorted(list(set(important_time_steps)))
        with open('../data/annotation/salient_event/{:05d}-{:03d}.txt'.format(int(template), int(task)), 'w') as f:
          for t in important_time_steps:
            f.write('{}\n'.format(t))

        if not write_html:
          continue

        with open('salient_event_annotation/{}.html'.format(task_id), 'w') as f:
          html_content = """ <!DOCTYPE html>
          <html lang="en">
          <head>
          <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
          <style>
          * {
            box-sizing: border-box;
          }

          .column {
            float: left;
            width: 20%;
            padding: 0px;
            text-align: center
          }

          .screenshot {
            width: 20%;
            height: 20%
          }

          /* Clearfix (clear floats) */
          .row::after {
            content: "";
            clear: both;
            display: table;
          }
          </style>
          </head>

          <body>
          <h3> 2. Initial State with Red Ball Added </h3> """
          f.write(html_content+'\n')

          f.write('{}<br>'.format(hitid))

          html_content = '<div class="row"><div class="column"><img src="{}" alt="screen_0" style="width:100%"></div></div>'.format(screen_url_0)
          f.write(html_content+'\n')

          html_content = '<h3> 3. Screenshots of Collisions </h3>\n<div class="row">'
          f.write(html_content+'\n')

          for i in range(len(import_labels)):
            if int(import_labels[i]) == 0:
              # html_content = '<div class="column"><img src="{}" alt="screen_1" style="width:100%"><p>Time Step {}<br /> <label><input type="radio" name="screen_{}_important" value="1" disabled />Yes</label><label><input type="radio" name="screen_{}_important" value="0" checked />No</label></p></div>'.format(screen_urls[i], time_steps[i], i, i)
              html_content = '<div class="column"><img src="{}" alt="screen_1" style="width:100%"><p>Time Step {}<br /> </p></div>'.format(screen_urls[i], time_steps[i], i, i)
            else:
              html_content = '<div class="column"><img src="{}" alt="screen_1" style="width:100%"><p><strong style="color: red;">Time Step {}</strong><br /> </p></div>'.format(screen_urls[i], time_steps[i], i, i)
            f.write(html_content+'\n')

          html_content = '</div> </body></html>'
          f.write(html_content+'\n')


  print('num_time_steps', len(num_time_steps), sum(num_time_steps)/float(len(num_time_steps)))
  print('num_important_time_steps', len(num_important_time_steps), sum(num_important_time_steps)/float(len(num_important_time_steps)))
  return salient_event_annotation, max_len


def create_phyre_task_sentence(salient_event_annotation, max_len, csv_path):
  data_dir = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs/'

  # all_task_path = []
  # with open(task_id_path) as f:
  #   for line in f:
  #     template, task = line.strip().split(':')
  #     print(template, task)
  #     task_path = (template, task)
  #     all_task_path.append(task_path)
  all_task_path = []
  for template in salient_event_annotation:
    for task in salient_event_annotation[template]:
      task_path = (template, task)
      all_task_path.append(task_path)

  all_goals = {}
  with open('../goal.txt') as f:
    for line in f:
      template, goal = line.strip().split(':')
      all_goals[template] = goal

  with open(csv_path, 'w') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['taskId', 'goal', 'demo']
    for i in range(max_len):
      header.append('screen_url_{}'.format(i))
    for i in range(max_len):
      header.append('time_step_{}'.format(i))

    csv_writer.writerow(header)
    for task_path in all_task_path:
      template, task = task_path
      task_id = '{}-{}'.format(template, task)
      # print('task_id', task_id)
      goal = all_goals[template]
      demo = os.path.join(data_dir, template, task, 'collisions.gif')

      # step_file = os.path.join(data_dir, template, task, 'step.txt')      
      # read step file
      all_screen_urls = salient_event_annotation[template][task]['screen_urls']
      all_time_steps = salient_event_annotation[template][task]['time_steps']
      import_labels = salient_event_annotation[template][task]['import_labels']

      assert len(all_screen_urls) == len(all_time_steps) == len(import_labels)

      screen_urls = [os.path.join(data_dir, template, task, '0.png')]
      time_steps = [0]
      for screen_url, time_step, important_label in zip(all_screen_urls, all_time_steps, import_labels):
        if important_label == 1:
          screen_urls.append(screen_url)
          time_steps.append(time_step)

      num_missing = max_len - len(screen_urls)
      screen_urls = screen_urls + [screen_urls[-1]] * num_missing
      # screen_urls = screen_urls + [''] * num_missing
      time_steps = time_steps + [time_steps[-1]] * num_missing
      # time_steps = time_steps + [-1] * num_missing
      
      csv_writer.writerow([task_id, goal, demo] + screen_urls + time_steps)
  return


def read_annotation_sentence_csv(sentence_annotation, csv_path_list, max_len=25, write=False, write_html=False):

  vocab = collections.Counter()
  initial_state_description_len = []
  simulation_description_len = []

  # sentence_annotation = {}
  tasks = []
  bad_tasks = []
  for csv_path in csv_path_list:
    with open(csv_path, 'r') as f:
      csv_reader = csv.DictReader(f)
      for row in csv_reader:
        # print(row)
        task_id = row['Input.taskId']
        
        template, task = task_id.split('-')
        if template not in sentence_annotation:
          sentence_annotation[template] = {}
        sentence_annotation[template][task] = {}
        hitid = row['HITId']
        screen_url_0 = row['Input.screen_url_0']
        demo = row['Input.demo']

        screen_urls = []
        time_steps = []
        for i in range(1, max_len+1):
          screen_urls.append(row['Input.screen_url_{}'.format(i)])
          time_steps.append(row['Input.time_step_{}'.format(i)])

        sentence_annotation[template][task]['screen_urls'] = screen_urls
        sentence_annotation[template][task]['time_steps'] = time_steps

        initial_state_description = row['Answer.initial_state_description']
        simulation_description = row['Answer.simulation_description']
        sentence_annotation[template][task]['initial_state_description'] = initial_state_description
        sentence_annotation[template][task]['simulation_description'] = simulation_description

        initial_state_description_words = initial_state_description.strip().split()
        for w in initial_state_description_words:
          vocab[w] += 1
        initial_state_description_len.append(len(initial_state_description_words))

        simulation_description_words = simulation_description.strip().split()
        for w in simulation_description_words:
          vocab[w] += 1
        simulation_description_len.append(len(simulation_description_words))

        # print('{}:{}'.format(template,task))
        if row['AssignmentStatus'] == 'Rejected':
          continue
        
        tasks.append('{}:{}'.format(template, task))

        example_str = 'The black platform is in the middle, with a distance to the right wall slightly larger than the size of the green ball.The green ball is hovering over the black platform.The red ball is placed left below the green ball.The purple bar is at the bottom.'
        if example_str == initial_state_description:
          print(task_id)
          print(initial_state_description)
          bad_tasks.append('{}:{}'.format(template, task))

        # if example_str == initial_state_description or 'good' in initial_state_description or 'stype' in initial_state_description:
        if 'good' in initial_state_description or 'stype' in initial_state_description or '' == initial_state_description.strip():
          print(task_id)
          print(initial_state_description)
          # initial_state_description = initial_state_description.replace(example_str +' |', '')
          # print(initial_state_description)
          # print()
          bad_tasks.append('{}:{}'.format(template, task))

        example_str = 'Both green ball and red ball fall down. The red ball lands on the black platform first, and the green ball falls onto the red ball. The green ball is then bounced to right, lands on the black platform, and moves to the right. The green ball falls through the black platform and finally lands on the purple bar at the bottom.'
        if example_str == simulation_description:
          print(task_id)
          print(simulation_description)
          bad_tasks.append('{}:{}'.format(template, task))
        if 'good' in simulation_description or 'stype' in simulation_description or '' == simulation_description.strip():
          print(task_id)
          print(simulation_description)
          # simulation_description = simulation_description.replace(example_str +'|', '')
          # print(simulation_description)
          # print()
          bad_tasks.append('{}:{}'.format(template, task))

        # if task_id == '00020-045':
        #   print(initial_state_description)
        #   print(simulation_description)

        if not write:
          continue

        with open('../data/annotation/initial_state_description/{:05d}-{:03d}.txt'.format(int(template), int(task)), 'w') as f:
          f.write('{}\n'.format(initial_state_description.strip().replace('\n', ' ')))
        with open('../data/annotation/simulation_description/{:05d}-{:03d}.txt'.format(int(template), int(task)), 'w') as f:
          f.write('{}\n'.format(simulation_description.strip().replace('\n', ' ')))
          
        if not write_html:
          continue

        with open('sentence_annotation/{}.html'.format(task_id), 'w') as f:
          html_content = """ <!DOCTYPE html>
          <html lang="en">
          <head>
          <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
          <style>
          * {
            box-sizing: border-box;
          }

          .column {
            float: left;
            width: 20%;
            padding: 0px;
            text-align: center
          }

          .screenshot {
            width: 20%;
          }

          /* Clearfix (clear floats) */
          .row::after {
            content: "";
            clear: both;
            display: table;
          }
          </style>
          </head>

          <body>
          <h3> 2. Initial State with Red Ball Added </h3> """
          f.write(html_content+'\n')

          f.write('{}<br>'.format(hitid))

          html_content = '<div class="row"><div class="column"><img src="{}" alt="screen_0" style="width:100%"></div></div>'.format(screen_url_0)
          f.write(html_content+'\n')


          html_content = '<h3> 3. Demo </h3>'
          f.write(html_content+'\n')
          html_content = '<div class="row"><div class="column"><img src="{}" alt="demo" style="width:100%"></div></div>'.format(demo)
          f.write(html_content+'\n')

          html_content = '<h3> 4. Screenshots of Important Collisions </h3>\n<div class="row">'
          f.write(html_content+'\n')

          for i in range(max_len):
            html_content = '<div class="column"><img src="{}" alt="screen_1" style="width:100%"><p><strong style="color: red;">Time Step {}</strong><br /> </p></div>'.format(screen_urls[i], time_steps[i])
            f.write(html_content+'\n')

          #
          html_content = '<p><label>1. Describe the initial state in your own words. You need to describe the object details (shape, color, position).<br /><textarea readonly id="initial_state_description" name="initial_state_description" rows="4" cols="80" onclick="assertNotPreviewMode();">{}</textarea></label></p>'.format(initial_state_description)
          f.write(html_content+'\n')

          html_content = '<p><label>2. Describe the whole process in your own words. You need to describe the collision details (which two objects collide, in which direction, to have what effect).<br /><textarea readonly id="simulation_description" name="simulation_description" rows="4" cols="80" onclick="assertNotPreviewMode();">{}</textarea></label></p>'.format(simulation_description)
          f.write(html_content+'\n')

          html_content = '</div> </body></html>'
          f.write(html_content+'\n')

  # print('simulation_description', len(simulation_description_len), sum(simulation_description_len) / float(len(simulation_description_len)))
  # print('initial_state_description', len(initial_state_description_len), sum(initial_state_description_len) / float(len(initial_state_description_len)))
  # print('vocab', len(vocab))
  # for w, count in vocab.most_common(3):
  #   print('{}: {}'.format(w, count))

  print('tasks', len(set(tasks)), len(tasks))
  print('bad_tasks', len(set(bad_tasks)))
  # print('\n'.join([t for t in tasks if t not in bad_tasks]))
  print(set(bad_tasks))
  return sentence_annotation


def create_phyre_task_evaluation(all_task_path, sentence_annotation, csv_path, to_evaluate='initial_state_description'):
  data_dir = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs/'
  data_dir_no_solution = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs-no-solution/'

  # all_task_path = []
  # for template in sentence_annotation:
  #   for task in sentence_annotation[template]:
  #     task_path = (template, task)
  #     all_task_path.append(task_path)

  all_goals = {}
  with open('../goal.txt') as f:
    for line in f:
      template, goal = line.strip().split(':')
      all_goals[template] = goal

  with open(csv_path, 'w') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    if to_evaluate == 'initial_state_description':
      header = ['taskId', 'initial_state_description', 'answer_idx']
    elif to_evaluate == 'simulation_description':
      header = ['taskId', 'goal', 'simulation_description', 'answer_idx']

    for i in range(1, 5):
      # 1,2,3,4
      header.append('screen_url_{}'.format(i))

    csv_writer.writerow(header)
    for task_path in all_task_path:
      template, task = task_path
      task_id = '{}-{}'.format(template, task)
      # print('task_id', task_id)
      goal = all_goals[template]
      
      if to_evaluate == 'initial_state_description':
        initial_state_description = sentence_annotation[template][task]['initial_state_description'].strip().replace('\n', ' ').replace("'", ' ')
        other_task_path = [t for t in all_task_path if t[0] != template]
        distractors = random.choices(other_task_path, k=3)
        screen_urls = [os.path.join(data_dir, distractors[0][0], distractors[0][1], '0.png'),
                       os.path.join(data_dir, distractors[1][0], distractors[1][1], '0.png'),
                       os.path.join(data_dir, template, task, '0.png'),
                       os.path.join(data_dir, distractors[2][0], distractors[2][1], '0.png')]
        random.shuffle(screen_urls)
        answer_idx = 1 + screen_urls.index(os.path.join(data_dir, template, task, '0.png'))
        assert answer_idx >= 1
        # print(initial_state_description)
        csv_writer.writerow([task_id, initial_state_description, answer_idx] + screen_urls)

      elif to_evaluate == 'simulation_description':
        simulation_description = sentence_annotation[template][task]['simulation_description'].strip().replace('\n', ' ').replace("'", ' ')
        screen_urls = [os.path.join(data_dir_no_solution, template, task, 'no-solution-1.png'),
                       os.path.join(data_dir_no_solution, template, task, 'no-solution-2.png'),
                       os.path.join(data_dir, template, task, '0.png'),
                       os.path.join(data_dir_no_solution, template, task, 'no-solution-3.png')]
        random.shuffle(screen_urls)
        answer_idx = 1 + screen_urls.index(os.path.join(data_dir, template, task, '0.png'))
        assert answer_idx >= 1
        csv_writer.writerow([task_id, goal, simulation_description, answer_idx] + screen_urls)
  return


def read_task_id_list(task_id_path):
  all_task_path = []
  with open(task_id_path) as f:
    for line in f:
      template, task = line.strip().split(':')
      # print(template, task)
      task_path = (template, task)
      all_task_path.append(task_path)
  return all_task_path


def read_evaluation_csv(csv_path_list):

  available_test_id = read_task_id_list('../data_cp/split/task_ids_test_annotation_0.txt')
  total = 0
  correct = {}

  for csv_path in csv_path_list:
    with open(csv_path, 'r') as f:
      csv_reader = csv.DictReader(f)
      for row in csv_reader:
        # total += 1
        task_id = row["Input.taskId"]
        tempalte, task = task_id.split('-')
        if (tempalte, task) not in available_test_id:
          continue
        if task_id not in correct:
          correct[task_id] = 0
        if row['Answer.initial_state_select'] == row['Input.answer_idx']:
          correct[task_id] += 1

  total = len(correct)
  correct_cnt = 0
  for task_id in correct:
    if correct[task_id] >= 2:
      correct_cnt += 1
  print(total, '{:.1f}'.format(100*correct_cnt/float(total)))
  return

def read_evaluation_csv_physics(csv_path_list):
  total = 0
  gravity = {}
  friction = {}
  collision = {}

  for csv_path in csv_path_list:
    with open(csv_path, 'r') as f:
      csv_reader = csv.DictReader(f)
      for row in csv_reader:
        # total += 1
        # print(row)
        task_id = row["Input.taskId"]
        if task_id not in gravity:
          gravity[task_id] = 0
          friction[task_id] = 0
          collision[task_id] = 0

        if row['Answer.gravity'] == '1':
          gravity[task_id] += 1
        if row['Answer.friction'] == '1':
          friction[task_id] += 1
        if row['Answer.collision'] == '1':
          collision[task_id] += 1

  gravity_cnt = 0
  friction_cnt = 0
  collision_cnt = 0
  total = len(gravity)
  for task_id in gravity:
    if gravity[task_id] >= 2:
      gravity_cnt += 1
    if friction[task_id] >= 2:
      friction_cnt += 1
    if collision[task_id] >= 2:
      collision_cnt += 1

  print('{:.1f}'.format(100*gravity_cnt/float(total)), '{:.1f}'.format(100*friction_cnt/float(total)), '{:.1f}'.format(100*collision_cnt/float(total)))

  return

if __name__ == "__main__":
  ############################
  # create_phyre_task_salient_event('../data_split/task_ids_train.txt', '../data_split/train_mturk.csv')
  # create_phyre_task_salient_event('../data_split/task_ids_dev.txt', '../data_split/dev_mturk.csv')
  # create_phyre_task_salient_event('../data_split/task_ids_test.txt', '../data_split/test_mturk.csv')

  # create_phyre_task_salient_event('../data_split/task_ids_train.txt', '../data_split/train_mturk_salient_event_30-40.csv')
  # create_phyre_task_salient_event('../data_split/task_ids_dev.txt', '../data_split/dev_mturk_salient_event_30-40.csv')
  # create_phyre_task_salient_event('../data_split/task_ids_test.txt', '../data_split/test_mturk_salient_event_30-40.csv')

  ############################
  # salient_event_annotation, max_len = read_annotation_salient_event_csv(['train_mturk_annotation_salient_event.csv'])
  # create_phyre_task_sentence(salient_event_annotation, max_len, '../data_split/train_mturk_sentence.csv')
  # salient_event_annotation, max_len = read_annotation_salient_event_csv(['dev_mturk_annotation_salient_event.csv'])
  # max_len = 26
  # create_phyre_task_sentence(salient_event_annotation, max_len, '../data_split/dev_mturk_sentence.csv')
  # salient_event_annotation, max_len = read_annotation_salient_event_csv(['salient_event_annotation_csv/test_mturk_annotation_salient_event.csv'])
  # max_len = 26
  # create_phyre_task_sentence(salient_event_annotation, max_len, '../data_split/test_mturk_sentence.csv')

  # read_annotation_salient_event_csv(['salient_event_annotation_csv/train_mturk_annotation_salient_event.csv',
    # 'salient_event_annotation_csv/dev_mturk_annotation_salient_event.csv'], write_html=False)

  # read_annotation_salient_event_csv(['salient_event_annotation_csv/recollect_salient_event.csv'], write_html=False)

  # salient_event_annotation, max_len = read_annotation_salient_event_csv(
    # ['salient_event_annotation_csv/train_mturk_annotation_salient_event_30-40.csv'], maxlen=40, write_html=False)
  # print(max_len)
  # max_len = 35
  # create_phyre_task_sentence(salient_event_annotation, max_len, '../data_split/train_mturk_sentence_30-40.csv')

  # salient_event_annotation, max_len = read_annotation_salient_event_csv(
  #   ['salient_event_annotation_csv/dev_mturk_annotation_salient_event_30-40.csv'], maxlen=40, write_html=False)
  # print(max_len)
  # max_len = 35
  # create_phyre_task_sentence(salient_event_annotation, max_len, '../data_split/dev_mturk_sentence_30-40.csv')

  # salient_event_annotation, max_len = read_annotation_salient_event_csv(
  #   ['salient_event_annotation_csv/test_mturk_annotation_salient_event_30-40.csv'], maxlen=40, write_html=False)
  # print(max_len)
  # max_len = 35
  # create_phyre_task_sentence(salient_event_annotation, max_len, '../data_split/test_mturk_sentence_30-40.csv')

  ############################
  # read_annotation_sentence_csv(['sentence_annotation_csv/train_mturk_annotation_sentence.csv'], write_html=False)
  # read_annotation_sentence_csv(['sentence_annotation_csv/dev_mturk_annotation_sentence.csv'], write_html=False)
  # read_annotation_sentence_csv(['sentence_annotation_csv/test_mturk_annotation_sentence.csv'], write_html=False)
  # read_annotation_sentence_csv(['sentence_annotation_csv/recollect.csv'], write_html=False)
  # read_annotation_sentence_csv(['sentence_annotation_csv/recollect_2.csv'])

  # read_annotation_sentence_csv(['sentence_annotation_csv/train_mturk_annotation_sentence_30-40.csv'], write=False)
  # read_annotation_sentence_csv(['sentence_annotation_csv/dev_mturk_annotation_sentence_30-40.csv'], write=False)
  # read_annotation_sentence_csv(['sentence_annotation_csv/test_mturk_annotation_sentence_30-40.csv'], write=False)

########
  # dev_ids = read_task_id_list('../data/split/task_ids_dev_annotation.txt')
  # sentence_annotation = {}
  # sentence_annotation = read_annotation_sentence_csv(sentence_annotation, ['sentence_annotation_csv/dev_mturk_annotation_sentence.csv'])
  # sentence_annotation = read_annotation_sentence_csv(sentence_annotation, ['sentence_annotation_csv/dev_mturk_annotation_sentence_30-40.csv'])
  # create_phyre_task_evaluation(dev_ids, sentence_annotation, '../data_split/dev_mturk_evaluate_initial_state_description_annotation.csv', to_evaluate='initial_state_description')
  # create_phyre_task_evaluation(dev_ids, sentence_annotation, '../data_split/dev_mturk_evaluate_simulation_description_annotation.csv', to_evaluate='simulation_description')

########
  # test_ids = read_task_id_list('../data/split/task_ids_test_annotation.txt')
  # sentence_annotation = {}
  # sentence_annotation = read_annotation_sentence_csv(sentence_annotation, ['sentence_annotation_csv/test_mturk_annotation_sentence.csv'])
  # sentence_annotation = read_annotation_sentence_csv(sentence_annotation, ['sentence_annotation_csv/test_mturk_annotation_sentence_30-40.csv'])
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_initial_state_description_annotation.csv', to_evaluate='initial_state_description')
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_simulation_description_annotation.csv', to_evaluate='simulation_description')

########
  # task_id_path = '../data/split/task_ids_dev_annotation.txt'
  # dev_ids = read_task_id_list(task_id_path)

  # task_id_path = '../data/split/task_ids_test_annotation.txt'
  # test_ids = read_task_id_list(task_id_path)

  # f = '../data2text-entity-py/phyre-data/gen/initial_state_description/phyre_lr_0.15_epoch_100/dev_test_phyre_lr_0.15_epoch_100_ppl_1.14_acc_95.61_e125.pt-beam5_gens.txt'
  # f = '../data2text-entity-py/phyre-data/gen/initial_state_description/phyre_lr_0.15_epoch_100_brnn/dev_test_phyre_lr_0.15_epoch_100_brnn_ppl_1.14_acc_95.67_e125.pt-beam5_gens.txt'
  # dev_system_output_initial_state_description, test_system_output_initial_state_description = read_system_output(dev_ids, test_ids, f)

  # f = '../data2text-entity-py/phyre-data/gen/simulation_description/phyre_lr_0.15_epoch_100/dev_test_phyre_lr_0.15_epoch_100_ppl_1.13_acc_96.13_e125.pt-beam5_gens.txt'
  # f = '../data2text-entity-py/phyre-data/gen/simulation_description/phyre_lr_0.15_epoch_100_brnn/dev_test_phyre_lr_0.15_epoch_100_brnn_ppl_1.14_acc_96.07_e125.pt-beam5_gens.txt'
  # dev_system_output_simulation_description, test_system_output_simulation_description = read_system_output(dev_ids, test_ids, f)


  # f = '../GPT/initial_1.txt'
  # test_gpt_initial_1 = read_gpt_system_output(test_ids, f)
  # test_system_output_initial_state_description = test_gpt_initial_1
  # f = '../GPT/simulation_1.txt'
  # test_gpt_simulation_1 = read_gpt_system_output(test_ids, f)
  # test_system_output_simulation_description = test_gpt_simulation_1

  # assert len(test_ids) == len(test_system_output_initial_state_description) == len(test_system_output_simulation_description)
  # sentence_annotation = {}
  # for i in range(len(test_ids)):
  #   template, task = test_ids[i]
  #   if template not in sentence_annotation:
  #     sentence_annotation[template] = {}
  #   sentence_annotation[template][task] = {}
  #   initial_state_description = test_system_output_initial_state_description[i]
  #   simulation_description = test_system_output_simulation_description[i]
  #   sentence_annotation[template][task]['initial_state_description'] = initial_state_description
  #   sentence_annotation[template][task]['simulation_description'] = simulation_description
  
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_initial_state_description_gpt.csv', to_evaluate='initial_state_description')
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_simulation_description_gpt.csv', to_evaluate='simulation_description')
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_initial_state_description_avg.csv', to_evaluate='initial_state_description')
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_simulation_description_avg.csv', to_evaluate='simulation_description')
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_initial_state_description_bilstm.csv', to_evaluate='initial_state_description')
  # create_phyre_task_evaluation(test_ids, sentence_annotation, '../data_split/test_mturk_evaluate_simulation_description_bilstm.csv', to_evaluate='simulation_description')

  # sentence_annotation = read_annotation_sentence_csv(['sentence_annotation_csv/recollect.csv'], write_html=False)

  # sentence_annotation = read_annotation_sentence_csv(['sentence_annotation_csv/test_mturk_annotation_sentence.csv'])
  # create_phyre_task_evaluation(sentence_annotation, '../data_split/test_mturk_evaluate_annotation.csv')

  # read_annotation_sentence_csv(['sentence_annotation_csv/train_mturk_annotation_sentence.csv',
  #   'sentence_annotation_csv/dev_mturk_annotation_sentence.csv'], write_html=False)

  read_evaluation_csv(['evaluation_csv/initial_gpt.csv'])
  read_evaluation_csv(['evaluation_csv/initial_avg.csv'])
  read_evaluation_csv(['evaluation_csv/initial_bilstm.csv'])
  read_evaluation_csv(['evaluation_csv/initial_annotation.csv'])

  print()

  read_evaluation_csv(['evaluation_csv/simulation_gpt.csv'])
  read_evaluation_csv(['evaluation_csv/simulation_avg.csv'])
  read_evaluation_csv(['evaluation_csv/simulation_bilstm.csv'])
  read_evaluation_csv(['evaluation_csv/simulation_annotation.csv'])

  print()
  read_evaluation_csv_physics(['evaluation_csv/physics_gpt.csv'])
  read_evaluation_csv_physics(['evaluation_csv/physics_avg.csv'])
  read_evaluation_csv_physics(['evaluation_csv/physics_bilstm.csv'])
  read_evaluation_csv_physics(['evaluation_csv/physics_annotation.csv'])


