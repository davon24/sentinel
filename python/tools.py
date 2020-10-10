#!/usr/bin/env python3

from subprocess import Popen, PIPE
import threading
import multiprocessing
#from multiprocessing import shared_memory


import sys
import time
import datetime
import collections
import socket
import copy
import json

#import smtplib
#import ssl
#import certifi

import logging
#import atexit
#import signal

from hashlib import blake2b, blake2s

from http.server import HTTPServer, BaseHTTPRequestHandler

import store

#import queue
#gQ = queue.Queue()

#gList = []
gDict = {}
sigterm = False

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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        #127.0.0.1 - - [31/May/2020 19:09:05] "GET /metrics HTTP/1.1" 200 -
        logging.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 200 -'))
        if self.path == '/metrics':
        #if self.path == config.param['metricPath']:
        #if self.path == config['path']:
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()

            #for item in gList:
            #for item in gQ:
            #    self.wfile.write(bytes(str(item) + str('\n'), 'utf-8'))
            #items = gQ.get()
            #for item in items:
            #    #self.wfile.write(bytes(str(item) + str('\n'), 'utf-8'))
            #    self.wfile.write(str(item) + str('\n'))
            #while not gQ.empty():
            #    #print(gQ.get())
            #    self.wfile.write(bytes(str(gQ.get()) + str('\n'), 'utf-8'))

            #for item in gList:
            #    self.wfile.write(bytes(str(item) + str('\n'), 'utf-8'))

            for k,v in gDict.items():
                #v should be a list
                for item in v:
                    self.wfile.write(bytes(str(item) + str('\n'), 'utf-8'))
            
            #print(gQ.get())

        else:
            logging.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 404 -'))
            self.send_error(404) #404 Not Found
        return

    def do_POST(self):
        logging.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 405 -'))
        self.send_error(405) #405 Method Not Allowed
        return


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

class NmapSN:
    # nmap -sn (No port scan) - hosts that responded to the host discovery probes.
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


def getPlatform():
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


#from hashlib import blake2b, blake2s
def b2sum(_file):
    is_64bits = sys.maxsize > 2**32
    if is_64bits:
        blake = blake2b(digest_size=20)
    else:
        blake = blake2s(digest_size=20)
    try:
        with open(_file, 'rb') as bfile:
            _f = bfile.read()
    except FileNotFoundError as e:
        return str(e)

    blake.update(_f)
    return str(blake.hexdigest())


def pingIp(ip):
    cmd = 'ping -c 1 ' + ip
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        line = line.decode('utf-8').strip('\n')
        match = '1 packets transmitted'
        if line.startswith(match, 0, len(match)):
            line = line.split()
            rcv = line[3]
    # 1 is True, 0 is False here
    return str(rcv) + ' ' + str(ip)


def nmapDetectScan(ip):
    cmd = 'nmap -n -O -sV ' + ip
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    return proc.stdout.readlines()

def nmapDetectScanStore(ip, db_store):
    data = ''
    report = None
    scan = nmapDetectScan(ip)
    for line in scan:
        #line = line.decode('utf-8').strip('\n')
        line = line.decode('utf-8')
        if line.startswith('Nmap done:'):
            report = line.split()[5].strip('(')
        print(line.strip('\n'))
        data += line

    #print(str(type(scan)))
    #print(str(scan))
    #data = str(''.join(scan))
    #update = store.replaceVulns(ip, data, None, db_store)
    #report = ''

    #report = processVulnData(data)
    #print(len(scan))

    if len(scan) == 0:
        report = '-1'

    insert = store.insertDetect(ip, report, data, db_store)
    return insert

def printDetectScan(db_store, did=None):
    #print('vid.vid: ' + str(vid))

    if did is None:
        vulns = store.getAllNmapDetects(db_store)
        for row in vulns:
            #print(row)
            rowid  = row[0]
            _id    = row[1]
            ip     = row[2]
            tstamp = row[3]
            report = row[4]
            data   = row[5]
            blob   = row[6]
            print(str(_id) + ' ' + str(ip) + ' ' + str(tstamp) + ' ' + str(report))
    else:
        v_ = store.getNmapDetect(did, db_store)
        vulns = [ v_ ]

        for row in vulns:
            #print(row)
            rowid  = row[0]
            _id    = row[1]
            ip     = row[2]
            tstamp = row[3]
            report = row[4]
            data   = row[5]
            blob   = row[6]
            print(str(_id) + ' ' + str(ip) + ' ' + str(tstamp) + ' ' + str(report))
            print(data)

    return True


def nmapVulnScan(ip):
    cmd = 'nmap -Pn --script=vuln ' + ip
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    return proc.stdout.readlines()

def nmapVulnScanStore(ip, db_store):
    data = ''
    scan = nmapVulnScan(ip)
    for line in scan:
        #line = line.decode('utf-8').strip('\n')
        line = line.decode('utf-8')
        print(line.strip('\n'))
        data += line

    #print(str(type(scan)))
    #print(str(scan))
    #data = str(''.join(scan))
    #update = store.replaceVulns(ip, data, None, db_store)
    #report = ''
    report = processVulnData(data)
    if len(report) == 0:
        report = '-'
    insert = store.insertVulns(ip, report, data, db_store)
    #processVulnData(data)
    return insert

def printVulnScan(db_store, vid=None):
    #print('vid.vid: ' + str(vid))
    
    if vid is None:
        vulns = store.getAllNmapVulns(db_store)
        for row in vulns:
            #print(row)
            rowid  = row[0]
            _id    = row[1]
            ip     = row[2]
            tstamp = row[3]
            report = row[4]
            data   = row[5]
            blob   = row[6]
            print(str(_id) + ' ' + str(ip) + ' ' + str(tstamp) + ' ' + str(report))
    else:
        v_ = store.getNmapVuln(vid, db_store)
        vulns = [ v_ ]

        for row in vulns:
            #print(row)
            rowid  = row[0]
            _id    = row[1]
            ip     = row[2]
            tstamp = row[3]
            report = row[4]
            data   = row[5]
            blob   = row[6]
            print(str(_id) + ' ' + str(ip) + ' ' + str(tstamp) + ' ' + str(report))
            print(data)

    return True

def nmapScanStore(ip, level, db_store):
    data = nmapScan(ip, level)
    print('(' + ip + ') ' + data)
    replace = store.replaceNmaps(ip, data, db_store)
    return True


def nmapScan(ip, level):

    up = 0
    c = 0
    #openDct = {}
    openLst = []

    nmapDct = getNmapScanDct(ip, level)

    for k,v in nmapDct.items():
        #print(v)
        line = v.split()

        if v.startswith('Host is up'):
            #print(v.split())
            up = 1

        try:
            #if (line[1] == 'open') or (str(line[1]).startswith('open')):
            if line[1] == 'open': #https://nmap.org/book/port-scanning.html #open, open|filtered
                #print('line.open ' + str(v))
                #c += 1
                #openDct[c] = line
                #openDct[c] = v
                #openDct[c] = str(v)
                port = line[0]
                openLst.append(port)
        except IndexError:
            c += 1
            
        #if v.startswith('Nmap done:'):
        #    #print('yes')
        #    up = v.split()[5].strip('(')
        #    #print(up)

    #rtnStr = str(up) + ' ' + str(openDct)
    #rtnStr = str(up) + ' ' + str(openLst)
    rtnStr = str(up) + ' ' + ','.join(openLst)
    return rtnStr

def getNmapScanDct(ip, level):

    level = str(level)
    #print('level ' + str(level))

    if level == '1':
        cmd = 'nmap -n -F -T5 ' + ip 
    elif level == '2':
        cmd = 'nmap -n -sT -sU -T4 –-top-ports 1000 ' + ip  #
    elif level == '3':
        cmd = 'nmap -n -sT -sU -p- ' + ip #
    elif level == '0':
        udp = 'U:53,111,137-139,514'
        tcp = 'T:21-25,53,80,137-139,443,445,465,631,993,995,8080,8443'
        cmd = 'nmap -n -sT -sU -T5 -p ' + udp + ',' + tcp + ' ' + ip 

    else:
        cmd = 'nmap ' + ip
        print('level: ' + str(level) + ' ' + str(cmd))

    rtnDct = {}
    c = 0
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        #line =  line.decode('utf-8').strip('\n').split()
        line =  line.decode('utf-8').strip('\n')
        #print(line)
        c += 1
        rtnDct[c] = line

    return rtnDct

