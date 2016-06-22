#!/usr/bin/env python3

import json
import os
import gzip
import urllib.request

import time
from urllib.error import HTTPError

import config

job_url = 'https://leancloud.cn/1.1/bigquery/job'
job_params = {"appId": config.app_id, "jobConfig": {"sql": "select * from caller"}}
cache_dir = 'cache/'

headers = {
    "X-LC-Id": config.app_id,
    "X-LC-Key": config.app_key,
    "Content-Type": "application/json"
}


def run():
    job = run_job()
    check_status(job.id)
    path = export(job.id)
    while True:
        try:
            dir_name, file_name = download(path)
            return extract(dir_name, file_name)
        except OSError:
            print('error extract file, try again.')
            time.sleep(10)
            continue


def run_job():
    data = json.dumps(job_params).encode('utf8')

    req = urllib.request.Request(job_url, data=data, headers=headers)
    res = urllib.request.urlopen(req)
    job_data = Job(res.read().decode('utf8'))
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
    res = None

    # download file and keep loop if server returned 404 error
    while True:
        try:
            res = urllib.request.urlopen(url)
            break
        except HTTPError:
            print('download error, try again.')
            time.sleep(3)
            continue

    dir_name = url.split('/')[-2] + '/'
    file_name = url.split('/')[-1]

    if not os.path.exists(cache_dir + dir_name):
        os.makedirs(cache_dir + dir_name)
    with open(cache_dir + dir_name + file_name, 'b+w') as f:
        f.write(res.read())
    return dir_name, file_name


def extract(dir_name, file_name):
    gz = gzip.open(cache_dir + dir_name + file_name, "rb")
    json_file = cache_dir + dir_name + get_filename(file_name)
    jf = open(json_file, 'wb')
    jf.write(gz.read())
    gz.close()
    gz.close()

    if not os.path.exists(json_file):
        return 'error'
    else:
        return json_file


def get_filename(path):
    filename = path.split('/')[-1].split('.')[0]
    return filename


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