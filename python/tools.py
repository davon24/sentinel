#!/usr/bin/env python3

__version__ = '1.6.13-1-jan-29-1'

from subprocess import Popen, PIPE, STDOUT
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

import sqlite3

from hashlib import blake2b, blake2s

from http.server import HTTPServer, BaseHTTPRequestHandler

import os, pwd, grp
import select
import re

import store

#import smtplib
#import ssl
#import certifi

#import atexit
#import signal

#import queue
#gQ = queue.Queue()
#gList = []
#global gDict
#gDict = {}

import logging
loglevel = logging.INFO
logformat = 'sentinel %(asctime)s %(filename)s %(levelname)s: %(message)s'
datefmt = "%b %d %H:%M:%S"
logging.basicConfig(level=loglevel, format=logformat, datefmt=datefmt)

#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.naive_bayes import MultinomialNB

#manager = multiprocessing.Manager()
#global gDict
#gDict = manager.dict()

import atexit
import signal

sigterm = False

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == _metric_path:
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()

            _prom = str(db_store) + '.prom'
            try:
                with open(_prom, 'r') as _file:
                    lines = _file.readlines()
                    for line in lines:
                        #self.wfile.write(bytes(str(line) + str('\n'), 'utf-8'))
                        self.wfile.write(bytes(str(line), 'utf-8'))
            except Exception as e:
                logging.info('Sentry Exception ' + str(e))
            
        else:
            self.send_error(404) #404 Not Found
        return

    def do_POST(self):
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

def b2checksum(_string):
    is_64bits = sys.maxsize > 2**32
    if is_64bits:
        blake = blake2b(digest_size=20)
    else:
        blake = blake2s(digest_size=20)

    s = _string.encode('utf-8')

    blake.update(s)
    return str(blake.hexdigest())

def tail_nonblocking(_file):

    if not os.path.isfile(_file):
        logging.critical('Sentry tail no file handle ' + str(_file))
        return False

    if sys.platform == 'darwin':
        cmd = ['tail', '-0', '-F', _file] #macos
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        cmd = ['tail', '-n', '0', '-F', _file] #linux
    else:
        cmd = ['tail', '-F', _file]

    try:
        f = Popen(cmd, shell=False, stdout=PIPE,stderr=PIPE)
        p = select.poll()
        p.register(f.stdout)

        while (f.returncode == None):
            if p.poll(1):
                line = f.stdout.readline()
                #print(line)
                yield line
            time.sleep(1)

    except Exception as e:
        logging.critical('Exception ' + str(e))
        return False
    return True

def tail(_file):

    if not os.path.isfile(_file):
        logging.critical('Sentry tail no file handle ' + str(_file))
        return False

    if sys.platform == 'darwin':
        cmd = ['tail', '-0', '-F', _file] #macos
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        cmd = ['tail', '-n', '0', '-F', _file] #linux
    else:
        cmd = ['tail', '-F', _file]

    try:
        #f = Popen(cmd, shell=False, stdout=PIPE,stderr=PIPE)
        f = Popen(cmd, shell=False, stdout=PIPE,stderr=STDOUT)
        while (f.returncode == None):
            line = f.stdout.readline()
            if not line:
                #break
                time.sleep(1)
            else:
                yield line
            sys.stdout.flush()

    except Exception as e:
        logging.critical('Exception ' + str(e))
        return False

    return True

def logstream(_format='json'):

    if sys.platform == 'darwin':
        #cmd = ['log', 'stream', '--style', _format] #macos
        cmd = ['log', 'stream', '--style', 'ndjson'] #macos
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        cmd = ['journalctl', '-f', '-o', _format] #linux
    else:
        logging.critical('Fail: No log stream.  No such file or directory')
        return False

    try:
        f = Popen(cmd, shell=False, stdout=PIPE,stderr=PIPE)
        while (f.returncode == None):

        #print('pid ', str(f.pid))
        #while (sigterm == False):

            line = f.stdout.readline()
            if not line:
                #break
                time.sleep(1)
            else:
                yield line
            sys.stdout.flush()

    #except Exception as e:
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        #os.kill(f.pid, signal.SIGKILL)
        #f.terminate() #SIGTERM
        f.kill() #SIGKILL
        logging.critical('Exception in logstream ' + str(e))
        return False

    return True


def extractLstDct(_list):
    Dct={}
    for _dct in _list:
        for k,v in _dct.items():
            Dct[k]=v
    return Dct


#def expertLogStreamRulesEngineGeneral_V1(jline, rulesDict, gDict):
#    h={}
#    ######################################################################
#    # process each rule one at a time
#    for _r,v in rulesDict.items():
#        #extract each rule and apply it to jline (jline is multi k,v)
#        #print('rule ',_r,v)
#
#        jrules = json.loads(v)
#        #print(jrules)
#
#        _data   = jrules.get('data', None)
#        data = jline.get(_data)
#        if data:
#            b = b2checksum(str(data))
#        else:
#            b = b2checksum(str(jline))
#
#        _k = str(_r) +'-'+ str(b)
#
#        _search = jrules.get('search', None)
#        _match  = jrules.get('match', None)
#        _not    = jrules.get('not', None)
#        _pass   = jrules.get('pass', None)
#
#
#        if _match: 
#
#            d1 = extractLstDct(_match)
#            d2 = jline
#            d3 = {}
#
#            for key in d1:
#                if key in d2:
#                    if d1[key] == d2[key]:
#                        d3[key] = d1[key]
#
#            if d1 == d3: #print('match ', d3)
#                h[_k] = jline
#
#
#        if _search and data:
#            #print(_search)
#            #print(data) #data is None #TypeError: expected string or bytes-like object
#            if re.search(_search, data, re.IGNORECASE):
#                h[_k] = data
#
#                if _not:
#                    for no in _not:
#                        #if no in data:
#                        if no.lower() in data.lower(): #ignorecase
#                            h.pop(_k, None)
#                            #if h.pop(_k, None):
#                            #    print('   _not this one...', _k, ' ', data)
#        #else:
#        #    print('no.search.no.data ',_r, ' ', str(_search), ' ' , str(data))
#
#        if _pass:
#            for p in _pass:
#                __k = str(_r) +'-'+ str(p)
#                h.pop(__k, None)
#                #if h.pop(__k, None):
#                #    print('   _pass this one...', __k, ' ', data)
#
#    ######################################################################
#    
#    for k,v in h.items():
#        #print(k,v)
#        #_prom = 'prog="syslog_watch",match="' + str(s) + '",b2sum="' + str(b) + '",seen="' + str(seen) + '",json="' + str(line) + '"'
#        #gDict[_k] = [ 'sentinel_syslog_watch_rule_engine{' + _prom + '} ' + str(kDict[b]) ]
#
#        _prom = 'prog="syslog_watch",engine="rules",rule="' + str(k) + '",value="' + str(v) + '"'
#        gDict[_k] = [ 'sentinel_watch_syslog_rule_engine{' + _prom + '} 1']
#
#    #return True
#    return h

def getKeysDict(keys, jline):
    keysDct={}
    for key in keys:
        if key in jline.keys():
            keysDct[key] = jline[key]
    return keysDct

