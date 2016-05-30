#!/usr/bin/env python3

import json
import os
import urllib.request

import time

import config

job_url = 'https://leancloud.cn/1.1/bigquery/job'
job_params = {"appId": config.app_id, "jobConfig": {"sql": "select * from caller"}}

headers = {
    "X-LC-Id": config.app_id,
    "X-LC-Key": config.app_key,
    "Content-Type": "application/json"
}


def run():
    job = run_job()
    check_status(job.id)
    path = export(job.id)
    download(path)


def run_job():
    data = json.dumps(job_params).encode('utf8')

    req = urllib.request.Request(job_url, data=data, headers=headers)
    res = urllib.request.urlopen(req)
    job_data = Job(res.read().decode('utf8'))
    job_data.dump()
    return job_data


def check_status(job_id):
    url = job_url + '/' + job_id + '?anchor=0&limit=1'

    while True:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        job_status = JobStatus(res.read().decode('utf8'))

        if job_status.status == 'RUNNING':
            print('RUNNING')
            time.sleep(3)
        elif job_status.status == 'OK':
            break


def export(job_id):
    url = 'https://leancloud.cn/1.1/bigquery/job/' + job_id + '/export'
    req = urllib.request.Request(url, data=''.encode('utf8'), headers=headers)
    res = urllib.request.urlopen(req)
    job_export = JobExport(res.read().decode('utf8'))

    if job_export.status == 'OK':
        return job_export.path
    else:
        print('Error, export failed.')
        return None


def download(url):
    res = urllib.request.urlopen(url)
    cache_dir = 'cache/'
    file_name = url.split('/')[-1]
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    with open(cache_dir + file_name, 'b+w') as f:
        f.write(res.read())
    return file_name


class Job:
    id = None
    appId = None

    def __init__(self, s):
        self.__dict__ = json.loads(s)

    def dump(self):
        print(self.id, self.appId)


class JobStatus:
    id = None
    status = None

    def __init__(self, s):
        self.__dict__ = json.loads(s)

    def dump(self):
        print(self.id, self.status)


class JobExport:
    status = None
    path = None

    def __init__(self, s):
        self.__dict__ = json.loads(s)

    def dump(self):
        print(self.status, self.path)
