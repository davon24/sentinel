#!/usr/bin/env python3

from subprocess import Popen, PIPE
import threading

#class PingNet:
#    def __init__(self):
#        self._running = True
#
#    def terminate(self):
#        self._running = False
#
#    def run(self, ip):
#
#        ipL = ip.split('.')
#        ipn = ipL[0] + '.' + ipL[1] + '.' + ipL[2] + '.'
#        for i in range(1, 255):
#            print(i)
#
#        print('PingNet: ' + ipn)
#        #cmd = 'ping -c 1 ' + ip
#        return True

class PingIp:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, ip):
        #print(ip)
        cmd = 'ping -c 1 ' + ip
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        out = proc.stdout.readlines()
        for line in out:
            line = line.decode('utf-8').strip('\n')
            #print(line)
            match = '1 packets transmitted'
            if line.startswith(match, 0, len(match)):
                line = line.split()
                #print(line)
                rcv = line[3]
        # 1 is True, 0 is False here
        #print(str(rcv))
        return int(rcv)

def pingNet(ip):
        ipL = ip.split('.')
        ipn = ipL[0] + '.' + ipL[1] + '.' + ipL[2] + '.'
        print('PingNet: ' + ipn)

        for i in range(1, 255):
            _ip = ipn + str(i)
            #print(_ip)
            ping = PingIp()
            t = threading.Thread(target=ping.run, args=(_ip,))
            t.start()

        return True

def getArps():
    arpDict = {}
    cmd = 'arp -an'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        try:
            ip = line[1]
        except IndexError:
            ip = 'Empty'
        try:
            mac = line[3].lower()
        except IndexError:
            mac = 'Empty'

        arpDict[ip] = mac
    return arpDict

def getDNSNamesLst(ip):
    #dns can take several seconds to time out
    nameLst = []
    #print(ip)
    cmd = 'nmap -sL ' + ip
    #print(cmd)
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    c = 0
    for line in out:
        #line = line.decode('utf-8').strip('\n').split()
        line = line.decode('utf-8').strip('\n')
        #print(str(c) + ' ' + str(line))

        if 'Nmap scan report for' in line:
            line = line.split()
            #print('X ' + str(line))
            if len(line) == 6:
                c += 1
                dnsname = line[4]
                _ip = line[5]
                #print(str(c) + ' ' + dnsname)
                nameLst.append(dnsname)

    #print(len(nameLst))
    #if len(nameLst) == 1:
    #    return str(''.join(nameLst))
    #else:
    #    return str(nameLst)
    return nameLst

def getDNSName(ip):
    nameLst = getDNSNamesLst(ip)
    #print(len(nameLst))
    if len(nameLst) == 0:
        return str('None')
    if len(nameLst) == 1:
        #return str(''.join(nameLst))
        fullname = ''.join(nameLst)
        name = fullname.split('.')[0]
        return str(name)
    else:
        #return str(nameLst)
        return str('WillNotPerformMultiples')



if __name__ == '__main__':

    ip = '192.168.0.1'
    pn = pingNet(ip)
    print(pn)

    #import sys

    #if sys.argv[1:]:
    #    ip = sys.argv[1]
    #else:
    #    ip = '192.168.0.1'

    #ping = PingIp()
    #t = threading.Thread(target=ping.run, args=(ip,))
    #t.start()
    ##t.join()
    #print('exit')
    #sys.exit(0)





# requires cli line tools: arp, ping, nmap

