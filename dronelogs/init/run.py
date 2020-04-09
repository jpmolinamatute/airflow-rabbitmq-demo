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
    f = open(file_name)
    lines = 0
    buf_size = 1024 * 1024
    buf = f.read(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = f.read(buf_size)
    f.close()
    return lines


def check_dependency(cursor, uuid):
    tablename = environ['PIPILE_NAME']
    query = f"SELECT * FROM {tablename} "
    query += "WHERE uuid = %s;"
    cursor.execute(query, (uuid,))
    return cursor.fetchone()

def insert_row(cursor, uuid, file_name):
    tablename = environ['PIPILE_NAME']
    values = (uuid, file_name, datetime.now())
    sql_str = f"INSERT INTO {tablename} "
    sql_str += "(uuid, file_name, started_at) VALUES (%s, %s, %s)"
    cursor.execute(sql_str, values)

def write_db(connection, uuid, file_name):
    if connection:
        cursor = connection.cursor()
        dependency_met = check_dependency(cursor, uuid)
        if dependency_met is None:
            insert_row(cursor, uuid, file_name)
            connection.commit()
        cursor.close()
    else:
        raise TypeError("Error: Connection to DB failed")

def get_range_file(file_name, batch_number, worklaod):

    count = bufcount(file_name)
    batch_size = int(count / worklaod)
    batch_range = None

    if batch_number == 1:
        batch_range = (0, batch_size)
    elif batch_number <= worklaod:
        batch_range = (batch_size * (batch_number - 1), batch_size * batch_number)
    elif batch_number == worklaod:
        batch_range = (batch_size * (batch_number - 1), count + 1)
    else:
        raise ValueError("Error: batch_number must be greater than 0")

    return batch_range

def write_summary(starts, ends):
    if path.isdir("/airflow/xcom"):
        result = {
            "start": starts,
            "end": ends
        }
        with open("/airflow/xcom/return.json", mode="w") as f:
            json.dump(result, f)
    else:
        raise ValueError("Error: /airflow/xcom doesn't exist")

def get_index_file(input_dict):
    keep_going = True
    while keep_going:
        try:
            download_file(
                environ['AWS_BUCKET_NAME'],
                f'{input_dict["index_prefix"]}/{input_dict["index_file"]}',
                f'./{input_dict["index_file"]}'
            )
            keep_going = False
        except:
            print("Waiting 60 seconds")
            sleep(60)

def get_file_list(input_dict):
    file_range = get_range_file(
        f'./{input_dict["index_file"]}',
        int(input_dict["batch_number"]),
        int(input_dict["worklaod"])
    )
    with open(f'./{input_dict["index_file"]}', "r") as text_file:
        lines = text_file.readlines()
        lines = lines[file_range[0]:file_range[1]]
    return {"list": lines, "starts": file_range[0], "ends": file_range[1]}

def init(input_dict):
    get_index_file(input_dict)
    result = get_file_list(input_dict)
    connection = get_db_conn()
    sub_index_name = f'subindex-{result["starts"]}-{result["ends"]}.txt'
    sub_index_obj = open(f'./{sub_index_name}', 'a+')
    for single_line in result["list"]:
        file_name = single_line.rstrip('\n')
        uuid = get_uuid(file_name)
        if isinstance(uuid, str):
            write_db(connection, uuid, file_name)
            sub_index_obj.write(f"{uuid}\n")
        else:
            print(f"Error: wrong UUID {file_name}")
    connection.close()
    sub_index_obj.close()
    upload_file(
        environ['AWS_BUCKET_NAME'],
        f'{input_dict["index_prefix"]}/{sub_index_name}',
        f'./{sub_index_name}'
    )
    write_summary(result["starts"], result["ends"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        global_input = json.loads(sys.argv[1])
        init(global_input)
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
