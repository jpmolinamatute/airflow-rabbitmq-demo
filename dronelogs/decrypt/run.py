#!/usr/bin/env python
import sys
import json
from os import environ, rename
from datetime import datetime
from dronelogs.shared.get_uuid_from_string import get_file_from_key, get_uuid
from dronelogs.shared.s3_upload_download import download_file, upload_file
from dronelogs.shared.db_conn import get_db_conn


def decrypt(single_file, uuid):
    print(f"Decrypting {single_file}")
    rename(single_file, f"./{uuid}.csv")
    return True


def check_dependency(connection, uuid):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]

    sql_str = f"SELECT * FROM {tablename} "
    sql_str += "WHERE uuid = %s "
    sql_str += "AND NOT decrypt_status;"

    cursor.execute(sql_str, (uuid,))
    result = cursor.fetchone()
    cursor.close()

    return result


def update_table_row(connection, uuid, success=False):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]
    sql_str = f"UPDATE {tablename} "
    sql_str += "SET decrypt_status = %s, completed_at = %s "
    sql_str += "WHERE uuid = %s;"
    values = (success, datetime.now(), uuid)
    cursor.execute(sql_str, values)
    connection.commit()
    cursor.close()


def copy_files(uuid, single_file):
    success = True
    try:
        localfile = get_file_from_key(single_file)
        download_file(environ["AWS_RAW_S3_BUCKET"], single_file, f"./{localfile}")
        decrypt(f"./{localfile}", uuid)
        upload_file(environ["AWS_CLEAN_S3_BUCKET"], f"juanpa-copy/{uuid}.csv", f"./{uuid}.csv")
    except Exception as error:
        print(error)
        success = False
    return success


def process_sub_index(connection, sub_index_name):
    file_name = get_file_from_key(sub_index_name)
    download_file(environ["AWS_BUCKET_NAME"], sub_index_name, f"./{file_name}")
    with open(f"./{file_name}", "r") as text_file:
        for line in text_file:
            uuid = get_uuid(line)
            if isinstance(uuid, str):
                if check_dependency(connection, uuid):
                    # success = copy_files(uuid, line)
                    success = True
                    print(f"Updating row with {uuid}")
                    update_table_row(connection, uuid, success)
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