def nmapUDP(ip, port):
    #sudo nmap -n -T5 -sU -p 53,514 192.168.0.254
    openLst = []
    up = 0
    cmd = 'nmap -n -T5 -sU -p ' + port + ' ' + ip
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        line =  line.decode('utf-8').strip('\n')
        _line = line.split()
        #print(line)
        if line.startswith('Host is up'):
            up = 1

        try:
            #if (_line[1] == 'open') or (str(_line[1]).startswith('open')):
            if _line[1] == 'open':
                port = _line[0]
                openLst.append(port)
        except IndexError: pass

    rtnStr = str(up) + ' ' + ','.join(openLst)
    return rtnStr

def nmapUDPscan(ip, ports=None):

    #if port is None:
    #    port = 

    ports =  '1-65535'
    for port in range(1,600):
        #print(i)
        s = nmapUDP(ip, str(port))
        l = s.split()
        try:
            if l[1]:
                print(s)
        except IndexError: pass

    return True

def pingNet(ip):
    rtnLst = []

    ipL = ip.split('.')
    ipn = ipL[0] + '.' + ipL[1] + '.' + ipL[2] + '.'

    print('PingNet: ' + ipn + '{1..254}')
    for i in range(1, 255):
        ip_ = ipn + str(i)
        ping = pingIp(ip_)
        _up = ping.split(' ')[0]
        _ip = ping.split(' ')[1]
        if str(_up) == '1':
            rtnLst.append(_ip)
    return rtnLst



def pingNetThreaded(ip): #OSError: [Errno 24] Too many open files
        rtnLst = []

        ipL = ip.split('.')
        ipn = ipL[0] + '.' + ipL[1] + '.' + ipL[2] + '.'
        #print('PingNet: ' + ipn + '{1..254}')

        threads = []
        for i in range(1, 255):
            _ip = ipn + str(i)
            #print(_ip)
            ping = PingIp()
            #t = threading.Thread(target=ping.run, args=(_ip,))
            t = ThreadWithReturnValue(target=ping.run, args=(_ip,))
            t.start()
            threads.append(t)

        for t in threads: 
            out = t.join()
            #print(o)
            _up = out.split(' ')[0]
            _ip = out.split(' ')[1]
            if str(_up) == '1':
                #print(out)
                rtnLst.append(_ip) 

        return rtnLst

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

def getNSlookupMulti(ip):
    name = None
    rLst = getNSlookupMultiLst(ip)
    for srv in rLst:
        name = getNSlookup(ip, srv)
        #print(name)
        if name is not None:
            return(name)

    return name

def getNSlookupMultiLst(ip):
    rLst = []
    try:
        resolvfile = open('/etc/resolv.conf', 'r')
        rlines = resolvfile.readlines()
    except FileNotFoundError:
        rlines = None

    if rlines:
        for rline in rlines:
            #print(rline)
            l_ = rline.split()
            if l_[0] == 'nameserver':
                _ip = l_[1]
                rLst.append(_ip)
    return rLst


def getNSlookup(ip, srv=None):
    dnsname = None
    if srv is None:
        srv = ''

    cmd = 'nslookup ' + str(ip) + ' ' + srv
    #print(cmd)
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        #print(line)
        try:
            if line[2] == '=':
                #print(line[3])
                dnsname = line[3]
        except IndexError:
            pass

    return dnsname


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
    cmd = 'netstat -na'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    return out


def getNetStatDcts():

    udp = {}
    listen = {}
    established = {}
    time_wait = {}

    out = getNetStat()
    #print(out)

    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        #print(line)
        try:
            if line[5] == 'LISTEN':
                #print(line)
                proto = line[0]
                laddr  = line[3]
                listen[laddr] = proto
        except IndexError:
            continue

    c = 0
    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        try:
            if line[5] == 'ESTABLISHED':
                c += 1
                proto = line[0]
                laddr  = line[3]
                faddr  = line[4]
                #established[laddr] = proto
                #established[c] = line
                _line = proto + ' ' + laddr + ' ' + faddr
                established[c] = _line
        except IndexError:
            continue

    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        try:
            if line[5] == 'TIME_WAIT':
                proto = line[0]
                laddr  = line[3]
                faddr  = line[4]
                time_wait[laddr] = proto
        except IndexError:
            continue

    for line in out:
        line = line.decode('utf-8').strip('\n').split()
        try:
            if str(line[0]).startswith('udp'):
                #print(line)
                proto = line[0]
                laddr  = line[3]
                faddr  = line[4]
                udp[laddr] = proto
        except IndexError:
            continue

    return udp, listen, established, time_wait


def listenPortsLst():
    udp, listen, established, time_wait = getNetStatDcts()
    portsLst = []

    for addrport,proto in listen.items():
        #print('TCP1 ' + addrport,proto)
        port, addr = splitAddr(addrport)
        portsLst.append(proto + ':' + port)
        #print('TCP2 ' + proto + ':' + port)

    for k,v in udp.items():
        #print('UDP1 ' + k,v)
        #print(k,v)
        if k == '*.*':
            #print('skip it ' + str(k))
            continue
        port, addr = splitAddr(k)
        #print(port, addr)
        #print(proto, port)
        portsLst.append(v + ':' + port)
        #print('UDP2 ' + v + ':' + port)

    #for k,v in established.items():
    #    print('ESTAB')
    #    print(k,v)

    return portsLst

def printLsOfPort(port):

    protoLst = [ '4tcp', '6tcp', '4udp', '6udp' ]

    for proto in protoLst:
        #print(proto)
        cmd = 'lsof -n -i' + proto + ':' + port
        proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
        out = proc.stdout.readlines()

        for line in out:
            #line = line.decode('utf-8').strip('\n').split()
            line = line.decode('utf-8').strip('\n')
            print(line)

    #print('done')
    return True


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
    elif proto.startswith('tcp6', 0, len('tcp6')):
        _proto = '6tcp'
    elif proto.startswith('udp4', 0, len('udp4')):
        _proto = '4udp'
    elif proto.startswith('udp6', 0, len('udp6')):
        _proto = '6udp'
    elif proto.startswith('udp46', 0, len('udp46')):
        _proto = '6udp'
    else:
        _proto = proto

    cmd = 'lsof -n -i' + _proto + ':' + port
    #print(cmd)

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    #print(str(len(out)) + ' ' + str(out))
    #print(str(len(out)))

    c = 0

    #print(out)

    if len(out) == 0:
        #_line = port + ' () root ' + proto + ' () ()'
        _line = port + ' ' + proto + ' nopriv () () () ()'
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
            #_line = port + ' ' + pname + ' ' + puser + ' ' +  proto + ' ' + ptype + ' ' + pid
            _line = port + ' ' + proto + ' ' + pname + ' ' + puser  + ' ' + pnode + ' ' + ptype + ' ' + pid
            #print(_line)
            c += 1
            lsofDct[c] = _line

    return lsofDct
    # sudo lsof -i TCP:631


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

def getListenPortsDct():
    portsLst = listenPortsLst()
    #print(portsLst)
    Dct = {}
    for protoport in portsLst:
        #print(protoport)
        proto = protoport.split(':')[0]
        port  = int(protoport.split(':')[1])
        Dct[port] = proto
    return Dct

def printListenPorts():
    open_ports = getListenPortsDct()
    for k,v in sorted(open_ports.items()):
        print(k,v)
    return True

