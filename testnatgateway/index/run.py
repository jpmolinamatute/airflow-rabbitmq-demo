#!/usr/bin/env python

import sys
from os import environ
from testnatgateway.shared.s3_upload_download import upload_file
import boto3

CONN = boto3.client("s3", region_name="us-east-2")


def create_no_lines_file(no_lines):
    with open("./no_lines.txt", "w") as file_obj:
        file_obj.write(str(no_lines))


def create_index(index_file_name):
    bucket = environ["AWS_RAW_S3_BUCKET"]
    prefix = environ["AWS_RAW_S3_PREFIX"]
    objs = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" not in objs or len(objs["Contents"]) == 0:
        raise Exception(f"Error: there are no files in {bucket}")

    no_lines = 0
    keep_going = True
    index_file_obj = open(f"./{index_file_name}", "w+")
    while keep_going:
        for name in objs["Contents"]:
            no_lines += 1
            index_file_obj.write(f'{name["Key"]}\n')
        if "NextContinuationToken" in objs:
            objs = CONN.list_objects_v2(
                Bucket=bucket, Prefix=prefix, ContinuationToken=objs["NextContinuationToken"]
            )
        else:
            keep_going = False
    index_file_obj.close()
    return no_lines


def init(file_prefix, file_name):
    # CONN.delete_object(Bucket=environ["AWS_BUCKET_NAME"], Key=f"{file_prefix}/{file_name}")
    no_lines = create_index(file_name)
    if no_lines > 0:
        create_no_lines_file(no_lines)
        upload_file(environ["AWS_BUCKET_NAME"], f"{file_prefix}/{file_name}", f"./{file_name}")
        upload_file(environ["AWS_BUCKET_NAME"], f"{file_prefix}/no_lines.txt", "./no_lines.txt")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        init(sys.argv[1], sys.argv[2])
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
