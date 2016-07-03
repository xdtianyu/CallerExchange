#!/usr/bin/env python3
import os

import qiniu

import config
from exchange import status

access_key = config.qn_access_key
secret_key = config.qn_secret_key
bucket_name = config.qn_bucket_name


def upload(name):
    upload_file(name)


def upload_file(file_name):
    q = qiniu.Auth(access_key, secret_key)

    key = os.path.basename(file_name)

    token = q.upload_token(bucket_name, key)
    ret, info = qiniu.put_file(token, key, file_name)
    if ret is not None:
        print(file_name + ' uploaded.')
    else:
        print(info)
