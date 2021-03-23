#!/usr/bin/env python3

match_this = 'expire'

s = 'sentinel_watch_syslog_rule_engine{config="watch-syslog",rule="rule-X",b2sum="2ed2fc412bfa54650d00fc5092b06ea320abf563",seen="True",data="LQM-WiFi: (5G) txRTSFrm=24 {txUcast=16} { } rxACKUcast=7",expire="3600",date="2021-03-23 10:28:07"} 2'

#data = s.lstrip("{")
#import re
#data = re.sub(r'^.*?{', '', s)

#slice it like a samari.

data = s
data = data[data.find('{'):]
data = data.lstrip('{')
data = data[:data.rfind('}')] #right find!
data = data.split(',')

#data is a list now...
#for item in data:
#    #item.split('=')
#    key = item.split('=')[0]
#    val = item.split('=')[1]
#    #print(key, val)
#    if key == match_this:
#        print(key, val)

for item in data:
    #print(item)
    #key = item.split('=')[0]
    #val = item.split('=')[1] #equal in the data!
    i = item.split('=', 1) #max split 1
    key = i[0]
    val = i[1]
    print(key, val)

#print(data)


