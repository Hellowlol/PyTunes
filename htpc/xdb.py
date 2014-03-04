#!/usr/bin/python
# -*- coding: utf-8 -*-

import htpc
import os
import sqlite3 as lite
import sys
data = []

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def table_dump(db, table, start, end):
    db = htpc.DATADIR + db
    #print db
    con = lite.connect(db)

    con.row_factory = dict_factory
    with con:
        cur = con.cursor()    
        cur.execute("SELECT * FROM " + table)

    while True:
        row = cur.fetchone()
        if row == None:
            break
        data.append(row)    

    return data

def art_count(db, media_type, media_id, type):
    db = htpc.DATADIR + db
    #print db
    con = lite.connect(db)
    with con:
        cur = con.cursor()    
        count = cur.execute("SELECT COUNT FROM art WHERE media_type = " + media_type + " AND media_id = " + media_id + " AND type = " + type)
    return count

    
