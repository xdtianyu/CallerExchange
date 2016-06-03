#!/usr/bin/env python3
import os
import tarfile
import zipfile

import qiniu

import config

access_key = config.qn_access_key
secret_key = config.qn_secret_key
bucket_name = config.qn_bucket_name

status_file = 'cache/status.json'


def upload(name):
    zip_file = compress(name)
    upload_file(zip_file)
    upload_file(status_file)


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