def printListenPortsDetailed():
    open_ports = getListenPortsDct()
    for k,v in sorted(open_ports.items()):
        #print(k,v)
        protoport = str(v) + ':' + str(k)
        #print(protoport)
        _lsofDct = lsofProtoPort(protoport)
        #print(_lsofDct)
        for k,v in _lsofDct.items():
            print(v)
    return True


def printListenPortsDetails(port):

    pDct = getListenPortsDct()
    #for k,v in pDct.items():
    #    print(k,v)

    _idx = int(port)
    proto = pDct[_idx]
    #print(proto)

    protoport = str(proto) + ':' + str(port)

    _lsofDct = lsofProtoPort(protoport)
    #print(_lsofDct)
    pidLst = []
    for k,v in _lsofDct.items():
        _pid = v.split(' ')[6]
        pidLst.append(_pid)

    #print(len(pidLst))
    #for p in pidLst:
    #    print(p)

    if len(pidLst) != 1:
        return False
    else:
        pid = ''.join(pidLst)

    #print('pid: ' + str(pid))

    cmd = 'lsof -n -p ' + str(pid)
    #print(cmd)

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        #line = line.decode('utf-8').strip('\n').split()
        line = line.decode('utf-8').strip('\n')
        print(line)

    return True

def printEstablished():
    Dct = getEstablishedDct()
    for k,v in Dct.items():
        print(v)
    return True


def getEstablishedDct():
    udp, listen, established, time_wait = getNetStatDcts()
    Dct = {}
    c = 0
    #for k,v in established.items():
    #    print(k,v)

    # Remove duplicate values in dictionary - deduped
    t_ = []
    r_ = {}
    for k,v in established.items():
        if v not in t_:
            t_.append(v)
            r_[k] = v

    for k,v in r_.items():
        #print(k,v)
        #print(v)
        proto = v.split(' ')[0]
        laddrport = v.split(' ')[1]
        lport, laddr = splitAddr(laddrport)
        faddrport = v.split(' ')[2]
        fport, faddr = splitAddr(faddrport)
        
        #print(len(addr))
        if len(laddr) == 1:
            laddr = ''.join(laddr)
        else:
            laddr = '.'.join(laddr)

        if len(faddr) == 1:
            faddr = ''.join(faddr)
        else:
            faddr = '.'.join(faddr)

        _l = str(proto) + ' ' + str(laddr) + ' ' + str(lport) + ' ' + str(faddr) + ' ' + str(fport)
        #print(_l)
        c += 1
        Dct[c] = _l

    return Dct
    #tcp6 fe80::aede:48ff:.49210

def getSelfIPLst(): #socket.gaierror: [Errno 8] nodename nor servname provided, or not known

    ipLst_ = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]
    #socket.gaierror: [Errno 8] nodename nor servname provided, or not known

    ipLst = list(dict.fromkeys(ipLst_)) #dedupe

    print(ipLst)
    #remove localhost
    try:
        ipLst.remove('::1')
        ipLst.remove('127.0.0.1')
    except ValueError:
        e = 1

    return ipLst

def getSelfIPv4():
    ipv4 = None
    ipLst = getSelfIPLst()
    #print(ipLst)
    for item in ipLst:
        i = item.split('.')
        #print(len(i))
        if len(i) == 4:
            #print(item)
            ipv4 = item
            return ipv4 #just return the first occurance

    return ipv4
    #myIPv4 = tools.getSelfIPv4()
    #print(myIPv4)

def getHostNameIP():
    ip = None
    try:
        hostname = socket.gethostname() 
        ip = socket.gethostbyname(hostname) 
    except:
        ip = None
    return ip # returns a lot of 'None' (macosx)

def getIfconfigIPv4():
    e = 0
    ipv4Lst = getIfconfigIPv4Lst()

    #remove localhost
    try:
        ipv4Lst.remove('127.0.0.1')
    except ValueError:
        e = 1

    for ip in ipv4Lst:
        return ip
    else:
        return '127.0.0.1'

def getIfconfigIPv4Lst(): #testing macosx now, linux later
    ipv4Lst = []
    cmd = 'ifconfig -a'
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
         line = line.decode('utf-8').strip('\n').lstrip()
         #print(line)
         if line.startswith('inet '):
             #print(line)
             _line = line.split()
             _ip = _line[1]
             #print(line)
             ipv4Lst.append(_ip)
    return ipv4Lst


def nmapNet(net):
    #nmap -sP 193.168.8.0/24 
    ipLst = []
    #cmd = 'nmap -sP ' + str(net)
    # -sn: Ping Scan - disable port scan
    cmd = 'nmap -n -sn ' + str(net)
    #print(cmd)
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()
    for line in out:
        #line = line.decode('utf-8').strip('\n').split()
        line = line.decode('utf-8').strip('\n')
        #print(line)
        if line.startswith('Nmap scan report for'):
            ip = line.split()[4]
            ipLst.append(ip)

    #print('done')
    return ipLst


def runDiscoverNet(ipnet, level, db_store):

    #ipnet values; '192.168.3.111', 'fe80::1c:8f5a:73ad:f0ea'
    _ipnet = ipnet.split('.')
    #print(len(_ipnet))
    if len(_ipnet) == 4:
        _ipv4 = ipnet
        ipn = _ipnet[0] + '.' + _ipnet[1] + '.' + _ipnet[2] + '.{1-254}'
        print('ping-net: ' + ipn)

    #ping-net for discovery
    hostLst = pingNet(ipnet)
    print('found: ' + str(hostLst))

    print('scan-ports:')
    scanDct = {}
    for ip in hostLst:
        #print('nmap-scan: ' + ip)
        scan = nmapScan(ip, level)
        #print(ip, ' ', scan)
        scanDct[ip] = scan

    for k,v in scanDct.items():
        line = v.split()
        #print('line: ' + str(line))
        success = line[0]
        try: data = line[1]
        except IndexError: data = None

        _data = str(success) + ' ' + str(data)

        #print('['+k+']', v)
        #print('(' + k + ') ' + str(success) + ' ' + str(data))
        print('(' + k + ') ' + str(_data))
        replace = store.replaceNmaps(k, _data, db_store)

    return True

def runDiscoverNetThreaded(ipnet, level, db_store):

    _ipnet = ipnet.split('.')
    if len(_ipnet) == 4:
        _ipv4 = ipnet
        ipn = _ipnet[0] + '.' + _ipnet[1] + '.' + _ipnet[2] + '.{1-254}'
        print('ping-net: ' + ipn)

    #ping-net for discovery
    hostLst = pingNet(ipnet) #already threading ThreadWithReturnValue 
    #OSError: [Errno 24] Too many open files

    print('found: ' + str(hostLst))

    print('scan-ports:')
    scanDct = {}
    #threads = []
    for ip in hostLst:
        t = ThreadWithReturnValue(target=nmapScan, args=(ip, level))
        t.start()
        #threads.append(t)
        scanDct[ip] = t

    for k,t in scanDct.items():
        out = t.join()
        #print(out)
        line = out.split()
        success = line[0]
        try: data = line[1]
        except IndexError: data = None
        _data = str(success) + ' ' + str(data)
        print('(' + k + ') ' + str(_data))
        replace = store.replaceNmaps(k, _data, db_store)

    return True

def runDiscoverNetMultiProcess(ipnet, level, db_store):

    _ipnet = ipnet.split('.')
    if len(_ipnet) == 4:
        _ipv4 = ipnet
        ipn = _ipnet[0] + '.' + _ipnet[1] + '.' + _ipnet[2] + '.1/24'
        print('nmap-net: ' + ipn)

    #ping-net for discovery
    #hostLst = pingNet(ipnet) #already threading ThreadWithReturnValue
    #hostLst = ['192.168.8.1', '192.168.8.109']

    #print('net: ' + str(ipn))
    hostLst = nmapNet(ipn)

    print('found: ' + str(hostLst))

    print('nmap-ports:')
    scanDct = {}
    for ip in hostLst:
        p = multiprocessing.Process(target=nmapScanStore, args=(ip, level, db_store))
        p.start()
        scanDct[ip] = p

    for k,p in scanDct.items():
        out = p.join()
        #print(out)

    return True

