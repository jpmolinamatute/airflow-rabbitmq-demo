#! /usr/bin/env python

import re


def get_file_from_key(single_file):
    file_array = single_file.split("/")
    index = 0 if len(file_array) == 1 else -1
    return file_array[index]


def get_uuid(message):
    pattern = "[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}"
    result = False
    if isinstance(message, str):
        if message == "empty":
            result = "empty"
        else:
            result = re.search(pattern, message.upper())
            if result:
                result = result[0].upper()
    return result


if __name__ == "__main__":
    UUID = get_uuid("000005CA-EA45-9AA2-D6BA-9A936376E459.dataLog")
    print(UUID)
