#!/usr/bin/env python3

from model.caller import Caller
import sqlite3

# 1. download offline file from LeanCloud

# 2. read file to caller model map

caller_map = {}  # number:[caller]

with open("result.json") as f:
    for line in f:
        # print(line)
        caller = Caller(line)
        # caller.dump()
        if caller.type < 0 or caller.type > 8 or caller.count == 10000 or caller.count < 0:
            continue
        if caller.number not in caller_map.keys():
            caller_map[caller.number] = []
        caller_map[caller.number].append(caller)

# 3. resort caller list from map

caller_list = []
for number in caller_map:
    cl = caller_map[number]
    caller_list.append(cl[0].dict())

# 4. write to database file

conn = sqlite3.connect('number.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS CALLER
    ( ID INTEGER PRIMARY KEY AUTOINCREMENT, NUMBER TEXT UNIQUE, NAME TEXT, COUNT INTEGER, TYPE INTEGER, SOURCE INTEGER,
    TIME INTEGER );''')
for caller in caller_list:
    print(caller)
    pass
cur.executemany('insert into caller (number, name, count, type, source, time) values (?, ?, ?, ?, ?, ?)', caller_list)
conn.commit()
cur.close()
conn.close()

# 5. upload offline database to QiNiu
