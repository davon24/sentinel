#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import uuid
import json
import base64

import subprocess
from subprocess import Popen, PIPE, STDOUT
#from subprocess import Popen, PIPE, STDOUT, check_output
#import subprocess

import requests

import store

def http_post(url, uuid):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication
    # Bearer https://datatracker.ietf.org/doc/html/rfc6750

    json_dict = { 'uuid': uuid }

    encoded_token = base64.b64encode(str(uuid).encode()).decode()

    response = requests.post(url=url,
                             headers={'Content-Type': 'application/json',
                                      'Authorization': 'Bearer ' + str(encoded_token)},
                             json=json.dumps(json_dict)
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
                remote_client = True
                _config = json.loads(store.getData('configs', key, db_file)[0])
                _uuid = _config['uuid']
                _url = _config['url']


        print(remote_client)
        print(_uuid)
        print(_url)

        #sys.exit(1)

        post, rcode = http_post(_url, _uuid)
        try:
            #data = json.dumps(post.json())
            data = post.json()
        except requests.exceptions.JSONDecodeError as e:
            print('Error ' + str(e))
            data = post

        #print(post.json(), rcode)
        print(data, rcode)

        #print(data.get('command', None))
        command = data.get('command', None)

#subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None)

        if command:
            print('run command...')
            seconds = 3
            try:
                proc = Popen(command.split(), stdout=PIPE, stderr=PIPE)
                output = proc.communicate(timeout=seconds)
                exitcode = proc.returncode

            except subprocess.TimeoutExpired as error_timeout:
                output = str(error_timeout)
                exitcode = 4

            except FileNotFoundError as error_filenotfound:
                output = str(error_filenotfound)
                exitcode = 1


        print(output)
        print(exitcode)


    else:
        #print('Usage: ' + sys.argv[0] + ' http://127.0.0.1:8081/api/post')
        print('Usage: ' + sys.argv[0] + ' db_file')