def expertLogStreamRulesEngineGeneral(jline, keys, rulesDict):

    h={}
    ######################################################################
    # process each rule one at a time
    for _r,v in rulesDict.items():
        #extract each rule and apply it to jline (jline is multi k,v)
        #print('rule ',_r,v)

        jrules = json.loads(v)
        #print(jrules)


        _data   = jrules.get('data', None)
        data = jline.get(_data)
        if data:
            b = b2checksum(data)
        else:
            #b = b2checksum(str(jline))
            keysDct = getKeysDict(keys, jline)
            b = b2checksum(str(keysDct))

        #if b in s.keys():
        #    seen = True
        #    v=s[b]
        #    v+=1
        #    s[b]=v
        #else:
        #    seen = False
        #    s[b]=1

        _k = str(_r) +'-'+ str(b)

        _search = jrules.get('search', None)
        _match  = jrules.get('match', None)
        _not    = jrules.get('not', None)
        _pass   = jrules.get('pass', None)


        if _match: 

            d1 = extractLstDct(_match)
            d2 = jline
            d3 = {}

            for key in d1:
                if key in d2:
                    if d1[key] == d2[key]:
                        d3[key] = d1[key]

            if d1 == d3: #print('match ', d3)
                #h[_k] = [_r,b,seen,s[b],jline]
                h[_k] = [_r,b,jline]


        if _search and data:
            #print(_search)
            #print(data) #data is None #TypeError: expected string or bytes-like object
            if re.search(_search, data, re.IGNORECASE):
                #h[_k] = [_r,b,seen,s[b],data]
                h[_k] = [_r,b,data]

                if _not:
                    for no in _not:
                        #if no in data:
                        if no.lower() in data.lower(): #ignorecase
                            h.pop(_k, None)
                            #if h.pop(_k, None):
                            #    print('   _not this one...', _k, ' ', data)
        #else:
        #    print('no.search.no.data ',_r, ' ', str(_search), ' ' , str(data))

        if _pass:
            for p in _pass:
                __k = str(_r) +'-'+ str(p)
                h.pop(__k, None)
                #if h.pop(__k, None):
                #    print('   _pass this one...', __k, ' ', data)

    ######################################################################
    
#    for k,v in h.items():
#        #print(k,v)
#        #_prom = 'prog="syslog_watch",match="' + str(s) + '",b2sum="' + str(b) + '",seen="' + str(seen) + '",json="' + str(line) + '"'
#        #gDict[_k] = [ 'sentinel_syslog_watch_rule_engine{' + _prom + '} ' + str(kDict[b]) ]
#
#        _rule  = v[0]
#        _b2sum = v[1]
#        _seen  = v[2]
#        _count = v[3]
#        _tdata = v[4]
#
#        _prom = 'prog="syslog_watch",engine="rules",rule="'+str(_rule)+'",b2sum="'+str(_b2sum)+'",seen="'+str(_seen)+'",data="' + str(_tdata) + '"'
#        gDict[_k] = [ 'sentinel_watch_syslog_rule_engine{' + _prom + '} ' + str(_count)]

    #return True
    return h



def getExpertRules(config, db_store):
    # ('watch-syslog-1', '2021-01-14 22:46:06', '{"config":"watch-syslog","search":[{"eventMessage":"error"}],"not":["NoError"]}')
    rulesDict = {}
    rules = store.selectAll('rules', db_store)
    for rule in rules:
        name = rule[0]
        jconf = rule[2]

        jdata = json.loads(jconf)
        jconfig = jdata.get('config', None)

        if config == jconfig:
            #print(name, jconf)
            rulesDict[name] = jconf
    return rulesDict


def updategDictR(gDict, rule_hit, s, verbose=False):

    for key in rule_hit:

        r = rule_hit[key][0]
        b = rule_hit[key][1]
        d = rule_hit[key][2]

        if b in s.keys():
            seen = True
            v=s[b]
            v+=1
            s[b]=v
        else:
            seen = False
            s[b]=1

        #gDict
        _k = str(r)+'-'+str(b)
        _prom = 'config="watch-syslog",rule="' + str(r) + '",b2sum="' + str(b) + '",seen="' + str(seen) + '",data="' + str(d) + '"'
        gDict[_k] = [ 'sentinel_watch_syslog_rule_engine{' + _prom + '} ' + str(s[b]) ]
        if verbose: print(_k, gDict[_k])

    return True

def sklearnNaiveBayesMultinomialNB(db_store):
    logging.info('Sentry watch-syslog naive_bayes.MultinomialNB')

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split

    X=[]
    y=[]

    #open/load training data
    rows = store.getAll('training', db_store)
    if len(rows) == 0:
        #print('Zero training data')
        logging.error('Zero training data. Can not perform naive_bayes.MultinomialNB')
        #print('pid ' + str(os.getpid()))
        #os.kill(os.getpid(),9)
        #sys.exit(1)
        #sigterm = True
        return (False, False)

    c=0
    t=0
    for row in rows:
        c+=1
        #print(row)
        _id = row[0]
        _tag = row[1]
        _jsn = row[2]
        #print(_id, _tag, _jsn)

        if int(_tag) != 0:
            t+=1

        y.append(_tag)
        X.append(_jsn)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    vectorizer = CountVectorizer()
    counts = vectorizer.fit_transform(X_train)
    classifier = MultinomialNB()
    targets = y_train
    classifier.fit(counts, targets)

    #print('training records ',str(c), ' tagged ', str(t))
    logging.info('training records '+str(c)+' tagged '+str(t))

    return (vectorizer, classifier)

def getAlgoDict(sklearn):
    algoDict={}
    for item in sklearn:
        #print('item ',item, ' ', str(type(item))) #<class 'dict'>
        for k,v in item.items():
            #print(k,v)
            algoDict[k]=v
    return algoDict


def sentryLogStream(db_store, gDict, verbose=False):
    logging.info('Sentry watch-syslog logstream ')

    conf = store.getData('configs','watch-syslog', db_store)
    if conf:
        config = json.loads(conf[0])
        #print('config.logfile ',config.get('logfile', None))
        logfile = config.get('logfile', None)
        rules   = config.get('rules', None)
        sklearn = config.get('sklearn', None)

    if rules:
        logging.info('Sentry watch-syslog expert_rules')
        rulesDct = getExpertRules('watch-syslog', db_store)

    if sklearn:
        algoDct = getAlgoDict(sklearn)

        if 'naive_bayes.MultinomialNB' in algoDct.keys():
            nbm_vectorizer, nbm_classifier = sklearnNaiveBayesMultinomialNB(db_store)


    s={}
    ##########################################################################
    for line in logstream():
        line = line.decode('utf-8')
        jline = json.loads(line)

        if rules:
            rule_hit = expertLogStreamRulesEngineGeneral(jline, rules, rulesDct)
            if rule_hit: updategDictR(gDict,rule_hit, s, verbose)

        if sklearn:
            _sample = json.dumps(jline) #this needs to be same as trained on
            sample = []
            sample.append(_sample)

            if 'naive_bayes.MultinomialNB' in algoDct.keys():
                sample_count = nbm_vectorizer.transform(sample)
                p_nbm = nbm_classifier.predict(sample_count)

                if int(p_nbm) == 1:
                    #gDict
                    _k = 'naive_bayes.MultinomialNB-'+str(b2checksum(_sample))
                    _prom = 'config="watch-syslog",algo="naive_bayes.MultinomialNB",predict="' + str(p_nbm) + '",data="' + str(json.dumps(jline)) + '"'
                    gDict[_k] = [ 'sentinel_watch_syslog_naive_bayes_multinomialnb{' + _prom + '} ' + str(p_nbm) ]
                    if verbose: print(_k, gDict[_k])

    ##########################################################################

    return True

