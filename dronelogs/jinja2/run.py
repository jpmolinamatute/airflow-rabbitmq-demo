#!/usr/bin/env python

import sys
from os import environ


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("================================================================")
        print("================================================================")
        print(environ["BATCH_FILE"])
        print(sys.argv[1])
        print("================================================================")
        print("================================================================")
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
