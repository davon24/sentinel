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

    #uuid_var = uuid.uuid4()
    #uuid_var = uuid.uuid1()

    uuid_var = '65724b0c-3796-11ed-9388-be25de1b53ca'

    print(uuid_var)

    data = '{"uuid":"' + str(uuid_var) + '"}'

    #username = 'test1'
    #password = 'test1'
                                 #auth=requests.auth.HTTPBasicAuth(username, password),

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication
    # Bearer https://datatracker.ietf.org/doc/html/rfc6750

#    try:


    import base64
    encoded_token = base64.b64encode(str(uuid_var).encode()).decode()

    response = requests.post(url=url,
                             headers={'Content-Type': 'application/json',
                                      'Authorization': 'Bearer ' + str(encoded_token)},
                             json=data
                            )
    response_code = response.status_code

                         #auth=requests.auth.HTTPBasicAuth('username', 'password'),

    #except requests.exceptions.RequestException as e:
    #    #print('requests.exceptions.RequestException ' + str(e))
    #    logging.error('requests.exceptions.RequestException ' + str(e))
    #    response = response + str(e)
    #    response_code = 0

#    except requests.exceptions.JSONDecodeError as e:
#        logging.error('requests.exceptions.JSONDecodeError ' + str(e))
#        response = response + str(e)


    return response, response_code

    


if __name__ == '__main__':

    if sys.argv[1:]:

        url = sys.argv[1]

        post,rcode = http_post(url)

        try:
            data = post.json()
        except requests.exceptions.JSONDecodeError as e:
            print('Error ' + str(e))
            data = post

        #print(post.json(), rcode)
        print(data, rcode)


    else:
        print('Usage: ' + sys.argv[0] + ' http://127.0.0.1:8081/api/post')



