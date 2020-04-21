#!/usr/bin/env python
import sys
import json
from os import environ
from testnatgateway.shared.get_uuid_from_string import get_file_from_key
from testnatgateway.shared.s3_upload_download import download_file, upload_file


def copy_files(single_file):
    success = True
    try:
        localfile = get_file_from_key(single_file)
        download_file(environ["AWS_RAW_S3_BUCKET"], single_file, f"./{localfile}")
        upload_file(environ["AWS_CLEAN_S3_BUCKET"], f"juanpa-copy/{localfile}", f"./{localfile}")
    except Exception as error:
        print(error)
        success = False
    return success


def init(input_dict):
    sub_index_name = f'subindex-{input_dict["batch_number"]}.txt'
    download_file(
        environ["AWS_BUCKET_NAME"],
        f'{input_dict["index_prefix"]}/{sub_index_name}',
        f"./{sub_index_name}",
    )
    with open(f"./{sub_index_name}", mode="r") as file_obj:
        for file_path in file_obj:
            copy_files(file_path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        GLOBAL_INPUT = json.loads(sys.argv[1])
        init(GLOBAL_INPUT)
        # print("================================================================")
        # print("================================================================")
        # print(environ["BATCH_FILE"])
        # print("================================================================")
        # print("================================================================")
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
