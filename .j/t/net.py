#!/usr/bin/env python3

#net = "192.168.1."
#hosts =  [ net + str(i) for i in range (1, 255) ]
#print(hosts)

net = '192.168.'
hosts = []
for i in range(1, 255):
    _net = net + str(i) + '.'
    for j in range(1, 255):
        #n = net + str(i)
        #hosts.append(n)
        hosts.append(_net + str(j))

print(hosts)


