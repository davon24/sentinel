#!/usr/bin/env python3

import os
import sqlite3

with open('manuf', 'r') as f:
    data = f.readlines()

db = 'manuf.db'

if not os.path.isfile(db):
    conn = sqlite3.connect(db) 
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS manuf (mac TEXT NOT NULL,name TEXT,data TEXT);''')
    cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_mac ON manuf (mac);''')
else:
    conn = sqlite3.connect(db) 
    cur = conn.cursor()


c = 0
for line in data:
    c += 1

    if len(line.strip()) == 0:
        continue
    
    if line.startswith('#'):
        continue

    line = line.split()

    mac = line[0].lower()
    name = line[1]
    data_ = line[2:]
    data = ' '.join(data_)

    #print(mac, sname, lname)
    cur.execute("INSERT INTO manuf VALUES (?, ?, ?)", (mac, name, data))
    conn.commit()
    print(mac + ' ' + ' ' + name + ' ' + data)






