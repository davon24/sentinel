#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sentinel import __version__

import sqlite3

import sys
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
import threading
import multiprocessing
from multiprocessing import shared_memory

import time
import datetime
import collections
import socket
import json
import base64

from hashlib import blake2b, blake2s

from http.server import HTTPServer, BaseHTTPRequestHandler

import os, pwd, grp
import select
import re
import signal

import asyncio

import resource

import logging
#logger = logging.getLogger(__name__)
#logger = logging.getLogger()

#loglevel = logging.INFO
#loglevel = logging.ERROR
#logformat = 'sentinel %(asctime)s %(filename)s %(levelname)s: %(message)s'
#datefmt = "%b %d %H:%M:%S"
#logging.basicConfig(level=loglevel, format=logformat, datefmt=datefmt)

import requests

sys.path.insert(0, os.path.dirname(__file__))
import store

import ssl
if sys.platform == 'darwin':
    #ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1108)
    #print('MACOSX...')

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.check_hostname = True
    ssl_context.load_default_certs()

    import certifi
    #print(certifi.where())
    #import os

    openssl_dir, openssl_cafile = os.path.split(
            ssl.get_default_verify_paths().openssl_cafile)

    ssl_context.load_verify_locations(
            cafile=os.path.relpath(certifi.where()),
            capath=None,
            cadata=None)
else:
    ssl._create_default_https_context = ssl._create_unverified_context
    #ssl_context = ssl.create_default_context()
    #ssl_context.check_hostname = False
    #ssl_context.verify_mode = ssl.CERT_NONE

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#import smtplib
#import ssl
#import certifi

#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.naive_bayes import MultinomialNB
#from sklearn.neural_network import MLPClassifier

class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == _metric_path: #/metrics
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()

            _prom = str(db_store) + '.prom'
            try:
                with open(_prom, 'r') as _file:
                    lines = _file.readlines()
                    for line in lines:
                        self.wfile.write(bytes(str(line), 'utf-8'))
            except Exception as e:
                logging.info('Sentry Exception ' + str(e))
            
        else:
            self.send_error(404) #404 Not Found
        return

    def do_POST(self):
        self.send_error(405) #405 Method Not Allowed
        return

    def do_HEAD(self):
        self.send_error(501) #501 Not Implemented
        return

class APIHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == _api_path: #/api
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()

            #line = '{"status":"ok", "method":"get"}'
            #self.wfile.write(line.encode('utf-8'))
            #self.wfile.write(bytes(str(line), 'utf-8'))
            line = {'status':'ok', 'method':'get'}
            self.wfile.write(json.dumps(line).encode('utf-8'))

        else:
            self.send_error(404) #404 Not Found
        return

    def do_HEAD(self):
        self.send_error(501) #501 Not Implemented
        return

    #self.send_error(405) #405 Method Not Allowed


    def do_POST(self):

        # make sure data is json
        self.content_type = self.headers['Content-Type']
        #print(self.content_type)
        if self.content_type != 'application/json':
            self.send_response(415)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            line = {'status':'Unsupported Media Type', 'status_code': 415, 'method':'post'}
            self.wfile.write(json.dumps(line).encode('utf-8'))
            #self.wfile.write(line.encode('utf-8'))
            #self.wfile.write(bytes(str(line), 'utf-8'))
            return

        # make sure has auth
        self.auth_string = self.headers['Authorization']
        #print(self.auth_string)
        if self.auth_string is None:
            self.send_response(401)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            line = {'status':'Unauthorized', 'status_code': 401, 'method':'post'}
            self.wfile.write(json.dumps(line).encode('utf-8'))
            #self.wfile.write(bytes(str(line), 'utf-8'))
            #self.wfile.write(line.encode('utf-8'))
            return

        bearer = self.auth_string.split(' ')[0]
        token = self.auth_string.split(' ')[1]
        
        if bearer != 'Bearer':
            self.send_response(401)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            line = {'status':'Unauthorized', 'status_code': 401, 'method':'post', 'bearer': 'none'}
            self.wfile.write(json.dumps(line).encode('utf-8'))
            #self.wfile.write(line.encode('utf-8'))
            return


        #---- register ----#
        if self.path == _api_path + '/register': # /api/register

            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            jdata = json.loads(json.loads(self.data_string))

            jdata_uuid = jdata.get('uuid', None)
            jdata_key  = jdata.get('key', None)

            # get key from config
            cDct={}
            configs = store.selectAll('configs', db_store)
            for config in configs:
                #print(config[0], config[1], config[2])
                config_ = json.loads(config[2])
                cDct[config[0]] = config_.get('config', None)
            for key,conf in cDct.items():
                if conf == 'api_server':
                    _config = json.loads(store.getData('configs', key, db_store)[0])
                    #_port = _config['port']
                    #_api_path = _config['path']
                    _key = _config['key']
            #print(_key)

            if jdata_key == _key:
                #print('insert bearer_token')
                #print(bearer_token[0])
                client_address = self.client_address[0]
                client_data = {'client_address': str(client_address)}
                register = store.replaceINTO('bearer', token, json.dumps(client_data), db_store)

            else:
                line = { 'status': 'Unauthorized',
                         'status_code': 401,
                         'method': 'post',
                         'uuid': str(jdata_uuid),
                         'key': 'invalid'
                       }
                self.send_response(401)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(line).encode('utf-8'))
                return

            line = { 'status': 'Ok',
                     'status_code': 200,
                     'method': 'post',
                     'uuid': str(jdata_uuid),
                     'registered': str(register)
                   }

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(line).encode('utf-8'))

            # client logging, then return

            client_address = self.client_address[0]

            _h = 'register-' + str(jdata_uuid) + '-' + str(client_address)
            server_Dict[_h] = server_Dict.get(_h, 0) + 1

            now = time.strftime("%Y-%m-%d %H:%M:%S")
            client_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")

            _k = 'sentinel_api_server_register_client_info-' + str(jdata_uuid)
            _prom = ''
            _prom += 'uuid="' + str(jdata_uuid) + '"'
            _prom += ',client_ip="' + str(client_address) + '"'
            _prom += ',time="' + str(client_time) + '"'

            api_Dict[_k] = [ 'sentinel_api_server_register_client_info{' + _prom + '} ' + str(server_Dict[_h]) ] # 🍺

            return
        #---- register ----#

        #---- post     ----#
        # get auth tokens from sqlite
        # bearer_token = store.get_bearer(token, db_bearer)
        # print(bearer_token)
        try:
            bearer_token = store.get_bearer(token, db_store)
        except sqlite3.OperationalError as err:
            self.send_response(500)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            #line = '{"status":"Internal Server Error", "status_code": 500, "method":"post", "sqlite3": "OperationalError",'
            #line += '"error": "' + str(err) + '"}'
            line = {'status':'Internal Server Error',
                    'status_code': 500,
                    'method':'post',
                    'sqlite3': 'OperationalError',
                    'error': str(err)
                   }
            self.wfile.write(json.dumps(line).encode('utf-8'))
            return


        #if token != bearer_token:
        if not bearer_token:
            self.send_response(401)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            line = {'status':'Unauthorized', 'status_code': 401, 'method':'post', 'authorization': 'bearer', 'token': 'invalid'}
            self.wfile.write(json.dumps(line).encode('utf-8'))
            return

        #print('accepted bearer_token')

        #print(bearer_token[0])
        #print(bearer_token[1])

        bearer_data = json.loads(bearer_token[1])
        #print(bearer_data) #{'command': 'ping google.com'}
        #encoded_bearer_data = base64.b64encode(str(bearer_data).encode('utf-8')).decode('utf-8')

        command = bearer_data.get('command', None)
        #print(command)

        if command:
            encoded_command = base64.b64encode(str(command).encode('utf-8')).decode('utf-8')
            #print(encoded_command)
            client_data = { 'command': encoded_command }
        else:
            client_data = {}


        # make sure has path
        if self.path == _api_path + '/post': # /api/post

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()

            self.data_string = self.rfile.read(int(self.headers['Content-Length']))

            # need try/catch here
            #data = self.data_string
            #print('------------------------')

            jdata = json.loads(json.loads(self.data_string))

            # safe get
            jdata_uuid = jdata.get('uuid', None)
            jdata_command = jdata.get('command', None)
            jdata_output = jdata.get('output', None)
            jdata_exitcode = jdata.get('exitcode', None)
            #print('this is the client command...' + str(jdata_command))

            line = { 'status': 'Ok',
                     'status_code': 200,
                     'method': 'post',
                     'uuid': str(jdata_uuid),
                   }

            line.update(client_data)

            if jdata_command:
                # wipe command from list-api-tokens
                #run = store.replaceINTO('bearer', bearer_token, json.loads('{}'), db_store)
                #this_data = json.loads('{}')
                #d_data = {'action':'done'}
                #no_data = {}
                #store.replaceINTO('bearer', str(bearer_token), this_data, db_store)
                #run = store.replaceINTO('bearer', 'token_1234', json.dumps('{}'), db_store)
                run = store.replaceINTO('bearer', bearer_token[0], json.dumps({}), db_store)
                #print(run)
                
                # put command in done w/ exitcode

                #token_bytes = base64.b64decode(command)
                #untoken = token_bytes.decode('utf-8')
                #print(untoken)

                command_token = base64.b64decode(jdata_command)
                command_untoken = command_token.decode('utf-8')

                output_token = base64.b64decode(jdata_output)
                output_untoken = output_token.decode('utf-8')


                client_command_data = { 'uuid': str(jdata_uuid),
                                        'command': str(command_untoken),
                                        'output': str(output_untoken),
                                        'exitcode': str(jdata_exitcode)
                                      }
                insert = store.insertINTOClientCommand(bearer_token[0], json.dumps(client_command_data), db_store)
                #print(insert)

                # update client knowledge
                line.update({'recieved': 'output'})
                #line.update({'recieved': str(jdata_output) })
                

            #jdata_hostname = jdata.get('hostname', None)
            #print('------------------------')

            #line = '{"status":"Ok", "status_code": 200, "method":"post", "bearer": true, "uuid": "' + str(jdata_uuid) + '",'
            #line += json.dumps(bearer_data)
            #line += '"hostname":"' + str(jdata_hostname) + '"}'


            #line.update(bearer_data)

            #print(str(type(line)))
            #print(str(type(bearer_data)))

            self.wfile.write(json.dumps(line).encode('utf-8'))

            client_address = self.client_address[0]
            #client_data = {'client_address': str(client_address)}

            _h = str(jdata_uuid) + '-' + str(client_address)
            server_Dict[_h] = server_Dict.get(_h, 0) + 1

            now = time.strftime("%Y-%m-%d %H:%M:%S")
            client_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")

            _k = 'sentinel_api_server_client_info-' + str(bearer_token[0])
            #_prom = 'this_loaded="'+str(len(rulesDct))+'",rules_b2sum="'+b2checksum(str(rulesDct))+'",load_time="'+str(time.strftime("%Y-%m-%d %H:%M:%S"))+'"'
            _prom = ''
            #_prom += 'bearer_token="' + str(bearer_token[0]) + '"'
            _prom += 'uuid="' + str(jdata_uuid) + '"'
            _prom += ',client_ip="' + str(client_address) + '"'
            _prom += ',time="' + str(client_time) + '"'
            #_prom += ',time_since="' + str(time_since) + '"'
            #print(_prom)

            #gDict[_k] = [ 'sentinel_api_server_engine_info{' + _prom + '} 1' ]
            #gd_Dict[_k] = [ 'sentinel_api_server_engine_info{' + _prom + '} 1' ]

            #api_Dict[_k] = [ 'sentinel_api_server_client_info{' + _prom + '} 1' ] #beer.here need to increment

            #api_Dict[_k] = [ 'sentinel_api_server_client_info{' + _prom + '} ' + str(server_Dict[jdata_uuid]) ] #beer.here need to increment
            api_Dict[_k] = [ 'sentinel_api_server_client_info{' + _prom + '} ' + str(server_Dict[_h]) ] # 🍺


            # PermissionError: [Errno 13] Permission denied


            return
        #---- post     ----#



        else:
            #self.send_error(404) #404 Not Found
            self.send_response(404)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            line = {'status':'Not Found', 'status_code': 404, 'method':'post'}
            self.wfile.write(json.dumps(line).encode('utf-8'))
            return

        return



class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

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


def register_client(job_name, server_key, db_store):

    #print(job_name)
    #print(server_key)

    jobs = store.selectAll('jobs', db_store)
    for job in jobs:
        #print(job[0]) # remote-client-2
        if job[0] == job_name:
            #print('get conf job ' + str(name) + ' now...')
            jconf = json.loads(job[2])
            _uuid = jconf.get('uuid', None)
            _url  = jconf.get('url', None)

    #print(_uuid)
    #print(_url)
    #print(_url.replace('post', 'register', 1))

    _reg_url = _url.replace('post', 'register', 1)

    d = { 'uuid': _uuid, 'key': server_key }

    try:
        post, code = http_post(_reg_url, d)
        data = post.json()
    except Exception as e:
        post = None
        data = { 'error': str(e) }
        code = 100

    print(data, code)

    #cDct={}
    #configs = store.selectAll('configs', db_store)
    #for config in configs:
    #    #print(config[0], config[1], config[2])
    #    config_ = json.loads(config[2])
    #    cDct[config[0]] = config_.get('config', None)
    #for key,conf in cDct.items():
    #    if conf == 'api_server':
    #        _config = json.loads(store.getData('configs', key, db_store)[0])
    #        _port = _config['port']
    #        _api_path = _config['path']
    #        _key = _config['key']
    #print(_key)


    return

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
        _format = 'ndjson'
        cmd = ['log', 'stream', '--style', _format] #macos
    elif sys.platform == 'linux' or sys.platform == 'linux2':
        cmd = ['journalctl', '-f', '-o', _format] #linux
    else:
        logging.critical('Fail: No log stream.  No such file or directory')
        return False

    f = Popen(cmd, shell=False, stdout=PIPE,stderr=PIPE)
    while not exit.is_set():
        line = f.stdout.readline()
        if not line:
            time.sleep(1) #break
        else:
            yield line
        sys.stdout.flush()

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

