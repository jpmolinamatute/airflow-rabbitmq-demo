#!/usr/bin/env python
import sys
from os import environ, rename
from datetime import datetime
from dronelogs.shared.get_uuid_from_string import get_uuid, get_file_from_key
from dronelogs.shared.s3_upload_download import download_file, upload_file
from dronelogs.shared.db_conn import get_db_conn

def decrypt(single_file, uuid):
    print(f'Decrypting {single_file}')
    rename(single_file, f'./{uuid}.csv')
    return True

def check_dependency(cursor, uuid):
    tablename = environ['PIPILE_NAME']
    query = f"SELECT * FROM {tablename} "
    query += "WHERE uuid = %s "
    query += "AND ( "
    query += f"NOT decrypt_status "
    query += "OR decrypt_status IS NULL);"
    cursor.execute(query, (uuid,))
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
                localfile = get_file_from_key(single_file)
                if not download_file(environ['AWS_RAW_S3_BUCKET'], single_file, f'./{localfile}') or\
                not decrypt(f'./{localfile}', uuid) or\
                not upload_file(environ['AWS_CLEAN_S3_BUCKET'], f'juanpa-copy/{uuid}.csv', f'./{uuid}.csv'):
                    success = False
                update_row(cursor, uuid, success)
                connection.commit()
            cursor.close()
            connection.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # global_input = json.loads(sys.argv[1])
        print(sys.argv[1])
        if path.isfile("/airflow/xcom/return.json"):
            with open("/airflow/xcom/return.json", mode="r") as f:
                for line in f:
                    print(line)
        else:
            print("Error: /airflow/xcom/return.json doesn't exists")
        # for line in sys.argv[1].split(" "):
        #     copy_files(line)
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
