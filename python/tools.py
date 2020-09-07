#!/usr/bin/env python3

from subprocess import Popen, PIPE
import threading
import sys
import time
import collections

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        #print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

def getPlatform():
    #>>> import sys
    #>>> sys.platform
    #'win32'  # 'linux', 'linux2, 'darwin', 'freebsd8' etc

    if sys.platform == 'linux' or sys.platform == 'linux2':
        # linux
        return 'linux'
    elif sys.platform == 'darwin':
        # MAC OS X
        return sys.platform
    elif sys.platform == 'win32':
        # Windows
        return sys.platform
    elif sys.platform == 'win64':
        # Windows 64-bit
        return sys.platform
    elif sys.platform == 'cygwin':
        # Windows DLL GNU
        return sys.platform
    else:
        return sys.platform

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
        #return int(rcv)
        #return str(ip) + ' ' + str(rcv)
        return str(rcv) + ' ' + str(ip)

# nmap -sn (No port scan) - hosts that responded to the host discovery probes.
class NmapSN:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, ip):
        ipL = []
        #cmd = 'nmap -sn -n --min-parallelism 256 192.168.0.0/24'
        cmd = 'nmap -sn -n ' + ip
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        out = proc.stdout.readlines()
        for line in out:
            line = line.decode('utf-8').strip('\n')
            #print(line)
            match = 'Nmap scan report for'
            if line.startswith(match, 0, len(match)):
                line = line.split()
                #print(line)
                ip = line[4]
                #print(ip)
                ipL.append(ip)

        return ipL

#def pingNet(ip):
#        ipL = ip.split('.')
#        ipn = ipL[0] + '.' + ipL[1] + '.' + ipL[2] + '.'
#        print('PingNet: ' + ipn + '{1..254}')
#
#        for i in range(1, 255):
#            _ip = ipn + str(i)
#            #print(_ip)
#            ping = PingIp()
#            t = threading.Thread(target=ping.run, args=(_ip,))
#            t.start()
#        return True

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
    # nmap -sL (List Scan) - without sending any packets to the target hosts.
    # does reverse-DNS resolution on the hosts
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

def splitAddr(addrport):

    if str(sys.platform).startswith('linux'):
        #print('linux')
        _list = addrport.split(':')
        #print(list)
        port = _list[-1]
        addr = _list[:-1]
        return port, addr


    elif sys.platform == 'darwin':
        _list = addrport.split('.')
        port = _list[-1]
        addr = _list[:-1]
        return port, addr

    else:
        port, addr = ''
        return port, addr


def getNetStat():

    listen = {}
    established = {}
    time_wait = {}

    cmd = 'netstat -na'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        #print(line)
        try:
            if line[5] == 'LISTEN':
                proto = line[0]
                laddr  = line[3]
                listen[laddr] = proto
        except IndexError:
            continue
        try:
            if line[5] == 'ESTABLISHED':
                proto = line[0]
                laddr  = line[3]
                faddr  = line[4]
                established[laddr] = proto
        except IndexError:
            continue
        try:
            if line[5] == 'TIME_WAIT':
                proto = line[0]
                laddr  = line[3]
                faddr  = line[4]
                time_wait[laddr] = proto
        except IndexError:
            continue
    return listen, established, time_wait

def listenPortsLst():
    listen, established, time_wait = getNetStat()
    portsLst = []
    for k,v in listen.items():
        #print(k,v)
        port, addr = splitAddr(k)
        proto = v
        #print(port, addr)
        portsLst.append(proto + ':' + port)
    return portsLst


