#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import uuid
import json
import base64
from subprocess import Popen, PIPE, TimeoutExpired

import requests

import store

def http_post(url, data_dict):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication
    # Bearer https://datatracker.ietf.org/doc/html/rfc6750

    #json_dict = { 'uuid': uuid }

    uuid = data_dict.get('uuid', None)

    encoded_token = base64.b64encode(str(uuid).encode('utf-8')).decode('utf-8')

    response = requests.post(url=url,
                             headers={'Content-Type': 'application/json',
                                      'Authorization': 'Bearer ' + str(encoded_token)},
                             json=json.dumps(data_dict)
                            )
    response_code = response.status_code

    return response, response_code

    


if __name__ == '__main__':

    if sys.argv[1:]:

        db_file = sys.argv[1]

        configs = store.selectAll('configs', db_file)
        cDct={}
        for config in configs:
            #print(config[0], config[1], config[2])
            config_ = json.loads(config[2])
            cDct[config[0]] = config_.get('config', None)

        for key,conf in cDct.items():
            if conf == 'remote_client':
                #remote_client = True
                _config = json.loads(store.getData('configs', key, db_file)[0])
                _uuid = _config['uuid']
                _url = _config['url']


        #print(remote_client)
        print(_uuid)
        print(_url)

        #sys.exit(1)

        d = { 'uuid': _uuid }

        post, code = http_post(_url, d)
        try:
            #data = json.dumps(post.json())
            data = post.json()
        except requests.exceptions.JSONDecodeError as e:
            print('Error ' + str(e))
            data = post

        #print(post.json(), rcode)
        print(data, code)

        #print(data.get('command', None))
        command = data.get('command', None)
        timeout = data.get('timeout', 10)
        
        output = None
        exitcode = 99

        if command:
            print('run command...')
            #seconds = 3

            token_bytes = base64.b64decode(command)
            untoken = token_bytes.decode('utf-8')
            print(untoken)

            try:
                proc = Popen(untoken.split(), stdout=PIPE, stderr=PIPE)
                output = proc.communicate(timeout=timeout)
                exitcode = proc.returncode

            except TimeoutExpired as error_timeout:
                output = str(error_timeout)
                exitcode = 4

            except FileNotFoundError as error_filenotfound:
                output = str(error_filenotfound)
                exitcode = 1


        print(str(type(output[0].decode('utf-8'))))
        print(output[0].decode('utf-8'))

        #print(str(type(output.decode('utf-8'))))
        #print(output.decode('utf-8'))

        #print(output.decode('utf-8'))
        #print(exitcode)

        if command and output:
            #encoded_output = base64.b64encode(str(output).encode('utf-8')).decode('utf-8')
            encoded_output = base64.b64encode(str(output[0].decode('utf-8')).encode('utf-8')).decode('utf-8')
            rd = { 'uuid': _uuid, 'command': command, 'output': encoded_output, 'exitcode': exitcode }
            rpost, rcode = http_post(_url, rd)
            try:
                rdata = rpost.json()
            except requests.exceptions.JSONDecodeError as e:
                print('Error ' + str(e))
                rdata = rpost

            print(rdata, rcode)

        #print(post.json(), rcode)
        #print(data, code)
        #print(rdata, rcode)



    else:
        #print('Usage: ' + sys.argv[0] + ' http://127.0.0.1:8081/api/post')
        print('Usage: ' + sys.argv[0] + ' db_file')