def sampleLogStream(count, db_store):

    count=int(count)

    for line in logstream():

        count-=1
        if count == 0:
            break

        line = line.decode('utf-8')
        #jline = json.loads(line)
        #print(jline)

        tag=0

        run = store.updateTraining(tag, line, db_store)
        print(line)

    return True


def sentryTailFile(db_store, gDict, _file):
    for line in tail(_file):
        print(line)
    return True

def sentryTailResinLog(db_store, gDict, _file):

    logging.info('Sentry resin.match ' + str(_file))

    re_match1 = re.compile(r'Watchdog starting Resin',re.I)
    c=0
    for line in tail(_file):
        #print('resin ' + line)
        #line = line.decode('utf-8')
        line = line.decode('utf-8').strip('\n')
        #print(line)
        if re_match1.search(line):
            #print('Sentry Tail resin match ' + str(line))
            c+=1
            _key = 'sentry-resin-tail-match-' + str(c)
            prom = 'prog="resin",logfile="' + str(_file) + '",match="' + str(line) + '"'
            gDict[_key] = [ 'sentinel_resin_watch{' + prom + '} ' + str(c) ]


    return True

def sentryTailMariaDBAuditLog(db_store, gDict, _file):
    #https://mariadb.com/kb/en/mariadb-audit-plugin-log-format/

    logging.info('Sentry mariadb.audit ' + str(_file))

    #re_match1 = re.compile(r'Watchdog starting Resin',re.I)

    import csv

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split


    ##X = df.text
    ##y = df.label_num 0|1 #0=ham,1=spam
    #X = bline
    #y = 0
    #X = list(range(15))
    #y = [x * x for x in X]

    #X_train, X_test, y_train, y_test = train_test_split(X, y)
    #vectorizer = CountVectorizer()
    #counts = vectorizer.fit_transform(X_train.values)
    #classifier = MultinomialNB()
    #targets = y_train.values
    #calssifier.fit(counts, targets)

    X = []
    y = []

    kDict = {}
    #load kDict
    rows = store.selectAll('b2sum', db_store)
    for k,v in rows:
        #print(k,v)
        #kDict[k] = '' #empty val
        #kDict[k] = 1
        #kDict[k] = v
        kDict[k] = 1

        X.append(v)
        y.append(0)

    #print(X)
    #print(y)

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    #X_train, y_train = train_test_split(X, y)

    vectorizer = CountVectorizer()
    #counts = vectorizer.fit_transform(X_train.values)
    counts = vectorizer.fit_transform(X_train)
    classifier = MultinomialNB()
    #targets = y_train.values
    targets = y_train
    classifier.fit(counts, targets)


    #c=0

    for line in tail(_file):
        line = line.decode('utf-8').strip('\n')
        #line = line.decode('utf-8')
        #print(line)
        _csv = csv.reader(line.splitlines(), quotechar="'")
        #_csv = csv.reader(line)
        #print(list(_csv))
        _line = list(_csv)
        #print(_line)

        #_line = line.split(',')
        #_line = line.splitlines()

        #print(_line)
        #print(_line[0])
        #print(_line[1])
        jdata = {
        #"timestamp"    : _line[0][0],
        "serverhost"   : _line[0][1],
        "username"     : _line[0][2],
        "host"         : _line[0][3],
        #"connectionid" : _line[0][4],
        #"queryid"      : _line[0][5],
        "operation"    : _line[0][6],
        "database"     : _line[0][7],
        "object"       : _line[0][8],
        "retcode"      : _line[0][9] }

        #bline = _serverhost +' '+ _username +' '+ _host +' '+ _operation +' '+ _database +' '+ _object +' '+ _retcode
        #print(str(bline))

        bline = json.dumps(jdata)

        b = b2checksum(bline)
        #print('b2checksum ' + str(b))

        if b in kDict.keys():
            #print('exist ' + b)
            v = kDict[b]
            v += 1
            kDict[b] = v
        else:
            #print('new ' + b)
            kDict[b] = 1
            update_sql = store.replaceINTO2('b2sum', b, bline, db_store)

    ###############################

        #if b not in kDict.keys():
        #    #print('new ' + b)
        #    kDict[b] = 1
        #    update_sql = store.replaceINTO2('b2sum', b, bline, db_store)

        #for k,v in kDict.items():
        #    print(k,v)

        #print(kDict)

        #if re_match1.search(line):
        #    #print('Sentry Tail resin match ' + str(line))
        #    c+=1
        #    _key = 'sentry-resin-tail-match-' + str(c)
        #    prom = 'prog="resin",logfile="' + str(_file) + '",match="' + str(line) + '"'
        #    gDict[_key] = [ 'sentinel_watch_resin{' + prom + '} ' + str(c) ]

    ###############################
        
        #print(max(kDict, key=kDict.get))
        max_key = max(kDict, key=kDict.get)
        max_val = kDict[max_key]
        #print(max_key, max_val)
       
        min_key = min(kDict, key=kDict.get)
        min_val = kDict[min_key]
        #print(min_key, min_val)
        #print(len(kDict))
    ###############################

        #_key  = 'sentry-mariadb_watch-max_key-' + str(max_key)
        _key  = 'sentry-mariadb_watch-max_key'
        _prom = 'prog="mariadb_watch",logfile="' + str(_file) + '",blake2="' + str(max_key) + '"'
        gDict[_key] = [ 'sentinel_mariadb_watch_max_key{' + _prom + '} ' + str(max_val) ]

        #_key  = 'sentry-mariadb_watch-min_key-' + str(min_key)
        _key  = 'sentry-mariadb_watch-min_key'
        _prom = 'prog="mariadb_watch",logfile="' + str(_file) + '",blake2="' + str(min_key) + '"'
        gDict[_key] = [ 'sentinel_mariadb_watch_min_key{' + _prom + '} ' + str(min_val) ]

    ###############################

        ##X = df.text
        ##y = df.label_num 0|1 #0=ham,1=spam
        #X = bline
        #y = 0
        #X_train, X_test, y_train, y_test = train_test_split(X, y)
        #vectorizer = CountVectorizer()
        #counts = vectorizer.fit_transform(X_train.values)
        #classifier = MultinomialNB()
        #targets = y_train.values
        #calssifier.fit(counts, targets)

        sample = [ bline ] 
        sample_count = vectorizer.transform(sample)
        prediction = classifier.predict(sample_count)
        #print(prediction)

        p=0
        if prediction == 0:
            #print('Zero: ' + str(prediction))
            p+=1
        else:
            print('One: ' + str(prediction))
            _key  = 'sentry-mariadb_watch-naive-bayes'
            _prom = 'prog="mariadb_watch_naive-bayes",logfile="' + str(_file) + '",blake2="' + str(b) + '"'
            gDict[_key] = [ 'sentinel_mariadb_watch_naive_bayes{' + _prom + '} ' + str('1') ]


    ###############################
    ###############################

    return True

#sentryIPSLinuxSSH
##############################################################################################3
##############################################################################################3

thresh = 60
attempts = 3
clear = 600
ssh_port = 22

iplist = [0]*attempts
tmlist = [0]*attempts
blocklist = []
blocktime = []

