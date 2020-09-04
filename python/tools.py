#!/usr/bin/env python3

from subprocess import Popen, PIPE
import threading

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

#class threadWithReturn(threading.Thread):
#    def __init__(self, *args, **kwargs):
#        super(threadWithReturn, self).__init__(*args, **kwargs)
#        self._return = None
#
#    def run(self):
#        if self._Thread__target is not None:
#            self._return = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
#
#    def join(self, *args, **kwargs):
#        super(threadWithReturn, self).join(*args, **kwargs)
#        return self._return

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



if __name__ == '__main__':

    import sys

    ip = sys.argv[1]

    ipL = ip.split('.')
    #ipn = ipL[0] + '.' + ipL[1] + '.' + ipL[2] + '.'
    net = ipL[0] + '.' + ipL[1] + '.'
    print('PingNet: ' + net + '{1..254}.{1..254}')

    p = []


    hosts = []
    for i in range(1, 255):
        _net = net + str(i) + '.'
        for j in range(1, 255):
            hosts.append(_net + str(j))


    threads = []
    for _ip in hosts:
        #print(_ip)
        ping = PingIp()
        t = ThreadWithReturnValue(target=ping.run, args=(_ip,))
        threads.append(t)

    #perhaps delay between here
    for t in threads: t.start()
#Exception in thread Thread-1281:
#File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/threading.py", line 932, in _bootstrap_inner
#OSError: [Errno 24] Too many open files

    for t in threads:
        ret = t.join()
        #print(ret)
        vL = ret.split(' ')
        v = vL[0]
        i = vL[1]
        if int(v) == 1:
            print(v, i)

    print('justified')

    #########################

    #ip = '192.168.0.1/24'
    #scan = NmapSN()
    ##t = threadWithReturn(target=scan.run, args=(ip,))
    #t = ThreadWithReturnValue(target=scan.run, args=(ip,))
    #t.start()
    ##ret,e = t.join()
    #ret = t.join()
    #print(ret)



    #threadsDct = {}
    #for i in range(1, 255):
    #    _ip = ipn + str(i)
    #    print(_ip)
    #    ping = PingIp()
    #    t = ThreadWithReturnValue(target=ping.run, args=(_ip,))
    #    threadsDct[ip] = t
    #    t.start()

    #for t in threads: t.start()
    #for key in threadsDct: t.start()

    #for i,t in threadsDct.items():
    #    ret = t.join()
    #    print(ret, i)



    #threads = []
    #for i in range(1, 255):
    #    _ip = ipn + str(i)
    #    #print(_ip)
    #    ping = PingIp()
    #    t = ThreadWithReturnValue(target=ping.run, args=(_ip,))
    #    threads.append(t)
#
#    for t in threads: t.start()
#    for t in threads:
#        ret = t.join()
#        print(ret)

    #t = ThreadWithReturnValue(target=scan.run, args=(ip,))
    #ret = t.join()
    #print(ret)
  
    #ip = '192.168.0.1/24'
    #scan = NmapSN()
    ##t = threadWithReturn(target=scan.run, args=(ip,))
    #t = ThreadWithReturnValue(target=scan.run, args=(ip,))
    #t.start()
    ##ret,e = t.join()
    #ret = t.join()
    #print(ret)

    #t = threading.Thread(target=scan.run, args=(ip,))
    #t.start()
    #t.join()
    #print(t)
    #sys.exit(0)


    #cmd = 'nmap -sn -n --min-parallelism 256 192.168.0.0/24'
    #proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    #out = proc.stdout.readlines()
    #for line in out:
    #    line = line.decode('utf-8').strip('\n')
    #    #print(line)
    #    match = 'Nmap scan report for'
    #    if line.startswith(match, 0, len(match)):
    #        line = line.split()
    #        #print(line)
    #        ip = line[4]
    #        print(ip)



    #ip = '192.168.0.1'
    #pn = pingNet(ip)
    #print(pn)

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

