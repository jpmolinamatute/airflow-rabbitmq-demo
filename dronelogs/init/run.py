#!/usr/bin/env python

import sys
import json
from time import sleep
from os import environ, path
from datetime import datetime
from dronelogs.shared.db_conn import get_db_conn
from dronelogs.shared.get_uuid_from_string import get_uuid
from dronelogs.shared.s3_upload_download import download_file, upload_file


def bufcount(file_name):
    file_obj = open(file_name)
    lines = 0
    buf_size = 1024 * 1024
    buf = file_obj.read(buf_size)
    while buf:
        lines += buf.count("\n")
        buf = file_obj.read(buf_size)
    file_obj.close()
    return lines


def check_dependency(connection, uuid):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]
    sql_str = f"SELECT * FROM {tablename} "
    sql_str += "WHERE uuid = %s;"
    cursor.execute(sql_str, (uuid,))
    result = cursor.fetchone()
    cursor.close()
    return result


def insert_row(connection, uuid, file_name):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]
    values = (uuid, file_name, datetime.now())
    sql_str = f"INSERT INTO {tablename} "
    sql_str += "(uuid, file_name, started_at) VALUES (%s, %s, %s)"
    cursor.execute(sql_str, values)
    connection.commit()
    cursor.close()


def get_range_file(file_name, batch_number, worklaod):
    count = bufcount(file_name)
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


def write_summary(sub_index_path):
    if path.isdir("/airflow/xcom"):
        result = {"sub_index_path": sub_index_path}
        with open("/airflow/xcom/return.json", mode="w") as file_obj:
            json.dump(result, file_obj)
    else:
        raise ValueError("Error: /airflow/xcom doesn't exist")


# def get_index_file(input_dict):
#     keep_going = True
#     while keep_going:
#         try:
#             download_file(
#                 environ["AWS_BUCKET_NAME"],
#                 f'{input_dict["index_prefix"]}/{input_dict["index_file"]}',
#                 f'./{input_dict["index_file"]}',
#             )
#             keep_going = False
#         except Exception:
#             print("Waiting 30 seconds")
#             sleep(30)


def get_file_list(input_dict):
    file_range = get_range_file(
        f'./{input_dict["index_file"]}',
        int(input_dict["batch_number"]),
        int(input_dict["worklaod"]),
    )
    with open(f'./{input_dict["index_file"]}', "r") as text_file:
        lines = text_file.readlines()
        lines = lines[file_range[0] : file_range[1]]
    return {"list": lines, "starts": file_range[0], "ends": file_range[1]}


def init(input_dict):
    # get_index_file(input_dict)
    download_file(
        environ["AWS_BUCKET_NAME"],
        f'{input_dict["index_prefix"]}/{input_dict["index_file"]}',
        f'./{input_dict["index_file"]}',
    )

    result = get_file_list(input_dict)
    connection = get_db_conn()
    if connection:
        sub_index_name = f'subindex-{result["starts"]}-{result["ends"]}.txt'
        sub_index_obj = open(f"./{sub_index_name}", "a+")
        for single_line in result["list"]:
            file_name = single_line.rstrip("\n")
            uuid = get_uuid(file_name)
            if isinstance(uuid, str):
                if check_dependency(connection, uuid):
                    print(f"UUID: {uuid} already in DB")
                else:
                    insert_row(connection, uuid, file_name)
                    sub_index_obj.write(f"{uuid}\n")
            else:
                print(f"Error: wrong UUID {file_name}")
        connection.close()
        sub_index_obj.close()
        upload_file(
            environ["AWS_BUCKET_NAME"],
            f'{input_dict["index_prefix"]}/{sub_index_name}',
            f"./{sub_index_name}",
        )
        write_summary(f'{input_dict["index_prefix"]}/{sub_index_name}')
    else:
        raise "Error: Connection to DB failed"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        GLOBAL_INPUT = json.loads(sys.argv[1])
        init(GLOBAL_INPUT)
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
