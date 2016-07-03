#!/usr/bin/env python3
import operator
import os

import re
import zipfile

import downloader
import uploader
from model import caller_type
from model.caller import Caller
import sqlite3

from model.status import Status, data_file


def compress(file_name):
    zip_file = file_name + ".zip"
    zf = zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED)
    zf.write(file_name, arcname=os.path.basename(file_name))
    zf.close()
    return zip_file


status = Status()

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

        # filter repeated number
        append = True
        for i in range(0, len(caller_map[caller.number])):
            c = caller_map[caller.number][i]

            if c.name == caller.name and c.type == caller.type and c.source == caller.source:

                if caller.count == 0:
                    caller_map[caller.number][i].count += 1
                elif caller.count > caller_map[caller.number][i].count:
                    caller_map[caller.number][i].count = caller.count
                caller_map[caller.number][i].repeat += 1
                append = False
                break
        if append:
            caller_map[caller.number].append(caller)

# 3. resort caller list from map

caller_list = []

for number in caller_map:
    c_list = caller_map[number]
    count = 0
    repeat = 0
    target = c_list[0]
    source = 8

    # find max count from baidu, 360 or sogou
    for caller in c_list:
        if caller.repeat > repeat:
            target = caller
            count = caller.count
            repeat = caller.repeat
        if 0 <= caller.source <= 2:
            source = caller.source
            # set caller type
            name = caller.name
            target.type = caller_type.from_name(name)

    # find max type count from user marked
    if count == 0 and source == 8 and len(c_list) > 2:
        counts = dict()
        for caller in c_list:
            t = caller.type
            counts[t] = counts.get(t, 0) + 1
        t = max(counts.items(), key=operator.itemgetter(1))[0]
        for caller in c_list:
            if caller.type == t:
                caller.count = counts[t]
                target = caller
                break

    caller_list.append(target.dict())

# 4. write to database file
status.new_count = len(caller_list) - status.count

if status.new_count == 0:
    print("No new data.")
    exit(0)

status.count = len(caller_list)
status.bump()

conn = sqlite3.connect('cache/caller_' + str(status.version) + '.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS caller
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT UNIQUE, name TEXT, count INTEGER, type INTEGER, source INTEGER,
    time INTEGER );''')
# for caller in caller_list:
#     print(caller)
#     pass
cur.executemany('insert into caller (number, name, count, type, source, time) values (?, ?, ?, ?, ?, ?)', caller_list)

cur.execute('''CREATE TABLE IF NOT EXISTS status
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, version INTEGER, count INTEGER, new_count INTEGER, time INTEGER );''')

cur.execute('insert into status (version, count, new_count, time) values (?, ?, ?, ?)', status.to_list())

conn.commit()
cur.close()
conn.close()

# 5. upload offline database to QiNiu

zip_file = compress('cache/caller_' + str(status.version) + '.db')
status.update(zip_file)

# upload files
uploader.upload(zip_file)
uploader.upload(data_file)
