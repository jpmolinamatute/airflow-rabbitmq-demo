#!/usr/bin/env python

import sys
from os import environ
from dronelogs.shared.s3_upload_download import upload_file
import boto3

CONN = boto3.client("s3")


def create_no_lines_file(index_prefix, no_lines):
    with open("./no_lines.txt", "w") as file_obj:
        file_obj.write(str(no_lines))
    upload_file(environ["AWS_BUCKET_NAME"], f"{index_prefix}/no_lines.txt", "./no_lines.txt")


def init(index_prefix, index_file):
    bucket = environ["AWS_RAW_S3_BUCKET"]
    prefix = environ["AWS_RAW_S3_PREFIX"]
    objs = CONN.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" not in objs or len(objs["Contents"]) == 0:
        raise Exception(f"Error: there are no files in {bucket}")

    no_lines = 0
    no_files = 0
    keep_going = True
    index_file_obj = open(f"./{index_file}", "w+")
    while keep_going:
        sub_index_file = open("./sub-index.txt", "w+")
        start_point = no_lines + 1
        for name in objs["Contents"]:
            no_lines += 1
            sub_index_file.write(f'{name["Key"]}\n')
        sub_index_file.close()
        upload_file_name = f"{index_prefix}/sub-index-{str(start_point)}-{str(no_lines)}"
        upload_file(environ["AWS_BUCKET_NAME"], upload_file_name, "./sub-index.txt")
        index_file_obj.write(f"{upload_file_name}\n")
        no_files += 1
        if "NextContinuationToken" in objs:
            objs = CONN.list_objects_v2(
                Bucket=bucket, Prefix=prefix, ContinuationToken=objs["NextContinuationToken"]
            )
        else:
            keep_going = False
    index_file_obj.close()
    create_no_lines_file(index_prefix, no_files)
    upload_file(environ["AWS_BUCKET_NAME"], f"{index_prefix}/{index_file}", f"./{index_file}")


if __name__ == "__main__":
    if len(sys.argv) > 2:
        init(sys.argv[1], sys.argv[2])
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
