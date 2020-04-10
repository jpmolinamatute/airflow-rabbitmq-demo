#! /usr/bin/env python

from os import path, stat, remove as remove_file
import boto3

CONN = boto3.client("s3")


def download_file(bucket, key, single_file):
    valid = True
    CONN.download_file(Bucket=bucket, Key=key, Filename=single_file)
    if not path.isfile(single_file):
        valid = False
    return valid


def upload_file(bucket, key, single_file):
    valid = False
    if path.isfile(single_file):
        if stat(single_file).st_size > 0:
            CONN.upload_file(Filename=single_file, Bucket=bucket, Key=key)
            valid = True
        remove_file(single_file)
    else:
        raise ValueError(f"Error: {single_file} doesn's exists")
    return valid