def expertLogStreamRulesEngineGeneralJson(jline, keys, rulesDict):

    h={}
    ######################################################################
    # process each rule one at a time
    for _r,v in rulesDict.items():

        jrules = json.loads(v)
        _data = jrules.get('data', None)

        if _data:
            data = concatJsnData(_data, json.dumps(jline))
        else:
            data = None

        if data:
            b = b2checksum(data)
        else:
            b = b2checksum(str(jline))

        _k = str(_r) +'-'+ str(b)

        _search = jrules.get('search', None)
        _match  = jrules.get('match', None)
        _not    = jrules.get('not', None)
        _pass   = jrules.get('pass', None)
        _ignorecase = jrules.get('ignorecase', None)


        if _match: 

            d1 = extractLstDct(_match)
            d2 = jline
            d3 = {}

            for key in d1:
                if key in d2:
                    if d1[key] == d2[key]:
                        d3[key] = d1[key]

            if d1 == d3: #print('match ', d3)
                h[_k] = [_r,b,jline]

        if _search and data:

            if _ignorecase == 'False':
                #ignorecase='0'
                ignorecase=None
                re_search = re.compile(_search)
            else:
                #print('ignorecase')
                ignorecase='re.IGNORECASE'
                re_search = re.compile(_search, re.IGNORECASE)

            #re.IGNORECASE
            #if re.search(_search, data, flags=ignorecase):
            if re_search.search(data):
                #h[_k] = [_r,b,seen,s[b],data]
                h[_k] = [_r,b,data]

                if _not:
                    for no in _not:
                        #if no in data:

                        if ignorecase:
                            if no.lower() in data.lower(): #ignorecase
                                h.pop(_k, None)
                                #if h.pop(_k, None):
                                #    print('   _not this one...', _k, ' ', data)
                        else:
                            if no in data:
                                h.pop(_k, None)
        #else:
        #    print('no.search.no.data ',_r, ' ', str(_search), ' ' , str(data))

        if _pass:
            for p in _pass:
                __k = str(_r) +'-'+ str(p)
                h.pop(__k, None)
                #if h.pop(__k, None):
                #    print('   _pass this one...', __k, ' ', data)

    #####################################################################
#    for k,v in h.items():
#        #print(k,v)
    return h

def expertLogStreamRulesEngineGeneralStr(line, _format, rulesDict):

    #print(str(_format))

    h={}
    ######################################################################
    # process each rule one at a time
    for _r,v in rulesDict.items():

        jrules = json.loads(v)

        #_data = jrules.get('data', None)
        #
        #if _data:
        #    data = concatJsnData(_data, json.dumps(jline))
        #else:
        #    data = None
        #
        #if data:
        #    b = b2checksum(data)
        #else:
        #    b = b2checksum(str(jline))

        #print('_rules ..... ' +str(_rules))
        #print('_format ..... ' +str(_format))

        if _format == 'verbose-access':

            #regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) - "(.*?)" "(.*?)"'
            #_tuple = re.match(regex, line).group()
            #_tuple = re.match(regex, line)
            #print(str(_tuple))

            _line = line.split('verbose-access:')
            try:
                line0 = _line[0]
                line1 = _line[1]
            except IndexError:
                logging.error('log format error')
                continue

            #print(line0)
            timestamp = line0.split(' ')[0]
            rhost     = line0.split(' ')[1]

            #print(line1)
            #regex = ' \[(.*?)\] \'(.*?)\' (.*?) (.*?) ([(\d\.)]+) "-" - - "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"'

            regex = ' \[(.*?)\] \'(.*?)\' (.*?) (.*?) ([(\d\.)]+) "-" - - "(.*?)" (\d+) (.*?) "(.*?)" "(.*?)" "(.*?)" "(.*?)" "(.*?)"'

            try:
                #_tuple_s = re.match(regex, line1).group()
                _tuple = re.match(regex, line1).groups()
            except AttributeError as e: #'NoneType' object has no attribute 'group'
                logging.error('log format AttributeError ' + str(e))
                continue

            #print(len(_tuple), '  ', str(type(_tuple)))
            (s1,s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13) = _tuple

            #print('s1 ', s1)   #date/time  #04/Mar/2021:03:59:58 -0800
            #print('s2 ', s2)   #id_num     #1426054
            #print('s3 ', s3)   #url_1      #www.Domain.com
            #print('s4 ', s4)   #url_2      #www.domain.com
            #print('s5 ', s5)   #ip_addr    #192.168.100.254
            #print('s6 ', s6)   #http_method+resource+version #GET /welcome.html?q=1 HTTP/1.1
            #print('s7 ', s7)   #http_code  #200|302|404
            #print('s8 ', s8)   #bytes_sent #138254
            #print('s9 ', s9)   #token_1    #aaabktlpO2QwnfCw1zWFx
            #print('s10 ', s10) #ref_url    #https://www.domain.org/Membersite/rcss/member.min.css
            #print('s11 ', s11) #dash_1     #-
            #print('s12 ', s12) #browser user agent #Mozilla/5.0 
            #print('s13 ', s13) #data_1     #-|adid=YRTO238500V20200527; JLUVr=e34c205e

            data = rhost +' '+ s3 +' '+ s4 +' '+ s6 +' '+ s7 +' '+ s10 +' '+ s12 +' '+ s13

            #print(data)

        else:
            data = line

        b = b2checksum(data)

        _k = str(_r) +'-'+ str(b)

        _search = jrules.get('search', None)
        #_match  = jrules.get('match', None)
        _not    = jrules.get('not', None)
        _pass   = jrules.get('pass', None)
        _ignorecase = jrules.get('ignorecase', None)
        _format = jrules.get('format', None)

        #if _match:

        #    d1 = extractLstDct(_match)
        #    d2 = jline
        #    d3 = {}

        #    for key in d1:
        #        if key in d2:
        #            if d1[key] == d2[key]:
        #                d3[key] = d1[key]

        #    if d1 == d3: #print('match ', d3)
        #        h[_k] = [_r,b,line]

        if _search and data:

            if _ignorecase == 'False':
                #ignorecase='0'
                ignorecase=None
                re_search = re.compile(_search)
            else:
                #print('ignorecase')
                ignorecase='re.IGNORECASE'
                re_search = re.compile(_search, re.IGNORECASE)

           #re.IGNORECASE
            #if re.search(_search, data, flags=ignorecase):
            if re_search.search(data):
                #h[_k] = [_r,b,seen,s[b],data]
                h[_k] = [_r,b,data]

                if _not:
                    for no in _not:
                        #if no in data:

                        if ignorecase:
                            if no.lower() in data.lower(): #ignorecase
                                h.pop(_k, None)
                                #if h.pop(_k, None):
                                #    print('   _not this one...', _k, ' ', data)
                        else:
                            if no in data:
                                h.pop(_k, None)
        #else:
        #    print('no.search.no.data ',_r, ' ', str(_search), ' ' , str(data))

        if _pass:
            for p in _pass:
                __k = str(_r) +'-'+ str(p)
                h.pop(__k, None)
                #if h.pop(__k, None):
                #    print('   _pass this one...', __k, ' ', data)

    #####################################################################
#    for k,v in h.items():
#        #print(k,v)
    return h



def getExpertRules(config, db_store):
    rulesDict = {}
    rules = store.selectAll('rules', db_store)
    for rule in rules:
        name = rule[0]
        jconf = rule[2]

        jdata = json.loads(jconf)
        jconfig = jdata.get('config', None)

        if config == jconfig:
            rulesDict[name] = jconf
    return rulesDict


def concatJsnData(scope, _jsn):
    jsn = json.loads(_jsn)
    dta=''

    if len(scope) == 1:
        item=scope[0]
        dta = str(jsn.get(item, None))
    else:
        for item in scope:
            dta += str(jsn.get(item, None)) + str(' ')
    return dta


def sklearnVectorizerClassifier(scope, db_store):

    #get CountVectorizer, HashingVectorizer, TfidfVectorizer

    #get naive_bayes.MultinomialNB, naive_bayes.BernoulliNB, 

    logging.info('Sentry watch-syslog naive_bayes.MultinomialNB')

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split

    #from sklearn.neural_network import MLPClassifier

    X=[]
    y=[]

    #open/load training data
    #rows = store.getAll('training', db_store)
    rows = store.getAll('model', db_store)
    if len(rows) == 0:
        #print('Zero training data')
        logging.error('Zero training data. Can not perform naive_bayes.MultinomialNB')
        return (False, False)
    b2 = b2checksum(str(rows))
    c=0
    t=0
    for row in rows:
        c+=1
        #print(row)
        _id = row[0]
        _tag = row[1]
        _jsn = row[2]
        #print(_id, _tag, _jsn)

        data = concatJsnData(scope, _jsn)

        if int(_tag) != 0:
            t+=1

        y.append(_tag)
        X.append(data)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    vectorizer = CountVectorizer()
    counts = vectorizer.fit_transform(X_train)
    classifier = MultinomialNB()
    targets = y_train
    classifier.fit(counts, targets)

    logging.info('naive_bayes.MultinomialNB model records '+str(c)+' tagged '+str(t)+ ' scope ' + str(scope) + ' b2sum ' + str(b2))

    return (vectorizer, classifier)


def sklearnNaiveBayesMultinomialNB(scope, db_store):
    logging.info('Sentry watch-syslog naive_bayes.MultinomialNB')

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split

    X=[]
    y=[]

    #open/load training data
    #rows = store.getAll('training', db_store)
    rows = store.getAll('model', db_store)
    if len(rows) == 0:
        #print('Zero training data')
        logging.error('Zero training data. Can not perform naive_bayes.MultinomialNB')
        return (False, False)
    b2 = b2checksum(str(rows))
    c=0
    t=0
    for row in rows:
        c+=1
        #print(row)
        _id = row[0]
        _tag = row[1]
        _jsn = row[2]
        #print(_id, _tag, _jsn)

        data = concatJsnData(scope, _jsn)

        if int(_tag) != 0:
            t+=1

        y.append(_tag)
        X.append(data)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    vectorizer = CountVectorizer()
    counts = vectorizer.fit_transform(X_train)
    classifier = MultinomialNB()
    targets = y_train
    classifier.fit(counts, targets)

    logging.info('naive_bayes.MultinomialNB model records '+str(c)+' tagged '+str(t)+ ' scope ' + str(scope) + ' b2sum ' + str(b2))

    return (vectorizer, classifier)

def sklearnNaiveBayesBernoulliNB(scope, db_store):
    logging.info('Sentry watch-syslog naive_bayes.BernoulliNB')

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import BernoulliNB
    from sklearn.model_selection import train_test_split

    X=[]
    y=[]

    #open/load training data
    #rows = store.getAll('training', db_store)
    rows = store.getAll('model', db_store)
    if len(rows) == 0:
        #print('Zero training data')
        logging.error('Zero training data. Can not perform naive_bayes.BernoulliNB')
        return (False, False)
    b2 = b2checksum(str(rows))

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
        data = concatJsnData(scope, _jsn)
        X.append(data)

    X_train, X_test, y_train, y_test = train_test_split(X, y)
    vectorizer = CountVectorizer()
    counts = vectorizer.fit_transform(X_train)
    classifier = BernoulliNB()
    targets = y_train
    classifier.fit(counts, targets)

    logging.info('naive_bayes.BernoulliNB model records '+str(c)+' tagged '+str(t)+ ' scope ' + str(scope) + ' b2sum ' + str(b2))

    return (vectorizer, classifier)


def sklearnNeuralNetworkMLPClassifier(scope, db_store):
    logging.info('Sentry watch-syslog neural_network.MLPClassifier')

    from sklearn.neural_network import MLPClassifier
    from sklearn.model_selection import train_test_split

    from sklearn.feature_extraction.text import CountVectorizer

    X=[]
    y=[]

    #open/load training data
    #rows = store.getAll('training', db_store)
    rows = store.getAll('model', db_store)
    if len(rows) == 0:
        #print('Zero training data')
        logging.error('Zero training data. Can not perform naive_bayes.MultinomialNB')
        return (False, False)
    b2 = b2checksum(str(rows))
    c=0
    t=0
    for row in rows:
        c+=1
        #print(row)
        _id = row[0]
        _tag = row[1]
        _jsn = row[2]
        #print(_id, _tag, _jsn)

        data = concatJsnData(scope, _jsn)

        if int(_tag) != 0:
            t+=1

        y.append(_tag)
        X.append(data)

    #training_set, validation_set = train_test_split(data, test_size = 0.2, random_state = 21)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 21)

    #X_train, X_test, y_train, y_test = train_test_split(X, y)
    #vectorizer = CountVectorizer()
    #counts = vectorizer.fit_transform(X_train)
    #classifier = MultinomialNB()
    #targets = y_train
    #classifier.fit(counts, targets)

    vectorizer = CountVectorizer()

    counts = vectorizer.fit_transform(X_train)

    targets = y_train

    classifier = MLPClassifier(hidden_layer_sizes=(150,100,50), max_iter=300,activation = 'relu',solver='adam',random_state=1)

    #classifier.fit(X_train, y_train)
    classifier.fit(counts, targets)

    # need to fit_transform the data...
    #ValueError: could not convert string to float: '[com.apple.calendar.store.log.caldav.http] [Task 63] Default calendar '

    logging.info('neural_network.MLPClassifier model records '+str(c)+' tagged '+str(t)+ ' scope ' + str(scope) + ' b2sum ' + str(b2))

    #return classifier
    return (vectorizer, classifier)

    #Predicting y for X_val
    #y_pred = classifier.predict(X_val)




def getAlgoDict(_sklearn):
    algoDict={}
    for item in _sklearn:
        #print('item ',item, ' ', str(type(item))) #<class 'dict'>
        for k,v in item.items():
            #print(k,v)
            algoDict[k]=v
    return algoDict

def sklearnPredict(line, algoDct, skInitDct):
    pDct={}

    #print('DEBUG '  + str(algoDct))
    #print('DEBUG '  + str(algoDct['naive_bayes.MultinomialNB'])) # ['eventMessage', 'messageType', 'category']


    scope = algoDct['naive_bayes.MultinomialNB'] #['eventMessage', 'messageType', 'category']
    sample = []
    #_sample = concatJsnData(algoDct['naive_bayes.MultinomialNB'], line)
    _sample = concatJsnData(scope, line)
    sample.append(_sample)

    #for key in algoDct.keys():
    #    print(key)
        #naive_bayes.MultinomialNB
        #naive_bayes.BernoulliNB

    #for k,v in skInitDct.items():
    #    print(k,v)
        #naive_bayes.MultinomialNB [CountVectorizer(), MultinomialNB()]
        #naive_bayes.BernoulliNB [CountVectorizer(), BernoulliNB()]

    for key in algoDct.keys():
        vc = skInitDct[key]
        #print(vc, ' ', str(type(vc)))
        vectorizer=vc[0]
        classifier=vc[1]
        #vectorizer, classifier = 
        sample_count = vectorizer.transform(sample)
        p = classifier.predict(sample_count)
        pDct[key]=[ _sample, p ]

    return pDct

def updategDictR(_key, gDict, rule_hit, r, line, rulesDct, db_store,  verbose=False):

    #print('_key ' + str(_key))
    #print('gDict ' + str(gDict))
    #print('rule_hit ' + str(rule_hit))
    #print('r ' + str(r))
    #print('rulesDct ' + str(rulesDct))

    for key in rule_hit:

        _r = rule_hit[key][0]
        b = rule_hit[key][1]
        d = rule_hit[key][2]

        #print('Expire in json ... ' + str(rulesDct[_r]))
        rdata = json.loads(rulesDct[_r])
        #print('rdata ' + str(rdata))
        expire = rdata.get("expire", None)
        #print('expire ' + str(expire))

        if b in r.keys():
            seen = True
            v=r[b]
            v+=1
            r[b]=v
        else:
            seen = False
            r[b]=1

        _k = 'sentinel_watch_syslog_rule_engine-'+str(_r)+'-'+str(b)

        _data = promDataSanitizer(str(d))

        now = time.strftime("%Y-%m-%d %H:%M:%S")

        if expire:
            _prom = 'config="'+str(_key)+'",rule="' + str(_r) + '",b2sum="' + str(b) + '",seen="' + str(seen) + '",data="' + str(_data) + '",expire="'+ str(expire) +'",date="'+str(now)+'"'
        else:
            _prom = 'config="'+str(_key)+'",rule="'+str(_r)+'",b2sum="'+str(b)+'",seen="'+str(seen)+'",data="'+str(_data)+'",date="'+str(now)+'"'

        gDict[_k] = [ 'sentinel_watch_syslog_rule_engine{' + _prom + '} ' + str(r[b]) ]

        #store_occurrence = store.replaceINTOtrio('occurrence', str(_k), str(r[b]), line, db_store)

        if verbose: print(_k, gDict[_k])

    return True



