#!/usr/bin/env python3

import sqlite3
import os
import time
import json
import threading

import manuf as mf
import tools

class DNSUpDateTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def sql_connection(self, db_file):
        con = sqlite3.connect(db_file)
        return con

    def run(self, mac, ip, db_file):
        #print(mac, ip, db_file)
        ip = ip.strip('(')
        ip = ip.strip(')')
        #print('IP: ' + ip)
        dnsname = tools.getDNSName(ip)
        #print('DNS: ' + dnsname)
        con = self.sql_connection(db_file)
        cur = con.cursor()
        cur.execute("SELECT data FROM arp WHERE mac=?", (mac,))
        record = cur.fetchone()
        if record is None:
            return None
        #print(record[0])
        jdata = json.loads(record[0])
        jdata['dns'] = dnsname
        update = json.dumps(jdata)
        cur.execute("UPDATE arp SET data=? WHERE mac=?", (update, mac))
        con.commit()
        print('t.updated.dns ' + str(mac) + ' ' + str(update))
        return True


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
                print('updated.2 ' + str(_mac) + ' ' + str(l))
            continue #print('SKIP (incomplete)')

        cur.execute("SELECT ip FROM arp WHERE mac='" + mac + "'")
        #_mac, _ip = cur.fetchone()
        _result = cur.fetchone()
        #print(_mac, _ip, _data)
        if not _result:
            t = time.strftime("%Y-%m-%dT%H:%M:%SZ")
            m = mf.get_manuf(mac, 'db/manuf')
            #print(m)
            data = '{"created":"' + t + '","manuf":"' + m + '"}'
            cur.execute("INSERT INTO arp VALUES (?, ?, ?)", (mac, ip, data))
            con.commit()
            print('new ' + str(mac) + ' ' + str(ip) + ' ' + str(data))
            # launch dns thread update async
            dns = DNSUpDateTask()
            t = threading.Thread(target=dns.run, args=(mac,ip,db_file,))
            #print('t.start')
            t.start()
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
                print('updated.1 ' + str(mac) + ' ' + str(_ip))
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


def update_data_manuf(mac, mfname, db_file):
    con = sql_connection(db_file)
    cur = con.cursor()
    #cur.execute("SELECT data FROM arp WHERE mac='" + str(mac) + "';")
    cur.execute("SELECT data FROM arp WHERE mac=?", (mac,))
    record = cur.fetchone()
    if record is None:
        return None
    #print(record[0])
    jdata = json.loads(record[0])
    jdata['manuf'] = mfname
    #print(json.dumps(jdata))
    update = json.dumps(jdata)
    cur.execute("UPDATE arp SET data=? WHERE mac=?", (update, mac))
    con.commit()
    print('updated.manuf ' + str(mac) + ' ' + str(update))
    return True

def update_data_dns(mac, dnsname, db_file):
    con = sql_connection(db_file)
    cur = con.cursor()
    cur.execute("SELECT data FROM arp WHERE mac=?", (mac,))
    record = cur.fetchone()
    if record is None:
        return None
    #print(record[0])
    jdata = json.loads(record[0])
    jdata['dns'] = dnsname
    #print(json.dumps(jdata))
    update = json.dumps(jdata)
    cur.execute("UPDATE arp SET data=? WHERE mac=?", (update, mac))
    con.commit()
    print('updated.dns ' + str(mac) + ' ' + str(update))
    return True

def get_data(mac, db_file):
    con = sql_connection(db_file)
    cur = con.cursor()
    cur.execute("SELECT data FROM arp WHERE mac=?", (mac,))
    record = cur.fetchone()
    if record is None:
        return None
    #print(record[0])
    jdata = json.loads(record[0])
    return jdata


def get_manuf(mac, manuf_file):
    #manuf = mf.get_manuf(mac, 'db/manuf')
    manuf = mf.get_manuf(mac, manuf_file)
    return manuf


#def update_manuf(mac, manuf_file, db_file):
#    mfname = get_manuf(mac, manuf_file)
#    update = update_data_manuf(mac, mfname, db_file)
#    return update


if __name__ == '__main__':

    #con = sql_connection('test.db')
    #insert = insert_table(con)
    #print(insert)

    #print('new ' + str(mac) + ' ' + str(ip) + ' ' + str(data))

    mac = '70:8b:cd:d0:67:10'
    ip  = '192.168.0.1'
    db_file = 'db/sentinel.db'

    dns = DNSUpDateTask()
    t = threading.Thread(target=dns.run, args=(mac,ip,db_file,))
    t.start()
    #print('t.start')





