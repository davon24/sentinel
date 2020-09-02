#!/usr/bin/env python3

__version__ = 'v0.0.0i'

import sys
sys.path.insert(0,'db')
import tools
from db import store

if __name__ == '__main__':

    db_store = 'db/sentinel.db'
    db_manuf = 'db/manuf'

    arpTbl = tools.getArps()
    update = store.update_arp_data(db_store, arpTbl)
    #print(update)

    if sys.argv[1:]:
        if sys.argv[1] == 'manuf':
            mac = sys.argv[2]
            mfname = store.get_manuf(mac, db_manuf)
            print(mfname)
        if sys.argv[1] == 'list':
            store.print_all(db_store)
        if sys.argv[1] == 'update-manuf':
            mac = sys.argv[2]
            mfname = store.get_manuf(mac, db_manuf)
            update = store.update_data_manuf(mac, mfname, db_store)
            print(update)
        if sys.argv[1] == 'dns':
            ip = sys.argv[2]
            dnsname = tools.getDNSName(ip)
            print(dnsname)
        if sys.argv[1] == 'update-dns':
            mac = sys.argv[2]
            ip = sys.argv[3]
            dnsname = tools.getDNSName(ip)
            update = store.update_data_dns(mac, dnsname, db_store)
            print(update)
            

