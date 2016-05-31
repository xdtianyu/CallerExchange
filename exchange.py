#!/usr/bin/env python3
import downloader
from model.caller import Caller
import sqlite3

from model.status import Status

# 1. download offline file from LeanCloud

result_json = downloader.run()

if result_json == 'error':
    print("Download error!")
    exit(-1)

# 2. read file to caller model map

caller_map = {}  # number:[caller]

with open(result_json) as f:
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

status = Status()
status.update()

conn = sqlite3.connect('cache/caller_' + str(status.version) + '.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS CALLER
    ( ID INTEGER PRIMARY KEY AUTOINCREMENT, NUMBER TEXT UNIQUE, NAME TEXT, COUNT INTEGER, TYPE INTEGER, SOURCE INTEGER,
    TIME INTEGER );''')
for caller in caller_list:
    print(caller)
    pass
cur.executemany('insert into caller (number, name, count, type, source, time) values (?, ?, ?, ?, ?, ?)', caller_list)

cur.execute('''CREATE TABLE IF NOT EXISTS STATUS
    ( ID INTEGER PRIMARY KEY AUTOINCREMENT, VERSION INTEGER, COUNT INTEGER, NEW_COUNT INTEGER, TIME INTEGER );''')

cur.execute('insert into status (version, count, new_count, time) values (?, ?, ?, ?)', status.to_list())

conn.commit()
cur.close()
conn.close()

# 5. upload offline database to QiNiu
