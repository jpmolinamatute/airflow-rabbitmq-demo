#!/usr/bin/env python
import sys
from os import environ
from datetime import datetime
from dronelogs.shared.db_conn import get_db_conn
from dronelogs.shared.get_uuid_from_string import get_uuid


def db_insert(body):
    uuid = get_uuid(body)
    if isinstance(uuid, str):
        print(f"Valid {uuid}!")
        connection = get_db_conn()
        if connection:
            tablename = environ['PIPILE_NAME']
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {tablename} WHERE uuid = '{uuid}' LIMIT 1;")
            if cursor.rowcount == 0:
                values = (uuid, body, '[{"step": "init", "status": "SUCCESS"}]', datetime.now())
                sql_str = f"INSERT INTO {tablename} "
                sql_str += "(uuid, file_name, progress, started_at) VALUES (%s, %s, %s, %s)"
                print(f"Inserting {uuid} into {tablename}")
                cursor.execute(sql_str, values)
                connection.commit()
            else:
                print(f"{uuid} alredy exists in {tablename}")
            cursor.close()
            connection.close()
        else:
            raise TypeError("Error: Connection to DB failed, most likely wrong credentials")
    else:
        print(f"Error: wrong UUID {body}")


def init(file_list):
    if isinstance(file_list, list):
        counter = 1
        for key in file_list:
            uuid = key['Key']
            print(f"Initializing: {uuid}")
            db_insert(uuid)
            counter += 1
        print(f'Total files sent per thread: {counter}')
    else:
        raise ValueError('Error: file_list is not a list')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        init(sys.argv[1].split("delimiter"))
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
