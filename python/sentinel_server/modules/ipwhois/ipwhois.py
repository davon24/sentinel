#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests

def ipwhois_iplocation(ipaddr):
    """get: iplocation.net/?ip=."""
    # https://api.iplocation.net/?ip=8.8.8.8
    _url = "https://api.iplocation.net/?ip=" + str(ipaddr)
    response = requests.get(_url)
    return response.json()


def ipwhois_ipapi(ipaddr):
    """get: ip-api.com/json/24.48.0.1"""
    # http://ip-api.com/json/24.48.0.1
    _url = "http://ip-api.com/json/" + str(ipaddr)
    response = requests.get(_url)
    return response.json()


if __name__ == '__main__':

    if sys.argv[1:]:

        ip = sys.argv[1]

        whois = ipwhois_iplocation(ip)

        print(whois)


    else:
        print('Usage: ' + sys.argv[0] + ' ip.addr')


