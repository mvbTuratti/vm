import csv
import os
import datetime
from multiprocessing import Lock

lock = Lock()

def log_peso(valor, file):

    with lock:
        data = [datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),valor]
        def older_than_last(time):
            rows = []
            with open(file, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                fields = next(csvreader)
                for row in csvreader:
                    rows.append(row)
            return True if len(rows) <= 1 else rows[-1][0] < time

        if not os.path.isfile(file):
            with open(file,'w', newline='', encoding='utf-8') as c:
                cw = csv.writer(c)
                cw.writerow(['Horario','Peso'])
            
        with open(file,'a', newline='', encoding='utf-8') as c:
            cw = csv.writer(c)
            if older_than_last(data[0]):
                cw.writerow(data)
        return valor
    
def get_last_peso(file):
    with lock:
        
        rows = []
        with open(file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            fields = next(csvreader)
            for row in csvreader:
                rows.append(row)
        return 0 if len(rows) <= 1 else rows[-1][1]
