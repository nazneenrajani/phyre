import csv
import sys

num2words = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
            6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', \
             19: 'Nineteen', 20: 'Twenty', 21: 'Twenty one', 22: 'Twenty two', \
             25:'Twenty five', 23: 'Twenty three', 24: 'Twenty four', 55: 'Fifty five',\
             38: 'Thirty eight', 43: 'Forty three', 49: 'Forty nine', 44: 'Forty four', \
             42: 'Forty two', 46: 'Forty six', 39: 'Thirty nine'}
def process_initial_file():
    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    objects = {}
    sent = ''
    with open(out_csv, 'w') as o_f:
        with open(in_csv) as f:
            reader = f.readlines()
            for row in reader:
                if row.startswith('object'):
                    print(objects)
                    for k in objects:
                        if objects[k] == 1:
                            sent = sent + 'one ' + k + ' '
                        elif objects[k] < 8:
                            sent = sent + 'few ' + k + ' '
                        elif objects[k] < 20:
                            sent = sent + 'fair number of ' + k + ' '
                        else:
                            sent = sent +  'many ' +  k + ' '
                    s = sent.strip().rsplit(' ', 1)[0]
                    o_f.write(s+ '\n')
                    objects.clear()
                    sent = ''
                    continue
                obj = row.split(',')
                if obj[1] == 'boundary':
                    continue
                if obj[1] == 'circle':
                    radius = obj[10].strip()
                    color = obj[3]
                    state = obj[2]
                    if float(radius) < 10:
                        size = 'small'
                    elif float(radius) < 20:
                        size = 'medium sized'
                    else:
                        size = 'big'
                    temp_sent = size + ' ' + state.lower() + ' ' + color.lower() + ' ball and'
                    if temp_sent in objects:
                        objects[temp_sent] = objects[temp_sent] + 1
                    else:
                        objects[temp_sent] = 1
                if obj[1] == 'jar' or obj[1] == 'bar':
                    color = obj[3]
                    state = obj[2]
                    temp_sent = state.lower() + ' ' + color.lower() + ' ' + obj[1] + ' and'
                    if temp_sent in objects:
                        objects[temp_sent] = objects[temp_sent] + 1
                    else:
                        objects[temp_sent] = 1
        o_f.write(sent + '\n')


def process_initial_rep():
    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    objects = {}
    sent = ''
    with open(out_csv, 'w') as o_f:
        with open(in_csv) as f:
            reader = f.readlines()
            for row in reader:
                if row.startswith('object'):
                    print(objects)
                    for k in objects:
                        if objects[k] == 1:
                            sent = sent  + k + ' '
                    s = sent.strip().rsplit(' ', 1)[0]
                    o_f.write(s + '\n')
                    objects.clear()
                    sent = ''
                    continue
                obj = row.split(',')
                if obj[1] == 'boundary':
                    continue
                if obj[1] == 'circle':
                    radius = obj[10].strip()
                    color = obj[3]
                    state = obj[2]
                    if float(radius) < 10:
                        size = 'small'
                    elif float(radius) < 20:
                        size = 'medium sized'
                    else:
                        size = 'big'
                    temp_sent = size + ' ' + state.lower() + ' ' + color.lower() + ' ball and'
                    if temp_sent in objects:
                        objects[temp_sent] = objects[temp_sent] + 1
                    else:
                        objects[temp_sent] = 1
                if obj[1] == 'jar' or obj[1] == 'bar':
                    color = obj[3]
                    state = obj[2]
                    temp_sent = state.lower() + ' ' + color.lower() + ' ' + obj[1] + ' and'
                    if temp_sent in objects:
                        objects[temp_sent] = objects[temp_sent] + 1
                    else:
                        objects[temp_sent] = 1
        o_f.write(sent + '\n')


if __name__ == '__main__':
    #process_initial_file()
    process_initial_rep()