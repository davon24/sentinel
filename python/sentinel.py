#!/usr/bin/env python3

__version__ = 'v0.0.0e'

import sys
sys.path.insert(0,'db')
from db import store

if __name__ == '__main__':

    db_file = 'db/sentinel.db'
    manuf   = 'db/manuf'

    arpTbl = store.getArps()
    update = store.update_arp_data(db_file, arpTbl)
    print(update)

    if sys.argv[1:]:
        if sys.argv[1] == 'manuf':
            mac = sys.argv[2]
            m = store.get_manuf(mac, manuf)
            print(m)
        if sys.argv[1] == 'list':
            store.print_all(db_file)
        if sys.argv[1] == 'update-manuf':
            mac = sys.argv[2]
            update = store.update_manuf(mac, manuf, db_file)
            print(update)
            

