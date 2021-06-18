#!/usr/bin/env python3

#promKey = 'expire'

s = 'sentinel_watch_syslog_rule_engine{config="watch-syslog",rule="rule-X",b2sum="2ed2fc412bfa54650d00fc5092b06ea320abf563",seen="True",data="LQM-WiFi: (5G) txRTSFrm=24 {txUcast=16} { } rxACKUcast=7",expire="3600",date="2021-03-23 10:28:07"} 2'
#s = 'sentinel_watch_syslog_rule_engine{config="watch-syslog",rule="rule-X",b2sum="2ed2fc412bfa54650d00fc5092b06ea320abf563",seen="True",data="LQM-WiFi: (5G) txRTSFrm=24 {txUcast=16} { } rxACKUcast=7",date="2021-03-23 10:28:07"} 2'


def promDataParser(promKey, promData):
    rtn = None

    if isinstance(promData, list):
        promData = promData[0]

    data = promData

    try:

        data = data[data.find('{'):]
        data = data.lstrip('{')
        data = data[:data.rfind('}')] #right find!
        data = data.split(',')

        #data is a list now...
        for item in data:
            #key = item.split('=')[0]
            #val = item.split('=')[1] #if the val has '=' in it!
            i = item.split('=', 1) #max split 1
            key = i[0]
            val = i[1]

            val = val.lstrip('"')
            val = val.rstrip('"')

            #print(key, val)
            if key == promKey:
                #print(key, val)
                rtn = val
    except IndexError as e:
        return None

    return rtn


_expire = promDataParser('data', s)

if _expire:
    print('_expire from gDict ' + str(_expire))





