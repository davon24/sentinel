#!/usr/bin/env python3

import sys
import json

def usage():
    print("""Usage: {0} [create|check] files.json 

        create files.json
        check files.json

    """.format(sys.argv[0]))


from hashlib import blake2b, blake2s
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

def run_check(jfile):
    with open(jfile, 'r') as jsonfile:
        jdata = json.load(jsonfile)

    for k,v in jdata.items():
        b = b2sum(k)
        if b != v:
            print(k + ' CHANGED')

def run_create(jfile):
    with open(jfile, 'r') as jsonfile:
        jdata = json.load(jsonfile)

    for k,v in jdata.items():
        b = b2sum(k)
        print(k + ' ' + b)
        jdata[k] = b

    with open(jfile, 'w') as jsonfile:
        json.dump(jdata, jsonfile, indent=4)


if __name__ == '__main__':
    if sys.argv[1:]:
        if sys.argv[2] and sys.argv[1] == "create":
            run_create(sys.argv[2])
        elif sys.argv[2] and sys.argv[1] == "check":
            run_check(sys.argv[2])
        else:
            usage()
    else:
        usage()



