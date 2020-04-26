#! /usr/bin/env python

import re


def get_uuid(message):
    pattern = "[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}"
    result = re.search(pattern, message)
    if result:
        result = result[0]
    return result
