#!/usr/bin/env python3
import os
import zipfile

import qiniu
import requests

import config

access_key = config.qn_access_key
secret_key = config.qn_secret_key
bucket_name = config.qn_bucket_name

status_file = 'cache/status.json'


def upload(name):
    zip_file = compress(name)
    upload_file(zip_file)
    upload_file(status_file)
    upload_file_to_coding(zip_file)
    upload_file_to_coding(status_file)


def compress(name):
    zip_file = name + ".zip"
    zf = zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED)
    zf.write(name, arcname=os.path.basename(name))
    zf.close()
    return zip_file


def upload_file(file_name):
    q = qiniu.Auth(access_key, secret_key)

    key = os.path.basename(file_name)

    token = q.upload_token(bucket_name, key)
    ret, info = qiniu.put_file(token, key, file_name)
    if ret is not None:
        print(file_name + ' uploaded.')
    else:
        print(info)


def upload_file_to_coding(file_name):

    class LastCommit:
        code = -1
        data = None

        def __init__(self, s):
            import json
            self.__dict__ = json.loads(s)

    # get last commit
    r = requests.get(config.coding_url, cookies={'sid': config.coding_sid})
    commit = LastCommit(r.text)
    last_commit = None
    try:
        if commit.code == 0:
            last_commit = commit.data['lastCommit']
            print(last_commit)
    except AttributeError:
        pass

    # make post
    if last_commit:
        data = {'lastCommitSha': last_commit, 'message': 'test'}
        files = {'files': open(file_name, 'rb')}
        cookies = {'sid': config.coding_sid}
        r = requests.post(config.coding_url, data=data, files=files, cookies=cookies)
        if r.text == '{"code":0}':
            print(file_name + ' uploaded.')
        else:
            print(r.text)
