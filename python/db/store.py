#!/usr/bin/env python3

import sqlite3
import os

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

def insert_table(con):
    cur = con.cursor()
    cur.execute("INSERT INTO arp VALUES('ff:ff:ff:ff:ff:ff', '(192.168.0.255)', '{}')")
    con.commit()



if __name__ == '__main__':

    con = sql_connection('test.db')
    update = insert_table(con)
    print(update)