def runDiscoverNetAll(ipnet, level, db_store):

    level = int(level)

    _ipnet = ipnet.split('.')
    if len(_ipnet) == 4:
        _ipv4 = ipnet
        ipn = _ipnet[0] + '.' + _ipnet[1] + '.' + _ipnet[2] + '.1/24'
        print('nmap-net: ' + ipn)

    #hostLst = ['192.168.8.1', '192.168.8.109']
    #print('net: ' + str(ipn))
    hostLst = nmapNet(ipn)

    print('found: ' + str(hostLst))

    print('scan-level: ' + str(level))
    nmapDct = {}
    vulnDct = {}
    detectDct = {}
    for ip in hostLst:
        p = multiprocessing.Process(target=nmapScanStore, args=(ip, level, db_store))
        p.start()
        nmapDct[ip] = p
        if level > 1:
            #print('level ' + str(level) + ' vuln-scan launch ')
            p2 = multiprocessing.Process(target=nmapVulnScanStore, args=(ip, db_store))
            p2.start()
            vulnDct[ip] = p2

            #print('level ' + str(level) + ' detect-scan launch ')
            p3 = multiprocessing.Process(target=nmapDetectScanStore, args=(ip, db_store))
            p3.start()
            detectDct[ip] = p3

    for k,p in nmapDct.items():
        out = p.join()

    for k,p in vulnDct.items():
        out = p.join()

    for k,p in detectDct.items():
        out = p.join()

    return True
    #https://stackoverflow.com/questions/26063877/python-multiprocessing-module-join-processes-with-timeout

def runNmapScanMultiProcess(hostLst, level, db_store):

    print('hostLst: ' + str(hostLst))
    print('scan-level: ' + str(level))

    nmapDct = {}
    for ip in hostLst:
        p = multiprocessing.Process(target=nmapScanStore, args=(ip, level, db_store))
        p.start()
        nmapDct[ip] = p

    for k,p in nmapDct.items():
        out = p.join()

    return True

def runNmapVulnMultiProcess(hostLst, db_store):

    print('hostLst: ' + str(hostLst))

    vulnDct = {}
    for ip in hostLst:
        #print('level ' + str(level) + ' vuln-scan launch ')
        p2 = multiprocessing.Process(target=nmapVulnScanStore, args=(ip, db_store))
        p2.start()
        vulnDct[ip] = p2

    for k,p in vulnDct.items():
        out = p.join()

    return True

def runNmapDetectMultiProcess(hostLst, db_store):

    print('found: ' + str(hostLst))

    detectDct = {}
    for ip in hostLst:
        #print('level ' + str(level) + ' detect-scan launch ')
        p3 = multiprocessing.Process(target=nmapDetectScanStore, args=(ip, db_store))
        p3.start()
        detectDct[ip] = p3

    for k,p in detectDct.items():
        out = p.join()

    return True

def getIpNet(ip):
    ipn = None
    _ipnet = ip.split('.')
    if len(_ipnet) == 4:
        _ipv4 = ip
        ipn = _ipnet[0] + '.' + _ipnet[1] + '.' + _ipnet[2] + '.1/24'
        #print('ip-net: ' + ipn)
    return ipn

def getHostLst(ipn):
    hostLst = nmapNet(ipn)
    return hostLst

def processVulnData(data):
    vulnerable = 0
    Dct = {}

    #print(str(type(data)))

    #if isinstance(data, tuple):
    if type(data) == tuple:
        data = data[0].split('\n') #<class 'tuple'>
    #elif isinstance(data, str):
    elif type(data) == str:
        data = data.split('\n')
    else:
        data = data.split('\n')

    #if str(type(data)) == 'tuple':
    #    data = data[0].split('\n')
    #else:
    #    data = data.split('\n') 

    #print('type.data ' + str(type(data)))
    #data = store.getVulnData(vid, db_store)
    #data = data[0].split('\n') #<class 'tuple'>
    #<class 'str'>

    for line in data:
        #print('START ' + str(line))
        _line = line.split()
        #print(line)
        #print(_line)
        #if str(_line[1]).startswith('VULNERABLE:'):
        #print(line)
        #if 'VULNERABLE' in line:
        #    print(line)

        #port = ''

        try:
            if _line[1] == 'open':
                #print(line)
                port = _line[0]
        except IndexError: pass

        if 'VULNERABLE' in line:
            #print(line)
            vulnerable += 1
            Dct[port] = vulnerable

    Lst = []
    for k,v in Dct.items():
        #print(k,v)
        Lst.append(k)

    return ','.join(Lst)


def sendEmail(subject, message, db_store):
    #import os
    import smtplib
    import ssl
    #if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    #    getattr(ssl, '_create_unverified_context', None)):
    #    ssl._create_default_https_context = ssl._create_unverified_context

    #try:
    #    _create_unverified_https_context = ssl._create_unverified_context
    #except AttributeError:
    #    pass
    #else:
    #    ssl._create_default_https_context = _create_unverified_https_context

    if sys.platform == 'darwin':
        #ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1108)
        print('MACOSX made me do it this way...')

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.check_hostname = True
        ssl_context.load_default_certs()

        import certifi
        #print(certifi.where())
        import os

        openssl_dir, openssl_cafile = os.path.split(
                ssl.get_default_verify_paths().openssl_cafile)

        ssl_context.load_verify_locations(
                cafile=os.path.relpath(certifi.where()),
                capath=None,
                cadata=None)
    else:
        ssl_context = ssl.create_default_context()

    if type(message) == tuple:
        message = message[0].split('\n')
    if type(message) == list:
        message = '\n'.join(message) 

    #print(str(type(message)))
    #print(str(message))

    conf = store.getConfig('email', db_store)
    #print('conf ' + str(conf))

    if conf is None:
        return 'email config is None'
    else:
        conf = conf[0]
    #print('conf ' + str(conf))

    try:
        jdata = json.loads(conf)
    except json.decoder.JSONDecodeError:
        return 'invalid json ' + str(conf)

    #print('ok json... ' + str(jdata))
    #print(jdata['smtp_to'])
    #print(jdata.get('smtp_from', None))

    smtp_to   = jdata.get('smtp_to', None)
    smtp_from = jdata.get('smtp_from', 'sentinel')
    smtp_host = jdata.get('smtp_host', '127.0.0.1')
    smtp_port = jdata.get('smtp_port', '25')
    smtp_user = jdata.get('smtp_user', None)
    smtp_pass = jdata.get('smtp_pass', None)

    if smtp_to is None:
        return 'smtp_to is None'

    print(smtp_to, smtp_from, smtp_host, smtp_port, smtp_user)

    msg = 'Subject: ' + str(subject) + '\r\n\r\n'
    msg += message

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls(context=ssl_context)
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_from, smtp_to, msg)
    print('smtp_to: ' + str(smtp_to))
    return True


def printConfigs(db_store):
    #configs = store.getAllConfigs(db_store)
    configs = store.selectAll('configs', db_store)
    for row in configs:
        print(row)
    return True

def printAllFims(db_store):
    #fims = store.getAll('fims', db_store)
    fims = store.selectAll('fims', db_store)
    for row in fims:
        print(row)
    return True

def printAllFimsChanged(db_store):
    #fims = store.getAll('fims', db_store)
    fims = store.selectAll('fims', db_store)
    for row in fims:
        #print(row)
        #name = row[1]
        name = row[0]
        #print(name)
        fDct = getFimDct(name, db_store)
        for k,v in fDct.items():
            #print(k, 'CHANGED')
            #print(k, v)
            #print('v is ' + str(type(v)) + ' ' + str(v) + ' ' + str(len(v)))
            if len(v) == 0:
                print(k, 'ADDED')
            else:
                print(k, 'CHANGED')
    return True


