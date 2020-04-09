#!/usr/bin/env python

import sys
from os import environ
from dronelogs.shared.s3_upload_download import upload_file
import boto3

def create_index(index_file_name):
    conn = boto3.client('s3')
    bucket = environ['AWS_RAW_S3_BUCKET']
    prefix = environ['AWS_RAW_S3_PREFIX']
    objs = conn.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if 'Contents' not in objs or len(objs['Contents']) == 0:
        raise Exception(f"Error: there are no files in {bucket}")
    i = 1
    files_counter = 0
    keep_going = True
    days_file = open(f'./{index_file_name}', 'w+')
    while keep_going:
        for name in objs['Contents']:
            files_counter += 1
            days_file.write(f'{name["Key"]}\n')
        if 'NextContinuationToken' in objs:
            objs = conn.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                ContinuationToken=objs['NextContinuationToken']
            )
            i += 1
        else:
            keep_going = False
    days_file.close()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_prefix = sys.argv[1]
        file_name = sys.argv[2]
        create_index(file_name)
        upload_file(environ['AWS_BUCKET_NAME'], f'{file_prefix}/{file_name}', f'./{file_name}')
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