def sentryIPSLinuxSSH(db_store, gDict, _file):
    logging.info('Sentry IPS ssh.watch ' + str(_file))

    ip = None

    re_sshd = re.compile(r'sshd')
    re_invalid_user = re.compile(r'Invalid user',re.I)
    re_failed_password = re.compile(r'Failed password',re.I)
    re_preauth = re.compile(r'preauth',re.I)

    for line in tail(_file):
        line = line.decode('utf-8').strip('\n')
        #print(line)

        if re_sshd.search(line) and re_failed_password.search(line) and re_invalid_user.search(line):
            ip = line.split()[12]
            logging.info("IPS ssh.watch match 12: %s", ip)
            tm = time.time()
            recordip(ip,tm)
        elif re_sshd.search(line) and re_failed_password.search(line) and not re_invalid_user.search(line):
            ip = line.split()[10]
            logging.info("IPS ssh.watch match 10: %s", ip)
            tm = time.time()
            recordip(ip,tm)
        #else:
        #    continue

        if re_sshd.search(line) and re_invalid_user.search(line) and not re_preauth.search(line):
            ip = line.split()[9]
            logging.info("IPS ssh.watch match 9: %s", ip)
            tm = time.time()
            recordip(ip,tm)

        if ip is None:
            continue

        if compare() >= len(iplist):
            elapsed = (tmlist[0] - tmlist[2])
            if thresh > elapsed:
                logging.info("IPS ssh.watch THRESH: %s %s", ip, elapsed)
                tm = time.time()
                ipblock(ip,tm, _file, gDict, db_store)
                logging.info("IPS ssh.watch ip: %s will clear in %s", ip, clear)

        #print('loop')

    return True

def recordip(ip,tm):
  logging.info("IPS ssh.watch listed: %s", ip)
  iplist.insert(0,ip)
  tmlist.insert(0,tm)
  iplist.pop()
  tmlist.pop()

def recordblock(ip,tm, _file, gDict, db_store):
  logging.info("IPS ssh.watch blocked ip: %s", ip)
  blocklist.insert(0,ip)
  blocktime.insert(0,tm)

  tmstr = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(tm))

  # get existing count,
  ipcount = store.getData('sshwatch', ip, db_store)
  if ipcount:
      _config = json.loads(ipcount[0])
      _c = _config['count']
      #print('existing _c ' + str(_c))
      _c += 1
  else:
      _c = 1

  #prom
  #_c=1
  _key  = 'sentry-sshwatch-' + str(ip)
  _prom = 'prog="sshwatch",logfile="' + str(_file) + '",block="' + str(ip) + '",time="' + str(tmstr) + '"'
  gDict[_key] = [ 'sentinel_ssh_watch{' + _prom + '} ' + str(_c) ]

  #sqlite
  jdata = { "logfile": str(_file), "time": str(tmstr), "count": _c }
  _json = json.dumps(jdata)
  replace_sql = store.replaceINTO2('sshwatch', ip, _json, db_store)

def compare():
  count = 0
  for index, item in enumerate(iplist):
    if item == iplist[0]:
      count += 1
  return count

def ipblock(ip,tm, _file, gDict, db_store):
  cmd = "iptables -I INPUT -s %s -p tcp --dport %s -j DROP" % (ip, ssh_port)
  os.system(cmd)
  logging.info("%s", cmd)
  recordblock(ip,tm, _file, gDict, db_store)

def ipremove(ip, gDict):
  cmd = "iptables -D INPUT -s %s -p tcp --dport %s -j DROP" % (ip, ssh_port)
  os.system(cmd)
  logging.info("%s", cmd)
  _key  = 'sentry-sshwatch-' + str(ip)
  gDict.pop(_key, None)

def checkblocklist():
  if len(blocklist) > 0:
    now = time.time()
    for index, item in enumerate(blocktime):
      diff = (now - item)
      logging.debug("diff: %s clear: %s", diff, clear)
      if diff > clear:
        ip = blocklist[index]
        ipremove(ip, gDict)
        del blocklist[index]
        del blocktime[index]

def cleanup():
  if len(blocklist) > 0:
    for ip in blocklist:
      ipremove(ip, gDict)


##############################################################################################3
##############################################################################################3

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
        line = line.decode('utf-8')
        print(line.strip('\n'))
        data += line

    report = processVulnData(data)
    if len(report) == 0:
        report = '-'
        val = -1
    else:
        val = len(report.split(','))

    insert = store.insertVulns(ip, report, data, db_store)
    return insert

def nmapVulnScanStoreDict(ip, db_store, gDict, name):
    data = ''
    scan = nmapVulnScan(ip)
    for line in scan:
        line = line.decode('utf-8')
        data += line

    report = processVulnData(data)
    if len(report) == 0:
        report = '-'
        val = -1
    else:
        val = len(report.split(','))

    insert = store.insertVulns(ip, report, data, db_store)

    #PROM INTEGRATION
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    _key = 'vuln-scan-' + str(ip)
    prom = 'name="' + str(name) + '",sentinel_job="vuln-scan",ip="' + str(ip) + '",done="' + str(now) + '",report="' + str(report) + '"'
    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

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
    #(192.168.0.156) 1 22/tcp,548/tcp
    replace = store.replaceNmaps(ip, data, db_store)
    return replace


def nmapScanStoreDict(ip, level, db_store, gDict, name):
    data = nmapScan(ip, level)
    print('(' + ip + ') ' + data)
    #(192.168.0.156) 1 22/tcp,548/tcp

    replace = store.replaceNmaps(ip, data, db_store)

    val_ = data.split(' ')[0]
    report_ = data.split(' ')[1]

    if val_ == 0:
        val = 0
        report = 'FAIL'
    else:
        rlen_ = len(report_.split(','))
        val = int(val_) + int(rlen_) - 1

    if len(report_) == 0:
        report = '-'
        val = -1
    else:
        report = report_

    #PROM INTEGRATION
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    _key = 'port-scan-' + str(ip)
    prom = 'name="' + str(name) + '",sentinel_job="port-scan",level="' + str(level) + '",ip="' + str(ip) + '",done="' + str(now) + '",report="' + str(report) + '"'
    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

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


def printEstablishedLsOf():

    Dct = getEstablishedDct()
    for k,v in Dct.items():
        #print(k, v)

        vL = v.split()

        #print(str(type(v)))
        #print(str(type(vL)))

        lport = vL[2]
        proto = vL[0]
        #print('lport: ' + str(lport), ' proto: ' + str(proto))

        #ppDict = getLsOfProtoPortDict(proto, lport)

        protoport = str(proto) + ':' + str(lport)
        ppDict = lsofProtoPort(protoport)
        L = []
        for _k,_v in ppDict.items():
            #print('ppDict ' + str(_k),_v)
            vLL = _v.split()
            prog = vLL[2]
            user = vLL[3]
            L.append(prog)
            L.append(user)
            #we'll use prod as over-write key

        print(v, L)

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