def printFim(name, db_store):
    fDct = getFimDct(name, db_store)
    for k,v in fDct.items():
        #print(k,v)
        #print(k, 'CHANGED')
        if len(v) == 0:
            print(k, 'ADDED')
        else:
            print(k, 'CHANGED')
    return True


def vulnScan(ips, db_store):
    hostLst = discoverHostLst(ips)
    scan = runNmapVulnMultiProcess(hostLst, db_store)
    return True

def portScan1(ips, db_store):
    level = 1
    return portScan(ips, level, db_store)

def portScan2(ips, db_store):
    level = 2
    return portScan(ips, level, db_store)

def portScan(ips, level, db_store):
    hostLst = discoverHostLst(ips)
    if level is None:
        level = 1
    scan = runNmapScanMultiProcess(hostLst, level, db_store)
    return scan

def isNet(ips):
    try:
        net = ips.split('/')[1]
    except IndexError:
        net = False
    return net

def isIPv6(ips):
    pass


def discoverHostLst(ips):
    hostLst = []
    #print('ips is... ' + str(type(ips)) + ' ' + str(ips))
    if type(ips) == str:
        ips = ips.split()

    #if type(ips) == list:
    #elif type(ips) == str:

    ipnet_ = []
    for ip in ips:
        try:
            net = ip.split('/')[1]
        except IndexError as e:
            net = None
        if net:
            ipnet_.append(ip)
        else:
            hostLst.append(ip)

    print('ipnet is ' + str(ipnet_))

    for net in ipnet_:
        discoveryLst =  nmapNet(net)
        hostLst.extend(discoveryLst)

    if len(hostLst) == 0:
        print('try self discovery...')
        ipnet = getIfconfigIPv4()
        ipn = getIpNet(ipnet)
        hostLst = nmapNet(ipn)

    #print('hostLst is... ' + str(hostLst))
    print('discovered: ' + str(hostLst))
    return hostLst

def detectScan(ips, db_store):
    pass


def b2sumFim(name, db_store):
    fim = store.getFim(name, db_store)
    if fim is None:
        return str(name) + ' is None'
    else:
        fim = fim[0]

    try:
        jdata = json.loads(fim)
    except json.decoder.JSONDecodeError:
        return 'invalid json ' + str(fim)

    #print('run.fim.run ' + str(fim))
    print(str(jdata)) 

    for k,v in jdata.items():
        b = b2sum(k)
        print(k + ' ' + b)
        jdata[k] = b

    #replace = store.replaceFim( name, json.dumps(jdata), db_store)
    replace = store.replaceINTO('fims', name, json.dumps(jdata), db_store)
    #print(replace)
    #return True
    return replace

def checkFim(name, db_store):
    #print('checkFim .now ' + str(name))
    fimDct = getFimDct(name, db_store)
    for k,v in fimDct.items():
        #print(k,v)
        #print(k, ' CHANGED')
        if len(v) == 0:
            print(k, 'ADDED')
        else:
            print(k, 'CHANGED')
    return True

#def checkFimAndReport(name, db_store):
#    Dct = {}
#    #print('checkFimAndReport ' + str(name))
#    fimDct = getFimDct(name, db_store)
#    
#    for k,v in fimDct.items():
#        #print(k,v)
#        #print(k, ' CHANGED')
#        if len(v) == 0:
#            #print(k, 'ADDED')
#            Dct[k] = 'ADDED'
#        else:
#            #print(k, 'CHANGED')
#            Dct[k] = 'CHANGED'
#
#    #try:
#    #    jdata = json.loads(Dct)
#    #except json.decoder.JSONDecodeError:
#    #    return 'invalid json ' + str(fim)
#    #replace = store.replaceINTO('reports', name, json.dumps(jdata), db_store)
#
#    #get current_report_dct
#    #current_report = store.getData('reports', name, db_store)
#    #current_report = current_report[0]
#    #current_report = json.loads(current_report)
#
#    #if Dct == current_report:
#    #    #print('same Dct')
#    #    run = True
#    #else:
#    #    #print('not.same.Dct')
#    #    run = store.replaceINTO('reports', name, json.dumps(Dct), db_store)
#    #    print('PERF replaceINTO occured Fim ')
#
#    gDict[name] = ['sentinel_fim_job' + json.dumps(Dct) ]
#
#
#    #replace = store.replaceINTO('reports', name, json.dumps(Dct), db_store)
#    #return replace
#    #return run
#    return True

def fimCheck(name, db_store):

    Dct = {}
    fimDct = getFimDct(name, db_store)
    
    for k,v in fimDct.items():
        #print(k,v)
        #print(k, ' CHANGED')
        if len(v) == 0:
            #print(k, 'ADDED')
            Dct[k] = 'ADDED'
        else:
            #print(k, 'CHANGED')
            Dct[k] = 'CHANGED'

    _key = 'fimcheck-' + str(name)

    if bool(Dct):
        val = 1
    else:
        val = 0

    Dct['config'] = name

    gDict[_key] = ['sentinel_job_output' + json.dumps(Dct) + ' ' + str(val) ]

    return True






    #print('fimCheck get config... ' + str(config))

    #data = store.getFim(name, db_store)
    #if data is None:
    #    return 'data is None'
#
#        #get current_report_dct
#
#    data = data[0]
#    data = json.loads(data)
#    print('data is type ' + str(type(config)) + ' ' + str(config))

    #check = checkFimAndReport(config, db_store)
    #check = checkFimAndReport(config, db_store)
    #print(check)

    #else:
    #    conf = conf[0]
    ##print('conf ' + str(conf))
    #try:
    #    jdata = json.loads(conf)
    #except json.decoder.JSONDecodeError:
    #    return 'invalid json ' + str(conf)
    #print(str(jdata))
    #return check

    #print('name ' + str(name))
    #print('conF is   ' + str(conf))

    #return check



def getFimDct(name, db_store):
    #print('getFimDct')
    Dct = {}
    fim = store.getFim(name, db_store)
    if fim is None:
        return str(name) + ' is None'
    else:
        fim = fim[0]

    try:
        jdata = json.loads(fim)
    except json.decoder.JSONDecodeError:
        return 'invalid json ' + str(fim)

    for k,v in jdata.items():
        b = b2sum(k)
        if b != v:
            #print(k + ' CHANGED')
            #Dct[k] = 'CHANGED'
            Dct[k] = v

    #return True
    return Dct

def addFimFile(name, _file, db_store):
    fim = store.getFim(name, db_store)
    if fim is None:
        return str(name) + ' is None'
    else:
        fim = fim[0]

    try:
        jdata = json.loads(fim)
    except json.decoder.JSONDecodeError:
        return 'invalid json ' + str(fim)

    jdata[_file] = ""

    #print('new.jdata ' + str(jdata))
    update = store.updateData('fims', name, json.dumps(jdata), db_store)
    #update = store.updateFims(name, json.dumps(jdata), db_store)
    #replace = store.replaceINTO('fims', name, json.dumps(jdata), db_store)
    #print(update)

    #return True
    return update

def delFimFile(name, _file, db_store):
    fim = store.getFim(name, db_store)
    if fim is None:
        return str(name) + ' is None'
    else:
        fim = fim[0]

    try:
        jdata = json.loads(fim)
    except json.decoder.JSONDecodeError:
        return 'invalid json ' + str(fim)

    #jdata[_file] = ""
    try:
        del jdata[_file]
    #except KeyError: pass
    except KeyError:
        return 'not found ' + str(_file)

    update = store.updateData('fims', name, json.dumps(jdata), db_store)
    return update

