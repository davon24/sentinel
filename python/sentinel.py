#!/usr/bin/env python3

__version__ = 'v0.0.0k7a'

import sys
#sys.path.insert(0,'db')
import tools
import store


def usage():
    print(sys.argv[0] + ''' [option]

    options:

        list
        list-db

        manuf mac
        dns ip

        update-manuf mac
        update-dns mac ip

        ping-net ip

    ''')


def printArps():
    arpTbl = tools.getArps()
    for k,v in arpTbl.items():
        if (v == '(incomplete)') or (v == '<incomplete>'):
            continue
        print(v,k)
    return True

def main():
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
            dnsname = tools.getDNSName(ip)
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
        else:
            usage()
            sys.exit(0)
    else:
        sys.exit(main())

            