def getEstablishedRulesMatchDct(db_store):

    #rtnDct = {}
    allowDct = {}
    denyDct = {}

    estDct = getEstablishedDct()
    _estDct = {}
    e = 0
    r = 0
    for k,v in estDct.items():
        #print(v)
        proto_ = v.split(' ')[0]
        laddr_ = v.split(' ')[1]
        lport_ = v.split(' ')[2]
        faddr_ = v.split(' ')[3]
        fport_ = v.split(' ')[4]
        #print(proto, laddr, lport, faddr, fport)
        e += 1
        _estDct[e] = [ proto_, laddr_, lport_, faddr_, fport_ ]

    #print('split')

    rlsDct = store.getEstablishedRulesDct(db_store)
    _rlsDct = {}
    for k,v in rlsDct.items():
        #print(v)
        rule__  = v[0]
        proto__ = v[1]
        laddr__ = v[2]
        lport__ = v[3]
        faddr__ = v[4]
        fport__ = v[5]
        #print(proto, laddr, lport, faddr, fport)
        r += 1
        _rlsDct[r] = [ rule__, proto__, laddr__, lport__, faddr__, fport__ ]

    #print(_estDct)
    #print(_rlsDct)

    c = 0
    for k,v in _rlsDct.items():

        #print('rule  ' + str(v))
        rule_r  = str(v[0])
        proto_r = str(v[1])
        laddr_r = str(v[2])
        lport_r = str(v[3])
        faddr_r = str(v[4])
        fport_r = str(v[5])
        #print(proto)

        for _k,_v in _estDct.items():
            #print(v)
            _proto = str(_v[0])
            _laddr = str(_v[1])
            _lport = str(_v[2])
            _faddr = str(_v[3])
            _fport = str(_v[4])

            if (proto_r == _proto) or (proto_r == '*'):
                #print('match1 ' + str(_v))
                if (laddr_r == _laddr) or (laddr_r == '*'):
                    #print('match2 ' + str(_v))
                    if (lport_r == _lport) or (lport_r == '*'):
                        #print('match3 ' + str(_v))
                        if (faddr_r == _faddr) or (faddr_r == '*'):
                            #print('match4 ' + str(_v))
                            if (fport_r == _fport) or (fport_r == '*'):
                                #continue
                                #break
                                #print('match ' + str(_v))
                                c += 1
                                #rtnDct[c] = _v
                                if rule_r == 'ALLOW':
                                    allowDct[c] = _v

                                if rule_r == 'DENY':
                                    denyDct[c] = _v

    #print('done')
    #return rtnDct
    return allowDct, denyDct

def printEstablishedRules(db_file):
    #print('id  proto  laddr  lport  faddr  fport')
    Dct = store.getEstablishedRulesDct(db_file)
    for k,v in Dct.items():
        print(k,v)
    return True



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

def runDiscoverNetAll(ipnet, level, db_store, gDict):

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
            p2 = multiprocessing.Process(target=nmapVulnScanStoreDict, args=(ip, db_store, gDict))
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

def runNmapScanMultiProcessDict(hostLst, level, db_store, gDict, name):
    nmapDct = {}
    for ip in hostLst:
        p = multiprocessing.Process(target=nmapScanStoreDict, args=(ip, level, db_store, gDict, name))
        p.start()
        nmapDct[ip] = p
    for k,p in nmapDct.items():
        out = p.join()
    return True

def runNmapVulnMultiProcess(hostLst, db_store):
    print('hostLst: ' + str(hostLst))
    vulnDct = {}
    for ip in hostLst:
        p2 = multiprocessing.Process(target=nmapVulnScanStore, args=(ip, db_store))
        p2.start()
        vulnDct[ip] = p2

    for k,p in vulnDct.items():
        out = p.join()

    return True

def runNmapVulnMultiProcessDict(hostLst, db_store, gDict, name):
    print('hostLst: ' + str(hostLst))
    vulnDct = {}
    for ip in hostLst:
        p2 = multiprocessing.Process(target=nmapVulnScanStoreDict, args=(ip, db_store, gDict, name))
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


def vulnScan(ips, db_store, gDict, name):
    hostLst = discoverHostLst(ips)
    scan = runNmapVulnMultiProcessDict(hostLst, db_store, gDict, name)
    return scan

def portScan1(ips, db_store, gDict, name):
    level = 1
    return portScan(ips, level, db_store, gDict, name)

def portScan2(ips, db_store, gDict, name):
    level = 2
    return portScan(ips, level, db_store, gDict, name)

def portScan(ips, level, db_store, gDict, name):
    hostLst = discoverHostLst(ips)
    if level is None:
        level = 1
    scan = runNmapScanMultiProcessDict(hostLst, level, db_store, gDict, name)
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

def fimCheck(name, db_store, gDict, _name):

    Dct = {}
    fimDct = getFimDct(name, db_store)
  
    a = 0
    c = 0
    for k,v in fimDct.items():
        #print(k,v)
        #print(k, ' CHANGED')
        if len(v) == 0:
            a += 1
            #print(k, 'ADDED')
            Dct[k] = 'ADDED' + str(a)
        else:
            c += 1
            #print(k, 'CHANGED')
            Dct[k] = 'CHANGED' + str(c)

    _key = 'fimcheck-' + str(name)

    if bool(Dct):
        #val = 1
        val = len(Dct)
    else:
        val = 0

    #Note... this is all backwards 
    #Dct['config'] = name
    Dct[name] = 'config'
    Dct[_name] = 'job'

    #promHELP = '# HELP sentinel_job_output The output of the sentinel job.'
    #promTYPE = '# TYPE sentinel_job_output gauge'
    #gDict[_key] = [ promHELP, promTYPE, 'sentinel_job_output' + json.dumps(Dct) + ' ' + str(val) ]
    #gDict[_key] = [ 'sentinel_job_output' + json.dumps(Dct) + ' ' + str(val) ]

    #prom = ''
    #c = len(Dct)
    #for k,v in Dct.items():
    #    c -= 1
    #    if c == 0:
    #        prom += str(k) + '="' + str(v) + '"'
    #    else:
    #        prom += str(k) + '="' + str(v) + '",'
    #gDict[name] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    prom = ''
    c = len(Dct)
    for k,v in Dct.items():
        c -= 1
        if c == 0:
            prom += str(v).lower() + '="' + str(k) + '"'
        else:
            prom += str(v).lower() + '="' + str(k) + '",'

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    prom += ',done="' + str(now) + '"'

    #if val != 0:
    #    val = len(Dct)

    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
    #gDict[name] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
    #print('Sentry fim-check ' + str(name))

    return True


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

    #jdata[_file] = ""

    bsum = b2sum(_file)

    jdata[_file] = bsum

    update = store.updateData('fims', name, json.dumps(jdata), db_store)
    store_file = store.storeFile(_file, db_store)

    if update == True and store_file == True:
        return True
    else:
        return False

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
    unstore_file = store.unstoreFile(_file, db_store)

    if update == True and unstore_file == True:
        return True
    else:
        return False



def psCheck(name, db_store, gDict, _name):
    #print(str(_data)) #None
    import modules.ps.ps
    psDct = modules.ps.ps.get_ps()
    #for k,v in psDct.items():
    #    print(k,v)
    #dump into reports...
    #check = checkPsAndReport(name, psDct, db_store)
    #return check

    _key = 'pscheck-' + str(name)

    #psDct['name'] = name
    psDct['sentinel_job'] = name
    val = 1

    #promHELP = '# HELP sentinel_job_output The output of the sentinel job.'
    #promTYPE = '# TYPE sentinel_job_output gauge'
    #gDict[_key] = [ promHELP, promTYPE, 'sentinel_job_output' + json.dumps(psDct) + ' ' + str(val) ]
    #gDict[_key] = [ 'sentinel_job_output' + json.dumps(psDct) + ' ' + str(val) ]

    #prom = 'job="' + str(_name) + '",'
    prom = ''
    c = len(psDct)
    for k,v in psDct.items():
        c -= 1
        if c == 0:
            prom += str(k) + '="' + str(v) + '"'
        else:
            prom += str(k) + '="' + str(v) + '",'

    #gDict[name] = [ 'sentinel_job_pscheck_output{' + prom + '} ' + str(val) ]
    #gDict[_key] = [ 'sentinel_job_pscheck_output{' + prom + '} ' + str(val) ]
    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
    #print('Sentry ps-check ' + str(name) + ' prom ' + str(prom))

    return True

