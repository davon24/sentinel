#!/usr/bin/env python3

import os
import sys

#_mac = sys.argv[1].lower()
#print(_mac)

def even_up(mac):
    mac = mac.split(':')
    mac_ = mac[0]
    for i in mac[1:]:
        #print(i)
        #print(len(i))
        if len(i) == 1:
            i = '0' + i
        #print(i)
        mac_ = mac_ + ':' + i
    return mac_

#_mac = even_up(_mac)
#print('even_up_mac: ' + _mac)

def get_manufDict(db_file):
    mfDict = {}

    with open(db_file, 'r') as f:
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
        #data_ = line[2:]
        #data = ' '.join(data_)
        #print(mac, name, data)

        #if len(mac) == 8:
        #    mac = mac + ':00:00:00'
        if len(mac) == 20:
            mac = mac.split('/')[0]
        #print(str(len(mac)), mac)
        #print(mac)
        mfDict[mac] = name

    #8 e4:1e:0a
    #20 e4:1e:0a:00:00:00/28
    return mfDict

def match_octets(mac, n, mfDict):
    #print(str(mfDict))
    #print(mac)
    mac = mac.split(':')
    n = int(n)
    matches = []
    m = mac[0]
    c = 0
    for i in mac[1:]:
        c += 1
        if c < n:
            #print(c)
            m = m + ':' + i

    #print(m)
    for k,v in mfDict.items():
        if m in k:
           #print(k,v)
           matches.append(v)
    return matches
         
def match(mac, mfDict):
    #mac = mac.split(':')
    #print(len(mac))

    c = 2
    for i in range(0, len(mac)):
        c += 1
        #print(i, c)
        m = match_octets(mac, c, mfDict)

        if len(m) == 0:
            return 'NoMatch'
        elif len(m) == 1:
            return ''.join(m)
        elif i >= 5:
            return 'MultiMatch: ' + str(m)

if __name__ == '__main__':

    mac = sys.argv[1].lower()
    mac = even_up(mac)

    db_file = 'manuf'
    manufDict = get_manufDict(db_file)

    m = match(mac, manufDict)
    print(m)


