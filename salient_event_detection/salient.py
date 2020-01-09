import os
import csv
import urllib
import urllib.request

from sklearn.metrics import classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from create_phyre_mturk import read_annotation_salient_event_csv as read_csv

train_raw, train_len = read_csv(['salient_event_annotation_csv\\train_mturk_annotation_salient_event.csv'])
test_raw, test_len = read_csv(['salient_event_annotation_csv\\test_mturk_annotation_salient_event.csv'])

def clean_output(raw, fake=False):
    x = np.zeros(shape=(0,13), dtype='float')
    y = np.zeros(shape=(0,1), dtype='int')
    for template in raw:
        print("Template " + str(template))
        sub_arr = train_raw[''+template]
        for task in sub_arr:
            temp = np.zeros(shape=(0,13), dtype='float')
            times = set({})

            csv_path = 'filtered_csvs\\'+str(template)+"\\"+str(task)+"_list.csv"
            with open(csv_path, 'r') as f:
              csv_reader = csv.reader(f)
              header = True
              for row in csv_reader:
                  if(header==True): header = False
                  else:
                      time, is_collision = row[1], row[11]
                      if(is_collision=='True'):
                          type = row[12]
                          if(type=='begin'):
                              if(not time in times):
                                  times.add(time)
                                  id_1, x_1, y_1 = row[13], row[16], row[17]
                                  x_vel_1, y_vel_1, angle_1 = row[18], row[19], row[20]
                                  id_2, x_2, y_2 = row[21], row[24], row[25]
                                  x_vel_2, y_vel_2, angle_2 = row[26], row[27], row[28]
                                  new = np.array([[time, id_1, x_1, y_1, x_vel_1, y_vel_1, angle_1,
                                      id_2, x_2, y_2, x_vel_2, y_vel_2, angle_2]], dtype='float')

                                  temp = np.append(temp, new, axis=0)

            print("Task " + str(task))
            sub_arr2 = sub_arr[''+task]
            for i in range(len(set(sub_arr2['time_steps']))):
                found = False
                time = sub_arr2['time_steps'][i]
                id = str(template)+"_"+str(task)+"_"+str(time)

                for i in range(temp.shape[0]):
                    if(temp[i][0]==float(time) and found==False):
                        found = True
                        x = np.append(x, np.array([temp[i]], dtype='float'), axis=0)
                        y = np.append(y, np.array([[int(sub_arr2['import_labels'][i])]], dtype='int'), axis=0)
                        i = temp.shape[0]

    return [x, y]

X_train, y_train = clean_output(train_raw)
X_test, y_test = clean_output(test_raw)

'''POSITIVE CLASSIFIER'''
preds = np.ones(shape=y_test.shape, dtype='float')

confusion = confusion_matrix(y_test, preds)
report = classification_report(y_test, preds)

print("POSITIVE CLASSIFIER")
print(confusion)
print(report)
print()

'''DECISION TREE CLASSIFIER'''
dtc = DecisionTreeClassifier()
dtc.fit(X_train, y_train)
preds = dtc.predict(X_test)

confusion = confusion_matrix(y_test, preds)
report = classification_report(y_test, preds)
importance = list(dtc.feature_importances_)

print("DECISION TREE CLASSIFIER")
print(confusion)
print(report)
print(importance)
print()

'''SUPPORT VECTOR CLASSIFIER'''
svc = SVC(gamma=2, C=1)
svc.fit(X_train, y_train)
preds = svc.predict(X_test)

confusion = confusion_matrix(y_test, preds)
report = classification_report(y_test, preds)

print("SUPPORT VECTOR CLASSIFIER")
print(confusion)
print(report)
print()
