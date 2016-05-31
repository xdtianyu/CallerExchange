#!/usr/bin/env python3
import json
import os
import time

from datetime import datetime

data_file = "cache/status.json"


class Status:

    version = 0
    count = 0
    new_count = 0
    timestamp = None

    def __init__(self):
        if not os.path.exists(data_file):
            return
        with open(data_file) as f:
            self.__dict__ = json.loads(f.read())

    def dump(self):
        print(self.version, self.timestamp)

    def json(self):
        return {"version": self.version, "count": self.count, "new_count": self.new_count, "timestamp": self.timestamp}

    def update(self):
        self.version += 1
        self.timestamp = int(time.mktime(datetime.now().utctimetuple()))
        with open(data_file, "w") as f:
            f.write(json.dumps(self.json()))

    def to_list(self):
        return [self.version, self.count, self.new_count, self.timestamp]
