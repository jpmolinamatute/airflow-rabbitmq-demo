#!/usr/bin/env python

import sys
from os import environ
from datetime import datetime
from dronelogs.shared.db_conn import get_db_conn
from dronelogs.shared.get_uuid_from_string import get_uuid

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

def init(file_name):
    uuid = get_uuid(file_name)
    if isinstance(uuid, str):
        connection = get_db_conn()
        if connection:
            cursor = connection.cursor()
            dependency_met = check_dependency(cursor, uuid)
            if dependency_met is None:
                insert_row(cursor, uuid, file_name)
                connection.commit()
            cursor.close()
            connection.close()
        else:
            raise TypeError("Error: Connection to DB failed, most likely wrong credentials")
    else:
        print(f"Error: wrong UUID {file_name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for line in sys.argv[1].split(" "):
            init(line)
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
