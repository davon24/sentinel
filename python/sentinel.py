#!/usr/bin/env python3

__version__ = 'v0.0.0b'

import os
from subprocess import Popen, PIPE
import sys
import sqlite3
import time

import db.manuf as mf
import db.store as db

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

def get_manuf(mac):
    manuf = mf.get_manuf(mac, 'db/manuf')
    return manuf

if __name__ == '__main__':

    db_file = 'db/sentinel.db'

    arpDict = getArps()
    update = db.update_arp_data(db_file, arpDict)
    #print(update)

    if sys.argv[1:]:
        if sys.argv[1] == "manuf":
            mac = sys.argv[2]
            m = get_manuf(mac)
            print(m)
        if sys.argv[1] == "list":
            db.print_all(db_file)
            

