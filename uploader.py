#!/usr/bin/env python3
import os
import tarfile
import qiniu

import config

access_key = config.qn_access_key
secret_key = config.qn_secret_key
bucket_name = config.qn_bucket_name

status_file = 'cache/status.json'


def upload(name):
    tar_file = compress(name)
    upload_file(tar_file)
    upload_file(status_file)


def compress(name):
    tar_name = name + ".tar.gz"
    tar = tarfile.open(tar_name, "w:gz")
    tar.add(name, arcname=os.path.basename(name))
    tar.close()
    return tar_name


def upload_file(file_name):
    q = qiniu.Auth(access_key, secret_key)

    key = os.path.basename(file_name)

    token = q.upload_token(bucket_name, key)
    ret, info = qiniu.put_file(token, key, file_name)
    if ret is not None:
        print(file_name + ' uploaded.')
    else:
        print(info)