#def updategDictR_V1(_key, gDict, rule_hit, r, line, db_store,  verbose=False):
#
#    for key in rule_hit:
#
#        _r = rule_hit[key][0]
#        b = rule_hit[key][1]
#        d = rule_hit[key][2]
#
#        if b in r.keys():
#            seen = True
#            v=r[b]
#            v+=1
#            r[b]=v
#        else:
#            seen = False
#            r[b]=1
#
#        _k = 'sentinel_watch_syslog_rule_engine-'+str(_r)+'-'+str(b)
#
#        _data = promDataSanitizer(str(d))
#
#        now = time.strftime("%Y-%m-%d %H:%M:%S")
#
#        _prom = 'config="'+str(_key)+'",rule="' + str(_r) + '",b2sum="' + str(b) + '",seen="' + str(seen) + '",data="' + str(_data) + '",date="'+str(now)+'"'
#
#        gDict[_k] = [ 'sentinel_watch_syslog_rule_engine{' + _prom + '} ' + str(r[b]) ]
#
#        #store_occurrence = store.replaceINTOtrio('occurrence', str(_k), str(r[b]), line, db_store)
#
#        if verbose: print(_k, gDict[_k])
#
#    return True

def promDataSanitizer(_str):

    _str = _str.replace('"','')  #quote
    _str = _str.replace("'",'')  #single quote
    _str = _str.replace("\\",' ') #backslash
    _str = _str.replace('`',' ')  #backtick
    _str = _str.replace(',','')  #comma
    _str = _str.replace('“',' ')  #italic quote
    _str = _str.replace('\n',' ') #lines breaks
    _str = _str.replace('\r',' ') #lines return
    _str = _str.replace('^M',' ') #ctrlM

    #_str = _str.replace(':',' ') #colon
    #_str = _str.decode('utf8', 'ignore')

    return _str


def updategDictS(_key, gDict, sklearn_hit, s, line, db_store, verbose=False):

    for k,v in sklearn_hit.items():

        _sample  = v[0]
        _predict = v[1]

        b = b2checksum(_sample)
        if b in s.keys():
            seen = True
            v=s[b]
            v+=1
            s[b]=v
        else:
            seen = False
            s[b]=1

        if '1' in _predict:
            #promDataSanitizer
            __sample = promDataSanitizer(_sample)
            _k = str(k)+'-'+str(b)
            #_prom = 'config="'+str(_key)+'",algo="'+str(k)+'",predict="1",seen="'+str(seen)+'",b2sum="'+str(b)+'",sample="' + str(__sample) + '"'
            _prom = 'config="'+str(_key)+'",algo="'+str(k)+'",predict="1",seen="'+str(seen)+'",b2sum="'+str(b)+'",data="' + str(__sample) + '"'
            gDict[_k] = [ 'sentinel_watch_syslog_sklearn{' + _prom + '} ' +str(s[b])]

            #no longer store in sql, uses shared_memory now...
            #store_occurrence = store.replaceINTOtrio('occurrence', str(_k), str(s[b]), line, db_store)

            if verbose: print(_k, gDict[_k])

    return True

def sklearnInitAlgoDict(algoDct, db_store):
    skInitDct={}

    if 'naive_bayes.MultinomialNB' in algoDct.keys():
        vectorizer, classifier = sklearnNaiveBayesMultinomialNB(algoDct['naive_bayes.MultinomialNB'], db_store)
        skInitDct['naive_bayes.MultinomialNB'] = [vectorizer, classifier]

    if 'naive_bayes.BernoulliNB' in algoDct.keys():
        vectorizer, classifier = sklearnNaiveBayesBernoulliNB(algoDct['naive_bayes.BernoulliNB'], db_store)
        skInitDct['naive_bayes.BernoulliNB'] = [vectorizer, classifier]

    if 'neural_network.MLPClassifier' in algoDct.keys():
        #vectorizer, classifier = sklearnNaiveBayesBernoulliNB(algoDct['naive_bayes.BernoulliNB'], db_store)
        #skInitDct['naive_bayes.BernoulliNB'] = [vectorizer, classifier]
        #from sklearn.neural_network import MLPClassifier
        #classifier = MLPClassifier(hidden_layer_sizes=(150,100,50),max_iter=300,activation='relu',solver='krink',random_state=1)
        vectorizer, classifier = sklearnNeuralNetworkMLPClassifier(algoDct['neural_network.MLPClassifier'], db_store)
        skInitDct['neural_network.MLPClassifier'] = [vectorizer, classifier]

    return skInitDct



def sentryLogStream(db_store, _key, gDict, verbose=False):
    #logging.info('Sentry watch-syslog logstream ')
    debug=True

    conf = store.getData('configs', _key, db_store)
    if conf:
        config = json.loads(conf[0])
        logfile = config.get('logfile', None)
        rules   = config.get('rules', None)
        sklearn = config.get('sklearn', None)

    #load rules (getExpertRules)
    if rules:
        rulesDct = getExpertRules(_key, db_store)

        _k = 'sentinel_watch_syslog_rule_engine_info-1'
        _prom = 'rules_loaded="'+str(len(rulesDct))+'",rules_b2sum="'+b2checksum(str(rulesDct))+'",load_time="'+str(time.strftime("%Y-%m-%d %H:%M:%S"))+'"'
        gDict[_k] = [ 'sentinel_watch_syslog_rule_engine_info{' + _prom + '} 1.0' ]
        logging.info('Sentry '+str(_key)+' Expert_Rules Scope '+ str(rules))
        logging.info('Sentry Expert_Rules Loaded ' + str(len(rulesDct)) + ' ' + b2checksum(str(rulesDct)) )

    if sklearn:
        algoDct = getAlgoDict(sklearn)
        if debug: print('algoDct ' + str(algoDct))
        skInitDct = sklearnInitAlgoDict(algoDct, db_store)
        db_hash = b2checksum(str(store.getAll('model', db_store)))

        _k = 'sentinel_watch_syslog_sklearn_info-1'
        _prom = 'sklearn_loaded="'+str(algoDct)+'",b2sum="'+str(db_hash)+'",load_time="'+str(time.strftime("%Y-%m-%d %H:%M:%S"))+'"'
        gDict[_k] = [ 'sentinel_watch_syslog_sklearn_info{' + _prom + '} 1.0' ]
        

    r={}
    s={}

    elapsed_interval = 30 #1h is 60*60 (3600 seconds)
    end_time = time.time() + elapsed_interval

    ##########################################################################
    #for line in logstream_v2():
    for line in logstream():

        if exit.is_set():
            print('logstream exit is set')
            break

        line = line.decode('utf-8')
        jline = json.loads(line)


        if time.time() > end_time:
            end_time = time.time() + elapsed_interval
            #print('end_time ' + str(end_time))

            if rules:
                new_rulesDct = getExpertRules(_key, db_store)
                if rulesDct != new_rulesDct:
                    rulesDct = getExpertRules(_key, db_store)
                    
                    _prom = 'rules_loaded="'+str(len(rulesDct))+'",rules_b2sum="'+b2checksum(str(rulesDct))+'",load_time="'+str(time.strftime("%Y-%m-%d %H:%M:%S"))+'"'
                    _k = 'sentinel_watch_syslog_rule_engine_info-1'
                    gDict[_k] = [ 'sentinel_watch_syslog_rule_engine_info{' + _prom + '} 1.0' ]
                    logging.info('Sentry Expert_Rules Reloaded ' + str(len(rulesDct)) + ' ' + b2checksum(str(rulesDct)) )

            if sklearn:
                new_db_hash = b2checksum(str(store.getAll('model', db_store)))
                if db_hash != new_db_hash:
                    db_hash = new_db_hash
                    skInitDct = sklearnInitAlgoDict(algoDct, db_store)

                    _k = 'sentinel_watch_syslog_sklearn_info-1'
                    _prom = 'sklearn_loaded="'+str(algoDct)+'",b2sum="'+str(db_hash)+'",load_time="'+str(time.strftime("%Y-%m-%d %H:%M:%S"))+'"'
                    gDict[_k] = [ 'sentinel_watch_syslog_sklearn_info{' + _prom + '} 1.0' ]

        if rules:

            rule_hit = expertLogStreamRulesEngineGeneralJson(jline, rules, rulesDct)
            if rule_hit: updategDictR(_key, gDict, rule_hit, r, line, rulesDct, db_store, verbose)

        if sklearn:

            sklearn_hit = sklearnPredict(line, algoDct, skInitDct)
            if sklearn_hit: updategDictS(_key, gDict, sklearn_hit, s, line, db_store, verbose)

    ##########################################################################

    #return True
    return 'logstream.done'  


#def sentryLogStream_v1(db_store, _key, gDict, verbose=False):
#    #logging.info('Sentry watch-syslog logstream ')
#
#    conf = store.getData('configs', _key, db_store)
#    if conf:
#        config = json.loads(conf[0])
#        logfile = config.get('logfile', None)
#        rules   = config.get('rules', None)
#        sklearn = config.get('sklearn', None)
#
#    #load rules (getExpertRules)
#    if rules:
#        logging.info('Sentry '+str(_key)+' expert_rules scope '+ str(rules))
#        rulesDct = getExpertRules(_key, db_store)
#
#    if sklearn:
#        algoDct = getAlgoDict(sklearn)
#        skInitDct = sklearnInitAlgoDict(algoDct, db_store)
#
#    r={}
#    s={}
#
#    ##########################################################################
#    #for line in logstream():
#    for line in logstream_v2():
#
#        line = line.decode('utf-8')
#        jline = json.loads(line)
#
#        if rules:
#            rule_hit = expertLogStreamRulesEngineGeneralJson(jline, rules, rulesDct)
#            if rule_hit: updategDictR(_key, gDict, rule_hit, r, line, db_store, verbose)
#
#        if sklearn:
#            sklearn_hit = sklearnPredict(line, algoDct, skInitDct)
#            if sklearn_hit: updategDictS(_key, gDict, sklearn_hit, s, line, db_store, verbose)
#
#    ##########################################################################
#    return True

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

        #run = store.updateTraining(tag, line, db_store)
        run = store.updateTable(tag, line, 'model', db_store)
        print(line)

    return True

def markTrainingRe(_search, db_store):

    rows = store.getAll('training', db_store)
    for rowid,tag,data in rows:

        if re.search(_search, data, re.IGNORECASE):
            print('mark ', rowid, ' ', data)
            mark = store.updateTrainingTag(rowid, '1', db_store)
            print(mark)

    return True


def markTrainingRe__v1__(_search, db_store):

    rows = store.getAll('training', db_store)
    for rowid,tag,data in rows:
        #print(data)
        #jdata = json.loads(data)
        #print(jdata.get('eventMessage', None))

        if re.search(_search, data, re.IGNORECASE):
            print('mark ', rowid, ' ', data)
            mark = store.updateTrainingTag(rowid, '1', db_store)
            print(mark)

    return True

def sentryTailFile(db_store, gDict, _file):
    for line in tail(_file):
        print(line)
    return True

#----------------------------------------------------------------------------------------

def genSystemProfile(db_store):

    if str(sys.platform).startswith('linux'):
        return genSystemProfileLinux(db_store)

    elif sys.platform == 'darwin':
        return genSystemProfileMac(db_store)

    else:
        logging.critical('no can do genSystemProfile')
        return None


def genSystemProfileLinux(db_store):
    print('TODO genSystemProfile Linux')
    return False


def genSystemProfileMac(db_store):
    print('genSystemProfile Mac')

    cmd = 'system_profiler -detailLevel full -json'
    #proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    #stderr=STDOUT
    #proc = Popen(cmd.split(), stdout=PIPE, stderr=STDOUT)
    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    #out = proc.stdout.readlines()
    out = proc.stdout.read()
    err = proc.stderr.readlines()

    #print('--------------------------------')
    
    #print(str(out))

    #for line in out:
    #    #line = line.decode('utf-8')
    #    #line = line.decode('utf-8').strip('\n')
    #    line = line.decode('utf-8').rstrip()
    #    print(line)

    #for line in err:
    #    print('err ' + str(line))
        

    #name = str(b2checksum(json.dumps(out[0].decode('utf-8'))))
    #print(' name ' + str(name))
    #update = store.replaceINTOducedate('system_profile', name, json.dumps(out[0].decode('utf-8')), db_store)
    #print(update)

    name = str(b2checksum(out.decode('utf-8')))
    #print(' name ' + str(name))
    #update = store.replaceINTOducedate('system_profile', name, json.dumps(out[0].decode('utf-8')), db_store)
    update = store.replaceINTOducedate('system_profile', name, out.decode('utf-8'), db_store)
    #print(update)
    #return True
    return update


#def ordered(obj):
#    if isinstance(obj, dict):
#        return sorted((k, ordered(v)) for k, v in obj.items())
#    if isinstance(obj, list):
#        return sorted(ordered(x) for x in obj)
#    else:
#        return obj


def diffSystemProfileIDs(rowid1, rowid2, db_store):
    #print('dict.differ.time')

    row1 = store.getByID('system_profile', rowid1, db_store)
    dta1 = row1[3]
    jsn1 = json.loads(dta1)

    row2 = store.getByID('system_profile', rowid2, db_store)
    dta2 = row2[3]
    jsn2 = json.loads(dta2)

