#!/usr/bin/env python3

from subprocess import Popen, PIPE
import threading
import sys
import time
import collections
import socket

import store

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
        cmd = 'nmap -n -sT -sU -T5 –-top-ports 1000 ' + ip  #
    elif level == '3':
        cmd = 'nmap -n -sT -sU -T5 -p- ' + ip #
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

    #udp, listen, established, time_wait = {}

    udp = {}
    listen = {}
    established = {}
    time_wait = {}

    #udp = listen = established = time_wait = {}

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
    cmd = 'nmap -sP ' + str(net)
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




if __name__ == '__main__':
# requires cli line tools: arp, ping, lsof, nslookup, nmap
    pass

    #net = '192.168.8.0/24'
    #ipLst = hostDiscoveryLst(net)
    #print(ipLst)


#https://nmap.org/docs/discovery.pdf
    #ip = '192.168.8.1'
    #hostLst = pingNet(ip)
    #print(hostLst)

    #net = '192.168.8.0/24'
    #ips = hostDiscovery(net)
    #print(ips)

    #my_ips = getSelfIPLst()
    #print(my_ips)


    #open_ports_root = printListenPortsDetailed()

    #open_ports = printListenPorts()

    #portsLst = listenPortsLst()
    #print(portsLst)

    #lsofDct = getLsOfDct()
    #print(lsofDct)

    #cntDct = cntLsOf()
    #for k,v in sorted(cntDct.items()):
    #    print(k,v)

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





