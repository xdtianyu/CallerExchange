#!/usr/bin/env python3
import os
import tarfile


def upload(name):
    compress(name)


def compress(name):
    tar = tarfile.open(name + ".tar.gz", "w:gz")
    tar.add(name, arcname=os.path.basename(name))
    tar.close()
