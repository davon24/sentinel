#!/usr/bin/env python3

with open('manuf', 'r') as f:
    data = f.readlines()

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
    lname = line[2:]
    lname_ = ' '.join(lname)

    #print(mac, sname, lname)
    print(mac + ' ' + ' ' + name + ' ' + lname_)