#def runAlert(name, db_store):
#    #print('start runAlert ' + str(name))
#    alert = False
#
#    _alert = store.getData('alerts', name, db_store)
#    #print('alertData is ' + str(type(_alert)) + ' ' + str(_alert))
#    #print('DATA Data is ' + str(type(data)) + ' ' + str(data))
#
#    if type(_alert) == tuple:
#        _alert = _alert[0]
#
#    try:
#        jdata = json.loads(_alert)
#    except json.decoder.JSONDecodeError:
#        jdata = None
#
#    #new_json = jdata
#    #new_json = copy.deepcopy(jdata)
#    new_json = copy.copy(jdata)
#
#    #print('jdata is ' + str(type(jdata)) + ' ' + str(jdata))
#
#    _report = jdata.get('report', None)
#    _config = jdata.get('config', None)
#    _job    = jdata.get('job', None)
#    _repeat = jdata.get('repeat', None)
#
#    #print('_report is ' + str(_report))
#    #print('_config is ' + str(_config))
#    #print('_repeat is ' + str(_repeat))
#
#    #getReport
#    report = store.getData('reports', _report, db_store)
#    #print('getReport report is ' + str(type(report)) + ' ' + str(report))
#
#    #getConfig
#    config = store.getData('configs', _config, db_store)
#    #print('getConfig configs is ' + str(type(config)) + ' ' + str(config))
#
#    #getJob just verifies options
#    #for k in options:
#    #    print(k)
#
#    if _job in options:
#        job = _job
#    else:
#        job = None
#        new_json['error'] = 'job is ' + str(_job)
#        
#
#    if report is None:
#        new_json['error'] = 'report is ' + str(_report)
#    else:
#        report = report[0] #tuple
#        report = json.loads(report) #<class 'dict'>
#
#    if config is None:
#        new_json['error'] = 'config is ' + str(_config)
#    else:
#        config = config[0] #tuple
#        config = json.loads(config) #<class 'dict'>
#
#    if report is not None and config is not None and job is not None:
#        #print('runAlert job name ' + str(job))
#        #print('report ' + name + ' is ' + str(type(report)) + ' ' + str(report))
#        #print('config is ' + str(type(config)) + ' ' + str(config))
#        # check if empty json {}
#        #bool True|False
#        #report_items = bool(report)
#        #if not report_items:
#        #    print('Empty Dct')
#        #if bool(report):
#        #    alert = True
#
#        #alert = isAlert(name, _report, report)
#        alert = isAlert(_report, job, report, _alert)
#
#    new_json['alert'] = alert
#
#    if new_json == jdata:
#        #print('same')
#        update = None
#    else:
#        #print('diff')
#
#        #post, may need to update/remove report_error or config_error
#
#        update = store.updateData('alerts', name, json.dumps(new_json), db_store)
#
#    #update = store.updateData('alerts', name, json.dumps(new_json), db_store)
#    #return alert
#    if alert is True:
#        return report
#    else:
#        return False

#alert = isAlert(_report, job, report, _alert)

#def isAlert(name, _report, report):
#    print('isAlert ' + name, _report, report)

#def isAlert(name, job, report, _alert):
#    #print('isAlert ' + name, job, _dct)
#    alert = False
#
#    #print('report ' + str(report))
#    #print('_alert ' + str(_alert))
#    _alert = json.loads(_alert)
#    #print('_alert.loads ' + str(_alert))
#
#
#    #isAlert fim-2 fim-check {'/etc/group': 'ADDED', '/Users/krink/.ssh/config': 'ADDED'}
#    if job == 'fim-check':
#        #print('...check if empty')
#        #report_items = bool(_dct)
#        if bool(report):
#            alert = True
#
#    #isAlert proc-monitor ps-check {'procs': 418, 'defunct': 0}
#    if job == 'ps-check':
#        #print(job, report)
#        _procs = report.get('procs', None)
#        _defunct = report.get('defunct', None)
#
#        #print('procs val ' + str(_procs))
#        #print('defunct val ' + str(_defunct))
#
#        _procs2 = _alert.get('procs', None)
#        _defunct2 = _alert.get('defunct', None)
#
#        #print('procs val2 ' + str(_procs2))
#        #print('defunct val2 ' + str(_defunct2))
#        if int(_procs) > int(_procs2):
#            #print(str(_procs) + ' greater than ' + str(_procs2))
#            alert = True
#
#        #print(str(_defunct) + ' over ' + str(_defunct2))
#        if int(_defunct) >= int(_defunct2):
#            #print(str(_procs) + ' greater than ' + str(_procs2))
#            alert = True
#
#    return alert

def psCheck(name, db_store):
    #print(str(_data)) #None
    import modules.ps.ps
    psDct = modules.ps.ps.get_ps()
    #for k,v in psDct.items():
    #    print(k,v)
    #dump into reports...
    #check = checkPsAndReport(name, psDct, db_store)
    #return check

    _key = 'pscheck-' + str(name)

    psDct['name'] = name
    val = 1
    gDict[_key] = ['sentinel_job_output' + json.dumps(psDct) + ' ' + str(val) ]

    return True


#def checkPsAndReport(name, Dct, db_store):
#
#    #for k,v in _dct.items():
#    #    print(k,v)
#
#    #print('psDct ' + str(psDct))
#    #io performance, compare psDct w/ current report vals
#    #and write/replace only if diff
#    #
#    current_report = store.getData('reports', name, db_store)
#    current_report = current_report[0]
#    current_report = json.loads(current_report)
#    #print('current_report ' + str(current_report))
#    #maybe revist this, procs keeps changing, just need know when alert.... but,
#
#    if Dct == current_report:
#        #print('same Dct')
#        run = True
#    else:
#        #print('not.same.Dct')
#        run = store.replaceINTO('reports', name, json.dumps(Dct), db_store)
#        print('PERF replaceINTO occured psCheck ')
#
#    return run
    

#we'll move these into db config store later
options = {
 'vuln-scan' : vulnScan,
 'port-scan' : portScan1,
 'port-scan2' : portScan2,
 'detect-scan' : detectScan,
 'fim-check' : fimCheck,
 'ps-check' : psCheck,
}
#options[sys.argv[2]](sys.argv[3:])

def runJob(name, db_store):
    #print('runJob')
    val = 0
    #-start
    start = time.strftime("%Y-%m-%d %H:%M:%S")

    job = store.getJob(name, db_store)
    if not job:
        #print('no job')
        return None
    #print(str(type(job)))
    #print(job)

    if type(job) == tuple:
        job = job[0]

    try:
        jdata = json.loads(job)
    except json.decoder.JSONDecodeError:
        #print('invalid json')
        return None

    #don't need to do this now either...
    #new_json = copy.copy(jdata)

    #new_json['start'] = start
    jdata['start'] = start
    jdata['name'] = name
    
    # del element['hours']
    try:
        #del new_json['done']
        del jdata['done']
    except KeyError: pass
    try:
        #del new_json['success']
        del jdata['success']
    except KeyError: pass

    gDict[name] = [ str('sentinel_job') + json.dumps(jdata) + ' ' + str(val) ]

    #replace = replaceJobsJson(name, json.dumps(new_json), db_store)
    #don't need to do this now...
    #replace = store.replaceINTO('jobs', name, json.dumps(new_json), db_store)
    #print('PERF replaceINTO occured on jobs')
    #print('replace was ' + str(replace))

    #_time = jdata.get('time', None) 
    #_repeat = jdata.get('repeat', None) 

    _job = jdata.get('job', None) 
    _ips = jdata.get('ips', None) 
    _config = jdata.get('config', None) 

    #if type(_ips) == list:
    #if type(_ips) == str:
        
    #run = options[_job](_ips, db_store)

    if _ips:
        _data = _ips
    elif _config:
        _data = _config
    elif _config is None:
        _data = name
    else:
        _data = None

    try:
        run = options[_job](_data, db_store)
    except KeyError:
        # unknown "job":"????"
        #return 'unknown job ' + str(_job)
        run = 'unknown job ' + str(_job)

    #-done
    done = time.strftime("%Y-%m-%d %H:%M:%S")
    #new_json['done'] = done
    #new_json['success'] = run
    jdata['done'] = done
    jdata['success'] = run
    #update = updateJobsJson(name, json.dumps(new_json), db_store)

    #don't need to do this now...
    #update = store.updateData('jobs', name, json.dumps(new_json), db_store)
    #print('PERF updateData occured on jobs')

    if run is True:
        val = 1

    #print('gDict  updateData occured on jobs')

    #may need to remove old gDict entries as well... perhaps here...

    #promHELP = '# HELP sentinel_job The sentinel job service.'
    #promTYPE = '# TYPE sentinel_job gauge'
    #gDict[name] = [ promHELP, promTYPE, str('sentinel_job') + json.dumps(new_json) + ' ' + str(val) ]
    #gDict[name] = [ str('sentinel_job') + json.dumps(new_json) + ' ' + str(val) ]
    gDict[name] = [ str('sentinel_job') + json.dumps(jdata) + ' ' + str(val) ]

    #gList.append('PERF updateData occured on jobs')
    #print('update was ' + str(update))
    #print('run ' + str(name) + ' was ' + str(run))
    #return True
    #print('run ' + str(run))
    return run
    #MARK