#    s = data['SPAirPortDataType'][0]['spairport_airport_interfaces'][0]['_name']
#    print('s is ' , s)
#
#    #x = data['SPPowerDataType'][1]['Battery Power']['Current Power Source']
#    i = data['SPPowerDataType'][1]['Battery Power']['Display Sleep Timer']
#    print('i  is ' , str(i))
#
#    ii = jsn2['SPPowerDataType'][1]['Battery Power']['Display Sleep Timer']
#    print('ii is ' , str(ii))
#
#    #jj = jsn2['SPPowerDataType'][4]['_items'][0]['_items'][1]['appPID'] #IndexError: list index out of range
#    #print('jj is ' , str(jj))
#
#    #jx = jsn2['SPPowerDataType'][4]['_items'][0]['_items'][1].get('appPID', None)
#    jx = jsn1.get('SPPowerDataType', None)[4]['_items'][0]['_items'][1].get('appPID', None) #IndexError
#    print('jx is ' , str(jx))


    ###############################

    D1 = jpaths(jsn1)
    D2 = jpaths(jsn2)

    #print(len(D1))
    #print(len(D2))
    #print(len(L3))

    #res = [x for x in L1 + L2 if x not in L1 or x not in L2]
    #print(len(res))

    d1 = dDct(jsn1, jsn2)
    n1={}
    n2={}
    for key in d1:
        n1[key]=d1[key]
        n2[key]=jsn2[key]

    N1 = jpaths(n1)
    N2 = jpaths(n2)
    #print(len(N1))
    #print(len(N2))


    #for item in L1:
    #    if item in L2:
    #        print('both have')
    #    else:
    #        print('missing from List2', item)

    D3={}

    for key in N1:
        if key not in N2.keys():
            D3[key]='<'
        else:
            if N1[key] == N2[key]:
                D3[key]='='
            else:
                D3[key]='x'


    for key in N2:
        if key not in N1.keys():
            D3[key]='>'


    for k,v in D3.items():
        #if '=' in v:
        #    continue
            #print(k)

        print(v, k)

    #WORK


    #q1 = jsn1['SPAirPortDataType'][0]['spairport_airport_interfaces'][0]['spairport_airport_local_wireless_networks'][27]['_name']
    #q2 = jsn2['SPAirPortDataType'][0]['spairport_airport_interfaces'][0]['spairport_airport_local_wireless_networks'][27]['_name']
    #print(q2)

    #q = jsn1['SPAirPortDataType'][0]['spairport_airport_interfaces'][0]['spairport_airport_local_wireless_networks'][26]['_name']
    #print(q)

    #q = jsn1['SPAirPortDataType'][0]['spairport_airport_interfaces'][0]['spairport_airport_local_wireless_networks'][18]['spairport_network_country_code']
    #print(q)

    return True

#----

def jpaths(data):

    D={}

    for element in data:
        if (isinstance(data[element], dict)):
            checkDict(data[element], element, D)
            #checkDict(data[element], 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'+str(element))
        elif (isinstance(data[element], list)):
            #checkList(data[element], element, L)
            #checkList(data[element], 'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL'+str(element))
            #checkList(data[element], str(element)+" ", D)
            checkList(data[element], "['"+str(element)+"']", D)

    return D


def checkList(ele, prefix, D):
    for i in range(len(ele)):
        if (isinstance(ele[i], list)):
            checkList(ele[i], prefix+"["+str(i)+"]", D)
        elif (isinstance(ele[i], str)):
            printField(ele[i], prefix+"["+str(i)+"]", D)
        elif (isinstance(ele[i], int)):
            printField(ele[i], prefix+"["+str(i)+"]", D)
        else:
            checkDict(ele[i], prefix+"["+str(i)+"]", D)

def checkDict(jsonObject, prefix, D):
    for ele in jsonObject:
        if (isinstance(jsonObject[ele], dict)):
            checkDict(jsonObject[ele], prefix+"['"+ele+"']", D)

        elif (isinstance(jsonObject[ele], list)):
            checkList(jsonObject[ele], prefix+"['"+ele+"']", D)

        elif (isinstance(jsonObject[ele], str)):
            printField(jsonObject[ele],  prefix+"['"+ele+"']", D)

        elif (isinstance(jsonObject[ele], int)):
            printField(jsonObject[ele],  prefix+"['"+str(ele)+"']", D)

def printField(ele, prefix, D):
    #print(prefix, ":" , ele)

    if (isinstance(ele, str)):
        #print(prefix, ":" , 'str')
        #L.append(prefix)
        D[prefix]=ele
    elif (isinstance(ele, int)):
        #print(prefix, ":" , 'int')
        #L.append(prefix)
        D[prefix]=ele

    return D
    #else:
    #    print(prefix, ":" , ele)
    #https://www.codementor.io/@simransinghal/working-with-json-data-in-python-165crbkiyk


#def id_generator(d):
#    for k, v in d.items():
#        if k == "_name":
#            yield v
#        elif isinstance(v, dict):
#            for id_val in id_generator(v):
#                yield id_val
#
#
#def recursion(dict):
#    for key, value in dict.items():
#        if type(value) == type(dict):
#            for key, value in value.items():
#                if isinstance (value,list):
#                    print(key)
#                        # place where I need to enter list comprehension?
#                if type(value) == type(dict):
#                    if key == "id":
#                        print(" id found " + value)
#                    if key != "id":
#                        print(key + " 1st level")
#                if key == "id":
#                    print(key)
#        else:
#            if key == "id":
#                print("id found " + value)
#
#
#
#def rObj(dct):
#
#    for k,v in dct.items():
#
#        if v == type(str):
#            return 'value_str'
#        if v == type(int):
#            return 'value_int'
#        if v == type(list):
#            return obj
#        if v == (dict):
#            return obj


def dDct(dct1, dct2):
    d={}
    for key in dct1:
        if key in dct2:
            if dct1[key] != dct2[key]:
                d[key]=dct1[key]
    return d


#def checkDifference(orig,new):
#	diff = {}
#	if type(orig) != type(new):
#		#print "Type difference"
#		return True
#	else:
#		if type(orig) is dict and type(new) is dict:
#			#print "Types are both dicts"
#			##	Check each of these dicts from the key level
#			diffTest = False
#			for key in orig:
#				result = checkDifference(orig[key],new[key])
#				if result != False:	## Means a difference was found and returned
#					diffTest = True
#					#print "key/Values different: " + str(key)
#					diff[key] = result
#			##	And check for keys in second dataset that aren't in first
#			for key in new:
#				if key not in orig:
#					diff[key] = ("KeyNotFound", new[key])
#					diffTest = True
#
#			if diffTest:
#				return diff
#			else:
#				return False
#		else:
#			#print "Types were not dicts, likely strings"
#			if str(orig) == str(new):
#				return False
#			else:
#				return (str(orig),str(new))
#	return diff


#def contained(a, b):
#    #""" checks if dictionary a is fully contained in b """
#    if not isinstance(a, dict):
#        return a == b
#    else:
#        return all(contained(v, b.get(k)) for k, v in a.items())
#
#print(contained(d1, d2))


#def compareJson(example_json_s, target_json_s):
# example_json = json.loads(example_json_s)
# target_json = json.loads(target_json_s)
# return compareParsedJson(example_json, target_json)
#
#def compareParsedJson(example_json, target_json):
# for x in example_json:
#   if type(example_json[x]) is not dict:
#     if not x in target_json or not example_json[x] == target_json[x]:
#       return False
#   else:
#     if x not in target_json or not compareParsedJson(example_json[x], target_json[x]):
#      return False
#
# return True
#
#
#def compare_object(a,b):
#    if type(a) != type(b):
#        return False
#    elif type(a) is dict:
#        return compare_dict(a,b)
#    elif type(a) is list:
#        return compare_list(a,b)
#    else:
#        return a == b
#
#def compare_dict(a,b):
#    if len(a) != len(b):
#        return False
#    else:
#        for k,v in a.items():
#            if not k in b:
#                return False
#            else:
#                if not compare_object(v, b[k]):
#                    return False
#    return True
#
#def compare_list(a,b):
#	if len(a) != len(b):
#		return False
#	else:
#		for i in range(len(a)):
#			if not compare_object(a[i], b[i]):
#				return False
#	return True
#
#print(compare_object(json_a, json_b)) 

#def recursively_parse_json(input_json, target_key):
#    #'target_key' must be unique key in the json tree
#    if type(input_json) is dict and input_json:
#        if key == target_key:
#            print(input_json[key])
#        for key in input_json:
#            recursively_parse_json(input_json[key], target_key)
#
#    elif type(input_json) is list and input_json:
#        for entity in input_json:
#            recursively_parse_json(entity, target_key)
#
#
#def item_generator(json_input, lookup_key):
#    if isinstance(json_input, dict):
#        for k, v in json_input.items():
#            if k == lookup_key:
#                yield v
#            else:
#                yield from item_generator(v, lookup_key)
#    elif isinstance(json_input, list):
#        for item in json_input:
#            yield from item_generator(item, lookup_key)
#




#def getRDct(Lst):
#    Dct={}
#    for item in Lst:
#        if item == list:
#            for i in 

#def getDct(Lst):
#    Dct={}
#    for item in Lst:
#        for k,v in item.items():
#            Dct[k]=v
#    return Dct

#----------------------------------------------------------------------------------------


def getSystemProfileData(rowid, data, db_store):
    
    row = store.getByID('system_profile', rowid, db_store)

    #print(row[0])
    #print(row[1])
    #print(row[2])
    #print(row[3])

    #L = [ v1, v2, v3 ]
    #"['SPSyncServicesDataType'][1]['_name']"

    jsn = json.loads(row[3])
    #print(data)

    #v1 = 'SPSoftwareDataType'
    #v2 = 0
    #v3 = 'os_version'

    #j = jsn[v1][v2][v3]
    #print(j)

    #print('jsn type ' + str(type(jsn)))
    #print('--------------------------------------------')


    #j = jsn.get(v1, None).get(v2, None).get(v3, None)

    #j = jsn['SPStorageDataType'][1]['size_in_bytes']


    #j = jsn['SPSyncServicesDataType'][1]['_name']
    #j = jsn['SPPowerDataType'][1]['AC Power']['Display Sleep Timer']

    #return row
    #return j

    #_path = "['SPPowerDataType'][1]['AC Power']['Display Sleep Timer']"
    #v = getNestedDictVal(jsn, _path)

    v = getNestedDictVal(jsn, data)
    #print('v ' + str(v))
    #return True
    return v



def getNestedDictVal(_json, _path):
    val = None

    #print('_json type ' + str(type(_json)))
    #_path = "['SPSyncServicesDataType'][1]['_name']"

    #print(_path)

    #print(len(_path), ' ', type(_path))

    #_path = _path.lstrip('[')
    #_path = _path.rstrip(']')
    #L = _path.split('][')
    #print('L _path ][ ' + str(type(L)) +' '+ str(L))

    L = unPath(_path)

    #print(str(L))
    #print(len(L))

    #print(L[0])

    #val = _json[str(L[0])][int(L[1])][L[2]][L[3]]
    #val = _json[L[0]][L[1]][L[2]][L[3]]

    #try:
    #    #val = _json[L[0]][L[1]][L[2]][L[3]]
    #    val = _json[L[0]][L[1]][L[2]]
    #except IndexError:
    #    val = None

    #val = _json[L[0]][L[1]][L[2]]
    #val = _json[str(L)]

    #for variable in L:
    #    _json[variable] = eval(variable)

    #val = _json[eval(_path)] #TypeError: string indices must be integers

    #for i in range(len(L)):
    #    print(' . ')

    #_len = len(L)

    #opt={
    #        1: _json[L[0]],
    #        2: _json[L[0]][L[1]],
    #        3: _json[L[0]][L[1]][L[2]],
    #        4: _json[L[0]][L[1]][L[2]][L[3]],
    #}
    #val = opt[len(L)]
    # 3
    # 4: _json[L[0]][L[1]][L[2]][L[3]] 
    # IndexError: list index out of range


    _len = len(L)

    if _len == 1:
        val = _json[L[0]]
    elif _len == 2:
        val = _json[L[0]][L[1]]
    elif _len == 3:
        val = _json[L[0]][L[1]][L[2]]
    elif _len == 4:
        val = _json[L[0]][L[1]][L[2]][L[3]]
    else:
        val = 'Error'



    #v1 = 'SPSoftwareDataType'
    #v2 = 0
    #v3 = 'os_version'
    #val = _json[v1][v2][v3]

    return val

def unPath(_path):
    #['SPPowerDataType'][1]['AC Power']['Display Sleep Timer']
    _path = _path.lstrip("[")
    _path = _path.rstrip("]")
    L1 = _path.split("][")
    L=[]
    for item in L1:
        #print('item', str(type(item)), ' ',  item)

        if not item.startswith("'"):
            #print(' oh an int, ...' + str(item))
            L.append(int(item))
        else:
            #item.lstrip("'")
            #item.rstrip("'")
            #item = item.replace("'", "")
            #print('item', str(type(item)), ' ',  item)

            item = item.strip("'")
            L.append(item)

    return L

#----------------------------------------------------------------------------------------

def sentryPushGateway(db_store, key, gDict, verbose=False):
    logging.info('Sentry PushGateway')

    #if verbose: print('key is ' + str(key))

    _config   = json.loads(store.getData('configs', key, db_store)[0]).get('config', None)
    _host     = json.loads(store.getData('configs', key, db_store)[0]).get('host', '127.0.0.1')
    _port     = json.loads(store.getData('configs', key, db_store)[0]).get('port', 9091)
    _proto    = json.loads(store.getData('configs', key, db_store)[0]).get('proto', 'http')
    _path     = json.loads(store.getData('configs', key, db_store)[0]).get('path', '/metrics')
    _interval = json.loads(store.getData('configs', key, db_store)[0]).get('interval', 30)

    #if verbose: print(str(_config))

    if _config != 'pushgateway':
        return False

    #_url = 'http://192.168.0.13:9091/metrics/job/sentinel_job/instance/10.10.0.9:9111'

    #instance_name = ""
    #hostname = socket.gethostname()
    #ip = socket.gethostbyname(hostname)

    short_hostname = socket.gethostname().split('.')[0]

    instance_name = str(short_hostname) + ':shared_memory'

    job_name = 'sentinel_push'

    url = str(_proto)+'://'+str(_host)+':'+str(_port)+str(_path)+'/job/'+str(job_name)+'/instance/'+str(instance_name)

    c=0
    while not exit.is_set():

        post = sentryPushGatewayPost(gDict, url)
        #print('post status ' + str(post))

        for i in range(_interval):
            try:
                time.sleep(1)
            except Exception as e:
                logging.critical('break.sentryPushGateway ' + str(e))
                exit.set()
                break

        c+=1
        if c > 5:
            if verbose: print('pushgateway ' + str(post))
            c=0
        #if verbose: print(str(c))

    return True


#----------------------------------------------------------------------------------------

def sentryPushGatewayPost(gDict, url):
    import requests

    data = ''

    for k,v in gDict.items():
        #print(v)
        for item in v:
            #print(item)
            data += str(item) + '\n'


    #_url = 'http://192.168.0.13:9091/metrics/job/sentinel_job/instance/10.10.0.9:9111'

    try:
        response = requests.post(url=url, data=data, headers={'Content-Type': 'application/octet-stream'})
        status_code = response.status_code

    except requests.exceptions.RequestException as e:
        #print('requests.exceptions.RequestException ' + str(e))
        logging.error('requests.exceptions.RequestException ' + str(e))
        status_code = 0

    #print(response.status_code)

    #print('post is done')
    #return True
    #return str(response.status_code)
    return status_code

#🌈 karl.rink@Karl-MacBook-Pro ~ % curl http://192.168.0.13:9091/metrics
#sentinel_up{cpu="3.03",instance="10.10.0.9:9111",job="sentinel_job",procs="2",rss="18628608",threads="5",uptime="5",version="1.7.8-5-20210623-1"} 1
#push metrics here and now
#200

