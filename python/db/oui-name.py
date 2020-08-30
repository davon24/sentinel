#!/usr/bin/env python3

import os
import sys

_mac = sys.argv[1].lower()

def get_oui_vals(mac):
    mac = mac.split(':')
    octet0 = mac[0]
    octet1 = mac[1]
    octet2 = mac[2]
    return (octet0, octet1, octet2)


db_file = 'manuf'
with open(db_file, 'r') as f:
    data = f.readlines()

manufDict = {}
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
    #data_ = line[2:]
    #data = ' '.join(data_)
    #print(mac, name, data)

    if len(mac) == 8:
        mac = mac + ':00:00:00'
    if len(mac) == 20:
        mac = mac.split('/')[0]


    #print(str(len(mac)), mac)
    print(mac)
    manufDict[mac] = name

#8 e4:1e:0a
#20 e4:1e:0a:00:00:00/28




