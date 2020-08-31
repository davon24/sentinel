#!/usr/bin/env python3

import os
import sys

_mac = sys.argv[1].lower()
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

_mac = even_up(_mac)
#print('even_up_mac: ' + _mac)

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

    #if len(mac) == 8:
    #    mac = mac + ':00:00:00'
    if len(mac) == 20:
        mac = mac.split('/')[0]
    #print(str(len(mac)), mac)
    #print(mac)
    manufDict[mac] = name

#8 e4:1e:0a
#20 e4:1e:0a:00:00:00/28

#ret = [val for key, val in manufDict.items() if _mac in key] 
#print(ret)

#for k,v in manufDict.items():
#    if _mac in k:
#        print(k,v)

#def get_oui_vals(mac):
#    mac = mac.split(':')
#    octet0 = mac[0]
#    octet1 = mac[1]
#    octet2 = mac[2]
#    return (octet0, octet1, octet2)

# try search/mach first 3 octets
print(_mac)
print('---')


def match_octets(mac, n):
    mac = _mac.split(':')
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
    for k,v in manufDict.items():
        if m in k:
           #print(k,v)
           matches.append(v)
    return matches
         
#######################

#m3 = match_octets(_mac, 3)
#print(m3)
#print(len(m3))
#if len(m3) == 0:
#    print('NoMatch')
#    sys.exit(0)
#elif len(m3) == 1:
#    print('Match ' + ''.join(m3))
#    sys.exit(0)
#else:
#    print('Multiples ' + str(len(m3)))
#    #m4 = match_4octets(_mac)
#    m4 = match_octets(_mac, 4)
#    if len(m4) == 0:
#        print('NoMatch')
#        sys.exit(0)
#    elif len(m4) == 1:
#        print('Match ' + ''.join(m4))
#        sys.exit(0)
#    else:
#        print('Multiples ' + str(len(m4)))

def match(mac):
    mac = _mac.split(':')
    #n = len(mac)
    #print(n)
    #print(mac)

    m = match_octets(mac, 3)
    if len(m) == 0:
        return 'NoMatch'
    elif len(m) == 1:
        return ''.join(m)
    else:
        m = match_octets(mac, 4)

    #print(m)
    if len(m) == 0:
        return 'NoMatch'
    elif len(m) == 1:
        return ''.join(m)
    else:
        m = match_octets(mac, 5)
    #print(m)    

    if len(m) == 0:
        return 'NoMatch'
    elif len(m) == 1:
        return ''.join(m)
    else:
        m = match_octets(mac, 6)

    #print(m)

    if len(m) == 0:
        return 'NoMatch'
    elif len(m) == 1:
        return ''.join(m)
    else:
        #return 'MultiMatch'
        return 'MultiMatch: ' + str(m)


    #if len(m3) == 0:
    #for i in range(0, 3):
    #    print(mac[i])
        



m = match(_mac)
print(m)







