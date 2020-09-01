#!/usr/bin/env python3

import sqlite3
import os
import time
import json

def sql_connection(db_file):

    if not os.path.isfile(db_file):
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS arp (mac TEXT PRIMARY KEY NOT NULL,ip TEXT,data TEXT);''')
        cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_mac ON arp (mac);''')
        con.commit()
    else:
        con = sqlite3.connect(db_file)

    return con

def update_arp_data(db_file, arpDict):

    con = sql_connection(db_file)
    cur = con.cursor()

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
                con.commit()
                print('updated2 ' + str(_mac) + ' ' + str(l))
            continue #print('SKIP (incomplete)')

        cur.execute("SELECT ip FROM arp WHERE mac='" + mac + "'")
        #_mac, _ip = cur.fetchone()
        _result = cur.fetchone()
        #print(_mac, _ip, _data)
        if not _result:
            data = '{"created":"' + time.strftime("%Y-%m-%dT%H:%M:%SZ") + '"}'
            cur.execute("INSERT INTO arp VALUES (?, ?, ?)", (mac, ip, data))
            con.commit()
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
                con.commit()
                print('updated1 ' + str(mac) + ' ' + str(_ip))
    return True

def select_all(db_file):
    con = sql_connection(db_file)
    cur = con.cursor()
    cur.execute('SELECT * FROM arp')
    rows = cur.fetchall()
    return rows

def print_all(db_file):
    rows = select_all(db_file)
    for row in rows:
        print(row)
    return True

def insert_table(con):
    cur = con.cursor()
    cur.execute("INSERT INTO arp VALUES('ff:ff:ff:ff:ff:ff', '(192.168.0.255)', '{}')")
    con.commit()
    return True

def update_data_manuf(mac, manuf, db_file):
    con = sql_connection(db_file)
    cur = con.cursor()
    #cur.execute("SELECT data FROM arp WHERE mac='" + str(mac) + "';")
    cur.execute("SELECT data FROM arp WHERE mac=?", (mac,))
    record = cur.fetchone()
    if record is None:
        return None
    #print(record[0])
    jdata = json.loads(record[0])
    jdata['manuf'] = manuf
    #print(json.dumps(jdata))
    update = json.dumps(jdata)
    cur.execute("UPDATE arp SET data=? WHERE mac=?", (update, mac))
    con.commit()
    print('updated1 ' + str(mac) + ' ' + str(update))
    return True

if __name__ == '__main__':

    con = sql_connection('test.db')
    update = insert_table(con)
    print(update)