def getDuration(_repeat):
    #amt, scale = getDuration(_repeat)
    #5min, 1hour, 3day
    import re

    num = None
    scale = None

    reLst = re.split('(\d+)', _repeat)
    for item in reLst:
        if item.isnumeric():
            num = item
        if item.isalpha():
            scale = item

    #print(num, scale)

    if scale == 'min':
        scale = 'minutes'
        amt = int(num)
    elif scale == 'hour':
        scale = 'hours'
        amt = int(num)
    elif scale == 'day':
        scale = 'days'
        amt = int(num)
    else:
        scale = 'seconds'
        amt = 0
        
    return scale, amt

#def sentryProcessAlerts(db_store):
#    #print( 'process Alerts')
#    Dct = {}
#    alerts = store.selectAll('alerts', db_store)
#    for alert in alerts:
#        #print(alert[0])
#        #name = alert[1]
#        #jdata = alert[3]
#        name = alert[0]
#        #jdata = alert[2]
#
#        try:
#            #jdata = json.loads(alert[3])
#            jdata = json.loads(alert[2])
#        except json.decoder.JSONDecodeError:
#            #print('invalid json')
#            #return None
#            jdata = json.loads('{}')
#        Dct[name] = jdata
#
#    #no name?
#    #print('this is my name right before runAlert ' + str(name))
#    #need job name...
#
#
#    #run = runAlert(name, db_store)
#    for name, data in Dct.items():
#        #print('runAlert ' + str(data))
#
#        #sent = None
#
#        #alert = runAlert(name, db_store)
#        alert = 'MANUAL'
#        #print('Alert ' + name + ' ' + str(alert) + ' ' + str(data))
#
#    return True


######################################################################
        #need config
        #print('config- ' + str(config))

        #config = data.get('config', None)
        #repeat = data.get('repeat', None)
        #_sent = data.get('sent', None)

        #cleared = data.get('cleared', None)
        #count = data.get('count', None)

        #print('repeat ' + str(repeat))

        #if repeat is not None:
        #if repeat is not None:
        #    if sent is not None:
        #if repeat and _sent:
        #    #getDuration
        #    scale, amt = getDuration(repeat)
        #    #print(scale, amt)
        #    #start_time = datetime.datetime.strptime(sent, "%Y-%m-%d %H:%M:%S")
        #    now = time.strftime("%Y-%m-%d %H:%M:%S")
        #    now_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        #    sent_time = datetime.datetime.strptime(_sent, "%Y-%m-%d %H:%M:%S")
#
#            arg_dict = {scale:amt}
#            delta_time = sent_time + datetime.timedelta(**arg_dict)
#            #print('delta_time ' + str(delta_time))
#                
#            if now_time > delta_time:
#                #print('re-send ' + str(name))
#                sent = None
#            else:
#                sent = _sent

        #print('DEBUG Alert ' + str(name) + ' alert: ' + str(alert) + ' repeat ' + str(repeat) + ' sent ' + str(sent))
        #DEBUG Alert alert-on-fim-2 alert: {'/opt/NO.FILE.txt': 'ADDED'} repeat 1min sent None


        #if alert is True:
        #if alert:
        #    #config = data.get('config', None)
        #    if sent is None:
        #if alert and sent is None:
        #if alert and not sent:
        #if alert is True and sent is None:
        #if alert and sent is None:

        #if alert and not sent:
#        if alert and sent is None:
#            subject = ''
#            #time_sent = sendAlertNotice(name, config, subject, alert, db_store)
#            time_sent = time.strftime("%Y-%m-%d %H:%M:%S")
#                #print('send Notice: ' + str(send))
#                #now = time.strftime("%Y-%m-%d %H:%M:%S")
#                #need the json...
#                #print('the json data currently is ' + str(data))
#                #lets update here, as opposed to in/at sendAlertNotice
#
#                #don't need to copy.copy here, just update the data reference
#            data['sent'] = time_sent
#                #print('name ' + name)
#                #print('data ' + str(data))
#
#            #lets remove cleared here
#            #del data['cleared']
#            try:
#                del data['cleared']
#            except KeyError: pass
#
#                #olde school update.  try just the data['sent'] = send
#            update = store.updateData('alerts', name, json.dumps(data), db_store)
#            print('PERF updateData occured on alerts')
#            #update = store.updateDataItem('sent', time_sent, 'alerts', name, db_store) #broken.broken.update wrong item
#            print(update)

        #print('DEBUG Alert ' + str(name) + ' alert: ' + str(alert) + ' repeat ' + str(repeat) + ' sent ' + str(sent) + ' cleared ' + str(cleared))

        #if not alert and sent:
        #if not alert and sent (and not 'cleared'):
        #if alert is False and sent:
        #if not alert and sent and not cleared:
        #if (alert is False and _sent and not cleared) or (alert is False and _sent and cleared):
#        if alert is False and _sent and not cleared:
#            # alert cleared, send notice
#            #time_cleared = time.strftime("%Y-%m-%d %H:%M:%S")
#            subject = 'cleared'
#            #time_cleared = sendAlertNotice(name, config, subject, alert, db_store)
#            time_cleared = time.strftime("%Y-%m-%d %H:%M:%S")
#
#            data['cleared'] = time_cleared
#
#            #lets remove _sent here
#            #del data['sent']
#            try:
#                del data['sent']
#            except KeyError: pass
#
#
#            if count:
#                count += int(count)
#            else:
#                count = 1
#
#            data['count'] = count
#
#            update = store.updateData('alerts', name, json.dumps(data), db_store)
#            print('PERF updateData occured on alerts')
#            print(update)
#
#
#    return True

#def sendAlertNotice(name, config, _subject, _message, db_store):
#    #print('sendNotice ' + str(name) + ' ' + str(config) + ' ' + str(_dct))
#
#    message = json.dumps(_message)
#
#    sent = False
#
#    if config == 'email':
#        # send email...
#        subject = 'sentinel alert ' + name + ' ' + str(_subject)
#        send = sendEmail(subject, message, db_store)
#        logging.info('alert email sent ' + name + ' ' + str(_subject))
#        sent = time.strftime("%Y-%m-%d %H:%M:%S")
#
#    if config == 'logfile':
#        _logfile = store.getData('configs', config, db_store)
#        _logfile = _logfile[0]
#        _logfile = json.loads(_logfile)
#        _logfile = _logfile.get('logfile', None)
#        #print(_logfile)
#        # write log...
#        subject = 'sentinel ' + str(time.strftime("%Y-%m-%d %H:%M:%S")) + ' ' + name + ' ' + str(_subject)
#        with open(_logfile, 'a+') as log:
#            log.write(subject + ' ' + message + '\n')
#        logging.info('alert logfile written ' + name + ' ' + str(_subject))
#        sent = time.strftime("%Y-%m-%d %H:%M:%S")
#
#    return sent


