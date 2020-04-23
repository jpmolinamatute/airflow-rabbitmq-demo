#!/usr/bin/env python
import sys
import json
import uuid
from os import environ
from testnatgateway.shared.get_uuid_from_string import get_file_from_key
from testnatgateway.shared.s3_upload_download import download_file, upload_file


def copy_files(single_file):
    localfile = get_file_from_key(single_file)
    uuid_string = uuid.uuid4()
    uuid_string = str(uuid_string)
    if not download_file(environ["AWS_RAW_S3_BUCKET"], single_file, f"./{localfile}"):
        raise Exception(f"Failed to Download file {environ['AWS_RAW_S3_BUCKET']}/single_file")
    upload_file(environ["AWS_CLEAN_S3_BUCKET"], f"juanpa-copy/{uuid_string}", f"./{localfile}")


def get_lines_count(input_dict):
    no_lines = "no_lines.txt"
    num_lines = None
    if download_file(
        environ["AWS_BUCKET_NAME"], f'{input_dict["index_prefix"]}/{no_lines}', f"./{no_lines}",
    ):
        with open(f"./{no_lines}", "r") as file_obj:
            one_line = file_obj.readlines()
            if len(one_line) > 0:
                num_lines = int(one_line[0])
    else:
        msg = f'Error: {input_dict["index_prefix"]}/{no_lines} '
        msg += f' doesn\'t exists in S3 {environ["AWS_BUCKET_NAME"]}'
        raise Exception(msg)
    return num_lines


def get_range_file(count, batch_number, worklaod):
    batch_size = int(round(count / worklaod))
    batch_range = None

    if batch_number == 1:
        batch_range = (0, batch_size)
    elif batch_number < worklaod:
        batch_range = (batch_size * (batch_number - 1), batch_size * batch_number)
    elif batch_number == worklaod:
        batch_range = (batch_size * (batch_number - 1), count + 1)
    else:
        raise ValueError("Error: batch_number must be greater than 0")

    return batch_range


def get_file_list(input_dict):
    num_lines = get_lines_count(input_dict)
    file_range = get_range_file(
        num_lines, int(input_dict["batch_number"]), int(input_dict["worklaod"]),
    )
    with open(f'./{input_dict["index_file"]}', "r") as text_file:
        lines = text_file.readlines()
        lines = lines[file_range[0] : file_range[1]]
    return {"list": lines, "starts": file_range[0], "ends": file_range[1]}


def init(input_dict):
    if not download_file(
        environ["AWS_BUCKET_NAME"],
        f'{input_dict["index_prefix"]}/{input_dict["index_file"]}',
        f'./{input_dict["index_file"]}',
    ):
        msg = f'Error: {input_dict["index_prefix"]}/{input_dict["index_file"]} '
        msg += f' doesn\'t exists in S3 {environ["AWS_BUCKET_NAME"]}'
        raise Exception(msg)

    result = get_file_list(input_dict)
    for single_line in result["list"]:
        line = single_line.rstrip("\n")
        print(line)
        copy_files(line)


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