#----------------------------------------------------------------------------------------


def sentryLogTail(db_store, key, gDict, verbose=False):

    _config  = json.loads(store.getData('configs', key, db_store)[0]).get('config', None)
    _logfile = json.loads(store.getData('configs', key, db_store)[0]).get('logfile', None)
    _type    = json.loads(store.getData('configs', key, db_store)[0]).get('type', None)
    _format  = json.loads(store.getData('configs', key, db_store)[0]).get('format', None)

    _rules   = json.loads(store.getData('configs', key, db_store)[0]).get('rules', None)
    _sklearn = json.loads(store.getData('configs', key, db_store)[0]).get('sklearn', None)


    #logging.info('Sentry TailLog ' + str(_logfile))

    if _rules:
        logging.info('Sentry '+str(key)+' expert_rules scope '+ str(_rules))
        rulesDct = getExpertRules(key, db_store)

    if _sklearn:
        algoDct = getAlgoDict(_sklearn)
        skInitDct = sklearnInitAlgoDict(algoDct, db_store)

    r={}
    s={}

    for line in tail(_logfile):
        #line = line.decode('utf-8').strip('\n')
        line = line.decode('utf-8')
        #print(line)

        if _rules: 
            #rule_hit = expertLogStreamRulesEngineGeneralStr(line, _rules, rulesDct)
            rule_hit = expertLogStreamRulesEngineGeneralStr(line, _format, rulesDct)
            if rule_hit: updategDictR(key, gDict, rule_hit, r, line, rulesDct, db_store, verbose)

        if _sklearn:
            sklearn_hit = sklearnPredict(line, algoDct, skInitDct)
            if sklearn_hit: updategDictS(key, gDict, sklearn_hit, s, line, db_store, verbose)


    return True

def sentryTailResinLog(db_store, gDict, _file):

    logging.info('Sentry resin.match ' + str(_file))

    re_match1 = re.compile(r'Watchdog starting Resin',re.I)
    c=0
    for line in tail(_file):
        line = line.decode('utf-8').strip('\n')
        if re_match1.search(line):
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
            #update_sql = store.replaceINTO2('b2sum', b, bline, db_store)
            update_sql = store.replaceINTOduce('b2sum', b, bline, db_store)

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
  #replace_sql = store.replaceINTO2('sshwatch', ip, _json, db_store)
  replace_sql = store.replaceINTOduce('sshwatch', ip, _json, db_store)

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
    openLst = []
    nmapDct = getNmapScanDct(ip, level)

    for k,v in nmapDct.items():
        line = v.split()

        if v.startswith('Host is up'):
            up = 1

        try:
            if line[1] == 'open': #https://nmap.org/book/port-scanning.html #open, open|filtered
                port = line[0]
                openLst.append(port)
        except IndexError:
            c += 1
            
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
        line =  line.decode('utf-8').strip('\n')
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

    #if isinstance(data, tuple):
    if type(data) == tuple:
        data = data[0].split('\n') #<class 'tuple'>
    #elif isinstance(data, str):
    elif type(data) == str:
        data = data.split('\n')
    else:
        data = data.split('\n')

    for line in data:
        _line = line.split()
        try:
            if _line[1] == 'open':
                port = _line[0]
        except IndexError: pass

        if 'VULNERABLE' in line:
            vulnerable += 1
            Dct[port] = vulnerable

    Lst = []
    for k,v in Dct.items():
        Lst.append(k)

    return ','.join(Lst)


def sendEmail(subject, message, db_store):
    #import os
    import smtplib
    #import ssl
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


def netScanProc(ips, db_store, gDict, name):
    scan = multiprocessing.Process(target=netScan, args=(ips, db_store, gDict, name))
    scan.start()
    scan.join()
    return True

def netScan(ips, db_store, gDict, name):
    logging.info('NetScan version 2')

    if isinstance(ips, list):
        ips = ' '.join([str(elem) for elem in ips])

    cmd = 'nmap -n -sU ' + str(ips)

    #read all ips from db
    ipDict={}
    rows = store.selectAll('ips', db_store)
    #for row in rows:
    #    print(row)
        #dbDict[ ] = 1
    for _ip, _date, _json in rows:
        #print(_ip)
        #print(_date)
        #print(_json)
        ipDict[_ip] = _date

    seen = -1


    #sys.exit(99)


    #print(cmd)
    #print(name)

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()

    #print('out is type ' + str(type(out))) #list

    #for line in out:
    #for i in range(0, len(out), 2):
    #for (a,b) in out:
    #for item in out:

    #l = len(out)
    ipList=[]
    for index, item in enumerate(out):

        line = item.decode('utf-8').strip('\n')

        if line.startswith('Nmap scan report for'):
            ip = line.split()[-1]
            ipList.append(ip)
            #print(ip)

            nextline = out[index + 1]
            nline = nextline.decode('utf-8').strip('\n')

            if nline.startswith('Host is up'):
                try:
                    latency = nline.split('(')[1].split()[0]
                except IndexError:
                    latency = None
            else:
                latency = None

            #print(latency)

            #check if ip is _ip
            if ip in ipDict.keys():
                seen = 3
            else:
                #print('insert+add ipDict ' + str(ip))
                replace = store.replaceINTO('ips', str(ip), json.dumps('{}'), db_store)
                #print(replace)
                ipDict[ip] = now
                seen = 1

            #else:
            #    seen = 2

            _key = 'net-scan-' + ip

            if _key in gDict.keys():
                seen = 2
            #else:
            #    seen = 0

            #if not ip _key not in gDict.keys():
            #    seen = 0

            # if in gDict but not in scanIP, host went away seen=0

            prom = 'name="'+str(name)+'",sentinel_job="net-scan",ip="'+str(ip)+'",latency="'+str(latency)+'",done="'+str(now)+'",seen="'+str(seen)+'"'
            #gDict[_key] = [ 'sentinel_net_scan{' + prom + '} ' + str('1') ]
            gDict[_key] = [ 'sentinel_net_scan_ip{' + prom + '} ' + str(seen) ]


        if line.startswith('Nmap done: '):
            addrs = line.split(':')[1].split()[0]
            #print(addrs)
            hosts_up = line.split('(')[1].split()[0]
            #print(hosts_up)
            scan_time = line.split()[-2]

            #_key = 'net-scan-info-' + b2checksum(ips)
            _key = 'net-scan-info-' + b2checksum(ips)

            prom = 'name="' + str(name) + '",sentinel_job="net-scan",ips="' + str(ips) + '",done="' + str(now) + '",b2sum="' + str(b2checksum(ips)) + '"'
            prom += ',addresses="'+str(addrs)+'",hosts_up="'+str(hosts_up)+'",scan_time="'+str(scan_time)+'"'
            gDict[_key] = [ 'sentinel_net_scan_info{' + prom + '} ' + str('1') ]

    #PROM INTEGRATION
    #val=1
    #now = time.strftime("%Y-%m-%d %H:%M:%S")
    #_key = 'net-scan-' + b2checksum(ips)
    #prom = 'name="' + str(name) + '",sentinel_job="net-scan",ips="' + str(ips) + '",done="' + str(now) + '",report="' + str('report') + '"'
    #gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    #seen=0 seen, but gone now
    #seen=1 first time seen
    #seen=2 second time
    #seen=3 from the sql db

    for ip_ in ipDict.keys():
        if not ip_ in ipList:
            #print('Not ip ' + ip_)
            k_ = 'net-scan-' + ip_

            if k_ in gDict.keys():
                #print('Yes.Yes ' + k_)
                prom = 'name="'+str(name)+'",sentinel_job="net-scan",ip="'+str(ip_)+'",latency="'+str('None')+'",done="'+str(now)+'",seen="'+str('0')+'"'
                gDict[k_] = [ 'sentinel_net_scan_ip{' + prom + '} ' + str('0') ]


    scan = True
    return scan

def netScan_v1(ips, db_store, gDict, name):

    #scan = runNmapScanMultiProcessDict(ips, db_store, gDict, name)

    #read all ips from db
    ipDict={}
    rows = store.selectAll('ips', db_store)
    #for row in rows:
    #    print(row)
        #dbDict[ ] = 1
    for _ip, _date, _json in rows:
        #print(_ip)
        #print(_date)
        #print(_json)
        ipDict[_ip] = _date

    seen = -1


    #sys.exit(99)

    if isinstance(ips, list):
        #ips = ips[0]
        #listToStr = ' '.join([str(elem) for elem in l])
        ips = ' '.join([str(elem) for elem in ips])

    cmd = 'nmap -n -sn ' + str(ips)

    #print(cmd)
    #print(name)

    now = time.strftime("%Y-%m-%d %H:%M:%S")

    proc = Popen(cmd.split(), stdout=PIPE, stderr=PIPE)
    out = proc.stdout.readlines()

    #print('out is type ' + str(type(out))) #list

    #for line in out:
    #for i in range(0, len(out), 2):
    #for (a,b) in out:
    #for item in out:

    #l = len(out)
    ipList=[]
    for index, item in enumerate(out):

        line = item.decode('utf-8').strip('\n')

        if line.startswith('Nmap scan report for'):
            ip = line.split()[-1]
            ipList.append(ip)
            #print(ip)

            nextline = out[index + 1]
            nline = nextline.decode('utf-8').strip('\n')

            if nline.startswith('Host is up'):
                try:
                    latency = nline.split('(')[1].split()[0]
                except IndexError:
                    latency = None
            else:
                latency = None

            #print(latency)

            #check if ip is _ip
            if ip in ipDict.keys():
                seen = 3
            else:
                #print('insert+add ipDict ' + str(ip))
                replace = store.replaceINTO('ips', str(ip), json.dumps('{}'), db_store)
                #print(replace)
                ipDict[ip] = now
                seen = 1

            #else:
            #    seen = 2

            _key = 'net-scan-' + ip

            if _key in gDict.keys():
                seen = 2
            #else:
            #    seen = 0

            #if not ip _key not in gDict.keys():
            #    seen = 0

            # if in gDict but not in scanIP, host went away seen=0

            prom = 'name="'+str(name)+'",sentinel_job="net-scan",ip="'+str(ip)+'",latency="'+str(latency)+'",done="'+str(now)+'",seen="'+str(seen)+'"'
            #gDict[_key] = [ 'sentinel_net_scan{' + prom + '} ' + str('1') ]
            gDict[_key] = [ 'sentinel_net_scan_ip{' + prom + '} ' + str(seen) ]


        if line.startswith('Nmap done: '):
            addrs = line.split(':')[1].split()[0]
            #print(addrs)
            hosts_up = line.split('(')[1].split()[0]
            #print(hosts_up)
            scan_time = line.split()[-2]

            #_key = 'net-scan-info-' + b2checksum(ips)
            _key = 'net-scan-info-' + b2checksum(ips)

            prom = 'name="' + str(name) + '",sentinel_job="net-scan",ips="' + str(ips) + '",done="' + str(now) + '",b2sum="' + str(b2checksum(ips)) + '"'
            prom += ',addresses="'+str(addrs)+'",hosts_up="'+str(hosts_up)+'",scan_time="'+str(scan_time)+'"'
            gDict[_key] = [ 'sentinel_net_scan_info{' + prom + '} ' + str('1') ]

    #PROM INTEGRATION
    #val=1
    #now = time.strftime("%Y-%m-%d %H:%M:%S")
    #_key = 'net-scan-' + b2checksum(ips)
    #prom = 'name="' + str(name) + '",sentinel_job="net-scan",ips="' + str(ips) + '",done="' + str(now) + '",report="' + str('report') + '"'
    #gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    #seen=0 seen, but gone now
    #seen=1 first time seen
    #seen=2 second time
    #seen=3 from the sql db

    for ip_ in ipDict.keys():
        if not ip_ in ipList:
            #print('Not ip ' + ip_)
            k_ = 'net-scan-' + ip_

            if k_ in gDict.keys():
                #print('Yes.Yes ' + k_)
                prom = 'name="'+str(name)+'",sentinel_job="net-scan",ip="'+str(ip_)+'",latency="'+str('None')+'",done="'+str(now)+'",seen="'+str('0')+'"'
                gDict[k_] = [ 'sentinel_net_scan_ip{' + prom + '} ' + str('0') ]


    scan = True
    return scan

#Nmap scan report for 192.168.0.253
#Host is up (0.0041s latency).
#Nmap scan report for 192.168.0.254
#Host is up (0.0068s latency).
#Nmap done: 256 IP addresses (16 hosts up) scanned in 24.44 seconds


def isNet(ips):
    try:
        net = ips.split('/')[1]
    except IndexError:
        net = False
    return net

def isIPv6(ips):
    print('TODO')
    pass

def detectScan(ips, db_store):
    print('TODO')
    pass

def discoverHostLst(ips):
    hostLst = []
    if type(ips) == str:
        ips = ips.split()

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

    print('discovered: ' + str(hostLst))
    return hostLst


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

    print(str(jdata)) 
    for k,v in jdata.items():
        b = b2sum(k)
        print(k + ' ' + b)
        jdata[k] = b

    replace = store.replaceINTO('fims', name, json.dumps(jdata), db_store)
    return replace

def checkFim(name, db_store):
    fimDct = getFimDct(name, db_store)
    for k,v in fimDct.items():
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
        if len(v) == 0:
            a += 1
            Dct[k] = 'ADDED' + str(a)
        else:
            c += 1
            Dct[k] = 'CHANGED' + str(c)

    _key = 'fimcheck-' + str(name)

    if bool(Dct):
        val = len(Dct)
    else:
        val = 0

    #Note... this is all backwards 
    #Dct['config'] = name
    Dct[name] = 'config'
    Dct[_name] = 'job'

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
    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    return True


def getFimDct(name, db_store):
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
            #Dct[k] = 'CHANGED'
            Dct[k] = v
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

    try:
        del jdata[_file]
    except KeyError:
        return 'not found ' + str(_file)

    update = store.updateData('fims', name, json.dumps(jdata), db_store)
    unstore_file = store.unstoreFile(_file, db_store)

    if update == True and unstore_file == True:
        return True
    else:
        return False



def psCheck(name, db_store, gDict, _name):
    #print('psCheck.run')
    import modules.ps.ps
    psDct = modules.ps.ps.get_ps()

    _key = 'pscheck-' + str(name)

    psDct['sentinel_job'] = name
    val = 1

    prom = ''
    c = len(psDct)
    for k,v in psDct.items():
        c -= 1
        if c == 0:
            prom += str(k) + '="' + str(v) + '"'
        else:
            prom += str(k) + '="' + str(v) + '",'

    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
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
        _p = 0
        _u = 0

        #dedup prog user
        _pD={}
        _uD={}

        for _k,_v in ppDict.items():
            #_c += 1
            vLL = _v.split()
            prog = vLL[2]
            user = vLL[3]

            #just overwrite each time
            _pD[prog] = 1
            _uD[user] = 1

            #if _c > 1:
            #    pdata += ',prog'+str(_p)+'="'+str(prog)+'",user'+str(_c)+'="'+str(user)+'"'
            #else:
            #    pdata += ',prog="'+str(prog)+'",user="'+str(user)+'"'

        #-

        for _k,_v in _pD.items():
            _p += 1
            pdata += ',prog'+str(_p)+'="'+str(_k)+'"'

        for _k,_v in _uD.items():
            _u += 1
            pdata += ',user'+str(_u)+'="'+str(_k)+'"'


        data = 'proto="'+str(proto)+'",laddr="'+str(laddr)+'",lport="'+str(lport)+'",faddr="'+str(faddr)+'",fport="'+str(fport)+'"' + pdata
        prom = 'name="' + str(_name) + '",sentinel_job="established-check",' + data + ',done="' + str(now) + '"'

        gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

    return True


