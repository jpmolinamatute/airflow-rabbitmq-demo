#!/usr/bin/env python
import sys
from os import environ, path, rename, remove as remove_file
from datetime import datetime
import boto3
from dronelogs.shared.get_uuid_from_string import get_uuid
from dronelogs.shared.db_conn import get_db_conn

CONN = boto3.client('s3')

bucket = 'rein-ai-data-warehouse'
prefix = 'juanpa'

def get_file_from_key(single_file):
    file_array = single_file.split("/")
    index = 0 if len(file_array) == 1 else -1
    return file_array[index]

def download_file(single_file):
    file_downloaded = get_file_from_key(single_file)
    valid = True
    CONN.download_file(bucket, single_file, f'./{file_downloaded}')
    if not path.isfile(f'./{file_downloaded}'):
        valid = False
    return valid

def upload_file(uuid):
    CONN.upload_file(
        Filename=f'./{uuid}.csv',
        Bucket='rein-ai-data-warehouse-clean',
        Key=f'juanpa-copy/{uuid}.csv'
    )
    remove_file(f'./{uuid}.csv')
    return True

def decrypt(single_file, uuid):
    print(f'Decrypting {single_file}')
    file_downloaded = get_file_from_key(single_file)
    rename(f'./{file_downloaded}', f'./{uuid}.csv')
    return True

def check_dependency(cursor, uuid):
    tablename = environ['PIPILE_NAME']
    query = f"SELECT * FROM {tablename} "
    query += "WHERE uuid = %s "
    query += "AND ( "
    query += "decrypt_status IS %s "
    query += "OR decrypt_status IS NULL);"
    cursor.execute(query, (uuid, False))
    return cursor.fetchone()

def update_row(cursor, uuid, success=False):
    tablename = environ['PIPILE_NAME']
    sql_str = f"UPDATE {tablename} "
    sql_str += "SET decrypt_status = %s, completed_at = %s "
    sql_str += "WHERE uuid = %s;"
    values = (success, datetime.now(), uuid)
    cursor.execute(sql_str, values)

def copy_files(single_file):
    uuid = get_uuid(single_file)
    if isinstance(uuid, str):
        connection = get_db_conn()
        if connection:
            cursor = connection.cursor()
            dependency_met = check_dependency(cursor, uuid)
            if dependency_met is not None:
                success = True
                if download_file(single_file):
                    if not decrypt(single_file, uuid) or not upload_file(uuid):
                        success = False
                else:
                    success = False
                update_row(cursor, uuid, success)
                connection.commit()
            cursor.close()
            connection.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for line in sys.argv[1].split(" "):
            copy_files(line)
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
