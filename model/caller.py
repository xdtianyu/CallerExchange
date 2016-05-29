#!/usr/bin/env python3
import json

from datetime import datetime
from time import mktime


class Caller:
    """model of caller class from LeanCloud"""
    number = None
    name = None
    count = None
    type = None
    source = None
    uid = None
    time = None

    def __init__(self, s):
        self.__dict__ = json.loads(s)
        self.source = self.__dict__['from']
        self.time = int(mktime(datetime.strptime(self.__dict__['createdAt'], "%Y-%m-%d %H:%M:%S.%f").timetuple()))

    def dump(self):
        print(self.number, self.name, self.count, self.type, self.source, self.time)

    def dict(self):
        return self.number, self.name, self.count, self.type, self.source, self.time