def establishedCheck__v1__(name, db_store, gDict, _name):
    eaDct = getEstablishedAlertsDct(db_store)

    for key in gDict.keys():
        if key.startswith('est-established-check-'):
            del gDict[key]

    c = 0
    for k,v in eaDct.items():
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
        gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]

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

    #TODO

    return True
    
#--------

#def virshCheck(name, db_store, gDict, _name):
def kvmCheck(name, db_store, gDict, _name):
    #print('kvmCheck')
    #print('name: ' + str(name))
    #print('_name: ' + str(_name))

    from modules.hv import kvm

    uri = 'qemu://'
    host = ''

    try:
        runningDict = kvm.ListDomainsDetailedClass(uri, host).get()
        #print(json.dumps(runningDict, indent=2, sort_keys=True))
    except Exception as e:
        logging.error('kvmCheck ' + str(e))
        return str(e)

    #print(str(type(runningDict)))
    #print(str(runningDict))
    #print(runningDict['hypervisor'])
    #print(runningDict['domains'])

    #hypervisor = runningDict['hypervisor']
    #domains    = runningDict['domains']

    hypervisor = runningDict.get('hypervisor')
    domains    = runningDict.get('domains')

    if hypervisor:
        #print('hypervisor')
        #cpu_count = runningDict['hypervisor']['cpu']['count']
        cpu_count  = runningDict.get('hypervisor', {}).get('cpu', {}).get('count')
        cpu_type   = runningDict.get('hypervisor', {}).get('cpu', {}).get('type')
        cpu_idle   = runningDict.get('hypervisor', {}).get('cpu', {}).get('idle')
        cpu_iowait = runningDict.get('hypervisor', {}).get('cpu', {}).get('iowait')
        cpu_user   = runningDict.get('hypervisor', {}).get('cpu', {}).get('user')
        cpu_kernel = runningDict.get('hypervisor', {}).get('cpu', {}).get('kernel')

        mem_total  = runningDict.get('hypervisor', {}).get('mem', {}).get('total')
        mem_free   = runningDict.get('hypervisor', {}).get('mem', {}).get('free')
        mem_used   = runningDict.get('hypervisor', {}).get('mem', {}).get('used')

        hv_type    = runningDict.get('hypervisor', {}).get('type')

        _key = 'virshcheck-hypervisor-' + str(name)

        prom =  'sentinel_job="'+str(name)+'",type="'+str(hv_type)+'",cpu="'+str(cpu_count)+'",arch="'+str(cpu_type)+'",'
        prom += 'cpu_idle="'+str(cpu_idle)+'",cpu_iowait="'+str(cpu_iowait)+'",cpu_user="'+str(cpu_user)+'",cpu_kernel="'+str(cpu_kernel)+'",'
        prom += 'mem_total="'+str(mem_total)+'",mem_free="'+str(mem_free)+'",mem_used="'+str(mem_used)+'"'

        gDict[_key] = [ 'sentinel_job_kvm_hypervisor{' + prom + '} ' + str('1') ]

    if domains:
        val=0
        #print('domains')
        for domain in domains:
        #for domain ###########
            dD={}
            #_key = 'virshcheck-domain-' + str(domain)
            #print('domain ' + str(domain))
            state = runningDict.get('domains', {}).get(domain, {}).get('state')
            #k = 'virshcheck-domain-'+str(domain)
            #k = domain
            #dD[k]=state
            dD['name']=str(domain)
            dD['state']=str(state)

            if state == 'running':

                val = 1

                d_cpu_count   = runningDict.get('domains', {}).get(domain, {}).get('cpu', {}).get('count')
                d_cpu_time    = runningDict.get('domains', {}).get(domain, {}).get('cpu', {}).get('cpu_time')
                d_system_time = runningDict.get('domains', {}).get(domain, {}).get('cpu', {}).get('system_time')
                d_user_time   = runningDict.get('domains', {}).get(domain, {}).get('cpu', {}).get('user_time')

                d_mem_actual  = runningDict.get('domains', {}).get(domain, {}).get('mem', {}).get('actual')
                d_mem_update  = runningDict.get('domains', {}).get(domain, {}).get('mem', {}).get('last_update')
                d_mem_rss     = runningDict.get('domains', {}).get(domain, {}).get('mem', {}).get('rss')

                #k = 'virshcheck-domain-'+str(domain)+'-d_cpu_count'
                #k = str(domain) +'_cpu_count'
                k = 'cpu_count'
                dD[k]=d_cpu_count

                #k = 'virshcheck-domain-'+str(domain)+'-d_cpu_time'
                #k = str(domain)+'_cpu_time'
                k = 'cpu_time'
                dD[k]=d_cpu_time

                #k = 'virshcheck-domain-'+str(domain)+'-d_system_time'
                #k = str(domain)+'_system_time'
                k = 'system_time'
                dD[k]=d_system_time

                #k = 'virshcheck-domain-'+str(domain)+'-d_user_time'
                #k = str(domain)+'_user_time'
                k = 'user_time'
                dD[k]=d_user_time

                #k = 'virshcheck-domain-'+str(domain)+'-d_mem_actual'
                #k = str(domain)+'_mem_actual'
                k = 'mem_actual'
                dD[k]=d_mem_actual

                #k = 'virshcheck-domain-'+str(domain)+'-d_mem_update'
                #k = str(domain)+'_mem_update'
                k = 'mem_update'
                dD[k]=d_mem_update

                #k = 'virshcheck-domain-'+str(domain)+'-d_mem_rss'
                #k = str(domain)+'_mem_rss'
                k = 'mem_rss'
                dD[k]=d_mem_rss

                disks = runningDict.get('domains', {}).get(domain, {}).get('disk')
                for disk in disks:
                    d_disk_device           = runningDict.get('domains', {}).get(domain, {}).get('disk', {}).get(disk, {}).get('device')
                    d_disk_bytes_read       = runningDict.get('domains', {}).get(domain, {}).get('disk', {}).get(disk, {}).get('bytes_read')
                    d_disk_bytes_written    = runningDict.get('domains', {}).get(domain, {}).get('disk', {}).get(disk, {}).get('bytes_written')
                    d_disk_errors           = runningDict.get('domains', {}).get(domain, {}).get('disk', {}).get(disk, {}).get('number_of_errors')
                    d_disk_read_requests    = runningDict.get('domains', {}).get(domain, {}).get('disk', {}).get(disk, {}).get('read_requests_issued')
                    d_disk_write_requests   = runningDict.get('domains', {}).get(domain, {}).get('disk', {}).get(disk, {}).get('write_requests_issued')

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(disk)+'-d_disk_device'
                    #k = str(domain)+'_'+str(disk)+'_device'
                    k = str(disk)+'_device'
                    dD[k]=d_disk_device

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(disk)+'-d_disk_bytes_read'
                    #k = str(domain)+'_'+str(disk)+'_bytes_read'
                    k = str(disk)+'_bytes_read'
                    dD[k]=d_disk_bytes_read

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(disk)+'-d_disk_bytes_written'
                    #k = str(domain)+'_'+str(disk)+'_bytes_written'
                    k = str(disk)+'_bytes_written'
                    dD[k]=d_disk_bytes_written

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(disk)+'-d_disk_errors'
                    #k = str(domain)+'_'+str(disk)+'_errors'
                    k = str(disk)+'_errors'
                    dD[k]=d_disk_errors

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(disk)+'-d_disk_read_requests'
                    #k = str(domain)+'_'+str(disk)+'_read_requests'
                    k = str(disk)+'_read_requests'
                    dD[k]=d_disk_read_requests

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(disk)+'-d_disk_write_requests'
                    #k = str(domain)+'-'+str(disk)+'_write_requests'
                    k = str(disk)+'_write_requests'
                    dD[k]=d_disk_write_requests



                nets = runningDict.get('domains', {}).get(domain, {}).get('net')
                for net in nets:
                    d_net_mac           = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('mac')
                    d_net_bridge        = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('bridge')
                    d_net_read_bytes    = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('read_bytes')
                    d_net_write_bytes   = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('write_bytes')
                    d_net_read_drops    = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('read_drops')
                    d_net_write_drops   = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('write_drops')
                    d_net_read_errors   = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('read_errors')
                    d_net_write_errors  = runningDict.get('domains', {}).get(domain, {}).get('net', {}).get(net, {}).get('write_errors')

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_mac'
                    #k = str(domain)+'_'+str(net)+'_mac'
                    k = str(net)+'_mac'
                    dD[k]=d_net_mac

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_bridge'
                    #k = str(domain)+'_'+str(net)+'_bridge'
                    k = str(net)+'_bridge'
                    dD[k]=d_net_bridge

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_read_bytes'
                    #k = str(domain)+'_'+str(net)+'_read_bytes'
                    k = str(net)+'_read_bytes'
                    dD[k]=d_net_read_bytes

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_write_bytes'
                    #k = str(domain)+'_'+str(net)+'_write_bytes'
                    k = str(net)+'_write_bytes'
                    dD[k]=d_net_write_bytes

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_read_drops'
                    #k = str(domain)+'_'+str(net)+'_read_drops'
                    k = str(net)+'_read_drops'
                    dD[k]=d_net_read_drops

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_write_drops'
                    #k = str(domain)+'_'+str(net)+'_write_drops'
                    k = str(net)+'_write_drops'
                    dD[k]=d_net_write_drops

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_read_errors'
                    #k = str(domain)+'_'+str(net)+'_read_errors'
                    k = str(net)+'_read_errors'
                    dD[k]=d_net_read_errors

                    #k = 'virshcheck-domain-'+str(domain)+'-'+str(net)+'-d_net_write_errors'
                    #k = str(domain)+'_'+str(net)+'_write_errors'
                    k = str(net)+'_write_errors'
                    dD[k]=d_net_write_errors

    #if domains ###########
        #for domain ###########
            #####

            prom = ''
            c = len(dD)
            for k,v in dD.items():
                c -= 1
                if c == 0:
                    prom += str(k) + '="' + str(v) + '"'
                else:
                    prom += str(k) + '="' + str(v) + '",'

            _key = 'virshcheck-domain-' + str(domain)
            gDict[_key] = [ 'sentinel_job_kvm_domain{' + prom + '} ' + str(val) ]

    return True

def http_post(url, dataDict):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication
    # Bearer https://datatracker.ietf.org/doc/html/rfc6750
    # dataDict = { 'uuid': uuid }

    uuid = dataDict.get('uuid', None)

    encoded_token = base64.b64encode(str(uuid).encode('utf-8')).decode('utf-8')

    response = requests.post(url=url,
                             headers={'Content-Type': 'application/json',
                                      'Authorization': 'Bearer ' + str(encoded_token)},
                             json=json.dumps(dataDict),
                             verify=False,
                             timeout=10
                            )
    response_code = response.status_code

    return response, response_code

def RClient(name, db_store):
    _name = name
    _gDict = {}
    return RemoteClient(name, db_store, _gDict, _name, verbose=True)

def RemoteClient(name, db_store, gDict, _name, verbose=False):
    #print(_name) remote-client-2

    post = None
    data = {}
    code = None

    rpost = None
    rdata = {}
    rcode = None

    _uuid = None
    _url = None

    output = None
    exitcode = 99

    #get uid and url
    # read the job table Sentry Job run remote-client-1 and remote-client-2
    # config get name remote-client-2

    jobs = store.selectAll('jobs', db_store)
    for job in jobs:
        #print(job[0]) # remote-client-2
        if job[0] == name:
            #print('get conf job ' + str(name) + ' now...')
            jconf = json.loads(job[2])
            _uuid = jconf.get('uuid', None)
            _url  = jconf.get('url', None)


    if verbose:
        print('_uuid ' + str(_uuid))
        print('_url ' + str(_url))

    d = { 'uuid': _uuid }

    #try:
    post, code = http_post(_url, d)

    if verbose:
        print('post ' + str(post))
        print('code ' + str(code))

        #if code == 200:
        #    data = post.json()
        #else:
        #    data = post
    #except Exception as e:
    #    post = None
    #    code = 99
        #data = { 'error': str(e) }

    #print('post ' + str(post))
    try:
        data = post.json()
    except requests.exceptions.JSONDecodeError as e:
        #data = { 'json_error': str(e) }
        data = { 'request_error': str(post) }

    try:
        command = data.get('command', None)
    except AttributeError:
        command = None
    try:
        timeout = data.get('timeout', 10)
    except AttributeError:
        timeout = 10


    if command:
        token_bytes = base64.b64decode(command)
        untoken = token_bytes.decode('utf-8')

        try:
            proc = Popen(untoken, stdout=PIPE, stderr=PIPE, shell=True)
            output = proc.communicate(timeout=timeout)
            exitcode = proc.returncode

        except TimeoutExpired as e:
            output = str(e)
            exitcode = 4

    if command and output:
        encoded_output = base64.b64encode(str(output[0].decode('utf-8')).encode('utf-8')).decode('utf-8')
        rd = { 'uuid': _uuid, 'command': command, 'output': encoded_output, 'exitcode': exitcode }

        #try:
        rpost, rcode = http_post(_url, rd)

        try:
            rdata = rpost.json()
        except requests.exceptions.JSONDecodeError as e:
            rdata = { 'request_error': str(rpost) }


            #if rcode == 200:
            #    rdata = rpost.json()
            #else:
            #    rdata = rpost

            #rdata = rpost.json()

        #except Exception as e:
        #    rpost = None
        #    rdata = { 'error': str(e) }
        #    rcode = 100


    rDct = {'post': promDataSanitizer(str(data)),
            'code': str(code),
            'rpost': promDataSanitizer(str(rdata)),
            'rrcode': str(rcode),
           }
    _key = 'remoteclient-' + str(name)

    rDct['sentinel_job'] = name
    val = 1

    prom = ''
    c = len(rDct)
    for k,v in rDct.items():
        c -= 1
        if c == 0:
            prom += str(k) + '="' + str(v) + '"'
        else:
            prom += str(k) + '="' + str(v) + '",'

    if verbose:
        print(prom)

    gDict[_key] = [ 'sentinel_job_output{' + prom + '} ' + str(val) ]
    return True