def lsofProtoPort(protoport):
    #lsof on ports < 1024 require root
    
    lsofDct = {}

    #print(protoport)

    proto = protoport.split(':')[0]
    port  = protoport.split(':')[1]

    #match = '1 packets transmitted'
    #if line.startswith(match, 0, len(match)):

    #print(proto)
    if proto.startswith('tcp4', 0, len('tcp4')):
        _proto = '4tcp'
    if proto.startswith('tcp6', 0, len('tcp6')):
        _proto = '6tcp'

    cmd = 'lsof -n -i' + _proto + ':' + port
    #print(cmd)

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    #print(str(len(out)) + ' ' + str(out))
    #print(str(len(out)))

    c = 0

    #print(out)

    if len(out) == 0:
        _line = port + ' () root ' + proto + ' () ()'
        lsofDct[c] = _line
        #return lsofDct
    else:
        for line in out:
            line = line.decode('utf-8').strip('\n').split()
            #['COMMAND', 'PID', 'USER', 'FD', 'TYPE', 'DEVICE', 'SIZE/OFF', 'NODE', 'NAME']
            #print(str(len(line)) + ' ' + str(line))

            if line[0] == 'COMMAND':
                continue

            pname = line[0]
            pid   = line[1]
            puser = line[2]
            ptype = line[4]
            pnode = line[7]
            #print(line)
            #print(str(len(line)) + ' ' + str(line))
            #print(port, ' ', pname, ' ', puser, ' ' ,  pnode, ' ', ptype, ' ', pid)
            #_line = port + ' ' + pname + ' ' + puser + ' ' +  pnode + ' ' + ptype + ' ' + pid
            _line = port + ' ' + pname + ' ' + puser + ' ' +  proto + ' ' + ptype + ' ' + pid
            #print(_line)
            c += 1
            lsofDct[c] = _line

    #print(len(lsofDct))

    #if len(lsofDct) > 1:
    #    #print('Yes, Multiples exist')
    #    mpids = []
    #    for k,v in lsofDct.items():
    #        print(' multi ' + str(v))
    #        _p = v.split(' ')[5]
    #        print(' mpid ' + _p)
    #        mpids.append(_p)

    return lsofDct
    # sudo lsof -i TCP:631
    # 'tcp4:631', 'tcp6:631'
    #sudo lsof -n  -i4tcp:631 
    #sudo lsof -n  -i6tcp:631 


def getLsOfDct():
    retDct = {}
    portsLst = listenPortsLst()
    #print(lports)

    c = 0
    for protoport in portsLst:
        _lsofDct = lsofProtoPort(protoport)
        #print(len(lsofDct))

        for k,v in _lsofDct.items():
            c += 1
            retDct[c] = v
            #print(v)

    return retDct

        #if len(lsofDct) == 0:
        #    #needs root
        #    print('needs.root')
        #elif len(lsofDct) == 1:
        #    #print('single')
        #    for k,v in lsofDct.items():
        #        print(v)
        #else:
        #    #print('multiple')
        #    pids = []
        #    for k,v in lsofDct.items():
        #        print(v)

def cntLsOf():
    Dct = {}
    lsofDct = getLsOfDct()
    #print(lsofDct)
    c = 0
    for k,v in lsofDct.items():
        c += 1
        _port  = v.split(' ')[0]
        _proto = v.split(' ')[3]
        #Dct[c] = int(v.split(' ')[0])
        Dct[c] = _port + ' ' + _proto

    cntDct = collections.Counter(Dct.values())

    rtnDct = {}
    for key in cntDct:
        _k = int(key.split(' ')[0])
        #_v = str(key.split(' ')[1]).lower()
        _v = str(key.split(' ')[1])
        rtnDct[_k] = _v

    return rtnDct

def printLsOfdetailed():
    lsofDct = getLsOfDct()
    for k,v in lsofDct.items():
        print(v)
    return True 

if __name__ == '__main__':

    cntDct = cntLsOf()

    for k,v in sorted(cntDct.items()):
        print(k,v)

    #print(cntDct)
    #for k,v in cntDct.items():
    #    print(k, v)
    #    #print(v.split(' '))



    #for k,v in sorted(cntDct.items()):
    #    print(k)
    #od = collections.OrderedDict(sorted(cntDct.items(), reverse=False))
    #for k, v in od.items(): print(k, v)
    #for k in od: print(k)
    #for k,v in od: print(v)



# requires cli line tools: arp, ping, lsof, nmap


