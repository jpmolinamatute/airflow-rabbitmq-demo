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


def get_file_path(connection, uuid):
    cursor = connection.cursor()
    tablename = environ["PIPILE_NAME"]
    sql_str = "SELECT file_name "
    sql_str += f"FROM {tablename} "
    sql_str += "WHERE uuid = %s;"
    cursor.execute(sql_str, (uuid,))
    result = cursor.fetchone()
    if isinstance(result, tuple):
        result = result[0]
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


def init(input_dict):
    # result = None
    # with open("/airflow/xcom/return.json", mode="r") as file_obj:
    #     result = json.load(file_obj)
    connection = get_db_conn()

    if connection:
        sub_index_name = f'subindex-{input_dict["batch_number"]}.txt'
        download_file(
            environ["AWS_BUCKET_NAME"],
            f'{input_dict["index_prefix"]}/{sub_index_name}',
            f"./{sub_index_name}",
        )
        with open(f"./{sub_index_name}", mode="r") as file_obj:
            for uuid in file_obj:
                uuid = get_uuid(uuid)
                if uuid:
                    if check_dependency(connection, uuid):
                        file_path = get_file_path(connection, uuid)
                        if isinstance(file_path, str):
                            success = copy_files(uuid, file_path)
                            update_table_row(connection, uuid, success)
                        else:
                            print(f"Error: {uuid} doesn't have a file_name in table")
                elif uuid == "empty":
                    print(f"Info: File is empty")
                else:
                    print(f"Warning: wronge uuid: {uuid}")
        connection.close()
    else:
        raise Exception("Error: Connection to DB failed")


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
