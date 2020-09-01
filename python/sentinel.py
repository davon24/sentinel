#!/usr/bin/env python3

__version__ = 'v0.0.0d'

import os
from subprocess import Popen, PIPE

import sys
sys.path.insert(0,'db')

import sqlite3
import time

#import db.manuf as mf
#import db.store
from db import store

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

#def get_manuf(mac):
#    manuf = mf.get_manuf(mac, 'db/manuf')
#    return manuf

#def update_data_manuf(mac, db_file):
#    manuf = get_manuf(mac)
#    update = db.update_data_manuf(mac, manuf, db_file)
#    return update

if __name__ == '__main__':

    db_file = 'db/sentinel.db'

    arpDict = getArps()
    update = store.update_arp_data(db_file, arpDict)
    #print(update)

    if sys.argv[1:]:
        if sys.argv[1] == "manuf":
            mac = sys.argv[2]
            #m = get_manuf(mac)
            #print(m)
        if sys.argv[1] == "list":
            db.print_all(db_file)
        if sys.argv[1] == "update-manuf":
            mac = sys.argv[2]
            #update = update_data_manuf(mac, db_file)
            #print(update)
            

