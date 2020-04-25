#!/usr/bin/env python

import sys
import json
from os import environ, path
from datetime import datetime
from dronelogs.shared.db_conn import get_db_conn
from dronelogs.shared.get_uuid_from_string import get_uuid, get_file_from_key
from dronelogs.shared.s3_upload_download import download_file, upload_file


def check_dependency(connection, uuid):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]
    sql_str = f"SELECT * FROM {tablename} "
    sql_str += "WHERE uuid = %s;"
    cursor.execute(sql_str, (uuid,))
    result = cursor.fetchone()
    cursor.close()
    return result


def insert_row_table(connection, uuid, file_name):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]
    values = (uuid, file_name, False, datetime.now())
    sql_str = f"INSERT INTO {tablename} "
    sql_str += "(uuid, file_name, decrypt_status, started_at) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql_str, values)
    connection.commit()
    cursor.close()


def process_sub_index(connection, sub_index_name):
    file_name = get_file_from_key(sub_index_name)
    download_file(environ["AWS_BUCKET_NAME"], sub_index_name, f"./{file_name}")
    with open(f"./{file_name}", "r") as text_file:
        for line in text_file:
            uuid = get_uuid(line)
            if isinstance(uuid, str):
                if check_dependency(connection, uuid):
                    print(f"UUID: {uuid} already in DB")
                else:
                    insert_row_table(connection, uuid, line)
            else:
                print(f"Error: wrong UUID {line}")


def init(input_dict):
    file_list = input_dict.replace("'", '"')
    file_list = json.loads(file_list)
    if "file_list" in file_list and isinstance(file_list["file_list"], list):
        connection = get_db_conn()
        for fl in file_list["file_list"]:
            process_sub_index(connection, fl)
        connection.close()
    else:
        raise Exception("Error: file_list wasn't provided")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        init(sys.argv[1])
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
