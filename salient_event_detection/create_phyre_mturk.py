import os
import csv
import urllib
import urllib.request
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import collections

def create_phyre_task_salient_event(task_id_path, csv_path):
  data_dir = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs/'

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
    for i in range(31):
      header.append('screen_url_{}'.format(i))
    for i in range(31):
      header.append('time_step_{}'.format(i))

    csv_writer.writerow(header)
    for task_path in all_task_path:
      template, task = task_path
      task_id = '{}:{}'.format(template, task)
      # print('task_id', task_id)
      step_file = os.path.join(data_dir, template, task, 'step.txt')
      goal = all_goals[template]
      # read step file
      screen_urls = []
      time_steps = []
      print(step_file)
      data = urllib.request.urlopen(step_file).read().decode("utf-8")
      for line in data.strip().split('\n'):
        if line:
          screen_url = os.path.join(data_dir, template, task, line)
          screen_urls.append(screen_url)
          time_steps.append(int(line.split('.')[0]))
      print('len', len(screen_urls))
      len_screen_urls.append(len(screen_urls))

      if len(screen_urls) == 0:
        continue
      if len(screen_urls) > 31:
        continue

      num_missing = 31 - len(screen_urls)
      #screen_urls = screen_urls + [screen_urls[-1]] * num_missing
      screen_urls = screen_urls + [''] * num_missing
      #time_steps = time_steps + [time_steps[-1]] * num_missing
      time_steps = time_steps + [-1] * num_missing
      
      csv_writer.writerow([task_id, goal] + screen_urls + time_steps)

  print(len(len_screen_urls), max(len_screen_urls), min(len_screen_urls))
  num_bins = 10
  n, bins, patches = plt.hist(len_screen_urls, num_bins, facecolor='blue', alpha=0.5)
  plt.savefig('num_images.png')
  return


def read_annotation_salient_event_csv(csv_path_list, write_html=False):
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
        for i in range(1,31):
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
        for i in range(30):
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

          for i in range(30):
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


def read_annotation_sentence_csv(csv_path_list, max_len=25, write_html=False):

  vocab = collections.Counter()
  initial_state_description_len = []
  simulation_description_len = []

  sentence_annotation = {}
  # max_len = 0
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
        # max_len = max(max_len, sum(import_labels)+1)

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

  print('simulation_description', len(simulation_description_len), sum(simulation_description_len) / float(len(simulation_description_len)))
  print('initial_state_description', len(initial_state_description_len), sum(initial_state_description_len) / float(len(initial_state_description_len)))
  print('vocab', len(vocab))
  for w, count in vocab.most_common(3):
    print('{}: {}'.format(w, count))
  return sentence_annotation


def create_phyre_task_evaluation(sentence_annotation, csv_path):
  data_dir = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs/'
  data_dir_no_solution = 'https://phyre-nlp.s3.us-east-2.amazonaws.com/data/imgs-no-solution/'

  all_task_path = []
  for template in sentence_annotation:
    for task in sentence_annotation[template]:
      task_path = (template, task)
      all_task_path.append(task_path)

  all_goals = {}
  with open('../goal.txt') as f:
    for line in f:
      template, goal = line.strip().split(':')
      all_goals[template] = goal

  with open(csv_path, 'w') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = ['taskId', 'goal', 'initial_state_description', 'simulation_description']
    for i in range(1, 5):
      header.append('screen_url_{}'.format(i))

    csv_writer.writerow(header)
    for task_path in all_task_path:
      template, task = task_path
      task_id = '{}-{}'.format(template, task)
      print('task_id', task_id)
      goal = all_goals[template]

      initial_state_description = sentence_annotation[template][task]['initial_state_description'].strip().replace('\n', ' ')
      simulation_description = sentence_annotation[template][task]['simulation_description'].strip().replace('\n', ' ')

      screen_urls = [os.path.join(data_dir_no_solution, template, task, 'no-solution-1.png'),
                     os.path.join(data_dir_no_solution, template, task, 'no-solution-2.png'),
                     os.path.join(data_dir, template, task, '0.png'),
                     os.path.join(data_dir_no_solution, template, task, 'no-solution-3.png')]
      
      csv_writer.writerow([task_id, goal, initial_state_description, simulation_description] + screen_urls)
  return


if __name__ == "__main__":
  ############################
  # create_phyre_task_salient_event('../data_split/task_ids_train.txt', '../data_split/train_mturk.csv')
  # create_phyre_task_salient_event('../data_split/task_ids_dev.txt', '../data_split/dev_mturk.csv')
  # create_phyre_task_salient_event('../data_split/task_ids_test.txt', '../data_split/test_mturk.csv')

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
  #   'salient_event_annotation_csv/dev_mturk_annotation_salient_event.csv'], write_html=False)

  ############################
  # read_annotation_sentence_csv(['sentence_annotation_csv/train_mturk_annotation_sentence.csv'], write_html=True)
  # sentence_annotation = read_annotation_sentence_csv(['sentence_annotation_csv/dev_mturk_annotation_sentence.csv'], write_html=False)
  # create_phyre_task_evaluation(sentence_annotation, '../data_split/dev_mturk_evaluate_new.csv')

  sentence_annotation = read_annotation_sentence_csv(['sentence_annotation_csv/recollect.csv'], write_html=False)

  # sentence_annotation = read_annotation_sentence_csv(['sentence_annotation_csv/test_mturk_annotation_sentence.csv'], write_html=False)
  # create_phyre_task_evaluation(sentence_annotation, '../data_split/test_mturk_evaluate.csv')

  # read_annotation_sentence_csv(['sentence_annotation_csv/train_mturk_annotation_sentence.csv',
  #   'sentence_annotation_csv/dev_mturk_annotation_sentence.csv'], write_html=False)