def sentryProcessJobs(db_store):
    #print('process Schedule')
    run = None

    rLst = []

    jobs = store.selectAll('jobs', db_store)
    if jobs is None:
        return None

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    now_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")

    for job in jobs:
        #name = job[1]
        #jdata = job[3]
        name = job[0]
        jdata = job[2]
        #print(job)
        #print(name)
        try:
            #jdata = json.loads(job[3])
            jdata = json.loads(job[2])
        except json.decoder.JSONDecodeError:
            print('invalid json')
            return None

        #what?
        _job = jdata.get('job', None)
        if _job is None:
            print('job is None')
            return None

        #when?
        _start = jdata.get('start', None)
        _done = jdata.get('done', None)
        _repeat = jdata.get('repeat', None)
        _time = jdata.get('time', None)


        if _time:
            #run at time
            run_time = datetime.datetime.strptime(_time, "%Y-%m-%d %H:%M:%S")

            #if now_time > run_time and _start is None and _done is None:
            if now_time > run_time and _start is None:
                #print('Over time and _start is None.  run_time')
                run = runJob(name, db_store)
                #print(run)

        if _repeat:
            scale, amt = getDuration(_repeat)
            #print(scale + ' amt ' + str(amt))

            if _start is None:
                run = runJob(name, db_store)

            else:
                start_time = datetime.datetime.strptime(_start, "%Y-%m-%d %H:%M:%S")
                #start_minute = int(str(start_time).split()[1].split(':')[1])
                #print('start ' + str(start_time) + ' m: ' + str(start_minute))
                if _done:
                    done_time = datetime.datetime.strptime(_done, "%Y-%m-%d %H:%M:%S")
                    #print('done       ' + str(done_time))

                    #td_time = done_time + datetime.timedelta(minutes=5)
                    #delta_time = done_time + datetime.timedelta(amt) #TypeError: unsupported type for timedelta days component: str
                    #delta_time = done_time + datetime.timedelta(minutes = 5)
                    #delta_time = done_time + datetime.timedelta(scale = amt) #TypeError: 'scale' is an invalid keyword argument for __new__()
                    
                    arg_dict = {scale:amt}
                    delta_time = done_time + datetime.timedelta(**arg_dict)
                    #print('delta_time ' + str(delta_time))

                    if now_time > delta_time:
                        #print('Over time.  repeat_time')
                        run = runJob(name, db_store)
                        #print(run)
    
    #print('end')
    #return True
    return run

#def replaceJobsJson(name, jdata, db_store):
#    #replaceINTO(tbl, item, data, db_file):
#    replace = store.replaceINTO('jobs', name, jdata, db_store)
#    return replace

#def updateJobsJson(name, jdata, db_store):
#    #replaceINTO(tbl, item, data, db_file):
#    #update = store.updateJobs(name, jdata, db_store)
#    update = store.updateData('jobs', name, jdata, db_store)
#    return update


def processD(List):
    sentinel_up = 1
    start = time.time()

    #gList.clear()

    promHELP = '# HELP sentinel_up Whether the sentinel service is up.'
    promTYPE = '# TYPE sentinel_up gauge'
    promDATA = 'sentinel_up ' + str(sentinel_up)
    #gList.append(promHELP)
    #gList.append(promTYPE)
    #gList.append(promDATA)
    #gQ.put(promHELP)
    #gQ.put(promTYPE)
    #gQ.put(promDATA)
    #gList[0] = promHELP
    #gList[1] = promTYPE
    #gList[2] = promDATA

    gDict['sentinel_up'] = [promHELP, promTYPE, promDATA]

    #gList.extend(List)
    #print(gList)

    return True



def sentryScheduler(db_store):
    #gList = []
    #sigterm = False
    while (sigterm == False):

        List = []
        #run = sentryProcessJobs(db_store)
        job = threading.Thread(target=sentryProcessJobs, args=(db_store,), name="SentryJobRunner")
        job.setDaemon(True)
        job.start()

        ##run = sentryProcessAlerts(db_store)
        #alert = threading.Thread(target=sentryProcessAlerts, args=(db_store,), name="SentryAlertRunner")
        #alert.setDaemon(True)
        #alert.start()


        tcount = 0
        #threads = []
        for thread in threading.enumerate():
            #print(str(thread.name))
            if thread.name == 'MainThread':
                continue
            if thread.name == 'Scheduler':
                continue
            #print(str(thread.name))
            tcount += 1
            #threads.append(thread)

        pcount = 0
        #process = []
        for proc in multiprocessing.active_children():
            #print(str(proc.name))
            pcount += 1
            #process.append(proc)



        List.append('threads ' + str(tcount))
        List.append('process ' + str(pcount))

        #cDct = {}
        #get current
        #counts = store.selectAll('counts', db_store)
        #for row in counts:
        #    #print(row)
        #    name = row[0]
        #    val  = row[1]
        #    #print(name, val)
        #    #cDct[name] = val
        #    if name == 'threads':
        #        #print('compare val to tcount ' + str(val) + ' ' + str(tcount))
        #        if int(val) == int(tcount):
        #            continue
        #        else:
        #            #update1 = store.updateCounts('threads', tcount, db_store)
        #            #print('PERF updateCounts occured on threads ' + str(update1))
        #            print('PERF updateCounts occured on threads ' + str(tcount))
        #            List.append('PERF updateCounts occured on threads ' + str(tcount))
#
#            if name == 'process':
#                #print('compare val to pcount ' + str(val) + ' ' + str(pcount))
#                if int(val) == int(pcount):
#                    continue
#                else:
#                    #update2 = store.updateCounts('process', pcount, db_store)
#                    #print('PERF updateCounts occured on process ' + str(update2))
#                    print('PERF updateCounts occured on process ' + str(pcount))
#                    List.append('PERF updateCounts occured on process ' + str(pcount))


        #for t in threads:
        #    t.join()

        #for p in process:
        #    p.join()

        processD(List)

        time.sleep(3)

    return True
    #return run

def listRunning(db_store):
    rows = store.getAllCounts(db_store)
    for row in rows:
        print(row)
    return True

def sentryCleanup(db_store):
    #import logging
    logging.info("Cleanup:")
    #update1 = store.replaceCounts('threads', 0, db_store)
    #update2 = store.replaceCounts('process', 0, db_store)
    return True

def sentryMode(db_store):

    #gList = []

    config = store.getData('configs', 'prometheus', db_store)
    #print(config)
    if config is None:
        update = store.replaceINTO('configs', 'prometheus', json.dumps({'port': 9111, 'path': '/metrics'}), db_store)
        config = store.getData('configs', 'prometheus', db_store)

    #config = config[0]
    config = json.loads(config[0])
    #print(config['port'])
    #print(config['path'])

    #global sigterm
    #sigterm = False

    #import logging
    import atexit
    import signal

    loglevel = logging.INFO
    logformat = 'sentinel %(asctime)s %(filename)s %(levelname)s: %(message)s'
    datefmt = "%b %d %H:%M:%S"
    logging.basicConfig(level=loglevel, format=logformat, datefmt=datefmt)
    
    atexit.register(sentryCleanup, db_store)
    signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    logging.info("Sentry startup")
    update1 = store.replaceCounts('threads', 0, db_store)
    update2 = store.replaceCounts('process', 0, db_store)

    #scheduler = threading.Thread(target=sentryScheduler, name="scheduler")
    scheduler = threading.Thread(target=sentryScheduler, args=(db_store,), name="Scheduler")
    scheduler.setDaemon(True)
    scheduler.start()

    #alertmgr = threading.Thread(target=sentryAlertManager, args=(db_store,), name="AlertManager")
    #alertmgr.setDaemon(True)
    #alertmgr.start()

    httpd = HTTPServer(('', config['port']), Handler)

    #while (sigterm == False):
    try:
        #print('sentry mode')
        #time.sleep(60)
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit, Exception):
        sigterm = True
        scheduler.join()
        httpd.server_close()
        logging.info("Sentry shutdown: " + str(sigterm))
        sys.exit(1)
    return True


if __name__ == '__main__':
# requires cli tools: arp, ping, lsof, nslookup, nmap
    pass

