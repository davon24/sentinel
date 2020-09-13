#!/usr/bin/env python3

__version__ = 'v0.0.0.o'

import sys
#sys.path.insert(0,'db')
import tools
import store


def usage():
    print(sys.argv[0] + ''' [option]

    options:

        ping-net ip/net
        nmap-net net

        scan ip [level]

        list
        list-db

        manuf mac
        dns ip
        lsof port

        update-manuf mac
        update-dns mac ip

        listening
        listening-detailed
        listening-details port
        listening-allowed
        listening-alerts
        listening-allow port
        listening-remove port

        established
        established-rules
        established-rules-filter
        established-rule ALLOW|DENY proto laddr lport faddr fport
        established-alerts

        list-ips
        add-ip ip
        del-ip ip
        update-ip ip data

    ''')


def printArps():
    arpTbl = tools.getArps()
    for k,v in arpTbl.items():
        if (v == '(incomplete)') or (v == '<incomplete>'):
            continue
        print(v,k)
    return True

def printListening():
    cntDct = cntLsOf()
    for k,v in sorted(cntDct.items()):
        print(k,v)
    return True

def run():
        arpTbl = tools.getArps()
        update = store.update_arp_data(db_store, arpTbl)
        print(update)
        return True

if __name__ == '__main__':

    db_store = 'db/sentinel.db'
    db_manuf = 'db/manuf'

    if sys.argv[1:]:
        if sys.argv[1] == 'manuf':
            mac = sys.argv[2]
            mfname = store.get_manuf(mac, db_manuf)
            print(mfname)
            sys.exit(0)
        if sys.argv[1] == 'list':
            printArps()
            sys.exit(0)
        if sys.argv[1] == 'list-db':
            store.print_all(db_store)
            sys.exit(0)
        if sys.argv[1] == 'update-manuf':
            mac = sys.argv[2]
            mfname = store.get_manuf(mac, db_manuf)
            update = store.update_data_manuf(mac, mfname, db_store)
            print(update)
            sys.exit(0)
        if sys.argv[1] == 'dns':
            ip = sys.argv[2]
            dnsname = tools.getNSlookup(ip)
            print(dnsname)
            sys.exit(0)
        if sys.argv[1] == 'update-dns':
            mac = sys.argv[2]
            ip = sys.argv[3]
            #dnsname = tools.getDNSName(ip)
            #update = store.update_data_dns(mac, dnsname, db_store)
            import threading
            dns = store.DNSUpDateTask()
            t = threading.Thread(target=dns.run, args=(mac,ip,db_store,))
            t.start()
            #print(t)
            sys.exit(0)
        if sys.argv[1] == 'ping-net':
            ip = sys.argv[2]
            pn = tools.pingNet(ip)
            print(pn)
            sys.exit(0)
        if sys.argv[1] == 'nmap-net':
            ip = sys.argv[2]
            pn = tools.nmapNet(ip)
            print(pn)
            sys.exit(0)
        if sys.argv[1] == 'listening':
            p = tools.printListenPorts()
            sys.exit(0)
        if sys.argv[1] == 'listening-detailed':
            p = tools.printListenPortsDetailed()
            sys.exit(0)
        if sys.argv[1] == 'listening-details':
            port = sys.argv[2]
            p = tools.printListenPortsDetails(port)
            sys.exit(0)
        if sys.argv[1] == 'listening-allowed':
            p = store.printListeningAllowed(db_store)
            sys.exit(0)
        if sys.argv[1] == 'listening-allow':
            port = sys.argv[2]
            insert = store.insertAllowedPort(port, db_store)
            print(insert)
            sys.exit(0)
        if sys.argv[1] == 'listening-remove':
            port = sys.argv[2]
            remove = store.deleteAllowedPort(port, db_store)
            print(remove)
            sys.exit(0)
        if sys.argv[1] == 'listening-alerts':
            alerts = store.printListeningAlerts(db_store)
            sys.exit(0)
        if sys.argv[1] == 'established':
            established = tools.printEstablished()
            sys.exit(0)
        if sys.argv[1] == 'established-rules':
            established_rules = store.printEstablishedRules(db_store)
            sys.exit(0)
        if sys.argv[1] == 'established-rule':
            #established-rule proto laddr lport faddr fport
            rule  = sys.argv[2]
            proto = sys.argv[3]
            laddr = sys.argv[4]
            lport = sys.argv[5]
            faddr = sys.argv[6]
            fport = sys.argv[7]
            insert_rule = store.insertEstablishedRules(rule, proto, laddr, lport, faddr, fport, db_store)
            sys.exit(0)
        if sys.argv[1] == 'established-rules-filter':
            print_alerts = store.printEstablishedRulesMatch(db_store)
            sys.exit(0)
        if sys.argv[1] == 'established-alerts':
            print_alerts = store.printEstablishedAlerts(db_store)
            sys.exit(0)
        if sys.argv[1] == 'lsof':
            port = sys.argv[2]
            lsof = tools.printLsOfPort(port)
            sys.exit(0)
        if sys.argv[1] == 'scan':
            ip = sys.argv[2]
            try: level = sys.argv[3]
            except IndexError: level = 1
            scan = tools.nmapScan(ip, level)
            print(scan)
            sys.exit(0)
        if sys.argv[1] == 'list-ips':
            run = store.printIPs(db_store)
            sys.exit(0)
        if sys.argv[1] == 'add-ip':
            ip = sys.argv[2]
            insert = store.insertIPs(ip, db_store)
            print(insert)
            sys.exit(0)
        if sys.argv[1] == 'del-ip':
            ip = sys.argv[2]
            insert = store.deleteIPs(ip, db_store)
            print(insert)
            sys.exit(0)
        if sys.argv[1] == 'update-ip':
            ip = sys.argv[2]
            data = sys.argv[3]
            update = store.updateIPs(ip, data, db_store)
            print(update)
            sys.exit(0)
        else:
            usage()
            sys.exit(0)
    else:
        sys.exit(run())

            
