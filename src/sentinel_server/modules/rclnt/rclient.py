#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import uuid


def http_post(url):

    #uuid_var = '12345678'
    #uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org')
    #string_data = 'python.org'

    #string_data = uuid.getnode()
    #print(string_data)

    #uuid_var = uuid.uuid3(uuid.NAMESPACE_DNS, string_data)

    uuid_var = uuid.uuid4()

    print(uuid_var)

    data = '{"uuid":"' + str(uuid_var) + '"}'

    try:
        response = requests.post(url=url, json=data, headers={'Content-Type': 'application/json'})
        response_code = response.status_code

    except requests.exceptions.RequestException as e:
        #print('requests.exceptions.RequestException ' + str(e))
        logging.error('requests.exceptions.RequestException ' + str(e))
        response = str(e)
        response_code = 0

    return response, response_code

    


if __name__ == '__main__':

    if sys.argv[1:]:

        url = sys.argv[1]

        post,rcode = http_post(url)

        print(post.json(), rcode)


    else:
        print('Usage: ' + sys.argv[0] + ' http://127.0.0.1:8081/api/post')