options = {
 'vuln-scan' : vulnScan,
 'port-scan' : portScan1,
 'port-scan2' : portScan2,
 #'detect-scan' : detectScan,
 'net-scan' : netScanProc,
 'fim-check' : fimCheck,
 'ps-check' : psCheck,
 'established-check' : establishedCheck,
 'kvm-check' : kvmCheck,
 'remote-client' : RemoteClient,
 #'rclnt-run' : rclntRun,
}
#options[sys.argv[2]](sys.argv[3:])

def runJob(name, db_store, gDict):

    fail = False

    #-start
    val = 0
    start = time.strftime("%Y-%m-%d %H:%M:%S")

    job = store.getJob(name, db_store)
    if not job:
        return None

    if type(job) == tuple:
        job = job[0]

    try:
        jdata = json.loads(job)
    except json.decoder.JSONDecodeError:
        logging.error('invalid json')
        return None

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
    try:
        #del new_json['error']
        del jdata['error']
    except KeyError: pass

    prom = ''
    c = len(jdata)
    for k,v in jdata.items():
        c -= 1
        if c == 0:
            prom += str(k) + '="' + str(v) + '"'
        else:
            prom += str(k) + '="' + str(v) + '",'

    gDict[name] = [ 'sentinel_job{' + prom + '} ' + str(val) ]
    replace = store.replaceINTO('jobs', name, json.dumps(jdata), db_store)

    _job = jdata.get('job', None) 
    _ips = jdata.get('ips', None) 
    _config = jdata.get('config', None) 

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
        run = 'Unknown job ' + str(_job)
        logging.error(run)
        fail = True
    except Exception as e:
        run = 'Exception job ' + str(_job) + ' ' + str(e)
        logging.error(run)
        fail = True

    #-done
    done = time.strftime("%Y-%m-%d %H:%M:%S")
    jdata['done'] = done

    if fail:
        jdata['success'] = 'Fail'
        jdata['error'] = run
        val = 0
    else:
        jdata['success'] = run
        val = 1

    #if run is True:
    #    val = 1
    #else:
    #    val = 0

    #update = updateJobsJson(name, json.dumps(new_json), db_store)

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

    logging.info('Sentry Job run ' + str(name))

    return run

def getDuration(_repeat):
    #amt, scale = getDuration(_repeat)
    #5min, 1hour, 3day
    #import re

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

def sentryProcessor(db_store, gDict, interval):
    logging.info('Sentry Processor')

    # run this every X

    _prom = str(db_store) + '.prom'

    #while (sigterm == False):
    c=0
    while not exit.is_set():
        try:
            with open(_prom, 'w+') as _file:
                for k,v in gDict.items():
                    for item in v:
                        _file.write(item + '\n')

        #except BrokenPipeError as e:
        #except (KeyboardInterrupt, SystemExit, Exception, BrokenPipeError) as e:
        except Exception as e:
            logging.critical('sentryProcessor sigterm True ' + str(e))
            exit.set()
            break

        #time.sleep(10)
        #time.sleep(interval)
        for i in range(interval):
            try:
                time.sleep(1)
            except Exception as e:
                logging.critical('break.sentryProcessor ' + str(e))
                exit.set()
                break
        c+=1
        if c > 5:
            c=0
        #print(str(c))

    return True

def apiProcessor(db_store, api_Dict, interval):
    logging.info('Sentry API Processor')

    # run this every X

    _prom = str(db_store) + '.api_server.prom'

    #while (sigterm == False):
    c=0
    while not exit.is_set():
        try:
            with open(_prom, 'w+') as _file:
                for k,v in api_Dict.items():
                    for item in v:
                        _file.write(item + '\n')

        #except BrokenPipeError as e:
        #except (KeyboardInterrupt, SystemExit, Exception, BrokenPipeError) as e:
        except Exception as e:
            logging.critical('sentry API Processor sigterm True ' + str(e))
            exit.set()
            break

        #time.sleep(10)
        #time.sleep(interval)
        for i in range(interval):
            try:
                time.sleep(1)
            except Exception as e:
                logging.critical('break.sentry API Processor ' + str(e))
                exit.set()
                break
        c+=1
        if c > 5:
            c=0
        #print(str(c))

    return True


def sentryProcessJobs(db_store, gDict):
    run = None

    rLst = []

    jobs = store.selectAll('jobs', db_store)
    if jobs is None:
        return None

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    now_time = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")

    for job in jobs:
        name = job[0]
        jdata = job[2]
        try:
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

            if now_time > run_time and _start is None:
                run = runJob(name, db_store, gDict)

        if _repeat:
            scale, amt = getDuration(_repeat)

            if _start is None:
                run = runJob(name, db_store, gDict)

            else:
                start_time = datetime.datetime.strptime(_start, "%Y-%m-%d %H:%M:%S")
                if _done:
                    done_time = datetime.datetime.strptime(_done, "%Y-%m-%d %H:%M:%S")

                    arg_dict = {scale:amt}
                    delta_time = done_time + datetime.timedelta(**arg_dict)

                    if now_time > delta_time:
                        run = runJob(name, db_store, gDict)
    return run

#def processD(List):
def processD(gDict, start):

    debug = False

    now = time.time()
    uptime = now - start
    #uptime = round(uptime, 1)
    #uptime = format(uptime,".1f")
    uptimef = format(uptime,".0f")

    #try:

    #sentinel_up = 1
    #promDATA = 'sentinel_up ' + str(sentinel_up)
    #gDict['sentinel_up'] = [ promDATA ]

    #c = 0
    #for item in List:
    #    c += 1
    #    k = 'sentinel_up_' + str(c)
    #    gDict[k] = [ item ]

    tcount = 0
    for thread in threading.enumerate():
        tcount += 1
        #print(str(thread.name))

    pcount = 0
    for proc in multiprocessing.active_children():
        pcount += 1
        #print(str(proc.name))

    #print('threading.stack_size ' + str(threading.stack_size()))
    #threading.current_thread().getName()

    #import resource
    #u_self = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    #u_all  = resource.getrusage(resource.RUSAGE_BOTH).ru_maxrss
    #print(u_self, u_all)

    #import resource
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    #rss_c = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss

    ru_utime = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    ru_stime = resource.getrusage(resource.RUSAGE_SELF).ru_stime

    #ru_inblock = resource.getrusage(resource.RUSAGE_SELF).ru_inblock
    #ru_oublock = resource.getrusage(resource.RUSAGE_SELF).ru_oublock

    #ru_msgsnd = resource.getrusage(resource.RUSAGE_SELF).ru_msgsnd
    #ru_msgrcv = resource.getrusage(resource.RUSAGE_SELF).ru_msgrcv

    #ru_nsignals = resource.getrusage(resource.RUSAGE_SELF).ru_nsignals

    #ru_nvcsw = resource.getrusage(resource.RUSAGE_SELF).ru_nvcsw
    #ru_nivcsw = resource.getrusage(resource.RUSAGE_SELF).ru_nivcsw

    total_rutime = ru_utime + ru_stime

    #print(str(total_rutime))
    #print(str(uptime))

    #calculate cpu
    try:
        cpu_usage = 100 * (total_rutime / uptime)
    except ZeroDivisionError as e:
        if debug: print('ZeroDivisionError ' + str(e))
        cpu_usage = -1

    cpu_u = format(cpu_usage,".2f")

    if debug: 
        print('rss         ' + str(rss))
        print('cpu         ' + str(cpu_u))


        #print('rss_c ' + str(rss))

        #print('ru_utime    ' + str(ru_utime))
        #print('ru_stime    ' + str(ru_stime))
        #print('ru_inblock  ' + str(ru_inblock))
        #print('ru_oublock  ' + str(ru_oublock))
        #print('ru_msgsnd   ' + str(ru_msgsnd))
        #print('ru_msgrcv   ' + str(ru_msgrcv))
        #print('ru_nsignals ' + str(ru_nsignals))
        #print('ru_nvcsw   ' + str(ru_nvcsw))
        #print('ru_nivcsw   ' + str(ru_nivcsw))

    #os.cpu_count()

    #promDATA = 'sentinel_app_info{version="' + __version__ + '",threads="'+str(tcount)+'",procs="'+str(pcount)+'"} 1.0'
    #gDict['sentinel_app_info'] = [ promDATA ]

# __version__

    promDATA = 'sentinel_up{version="'+ __version__ +'",threads="'+str(tcount)+'",procs="'+str(pcount)+'",cpu="'+str(cpu_u)+'",rss="'+str(rss)+'",uptime="'+str(uptimef)+'"} 1'
    gDict['sentinel_up'] = [ promDATA ]

    _arch = sys.implementation._multiarch
    _implementation = sys.implementation.name
    _major = str(sys.version_info.major)
    _minor = str(sys.version_info.minor)
    _micro = str(sys.version_info.micro)
    _releaselevel = sys.version_info.releaselevel
    _serial = sys.version_info.serial
    _version = _major + '.' + _minor + '.' + _micro

    promDATA = 'sentinel_python_info{arch="' + _arch + '",implementation="' + _implementation + '",major="' + _major + '",minor="' + _minor
    promDATA += '",micro="' + _micro + '",version="' + _version + '"} 1.0'
    gDict['sentinel_python_info'] = [ promDATA ]

    sqlite3_version = str(sqlite3.version)
    sqlite3_sqlite_version = str(sqlite3.sqlite_version)

    promDATA = 'sentinel_python_sqlite_info{sqlite3="' + sqlite3_version + '",library="' + sqlite3_sqlite_version + '"} 1.0'
    gDict['sentinel_python_sqlite_info'] = [ promDATA ]

    #except BrokenPipeError as e:
    #    logging.error('processD ' + str(e))
    #    return False

    #sz = sys.getsizeof(__main__)
    #print('sz ' + str(sz))
  
    #n = __name__
    #sz = __name__.__sizeof__()
    #print('sz ' + str(n) + ' ' + str(sz))

    return True

def processE(gDict, eDict, expire=864000): # i exist to expire

    debug = False
    verbose = False

    #print('process E in the house')
    #1h  is 60*60 (3600 seconds)
    #10d is 864000

    # as of python 3.7, "Dict keeps insertion order"
    # https://mail.python.org/pipermail/python-dev/2017-December/151283.html
    #first_item = gDict.get(next(iter(gDict)))
    #print(str(first_item)) # ['sentinel_up 1']

    #pickup sml
    try:
        sml = shared_memory.ShareableList(name='sentinel-update')
        #print('sml internal update ' + str(sml))

        for item in sml:
            if debug: print('debug. expiring ' + str(item))
            gDict.pop(item, None)

        #for i in range(0,len(sml),2):
        #    key = sml[i]
        #    val = sml[i+1]
        #    gDict.pop(key, None)
            
    except FileNotFoundError as e:
        if verbose: print('sml FileNotFoundError '+ str(e))
        pass

    ################################################################

    eL=[]
    for k,v in gDict.items():
        if k.startswith('sentinel_watch_syslog_rule_engine-'):
            #if verbose: print('Expire item: ' + str(k))
            eL.append(k)

        #put other custom here...
        #if k.startswith('sentinel_watch_syslog_rule_engine-'):
        #    eL.append(k)


    ################################################################

    #print('eL sz ' + str(len(eL)))
    if len(eL) > 0:
        #print('process eL')
        now = time.time()

        for _e in eL:

            if _e in eDict:
                #compare
                if int(now) > int(eDict[_e]):
                    #if debug: print('ExpireThis ' + str(_e) + ' expire '+str(expire)+' now '+str(int(now))+ ' eDict ' + str(int(eDict[_e])))
                    if debug: print('debug. ExpireThis ' + str(_e) + ' now '+str(int(now))+ ' eDict ' + str(int(eDict[_e])))
                    gDict.pop(_e, None)
            else:
                #add

                #get expire from prom data?
                _expire = promDataParser('expire', gDict[_e]) #may return None depends on the data

                if _expire:
                    if verbose: print('_expire via gDict ' + str(_expire))
                    end_time = now + int(_expire)
                else:
                    if debug: print('debug. DEFAULT expire via default ' + str(_expire) + ' '+str(expire) +' ' + str(_e))
                    end_time = now + expire

                #if debug: print('expire ' + str(_expire) + ' set ' +str(end_time))

                eDict[_e] = int(end_time)

    return True


def sentrySharedMemoryManager(gDict, eList, interval):
    logging.info('Sentry SharedMemoryManager')

    verbose = False
    debug = False

    while not exit.is_set():

        KeyList = []
        try:
            #for __k in gDict:
            for __k,__v in gDict.items():
                KeyList.append(__k)

                #print(str(type(__k))) #str
                #print(str(__k))
                #KeyList.append(__k)
                #v=gDict[__k]

                #if len(__v) == 1:
                #    KeyList.append(__v[0])
                #else:
                #    print('ERROR keylist')
                #    logging.error('keylist_error')
                #    KeyList.append('keylist_error')
                        
                #KeyList.append(__v[0])
                KeyList.append(__v[0] + '\n')

                #print(str(type(__v))) #lst
                #print(str(__v))
                #ValList.append(__v[0])

                #KeyList.append(str(__v[0]))
                #KeyList.append(__v[0])
                  

        except RuntimeError as e:
            if debug: logging.debug('debug. RuntimeError sentrySharedMemoryManager ' + str(e))
        except AttributeError as e:
            if debug: logging.debug('debug. AttributeError sentrySharedMemoryManager ' + str(e))

        klstsize = len(KeyList)
        smklsize = eList[0]

        try:
            smkl = shared_memory.ShareableList(KeyList, name='sentinel-shm')
            smklsize = len(smkl)
            eList.insert(0, smklsize)

        except FileExistsError as e:
            if verbose: print('FileExistsError ' + str(e))

            if klstsize != smklsize:
                if debug: print('debug. not equal ShareableList ' +str(klstsize)+' '+str(smklsize))

                #read
                smklr = shared_memory.ShareableList(name='sentinel-shm')
                smklr.shm.close()
                smklr.shm.unlink()

                #write
                smkl = shared_memory.ShareableList(KeyList, name='sentinel-shm')

                smklsize = len(smkl)
                eList.insert(0, smklsize)

        if debug: print('debug. klstsize '+str(klstsize)+' smklsize '+str(smklsize))

        time.sleep(interval)

    smkl = shared_memory.ShareableList(name='sentinel-shm')
    smkl.shm.close()
    smkl.shm.unlink()

    return True