def establishedCheck(name, db_store, gDict, _name):
    eaDct = getEstablishedAlertsDct(db_store)

    for key in gDict.keys():
        if key.startswith('est-established-check-'):
            del gDict[key]

    c = 0
    for k,v in eaDct.items():
        #print(k,v)
        val = 1
        c += 1
        proto = v[0]
        laddr = v[1]
        lport = v[2]
        faddr = v[3]
        fport = v[4]

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        _key = 'est-established-check-' + str(_name) + '-' + str(c)


        protoport = str(proto) + ':' + str(lport)
        ppDict = lsofProtoPort(protoport)

        pdata = ''
        #_c = len(ppDict.keys()) 
        _c = 0
        for _k,_v in ppDict.items():
            #_c -= 1
            _c += 1
            vLL = _v.split()
            prog = vLL[2]
            user = vLL[3]

            #pdata += ',prog'+str(_c)+'="'+str(prog)+'",user'+str(_c)+'="'+str(user)+'"'

            if _c > 1:
                pdata += ',prog'+str(_c)+'="'+str(prog)+'",user'+str(_c)+'="'+str(user)+'"'
            else:
                pdata += ',prog="'+str(prog)+'",user="'+str(user)+'"'


        data = 'proto="'+str(proto)+'",laddr="'+str(laddr)+'",lport="'+str(lport)+'",faddr="'+str(faddr)+'",fport="'+str(fport)+'"' + pdata
        prom = 'name="' + str(_name) + '",sentinel_job="established-check",' + data + ',done="' + str(now) + '"'

        #Dict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
        gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    return True


def establishedCheck__1__(name, db_store, gDict, _name):
    #print('establishedCheck')
    #getEstablishedAlertsDct should really get moved to tools
    eaDct = getEstablishedAlertsDct(db_store)

    for key in gDict.keys():
        if key.startswith('est-established-check-'):
            del gDict[key]

    #Dict = {}
    c = 0
    for k,v in eaDct.items():
        #print(k,v)
        val = 1
        c += 1
        proto = v[0]
        laddr = v[1]
        lport = v[2]
        faddr = v[3]
        fport = v[4]

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        _key = 'est-established-check-' + str(_name) + '-' + str(c)

        data = 'proto="'+str(proto)+'",laddr="'+str(laddr)+'",lport="'+str(lport)+'",faddr="'+str(faddr)+'",fport="'+str(fport)+'"'
        prom = 'name="' + str(_name) + '",sentinel_job="established-check",' + data + ',done="' + str(now) + '"'
        #Dict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
        gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    #compare local Dict w/ gDict, but gDict has more keys...
    #first_dict  = gDict
    #second_dict = Dict

    return True


def printEstablishedAlerts(db_store):
    eaDct = getEstablishedAlertsDct(db_store)
    for k,v in eaDct.items():
        print(v)
    return True


def getEstablishedAlertsDct(db_store):

    estDct = getEstablishedDct()
    allowDct, denyDct = getEstablishedRulesMatchDct(db_store)

    estDct_ = {}
    for ek,ev in estDct.items():
        line = ev.split(' ')
        estDct_[ek] = line

    returnADct = {}
    for key,value in estDct_.items():
        if value not in allowDct.values():
            returnADct[key] = value

    returnDct = {}
    c = 0

    for k,v in returnADct.items():
        c += 1
        returnDct[c] = v

    for k,v in denyDct.items():
        c += 1
        returnDct[c] = v

    return returnDct

def printEstablishedRulesMatch(db_store):
    estDct = getEstablishedDct()
    _estDct = {}
    e = 0
    r = 0
    for k,v in estDct.items():
        #print(v)
        proto_ = v.split(' ')[0]
        laddr_ = v.split(' ')[1]
        lport_ = v.split(' ')[2]
        faddr_ = v.split(' ')[3]
        fport_ = v.split(' ')[4]
        #print(proto, laddr, lport, faddr, fport)
        e += 1
        _estDct[e] = [ proto_, laddr_, lport_, faddr_, fport_ ]

    #print('split')

    rlsDct = store.getEstablishedRulesDct(db_store)
    _rlsDct = {}
    for k,v in rlsDct.items():
        #print(v)
        rule__  = v[0]
        proto__ = v[1]
        laddr__ = v[2]
        lport__ = v[3]
        faddr__ = v[4]
        fport__ = v[5]
        #print(proto, laddr, lport, faddr, fport)
        r += 1
        _rlsDct[r] = [ rule__, proto__, laddr__, lport__, faddr__, fport__ ]

    #print(_estDct)
    #print(_rlsDct)

    for k,v in _rlsDct.items():
        #print('rule  ' + str(v))
        rule_r  = str(v[0])
        proto_r = str(v[1])
        laddr_r = str(v[2])
        lport_r = str(v[3])
        faddr_r = str(v[4])
        fport_r = str(v[5])
        #print(proto)
        _l = [ proto_r, laddr_r, lport_r, faddr_r, fport_r ]
        print(str(rule_r).lower() + ' ' + str(_l))

        for _k,_v in _estDct.items():
            #print(v)
            _proto = str(_v[0])
            _laddr = str(_v[1])
            _lport = str(_v[2])
            _faddr = str(_v[3])
            _fport = str(_v[4])

            if (proto_r == _proto) or (proto_r == '*'):
                #print('match1 ' + str(_v))
                if (laddr_r == _laddr) or (laddr_r == '*'):
                    #print('match2 ' + str(_v))
                    if (lport_r == _lport) or (lport_r == '*'):
                        #print('match3 ' + str(_v))
                        if (faddr_r == _faddr) or (faddr_r == '*'):
                            #print('match4 ' + str(_v))
                            if (fport_r == _fport) or (fport_r == '*'):
                                #print('match5 ' + str(_v))
                                #continue
                                #break
                                print('match ' + str(_v))
    #print('done')
    return True

#--------

def fileType(_file):
    try:
        with open(_file, 'r', encoding='utf-8') as f:
            f.read(4)
            return 'text'
    except UnicodeDecodeError:
        return 'binary'


def fimDiff(_file, db_store):

    store_file_ = store.getData('files', _file, db_store)
    store_file_blob = store_file_[0]
   
    with open(_file, 'rb') as binary_file:
        disk_file_blob = binary_file.read()

    #print(disk_file_blob)
    #print(store_file_blob)

    disk_file_type = store_file_type = None

    try:
        disk_file = disk_file_blob.decode('utf-8')
    except UnicodeDecodeError as e:
        disk_file_type = 'binary'

    try:
        store_file = store_file_blob.decode('utf-8')
    except UnicodeDecodeError as e:
        store_file_type = 'binary'

    #print(disk_file)
    #print(store_file)


    if disk_file_blob != store_file_blob:
        #print('diff')
        #file_type = fileType(disk_file)

        #if file_type == 'text':
        #    import difflib
        #    diff = difflib.ndiff(disk_file, store_file)
        #    delta = ''.join(x[2:] for x in diff if x.startswith('- '))
        #    print(delta)
        #else:
        #    print('diff ' + str(file_type))
        #output_list = [li for li in difflib.ndiff(disk_file, store_file) if li[0] != ' ']
        #print(output_list)

        if disk_file_type == 'binary':
            print('diff binary')
        else:
            import difflib
            diff = difflib.ndiff(disk_file, store_file)
            delta = ''.join(x[2:] for x in diff if x.startswith('- '))
            print(delta)
        return True
    return False


