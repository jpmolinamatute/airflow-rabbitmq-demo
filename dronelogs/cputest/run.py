#!/usr/bin/env python

import sys
import random
from os import environ
import boto3
from dronelogs.shared.s3_upload_download import upload_file

CONN = boto3.client("s3")


def init():
    in_square = in_circle = pi = 0
    for i in range(10000000):
        x = random.random()
        y = random.random()
        dist = (x * x + y * y) ** 0.5

        in_square += 1
        if dist <= 1.0:
            in_circle += 1

    pi = 4 * in_circle / in_square
    print(pi)


def list_files(index_file_name):
    bucket = environ["AWS_RAW_S3_BUCKET"]
    prefix = environ["AWS_RAW_S3_PREFIX"]
    objs = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" not in objs or len(objs["Contents"]) == 0:
        raise Exception(f"Error: there are no files in {bucket}")

    no_lines = 0
    keep_going = True
    days_file = open(f"./{index_file_name}", "w+")
    print("While loop start now")
    while keep_going:
        for name in objs["Contents"]:
            no_lines += 1
            days_file.write(f'{name["Key"]}\n')
        if "NextContinuationToken" in objs:
            objs = CONN.list_objects_v2(
                Bucket=bucket, Prefix=prefix, ContinuationToken=objs["NextContinuationToken"]
            )

        else:
            keep_going = False
    days_file.close()
    print("While loop ended")
    return no_lines


if __name__ == "__main__":
    for num in range(10):
        print(str(num))
        init()
    # print("cputest has started!!!")
    # list_files("hola.txt")
    # upload_file(environ["AWS_CLEAN_S3_BUCKET"], "deleteme/hola.txt", "./hola.txt")
    sys.exit(0)