##################################################################################
#from multiprocessing.managers import BaseManager
#class SharesClass:
#    def set(self, List):
#        return shared_memory.ShareableList(List, name='sentinel-keys')
#
#class sentrySMM(BaseManager):
#    pass
#
#sentrySMM.register('Shares', SharesClass)
#
#def getKeyList(gDict):
#    KeyList = []
#    for __k in gDict:
#        KeyList.append(__k)
#    return KeyList
###################################################################################
#from multiprocessing.shared_memory import SharedMemory
#def free_shared_memory(name):
#    try:
#        shared_memory = SharedMemory(name=name)
#        shared_memory.unlink()
#    except FileNotFoundError as e:
#        return None
#    return None
##################################################################################
#
#def sentrySharedMemoryManager_TEST(gDict, eList, interval):
#    print('init sentrySharedMemoryManager')
#
#    debug = True
#
#    smm = sentrySMM()
#    smm.start()
#    shares = smm.Shares()
#
#    KeyList = []
#
#    while not exit.is_set():
#
#        try:
#            KeyList = getKeyList(gDict)
#        except RuntimeError as e:
#            if debug: logging.debug('debug. RuntimeError sentrySharedMemoryManager ' + str(e))
#        except AttributeError as e:
#            if debug: logging.debug('debug. AttributeError sentrySharedMemoryManager ' + str(e))
#
#        klstsize = len(KeyList)
#        smklsize = eList[0]
#
#        if debug: print('debug. klstsize '+str(klstsize)+' smklsize '+str(smklsize))
#
#        if klstsize != smklsize:
#            #smklr = shared_memory.ShareableList(name='sentinel-keys')
#            free = free_shared_memory(name='sentinel-keys')
#            try:
#                shares.set(KeyList)
#                eList.insert(0, smklsize)
#            except FileExistsError as e:
#                if debug: print('debug. FileExistsError ' + str(e))
#
#        time.sleep(interval)
#
#    smm.shutdown()
#    return True



#def free_shared_memory(name) -> None:
#    shared_memory = SharedMemory(name=name)
#    shared_memory.unlink()

#def sentrySharedMemoryManager(gDict, eList, interval):
#    print('init sentrySharedMemoryManager')
#
#    debug = True
#
#    smm = sentrySMM()
#    smm.start()
#    shares = smm.Shares()
#
#    while not exit.is_set():
#
#        try:
#            KeyList = getKeyList(gDict)
#        except RuntimeError as e:
#            if debug: logging.debug('debug. RuntimeError sentrySharedMemoryManager ' + str(e))
#        except AttributeError as e:
#            if debug: logging.debug('debug. AttributeError sentrySharedMemoryManager ' + str(e))
#
#        try:
#            shares.set(KeyList)
#        except FileExistsError as e:
#            if debug: print('debug. FileExistsError ' + str(e))
#
#        time.sleep(interval)
#
#    smm.shutdown()



def promDataParser(promKey, promData):
    rtn = None

    #print('promData ' + str(type(promData))) #<class 'list'>
    if isinstance(promData, list):
        #print("its a list")
        promData = promData[0]
    #print('promData ' + str(type(promData))) #<class 'str'>
    #print('promData: ' + promData)
    #sentinel_watch_syslog_rule_engine{config="watch-syslog",rule="rule-X",b2sum="2ed2fc412bfa54650d00fc5092b06ea320abf563",seen="True",data="LQM-WiFi: (5G) txRTSFrm=24 {txUcast=16} { } rxACKUcast=7",expire="3600",date="2021-03-23 10:28:07"} 2
    #sentinel_watch_syslog_rule_engine{config="watch-syslog",rule="rule-t",b2sum="915d0fdf0b9b71fdfbb24d7e80702b0410836179",seen="False",data="WifiLoc, timer, sinceLastScanRequest, 300.4, lastScanRequestTimestamp, 639077012.2, erroredRequestType, 0, fIsActivelyScheduleWifiScans, 1",expire="30",date="2021-04-02 10:28:32"} 1

    data = promData

    try:

        data = data[data.find('{'):]
        data = data.lstrip('{')
        data = data[:data.rfind('}')] #right find!

        #data = data.split(',')  # commas in the data?
        data = data.split('",')

        #print(str(data))
        #data is a list now...
        for item in data:
            #key = item.split('=')[0]
            #val = item.split('=')[1] #if the val has '=' in it!
            i = item.split('=', 1) #max split 1
            key = i[0]
            val = i[1]

            #remove left and right quotes
            val = val.lstrip('"')
            val = val.rstrip('"')

            #print(key, val)
            #print(key)
            #print(val)
            if key == promKey:
                #print(key, val)
                rtn = val
    except IndexError as e:
        return None

    return rtn


def sentryScheduler(db_store, gDict, interval):
    logging.info('Sentry Scheduler')

    #run this every X

    c=0

    eDict={}
    #eList=[0]

    start = time.time()

    #while (sigterm == False):
    while not exit.is_set():

        try:
            job = threading.Thread(target=sentryProcessJobs, args=(db_store, gDict), name="SentryJobRunner")
            job.start()
        #except BrokenPipeError as e:
        #except (KeyboardInterrupt, SystemExit, Exception, BrokenPipeError) as e:
        except Exception as e:
            logging.critical('sentryProcessJobs thread ' + str(e))
            exit.set()
            job.join()
            break

        try:
            pd = processD(gDict, start)
        #except BrokenPipeError as e:
        #except (KeyboardInterrupt, SystemExit, Exception, BrokenPipeError) as e:
        except Exception as e:
            logging.critical('processD ' + str(e))
            exit.set()
            break

        #pe = processE(db_store, gDict, eDict, expire=864000)
        try:
            #pe = processE(gDict, eDict, eList, expire=864000)
            pe = processE(gDict, eDict, expire=864000)
        except RuntimeError as e:
            logging.error('sentryScheduler processE RuntimeError ' + str(e))
        #10d 864000
        #5d  432000
        #3d  259200
        #1d  86400
        #1h  3600
        #30s 30

        #time.sleep(3)
        #time.sleep(interval)

        #rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        #print('rss_t ' + str(rss))

        for i in range(interval):
            try:
                time.sleep(1)
            except Exception as e:
                logging.critical('break.sentryScheduler ' + str(e))
                exit.set()
                break

        c+=1
        if c > 5:
            #only run this every 5th...
            #pe = processE(gDict, eDict, expire=864000)
            c=0
        #print('c is ...' + str(c))

    return True


def sentryCleanup(db_store):

    exit.set()

    _prom = str(db_store) + '.prom'

    with open(_prom, "r") as _f:
        content = _f.read()

    with open(_prom + '.save', "w+") as _sf:
        _sf.write(content)

    with open(_prom, "w") as _cf:
        _cf.write('')


    for proc in multiprocessing.active_children():
        print('proc name ', proc, ' ', proc.pid)
        #os.kill(proc.pid, 9)
        proc.terminate()

    for thread in threading.enumerate():
        if thread.name == 'MainThread':
            continue
        else:
            print('thread name', thread, ' ', thread.name)
            thread.join()

    logging.info("Sentry Cleanup: True")
    return True


def procHTTPServer(port, metric_path, db_file):
    logging.info('Sentry start HTTPServer port: '+str(port)+' path: '+str(metric_path))
    global _metric_path
    _metric_path = metric_path

    global db_store
    db_store = db_file

    if os.getuid() == 0:
        run_as_user = "nobody"
        uid = pwd.getpwnam(run_as_user)[2]
        logging.info('Sentry HTTPServer Drop Privileges to uid ' + str(uid))
        os.setuid(uid)

    httpd = HTTPServer(('', port), HTTPHandler)
    return httpd.serve_forever()


def apiHTTPServer(port, api_path, db_file, key_file, cert_file, runuser, loglevel):
    #print('apiHTTP Server')

    # print(logging.root.level) # 30 default

    #print(logging.level)
    #logging.getLevelName(myLogger.level)
    #logging.info('Sentry start API HTTPServer port: '+str(port)+' path: '+str(api_path))

    if loglevel == 30:
        #print('loglevel 30 warning')
        logformat = 'sentinel %(asctime)s: %(message)s'
    else:
        logformat = 'sentinel %(asctime)s %(filename)s %(levelname)s: %(message)s'

    logging.basicConfig(datefmt='%b %d %H:%M:%S',
                        format=logformat,
                        level=loglevel)

    #print(logging.root.level) # 30 default

    #logger.log(logging.root.level, 'Sentry start API HTTPServer port: '+str(port)+' path: '+str(api_path))
    #logger.log(logging.root.level, 'Sentry start API HTTPServer port: '+str(port)+' path: '+str(api_path))
    logging.log(logging.root.level, 'Sentry start API HTTPServer port: '+str(port)+' path: '+str(api_path))

    global _api_path
    _api_path = api_path

    global db_store
    db_store = db_file

    #global gd_Dict
    #gd_Dict = gDict

    if os.getuid() == 0:
        #run_as_user = "nobody"
        run_as_user = runuser
        uid = pwd.getpwnam(run_as_user)[2]

        logging.info('Sentry API HTTPServer Drop Privileges to uid ' + str(uid))
        os.setuid(uid)

    global api_Dict
    api_manager = multiprocessing.Manager()
    api_Dict = api_manager.dict()

    global server_Dict
    server_manager = multiprocessing.Manager()
    server_Dict = server_manager.dict()

    api_processor = threading.Thread(target=apiProcessor, args=(db_store, api_Dict, 10), name="APIProcessor")
    api_processor.start()

    httpd = HTTPServer(('', port), APIHTTPHandler)
    #import ssl
    #print('httpd.HTTPServer ' + str(port))
    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   keyfile=key_file,
                                   certfile=cert_file,
                                   server_side=True)
    # openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -sha256 -nodes -days 3650 -subj '/CN=localhost'
    return httpd.serve_forever()





# function to return key for any value
#def get_key(_dct, val):
#    for key, value in _dct.items():
#         if val == value:
#             return key
#    return None #"key doesn't exist"

#def signal_handler(signal, frame):
#    print("\nprogram exiting gracefully")
#    sys.exit(0)

#def quit(signo, _frame):
#    print("Interrupted by %d, shutting down" % signo)
#    exit.set()

def sentrySIGHUP(signum, stack):
    logging.error('Sentry SIGHUP ' + str(signum))
    return True

#def sentrySIGINT(signum, stack):
#    logging.error('sentrySIGINT')
#    exit.set()
#    return True


#############################################################################################################################

#from multiprocessing.shared_memory import SharedMemory
#MEMORY_NAME = "sentinel"
#def create_shared_memory(name: str, size: int) -> None:
#    SharedMemory(MEMORY_NAME.format(name=name), create=True, size=size)
#def free_shared_memory(name: str) -> None:
#    shared_memory = SharedMemory(MEMORY_NAME.format(name=name))
#    shared_memory.unlink()


#def setExpiregDictKeyFile(_key, db_store):
#    expire_file = db_store + '.expire'
#    with open(expire_file, 'a+') as _file:
#        _file.write(_key + '\n')
#    return True


exit = threading.Event()

def sentryMode(db_store, verbose=False):

    logformat = 'sentinel %(asctime)s %(filename)s %(levelname)s: %(message)s'
    datefmt = "%b %d %H:%M:%S"

    # python default level is WARNING
    # loglevel = logging.INFO

    if verbose:
        #print(verbose)
        if verbose.lower() == 'debug':
            loglevel = logging.DEBUG
        elif verbose.lower() == 'info':
            loglevel = logging.INFO
        elif verbose.lower() == 'warning':
            loglevel = logging.WARNING
            logformat = 'sentinel %(asctime)s: %(message)s'
        elif verbose.lower() == 'error':
            loglevel = logging.ERROR
        elif verbose.lower() == 'critical':
            loglevel = logging.CRITICAL
        else:
            loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
        logformat = 'sentinel %(asctime)s: %(message)s'

    logging.basicConfig(level=loglevel,
                        format=logformat,
                        datefmt=datefmt,
                        handlers=[
                            #logging.FileHandler("sentinel.log"),
                            logging.StreamHandler(sys.stdout)
                        ]
                       )


    #logging.critical("Sentry critical") # 50
    #logging.error("Sentry error")       # 40
    #logging.warning("Sentry warning")   # 30
    #logging.info("Sentry info")         # 20
    #logging.debug("Sentry debug")       # 10
    #logging.notset("Sentry notest")     #  0

    #print(logging.root.level)

    logging.log(30, "Sentry Startup")
    logging.info("Sentry Logging " + str(loglevel))

    manager = multiprocessing.Manager()
    gDict = manager.dict()

    signal.signal(signal.SIGHUP, sentrySIGHUP)

    eList=[0]

    sharedmmgr = threading.Thread(target=sentrySharedMemoryManager, args=(gDict, eList, 1), name="SharedMemoryManager")
    sharedmmgr.start()

    scheduler = threading.Thread(target=sentryScheduler, args=(db_store, gDict, 5), name="Scheduler")
    scheduler.start()

    processor = threading.Thread(target=sentryProcessor, args=(db_store, gDict, 10), name="Processor")
    processor.start()


    cDct={}
    configs = store.selectAll('configs', db_store)
    for config in configs:
        #print(config[0], config[1], config[2])
        config_ = json.loads(config[2])
        cDct[config[0]] = config_.get('config', None)

    for key,conf in cDct.items():

        #if conf == 'remote_client':
        #    remote_client = True
        #    _config = json.loads(store.getData('configs', key, db_store)[0])
        #    _uuid = _config['uuid']
        #    _url = _config['url']

        if conf == 'api_server':
            #api_server = True
            #print('api_server: True!')
            _config = json.loads(store.getData('configs', key, db_store)[0])
            _port = _config['port']
            _api_path = _config['path']

            _keyfile  = _config['keyfile']
            _certfile = _config['certfile']

            try:
                _runuser  = _config['user']
            except KeyError:
                _runuser = 'nobody'

            #p = multiprocessing.Process(target=apiHTTPServer, args=(_port, _api_path, db_store, _keyfile, _certfile, gDict))
            p = multiprocessing.Process(target=apiHTTPServer, args=(_port, _api_path, db_store, _keyfile, _certfile, _runuser, loglevel))
            p.start()

            #api_processor = threading.Thread(target=apiProcessor, args=(db_store, gDict, 10), name="Processor")
            #api_processor.start()

        if conf == 'http_server':
            #http_server = True
            _config = json.loads(store.getData('configs', key, db_store)[0])
            _port = _config['port']
            _metric_path = _config['path']

            p = multiprocessing.Process(target=procHTTPServer, args=(_port, _metric_path, db_store))
            p.start()

        if conf == 'logstream':
            logstream = multiprocessing.Process(target=sentryLogStream, args=(db_store, key, gDict, verbose))
            logstream.start()
            #running.append(tailer)

        if conf == 'tail':
            tailer = multiprocessing.Process(target=sentryLogTail, args=(db_store, key, gDict, verbose))
            tailer.start()
            #running.append(tailer)

        if conf == 'pushgateway':
            pushgw = multiprocessing.Process(target=sentryPushGateway, args=(db_store, key, gDict, verbose))
            pushgw.start()
            #running.append(tailer)


    loop = asyncio.get_event_loop()
    try:

        logging.info("Sentry Daemon")
        loop.run_forever()

        print('pid ' + str(os.getpid()))
        #sys.exit(99)

    except (KeyboardInterrupt, SystemExit, Exception):
        exit.set()
        sentryCleanup(db_store)
        loop.close()

        try:
            smklr = shared_memory.ShareableList(name='sentinel-shm')
            smklr.shm.close()
            smklr.shm.unlink()
        except FileNotFoundError:
            pass

        logging.info("Sentry Shutdown: " + str(exit.is_set()))
        #sys.exit(1)

    #return True
    return 'sentry.loop'


if __name__ == '__main__':
# requires cli tools: arp, ping, lsof, nslookup, nmap, tail
    pass