#--------

def avScan(filedir, db_store):

    cmd = 'clamscan -r -i ' + str(filedir)

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    exit_code = proc.wait()

    #print(stdout,stderr,exit_code)

    print(stdout.decode('utf-8'))


    #save av-scan



    return True
    

#--------

options = {
 'vuln-scan' : vulnScan,
 'port-scan' : portScan1,
 'port-scan2' : portScan2,
 'detect-scan' : detectScan,
 'fim-check' : fimCheck,
 'ps-check' : psCheck,
 'established-check' : establishedCheck,
}
#options[sys.argv[2]](sys.argv[3:])

def runJob(name, db_store, gDict):

    #print('runJob')
    #-start
    val = 0
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

    #promHELP = '# HELP sentinel_job The sentinel job service.'
    #promTYPE = '# TYPE sentinel_job gauge'
    #gDict[name] = [ promHELP, promTYPE, str('sentinel_job') + json.dumps(jdata) + ' ' + str(val) ]

    #print(jdata)
    prom = ''
    #print(len(jdata))
    c = len(jdata)
    for k,v in jdata.items():
        c -= 1
        if c == 0:
            prom += str(k) + '="' + str(v) + '"'
        else:
            prom += str(k) + '="' + str(v) + '",'

    #print(prom)
        
    #gDict[name] = [ str('sentinel_job') + json.dumps(jdata) + ' ' + str(val) ]
    gDict[name] = [ 'sentinel_job{' + prom + '} ' + str(val) ]
    replace = store.replaceINTO('jobs', name, json.dumps(jdata), db_store)
    #print('PERF replaceINTO occured on jobs')

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
        run = options[_job](_data, db_store, gDict, name)
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

    #promHELP = '# HELP sentinel_job The sentinel job service.'
    #promTYPE = '# TYPE sentinel_job gauge'
    #gDict[name] = [ promHELP, promTYPE, str('sentinel_job') + json.dumps(jdata) + ' ' + str(val) ]
    #gDict[name] = [ str('sentinel_job') + json.dumps(jdata) + ' ' + str(val) ]

    prom = ''
    c = len(jdata)
    for k,v in jdata.items():
        c -= 1
        if c == 0:
            prom += str(k) + '="' + str(v) + '"'
        else:
            prom += str(k) + '="' + str(v) + '",'

    gDict[name] = [ 'sentinel_job{' + prom + '} ' + str(val) ]
    update = store.updateData('jobs', name, json.dumps(jdata), db_store)
    #print('PERF updateData occured on jobs')

    logging.info('Sentry Job run ' + str(name))

    return run

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

def sentryProcessor(db_store, gDict):

    while (sigterm == False):
    #while True:
        #print('process Reports')

        _prom = str(db_store) + '.prom'
        #try:
        #    with open(_prom, 'w+') as _file:
        #        for k,v in gDict.items():
        #            for item in v:
        #                #print(k, v)
        #                _file.write(item + '\n')
        #except EOFError as e:
        #    print('EOFError ' + str(e))

        with open(_prom, 'w+') as _file:
            for k,v in gDict.items():
                for item in v:
                    _file.write(item + '\n')

        #print('sentryProcessor')
        time.sleep(10)

    return True


def sentryProcessJobs(db_store, gDict):
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
                run = runJob(name, db_store, gDict)
                #print(run)

        if _repeat:
            scale, amt = getDuration(_repeat)
            #print(scale + ' amt ' + str(amt))

            if _start is None:
                run = runJob(name, db_store, gDict)

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
                        run = runJob(name, db_store, gDict)
                        #print(run)
    
    #return True
    return run

def processD(List):

    #try:
    sentinel_up = 1
    #start = time.time()

    #promHELP = '# HELP sentinel_up Whether the sentinel service is up.'
    #promTYPE = '# TYPE sentinel_up gauge'
    promDATA = 'sentinel_up ' + str(sentinel_up)
    #gDict['sentinel_up'] = [promHELP, promTYPE, promDATA]
    gDict['sentinel_up'] = [ promDATA ]

    c = 0
    for item in List:
        #print(item)
        c += 1
        k = 'sentinel_up_' + str(c)
        gDict[k] = [ item ]

    promDATA = 'sentinel_app_info{version="' + __version__ + '"} 1.0'
    gDict['sentinel_app_info'] = [ promDATA ]

    #print(sys.version)
    #print(sys.version_info)
    #print(sys.implementation)a

    #print(sys.implementation)
    #namespace(_multiarch='darwin', cache_tag='cpython-38', hexversion=50857712, name='cpython', version=sys.version_info(major=3, minor=8, micro=6, releaselevel='final', serial=0))

    _arch = sys.implementation._multiarch
    _implementation = sys.implementation.name
    _major = str(sys.version_info.major)
    _minor = str(sys.version_info.minor)
    _micro = str(sys.version_info.micro)
    _releaselevel = sys.version_info.releaselevel
    _serial = sys.version_info.serial
    _version = _major + '.' + _minor + '.' + _micro

    #python_info{implementation="CPython",major="3",minor="8",patchlevel="1",version="3.8.1"} 1.0

    promDATA = 'sentinel_python_info{arch="' + _arch + '",implementation="' + _implementation + '",major="' + _major + '",minor="' + _minor
    promDATA += '",micro="' + _micro + '",version="' + _version + '"} 1.0'
    gDict['sentinel_python_info'] = [ promDATA ]

    sqlite3_version = str(sqlite3.version)
    sqlite3_sqlite_version = str(sqlite3.sqlite_version)

    promDATA = 'sentinel_python_sqlite_info{sqlite3="' + sqlite3_version + '",library="' + sqlite3_sqlite_version + '"} 1.0'
    gDict['sentinel_python_sqlite_info'] = [ promDATA ]

    #except BrokenPipeError:
    #    sigterm = True
    #    sys.exit(1)

    return True


def sentryScheduler(db_store, gDict):
    while (sigterm == False):
    #while True:

        List = []
        job = threading.Thread(target=sentryProcessJobs, args=(db_store, gDict), name="SentryJobRunner")
        #job.setDaemon(True)
        job.start()

        ##run = sentryProcessAlerts(db_store)
        #alert = threading.Thread(target=sentryProcessAlerts, args=(db_store,), name="SentryAlertRunner")
        #alert.setDaemon(True)
        #alert.start()


        tcount = 0
        #threads = []
        for thread in threading.enumerate():
            #print(str(thread.name))
            #if thread.name == 'MainThread':
            #    continue
            #if thread.name == 'Scheduler':
            #    continue
            #print(str(thread.name))
            tcount += 1
            #threads.append(thread)

        pcount = 0
        #process = []
        for proc in multiprocessing.active_children():
            #print(str(proc.name))
            pcount += 1
            #process.append(proc)


        #promHELP = '# HELP sentinel_threads Number of sentinel threads.'
        #List.append(promHELP)
        #promTYPE = '# TYPE sentinel_threads gauge'
        #List.append(promTYPE)
        List.append('sentinel_threads ' + str(tcount))

        #promHELP = '# HELP sentinel_process Number of sentinel process.'
        #List.append(promHELP)
        #promTYPE = '# TYPE sentinel_process gauge'
        #List.append(promTYPE)
        List.append('sentinel_process ' + str(pcount))

        #for t in threads:
        #    t.join()

        #for p in process:
        #    p.join()

        #try:
        #    processD(List)
        #except Exception as e:
        #    print(str(e))

        processD(List)

        time.sleep(3)

    return True
    #return run


