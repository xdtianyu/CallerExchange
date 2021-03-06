#!/usr/bin/env python3
import json

from datetime import datetime
from time import mktime


class Caller:
    """model of caller class for LeanCloud data"""
    number = None
    name = None
    count = 0
    type = None
    source = None
    uid = None
    time = None
    repeat = 0

    def __init__(self, s):
        self.__dict__ = s
        self.source = self.__dict__['from']
        self.time = int(mktime(datetime.strptime(self.__dict__['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple()))
        if '+86' in self.number:
            self.number = self.number.replace('+86', '')
        if ' ' in self.number:
            self.number = self.number.replace(' ', '')
        if '：0' in self.name:
            self.name = self.name.replace('：0', '')

    def dump(self):
        print(self.number, self.name, self.count, self.type, self.source, self.time)

    def dict(self):
        return self.number, self.name, self.count, self.type, self.source, self.time
