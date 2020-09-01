#!/usr/bin/env python3

__version__ = 'v0.0.0'

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


def update_arp_data(db_file):

    arpDict = getArps()

    #db = 'db/sentinel.db'
    #if not os.path.isfile(db):
    #    conn = sqlite3.connect(db) 
    #    cur = conn.cursor()
    #    cur.execute('''CREATE TABLE IF NOT EXISTS arp (mac TEXT NOT NULL,ip TEXT,data TEXT);''')
    #    cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_mac ON arp (mac);''')
    #else:
    #    conn = sqlite3.connect(db) 
    #    cur = conn.cursor()

    conn = db.sql_connection(db_file)
    cur = conn.cursor()

    for ip,mac in arpDict.items():

        if mac == '(incomplete)':
            #print('SKIP (incomplete) ' + ip)
            #check if leftover ip,
            cur.execute("SELECT mac,ip FROM arp WHERE ip LIKE '%" + ip + "%'")
            rows = cur.fetchall()
            for row in rows:
                _mac = row[0]
                line = row[1].split(',')
                #print('Match.This.Row ' + str(line))
                line.remove(ip) #remove doesn't return anything, it modifies existing list in place
                #print('new list ', line)
              
                l = ''
                c = len(line)
                for i in line:
                    #print(c, i)
                    if c == 1:
                        l = l + i
                    else:
                        l =  i + ',' + l
                    c -= 1

                #print(l)
                cur.execute("UPDATE arp SET ip=? WHERE mac=?", (l, _mac))
                conn.commit()
                print('updated2 ' + str(_mac) + ' ' + str(l))
            continue #print('SKIP (incomplete)')

        cur.execute("SELECT ip FROM arp WHERE mac='" + mac + "'")
        #_mac, _ip = cur.fetchone()
        _result = cur.fetchone()
        #print(_mac, _ip, _data)
        if not _result:
            data = '{"created":"' + time.strftime("%Y-%m-%dT%H:%M:%SZ") + '"}'
            cur.execute("INSERT INTO arp VALUES (?, ?, ?)", (mac, ip, data))
            conn.commit()
            print('new ' + str(mac) + ' ' + str(ip))
        else:
            #print(ip, _result[0]) #tuple _result
            if ip not in _result[0]:
                #print(len(_result[0]))
                if len(_result[0]) == 0:
                    _ip = ip + _result[0]
                else:
                    _ip = ip + ',' + _result[0] #csv

                #if len(_result[0]) > 0:
                #    _ip = ip + ',' + _result[0] #csv
                #else:
                #    _ip = ip + _result[0]

                cur.execute("UPDATE arp SET ip=? WHERE mac=?", (_ip, mac))
                conn.commit()
                print('updated1 ' + str(mac) + ' ' + str(_ip))
    return True
    ##########################################################

def get_manuf(mac):
    db_file = 'db/manuf'
    mac = mf.even_up(mac.lower())
    manufDict = mf.get_manufDict(db_file)
    manuf = mf.match(mac, manufDict)
    return manuf



if __name__ == '__main__':

    update = update_arp_data('db/sentinel.db')

    if sys.argv[1:]:
        if sys.argv[1] == "manuf":
            mac = sys.argv[2]
            m = get_manuf(mac)
            print(m)
        #if sys.argv[1] == "update_manuf_db":
            




