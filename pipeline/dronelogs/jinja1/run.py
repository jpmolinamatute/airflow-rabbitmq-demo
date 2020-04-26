#!/usr/bin/env python
from os import path
import sys
import json


def init():
    if path.isdir("/airflow/xcom"):
        result = {"sub_index_path": "blah blah blah"}
        with open("/airflow/xcom/return.json", mode="w") as file_obj:
            json.dump(result, file_obj)
    else:
        raise ValueError("Error: /airflow/xcom doesn't exist")


if __name__ == "__main__":
    init()
    sys.exit(0)
