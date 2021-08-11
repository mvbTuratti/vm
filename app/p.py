import os
import csv
import datetime

file = "logpesos.csv"
data = [datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),1]
def older_than_last(time):
    rows = []
    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
                rows.append(row)
    return True if len(rows) < 1 else rows[-1][0] < time

if not os.path.isfile(file):
    with open(file,'w', newline='', encoding='utf-8') as c:
        cw = csv.writer(c)
        cw.writerow(['Horario','Peso'])
      
with open(file,'a', newline='', encoding='utf-8') as c:
    cw = csv.writer(c)
    if older_than_last(data[0]):
        cw.writerow(data)