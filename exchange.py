#!/usr/bin/env python3
import operator

import re

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
        caller = Caller(line)

        # filter wrong number
        if not re.match("^[\d\+]*$", caller.number):
            continue

        # filter wrong tagged number
        if caller.type < 0 or caller.type > 16 or caller.count == 10000 or caller.count < 0:
            continue

        # add to caller map
        if caller.number not in caller_map.keys():
            caller_map[caller.number] = []
        caller_map[caller.number].append(caller)

# 3. resort caller list from map

caller_list = []

for number in caller_map:
    c_list = caller_map[number]
    count = 0
    target = c_list[0]
    source = 8

    # find max count from baidu, 360 or sogou
    for caller in c_list:
        if caller.count > count:
            target = caller
            count = caller.count
        if 0 <= caller.source <= 2:
            source = caller.source

    # find max type count from user marked
    if count == 0 and source == 8 and len(c_list) > 2:
        counts = dict()
        for caller in c_list:
            t = caller.type
            counts[t] = counts.get(t, 0) + 1
        t = max(counts.items(), key=operator.itemgetter(1))[0]
        for caller in c_list:
            if caller.type == t:
                target = caller
                break

    caller_list.append(target.dict())

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
