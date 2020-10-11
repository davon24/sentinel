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

    def sqlConnection(self, db_file):
        con = sqlite3.connect(db_file)
        return con

    def run(self, mac, ip, db_file):
        #print(mac, ip, db_file)
        ip = ip.strip('(')
        ip = ip.strip(')')
        #print('IP: ' + ip)

        #dnsname = tools.getDNSName(ip)
        dnsname = str(tools.getNSlookup(ip))

        #print('DNS: ' + dnsname)
        con = self.sqlConnection(db_file)
        cur = con.cursor()
        cur.execute("SELECT data FROM arp WHERE mac=?", (mac,))
        record = cur.fetchone()
        if record is None:
            return False
        #print(record[0])
        jdata = json.loads(record[0])
        jdata['dns'] = dnsname
        update = json.dumps(jdata)
        cur.execute("UPDATE arp SET data=? WHERE mac=?", (update, mac))
        con.commit()
        print('updated dns ' + str(mac) + ' ' + str(update))
        if cur.rowcount == 0:
            return False
        return True

def sqlConnection(db_file):
    if not os.path.isfile(db_file):
        con = createDB(db_file)
    else:
        con = sqlite3.connect(db_file)
    return con

def createDB(db_file):

    con = sqlite3.connect(db_file)
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS arp (mac TEXT PRIMARY KEY NOT NULL,ip TEXT,data TEXT);''')
    cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_mac ON arp (mac);''')

    cur.execute('''CREATE TABLE IF NOT EXISTS ports (port INTEGER PRIMARY KEY NOT NULL,data TEXT);''')
    cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_port ON ports (port);''')

    create_established =  "CREATE TABLE IF NOT EXISTS established (rule TEXT CHECK(rule IN ('ALLOW','DENY')) NOT NULL DEFAULT 'ALLOW',"
    create_established += "proto TEXT,laddr TEXT,lport INTEGER,faddr TEXT,fport INTEGER,UNIQUE(rule,proto,laddr,lport,faddr,fport));"
    cur.execute(create_established)

    create_nmap  = "CREATE TABLE IF NOT EXISTS nmap (ip TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
    create_nmapi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_nmap ON nmap (ip);"
    cur.execute(create_nmap)
    cur.execute(create_nmapi)

    create_vulns  = "CREATE TABLE IF NOT EXISTS vulns (vid INTEGER PRIMARY KEY NOT NULL,ip TEXT,timestamp TEXT,report TEXT,data TEXT,blob BLOB);"
    create_vulnsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_vulns ON vulns (vid);"
    cur.execute(create_vulns)
    cur.execute(create_vulnsi)

    create_detect  = "CREATE TABLE IF NOT EXISTS detect (did INTEGER PRIMARY KEY NOT NULL,ip TEXT,timestamp TEXT,report TEXT,data TEXT,blob BLOB);"
    create_detecti = "CREATE UNIQUE INDEX IF NOT EXISTS idx_detect ON detect (did);"
    cur.execute(create_detect)
    cur.execute(create_detecti)

    #create_ip  = "CREATE TABLE IF NOT EXISTS ips (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
    create_ip  = "CREATE TABLE IF NOT EXISTS ips (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON) WITHOUT ROWID;"
    create_ipi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_ip ON ips (name);"
    cur.execute(create_ip)
    cur.execute(create_ipi)

    #create_configs  = "CREATE TABLE IF NOT EXISTS configs (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
    create_configs  = "CREATE TABLE IF NOT EXISTS configs (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON) WITHOUT ROWID;"
    create_configsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_config ON configs (name);"
    cur.execute(create_configs)
    cur.execute(create_configsi)

    #create_fims  = "CREATE TABLE IF NOT EXISTS fims (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
    create_fims  = "CREATE TABLE IF NOT EXISTS fims (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON) WITHOUT ROWID;"
    create_fimsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_fims ON fims (name);"
    cur.execute(create_fims)
    cur.execute(create_fimsi)

    #create_reports  = "CREATE TABLE IF NOT EXISTS reports (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
    create_reports  = "CREATE TABLE IF NOT EXISTS reports (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON) WITHOUT ROWID;"
    create_reportsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_reports ON reports (name);"
    cur.execute(create_reports)
    cur.execute(create_reportsi)

    #create_alerts  = "CREATE TABLE IF NOT EXISTS alerts (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON,status INT,run JSON);"
    create_alerts  = "CREATE TABLE IF NOT EXISTS alerts (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON) WITHOUT ROWID;"
    create_alertsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_alerts ON alerts (name);"
    cur.execute(create_alerts)
    cur.execute(create_alertsi)

    #create_jobs  = "CREATE TABLE IF NOT EXISTS jobs (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
    create_jobs  = "CREATE TABLE IF NOT EXISTS jobs (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data JSON) WITHOUT ROWID;"
    create_jobsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs ON jobs (name);"
    cur.execute(create_jobs)
    cur.execute(create_jobsi)

    create_counts  = "CREATE TABLE IF NOT EXISTS counts (name TEXT PRIMARY KEY NOT NULL,count INTEGER) WITHOUT ROWID;"
    create_countsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_counts ON counts (name);"
    cur.execute(create_counts)
    cur.execute(create_countsi)

    create_proms  = "CREATE TABLE IF NOT EXISTS proms (name TEXT PRIMARY KEY NOT NULL,data TEXT) WITHOUT ROWID;"
    create_promsi = "CREATE UNIQUE INDEX IF NOT EXISTS idx_proms ON proms (name);"
    cur.execute(create_proms)
    cur.execute(create_promsi)

    con.commit()

    return con

#def createMemDB(memdb):
#    create_table  = "CREATE TABLE IF NOT EXISTS counts (name TEXT PRIMARY KEY NOT NULL,count INTEGER) WITHOUT ROWID;"
#    with memdb:
#        memdb.execute(create_table)
#        # Successful memdb.commit() is called automatically afterwards
#    return True
# Within one process it is possible to share an in-memory database if you use the file::memory:?cache=shared
# but this is still not accessible from other another process.

def update_arp_data(db_file, arpDict):

    con = sqlConnection(db_file)
    cur = con.cursor()

    for ip,mac in arpDict.items():

        #if mac == '(incomplete)':
        if (mac == '(incomplete)') or (mac == '<incomplete>'):
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
    con = sqlConnection(db_file)
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
    con = sqlConnection(db_file)
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
    con = sqlConnection(db_file)
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
    con = sqlConnection(db_file)
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

def printListeningAllowed(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT * FROM ports')
    rows = cur.fetchall()
    for row in rows:
        print(row)
    return True

def gettListeningAllowedLst(db_file):
    portLst = []
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT port FROM ports')
    rows = cur.fetchall()
    for row in rows:
        #print(row)
        _row = row[0]
        portLst.append(_row)
    return portLst


def insertAllowedPort(port, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("INSERT INTO ports VALUES(?,?)", (port, '{}'))
    con.commit()
    return True

def deleteAllowedPort(port, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM ports WHERE port=?", (port,))
    con.commit()
    return True

def getListenPortsLst():
    open_portsLst = []
    open_portsDct = tools.getListenPortsDct()
    for open_port in open_portsDct:
        open_portsLst.append(open_port)
    return open_portsLst

def printListeningAlerts(db_file):

    open_portsLst = getListenPortsLst()
    allow_portsLst = gettListeningAllowedLst(db_file)

    diffLst = list(set(open_portsLst) - set(allow_portsLst))
    print(sorted(diffLst))

    return True
    #tools.listenPortsLst() #unsorted list tcp4:631, tcp6:631


def printEstablishedRules(db_file):
    #print('id  proto  laddr  lport  faddr  fport')
    Dct = getEstablishedRulesDct(db_file)
    for k,v in Dct.items():
        print(v)
    return True

def getEstablishedRulesDct(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT * FROM established')
    rows = cur.fetchall()

    Dct = {}
    c = 0
    for row in rows:
        #print(row)
        c += 1
        Dct[c] = row
        #_row = row[0]
        #portLst.append(_row)
    #return portLst
    #return True
    return Dct

def insertEstablishedRules(rule, proto, laddr, lport, faddr, fport, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("INSERT INTO established VALUES(?,?,?,?,?,?)", (rule, proto, laddr, lport, faddr, fport))
    con.commit()
    return True

def getEstablishedRulesMatchDct(db_store):

    #rtnDct = {}
    allowDct = {}
    denyDct = {}

    estDct = tools.getEstablishedDct()
    _estDct = {}
    e = 0
    r = 0
    for k,v in estDct.items():
        #print(v)
        proto_ = v.split(' ')[0]
        laddr_ = v.split(' ')[1]
        lport_ = v.split(' ')[2]
        faddr_ = v.split(' ')[3]
        fport_ = v.split(' ')[4]
        #print(proto, laddr, lport, faddr, fport)
        e += 1
        _estDct[e] = [ proto_, laddr_, lport_, faddr_, fport_ ]

    #print('split')

    rlsDct = getEstablishedRulesDct(db_store)
    _rlsDct = {}
    for k,v in rlsDct.items():
        #print(v)
        rule__  = v[0]
        proto__ = v[1]
        laddr__ = v[2]
        lport__ = v[3]
        faddr__ = v[4]
        fport__ = v[5]
        #print(proto, laddr, lport, faddr, fport)
        r += 1
        _rlsDct[r] = [ rule__, proto__, laddr__, lport__, faddr__, fport__ ]

    #print(_estDct)
    #print(_rlsDct)

    c = 0
    for k,v in _rlsDct.items():

        #print('rule  ' + str(v))
        rule_r  = str(v[0])
        proto_r = str(v[1])
        laddr_r = str(v[2])
        lport_r = str(v[3])
        faddr_r = str(v[4])
        fport_r = str(v[5])
        #print(proto)

        for _k,_v in _estDct.items():
            #print(v)
            _proto = str(_v[0])
            _laddr = str(_v[1])
            _lport = str(_v[2])
            _faddr = str(_v[3])
            _fport = str(_v[4])

            if (proto_r == _proto) or (proto_r == '*'):
                #print('match1 ' + str(_v))
                if (laddr_r == _laddr) or (laddr_r == '*'):
                    #print('match2 ' + str(_v))
                    if (lport_r == _lport) or (lport_r == '*'):
                        #print('match3 ' + str(_v))
                        if (faddr_r == _faddr) or (faddr_r == '*'):
                            #print('match4 ' + str(_v))
                            if (fport_r == _fport) or (fport_r == '*'):
                                #continue
                                #break
                                #print('match ' + str(_v))
                                c += 1
                                #rtnDct[c] = _v
                                if rule_r == 'ALLOW':
                                    allowDct[c] = _v

                                if rule_r == 'DENY':
                                    denyDct[c] = _v

    #print('done')
    #return rtnDct
    return allowDct, denyDct

def printEstablishedRulesMatch(db_store):
    estDct = tools.getEstablishedDct()
    _estDct = {}
    e = 0
    r = 0
    for k,v in estDct.items():
        #print(v)
        proto_ = v.split(' ')[0]
        laddr_ = v.split(' ')[1]
        lport_ = v.split(' ')[2]
        faddr_ = v.split(' ')[3]
        fport_ = v.split(' ')[4]
        #print(proto, laddr, lport, faddr, fport)
        e += 1
        _estDct[e] = [ proto_, laddr_, lport_, faddr_, fport_ ]

    #print('split')

    rlsDct = getEstablishedRulesDct(db_store)
    _rlsDct = {}
    for k,v in rlsDct.items():
        #print(v)
        rule__  = v[0]
        proto__ = v[1]
        laddr__ = v[2]
        lport__ = v[3]
        faddr__ = v[4]
        fport__ = v[5]
        #print(proto, laddr, lport, faddr, fport)
        r += 1
        _rlsDct[r] = [ rule__, proto__, laddr__, lport__, faddr__, fport__ ]

    #print(_estDct)
    #print(_rlsDct)

    for k,v in _rlsDct.items():
        #print('rule  ' + str(v))
        rule_r  = str(v[0])
        proto_r = str(v[1])
        laddr_r = str(v[2])
        lport_r = str(v[3])
        faddr_r = str(v[4])
        fport_r = str(v[5])
        #print(proto)
        _l = [ proto_r, laddr_r, lport_r, faddr_r, fport_r ]
        print(str(rule_r).lower() + ' ' + str(_l))

        for _k,_v in _estDct.items():
            #print(v)
            _proto = str(_v[0])
            _laddr = str(_v[1])
            _lport = str(_v[2])
            _faddr = str(_v[3])
            _fport = str(_v[4])

            if (proto_r == _proto) or (proto_r == '*'):
                #print('match1 ' + str(_v))
                if (laddr_r == _laddr) or (laddr_r == '*'):
                    #print('match2 ' + str(_v))
                    if (lport_r == _lport) or (lport_r == '*'):
                        #print('match3 ' + str(_v))
                        if (faddr_r == _faddr) or (faddr_r == '*'):
                            #print('match4 ' + str(_v))
                            if (fport_r == _fport) or (fport_r == '*'):
                                #print('match5 ' + str(_v))
                                #continue
                                #break
                                print('match ' + str(_v))
    #print('done')
    return True

def printEstablishedAlerts(db_store):
    eaDct = getEstablishedAlertsDct(db_store)
    for k,v in eaDct.items():
        print(v)
    return True


def getEstablishedAlertsDct(db_store):

    estDct = tools.getEstablishedDct()
    allowDct, denyDct = getEstablishedRulesMatchDct(db_store)

    estDct_ = {}
    for ek,ev in estDct.items():
        line = ev.split(' ')
        estDct_[ek] = line

    returnADct = {}
    for key,value in estDct_.items():
        if value not in allowDct.values():
            returnADct[key] = value

    returnDct = {}
    c = 0

    for k,v in returnADct.items():
        c += 1
        returnDct[c] = v

    for k,v in denyDct.items():
        c += 1
        returnDct[c] = v

    return returnDct


#def printIPs(db_file):
#    rows = getIPs(db_file)
#    for row in rows:
#        print(row)
#    return True
#
#def getIPs(db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    #cur.execute('SELECT rowid,* FROM ips ORDER by rowid DESC;')
#    cur.execute('SELECT * FROM ips ORDER by rowid DESC;')
#    rows = cur.fetchall()
#    return rows

def insertIPs(ip, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    #cur.execute("INSERT INTO ips VALUES(?, DATETIME('now'), ?)", (ip, None ))
    cur.execute("INSERT INTO ips VALUES(?, DATETIME('now'), NULL)", (ip, ))
    con.commit()
    return True

def updateIPs(ip, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    #print('UPDATE ' + ip + ' ' + data)
    #cur.execute("UPDATE ips SET data=? WHERE ip=?", (ip, data))
    sql = "UPDATE ips SET data='" + data + "', timestamp=DATETIME('now') WHERE ip='" + ip + "';"
    cur.execute(sql)
    con.commit()
    return True

def replaceIPs(ip, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO ips VALUES(?, DATETIME('now'), ?)", (ip, data))
    con.commit()
    return True

#def clearAllIPs(db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    cur.execute("DELETE FROM ips;")
#    cur.execute("REINDEX ips;")
#    con.commit()
#    return True

def deleteIPs(ip, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM ips WHERE ip=? ;", (ip,))
    con.commit()
    return True


def getNmaps(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT rowid,* FROM nmap ORDER by rowid DESC;')
    rows = cur.fetchall()
    return rows

def replaceNmaps(ip, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO nmap VALUES(?, DATETIME('now'), ?)", (ip, data))
    con.commit()
    return True

def deleteNmaps(ip, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM nmap WHERE ip=? ;", (ip,))
    con.commit()
    return True

def clearAllNmaps(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM nmap;")
    cur.execute("REINDEX nmap;")
    con.commit()
    return True

def getNmapVuln(vid, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT rowid,* FROM vulns WHERE rowid=? ;', (vid,))
    row = cur.fetchone()
    return row

def getAllNmapVulns(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT rowid,* FROM vulns ORDER by rowid DESC;')
    rows = cur.fetchall()
    return rows

def replaceVulns(ip, data, blob, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO vulns VALUES(?,DATETIME('now'),?,?)", (ip, data, blob))
    con.commit()
    return True

def clearAllVulns(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM vulns;")
    cur.execute("REINDEX vulns;")
    con.commit()
    return True

def deleteVulns(rowid, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM vulns WHERE rowid=? ;", (rowid,))
    con.commit()
    return True

def insertVulns(ip, report, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("INSERT INTO vulns VALUES(NULL,?,DATETIME('now'),?,?,NULL)", (ip,report,data))
    con.commit()
    return True

def updateVulnsReport(vid, report, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    sql = "UPDATE vulns SET report='" + report + "' WHERE vid='" + str(vid) + "';"
    cur.execute(sql)
    con.commit()
    return True

def getVulnData(vid, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT data FROM vulns WHERE rowid=? ;', (vid,))
    row = cur.fetchone()
    return row

def getNmapDetect(did, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT rowid,* FROM detect WHERE rowid=? ;', (did,))
    row = cur.fetchone()
    return row

def getAllNmapDetects(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT rowid,* FROM detect ORDER by rowid DESC;')
    rows = cur.fetchall()
    return rows

def insertDetect(ip, report, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("INSERT INTO detect VALUES(NULL,?,DATETIME('now'),?,?,NULL)", (ip,report,data))
    con.commit()
    return True

def deleteDetect(rowid, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM detect WHERE rowid=? ;", (rowid,))
    con.commit()
    return True

def clearAllDetects(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM detect;")
    cur.execute("REINDEX detect;")
    con.commit()
    return True

#def getAllConfigs(db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    cur.execute('SELECT rowid,* FROM configs;')
#    rows = cur.fetchall()
#    return rows

#def getAllFims(db_file):
#    rows = getAll('fims', db_file)
#    return rows


def clearAll(tbl, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('DELETE FROM ' + str(tbl) + ';')
    cur.execute('REINDEX ' + str(tbl) + ';')
    con.commit()
    return True


#def getConfig(name, db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    cur.execute('SELECT data FROM configs WHERE name=? ;', (name,))
#    row = cur.fetchone()
#    return row

def getFim(name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT data FROM fims WHERE name=? ;', (name,))
    row = cur.fetchone()
    if cur.rowcount == 0:
        return None
    return row

def getData(tbl, name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT data FROM ' + str(tbl) + ' WHERE name=? ;', (name,))
    row = cur.fetchone()
    if cur.rowcount == 0:
        return None
    return row


#def replaceFim(name, data, db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    cur.execute("REPLACE INTO fims VALUES(?,DATETIME('now'),?)", (name, data))
#    con.commit()
#    return True


def insertConfig(name, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("INSERT INTO configs VALUES(?,DATETIME('now'),?)", (name,data))
    con.commit()
    return True

def replaceConfig(name, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO configs VALUES(?,DATETIME('now'),?)", (name, data))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True

def replaceINTOproms(name, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO proms VALUES(?,?)", (name, data))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True


def replaceINTO(tbl, name, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO " + str(tbl) + " VALUES(?,DATETIME('now'),?)", (name, data))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True

# need to standardize on name, timestamp, data for all...
# create_fims  = "CREATE TABLE IF NOT EXISTS fims (name TEXT PRIMARY KEY NOT NULL,timestamp TEXT,data TEXT);"
#def updateTbl(tbl, name, data, db_file):
def updateData(tbl, name, data, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("UPDATE " + str(tbl) + " SET data=?, timestamp=DATETIME('now') WHERE name=?", (data, name))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True

def updateDataItem(item, val, tbl, name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    #cur.execute("UPDATE " + str(tbl) + " SET data=?, timestamp=DATETIME('now') WHERE name=?", (data, name))
    cur.execute("UPDATE " + str(tbl) + " SET data=(select json_set(" + str(tbl) + ".data, '$." + str(item) + "', ? ) from " + str(tbl) + ") where name='" + str(name) + "';", (val,))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True

def deleteDataItem(item, tbl, name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("UPDATE " + str(tbl) + " SET data=(select json_remove(" + str(tbl) + ".data, '$." + str(item) + "') from " + str(tbl) + ") where name=?", (name,))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True


def updateFims(name, data, db_file): #not working?  ah, name,data...data,name
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("UPDATE fims SET data=?, timestamp=DATETIME('now') WHERE name=?", (data, name))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True


#def deleteFromrowid(tbl, rowid, db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    cur.execute("DELETE FROM " + str(tbl) + " WHERE rowid=? ;", (rowid,))
#    con.commit()
#    if cur.rowcount == 0:
#        return False
#    return True

def deleteFrom(tbl, name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM " + str(tbl) + " WHERE name=? ;", (name,))
    con.commit()
    if cur.rowcount == 0:
        return False
    return True


#def selectAllrowid(tbl, db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    cur.execute("SELECT rowid,* FROM " + str(tbl) + ";")
#    #cur.execute("SELECT * FROM " + str(tbl) + ";")
#    rows = cur.fetchall()
#    return rows

def selectAll(tbl, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    #cur.execute("SELECT rowid,* FROM " + str(tbl) + ";")
    cur.execute("SELECT * FROM " + str(tbl) + ";")
    rows = cur.fetchall()
    #if cur.rowcount == 0:
    #    return False
    return rows

def getAll(tbl, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT rowid,* FROM ' + str(tbl) + ';')
    rows = cur.fetchall()
    #if cur.rowcount == 0:
    #    return False
    return rows


def getJob(name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT data FROM jobs WHERE name=? ;', (name,))
    row = cur.fetchone()
    #print(len(row))
    return row

def deleteJob(name, db_file):
    #print('let us delete...')
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM jobs WHERE name=? ;", (name,))
    con.commit()
    #print('cur.rowcount ' + str(cur.rowcount))
    if cur.rowcount == 0:
        return False
    return True

def clearAllJobs(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("DELETE FROM jobs;")
    cur.execute("REINDEX jobs;")
    con.commit()
    return True

def replaceCounts(name, count, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("REPLACE INTO counts VALUES(?,?)", (name, count))
    con.commit()
    return True

#def replaceMemDBCounts(name, count, memdb):
#    try:
#        with memdb:
#            cur = memdb.cursor()
#            cur.execute("REPLACE INTO counts VALUES(?,?)", (name, count))
#            return True
#    except Exception as e:
#        print(str(e))
#        return False

#def getAllMemDBCounts(memdb):
#    try:
#        with memdb:
#            cur = con.cursor()
#            cur.execute("SELECT * FROM counts;")
#            rows = cur.fetchall()
#            return rows
#    except Exception as e:
#        print(str(e))
#        return None
    #Within one process it is possible to share an in-memory database if you use the file::memory:?cache=shared
    #but this is still not accessible from other another process.


def updateCounts(name, count, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    #sql = "UPDATE counts SET count='" + count + "' WHERE name='" + str(name) + "';" 
    #cur.execute(sql)
    #TypeError: can only concatenate str (not "int") to str
    cur.execute("UPDATE counts SET count=? WHERE name=? ;", (count, name))
    con.commit()
    return True

def getCount(name, db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute('SELECT count FROM counts WHERE name=? ;', (name,))
    row = cur.fetchone()
    return row

def getAllCounts(db_file):
    con = sqlConnection(db_file)
    cur = con.cursor()
    cur.execute("SELECT * FROM counts;")
    rows = cur.fetchall()
    return rows

#def updateData(tbl, name, data, db_file):
#def updateJobs(name, jdata, db_file):
#    con = sqlConnection(db_file)
#    cur = con.cursor()
#    sql = "UPDATE jobs SET data='" + jdata + "' WHERE name='" + str(name) + "';"
#    cur.execute(sql)
#    con.commit()
#    return True




if __name__ == '__main__':
#uses built-in sqlite3
    pass