def sentryCleanup(db_store):
    _prom = str(db_store) + '.prom'
    with open(_prom, "w") as _file:
        _file.write('')
    logging.info("Sentry Cleanup: True")
    return True


#def procHTTPServer(port, metric_path, db_file, Dict):
def procHTTPServer(port, metric_path, db_file):
    global _metric_path
    _metric_path = metric_path

    global db_store
    db_store = db_file

    #global gDict
    #gDict = Dict

    #print(os.getuid())
    if os.getuid() == 0:
        run_as_user = "nobody"
        uid = pwd.getpwnam(run_as_user)[2]
        #print('user.nobody ' + str(uid))
        logging.info('Sentry HTTPServer Drop Privileges to uid ' + str(uid))
        os.setuid(uid)

    #run_as_group = "nobody"
    #gid = grp.getgrnam(run_as_group)[2]
    #print('group.nobody ' + str(gid))
    #os.setgid(gid)

    httpd = HTTPServer(('', port), Handler)
    httpd.serve_forever()



def sentryMode(db_file, verbose=False):

    global db_store
    db_store = db_file

    manager = multiprocessing.Manager()
    global gDict
    gDict = manager.dict()

    #import atexit
    #import signal

    atexit.register(sentryCleanup, db_store)
    signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    logging.info("Sentry Startup")

    #runlist=[]

    scheduler = threading.Thread(target=sentryScheduler, args=(db_store, gDict), name="Scheduler")
    #scheduler.setDaemon(True)
    scheduler.start()
    #runlist.append(scheduler)

    processor = threading.Thread(target=sentryProcessor, args=(db_store, gDict), name="Processor")
    #processor.setDaemon(True)
    processor.start()
    #runlist.append(processor)

    #if not conf:
    #    update = store.replaceINTO('configs', 'prometheus', json.dumps({'port': 9111, 'path': '/metrics'}), db_store)
    #    conf = store.getData('configs', 'prometheus', db_store)
    #conf = json.loads(conf[0])

    #tailer = threading.Thread(target=sentryTailFile, args=(db_store, gDict, '/tmp/log.txt'), name="TailFile")
    #tailer.setDaemon(True)
    #tailer.start()

    #confs = store.selectAll('configs', db_store)
    #for conf in confs:
    #    print(conf[0], conf[1], conf[2])
    #    resin_watch = store.getData('configs', 'watch-resin-log', db_store)
    #    watch = store.getData('configs', conf[0], db_store)
    #    jconf = json.loads(conf[0])


    resin_watch = store.getData('configs', 'watch-resin-log', db_store)
    if resin_watch:
        resin_watch_config = json.loads(resin_watch[0])
        _logfile = resin_watch_config['logfile']
        _match   = resin_watch_config['match']
        #resin_tailer = threading.Thread(target=sentryTailResinLog, args=(db_store, gDict, _logfile), name="ResinLogWatch")
        #resin_tailer.setDaemon(True)
        #resin_tailer.start()
        resin_tailer = multiprocessing.Process(target=sentryTailResinLog, args=(db_store, gDict, _logfile))
        resin_tailer.start()
        #resin_tailer.join()
        #runlist.append(resin_tailer)

    mariadb_watch = store.getData('configs', 'watch-mariadb-audit-log', db_store)
    if mariadb_watch:
        mariadb_watch_config = json.loads(mariadb_watch[0])
        _logfile = mariadb_watch_config['logfile']
        mariadb_tailer = multiprocessing.Process(target=sentryTailMariaDBAuditLog, args=(db_store, gDict, _logfile))
        mariadb_tailer.start()
        #mariadb_tailer.join()
        #runlist.append(mariadb_tailer)

    ssh_watch = store.getData('configs', 'watch-ssh-linux-log', db_store)
    if ssh_watch:
        ssh_watch_config = json.loads(ssh_watch[0])
        _logfile  = ssh_watch_config['logfile']
        _thresh   = ssh_watch_config['thresh']
        _attempts = ssh_watch_config['attempts']
        _clear    = ssh_watch_config['clear']
        ssh_tailer = multiprocessing.Process(target=sentryIPSLinuxSSH, args=(db_store, gDict, _logfile))
        ssh_tailer.start()
        #ssh_tailer.join()
        #runlist.append(ssh_tailer)

    syslog_watch = store.getData('configs', 'watch-syslog', db_store)
    if syslog_watch:
        #syslog_watch_config = json.loads(syslog_watch[0])
        #_search   = syslog_watch_config['search'] #KeyError:
        #_search   = syslog_watch_config.get('search', None)

        syslog_tailer = multiprocessing.Process(target=sentryLogStream, args=(db_store, gDict, verbose))
        syslog_tailer.start()
        #syslog_tailer.join()
        #runlist.append(syslog_tailer)

    prometheus_config = store.getData('configs', 'prometheus', db_store)
    #print(str(type(prometheus_config)) + ' prometheus_config ' + str(prometheus_config))
    if prometheus_config:
        prometheus_config = json.loads(prometheus_config[0])
        _port = prometheus_config['port']
        global _metric_path
        _metric_path = prometheus_config['path']

    try:
        if prometheus_config:
            p = multiprocessing.Process(target=procHTTPServer, args=(_port, _metric_path, db_store))
            p.start()
            p.join()
        else:
            #time.sleep(60)
            #time.sleep(-1)
            #ValueError: sleep length must be non-negative
            signal.pause()

            #import asyncio
            #loop = asyncio.get_event_loop()
            #try:
            #    loop.run_forever()
            #finally:
            #    loop.close()

        print('pid ' + str(os.getpid()))

    except (KeyboardInterrupt, SystemExit, Exception):
        sigterm = True
        sentryCleanup(db_store)
        #for run in runlist: run.join()

        #scheduler.join()
        #processor.join()
        #if resin_watch: resin_tailer.join()
        #if mariadb_watch: mariadb_tailer.join()
        #if ssh_watch: ssh_tailer.join()
        #httpd.server_close()
        #clear_iptables = cleanup()

        #for proc in multiprocessing.active_children():
        #    print('proc name ', proc)

        #for thread in threading.enumerate():

        #for run in runlist: run.join()

        for proc in multiprocessing.active_children():
            print('proc name ', proc, ' ', proc.pid)
            #print('proc pid ', proc.pid)
            os.kill(proc.pid, 9)

        #for run in runlist: run.join()

        for thread in threading.enumerate():
            #print('thread name', thread, ' ', thread.name)
            #print('thread name.Name', thread.name)
            #thread.join()
            if thread.name == 'MainThread':
                continue
            else:
                print('thread name', thread, ' ', thread.name)
                thread.join()

        logging.info("Sentry Shutdown: " + str(sigterm))
        sys.exit(1)

    return True


if __name__ == '__main__':
# requires cli tools: arp, ping, lsof, nslookup, nmap, tail
    pass

