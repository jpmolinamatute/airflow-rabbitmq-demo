#! /usr/bin/env python

import re


def get_uuid(message):
    pattern = "[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}"
    result = False
    if isinstance(message, str):
        result = re.search(pattern, message)
        if result:
            result = result[0]
    return result

if __name__ == "__main__":
    result = get_uuid("000005CA-EA45-9AA2-D6BA-9A936376E459.dataLog")
    print(result)
