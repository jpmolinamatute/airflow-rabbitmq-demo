#!/usr/bin/env python
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for line in sys.argv[1].split("delimiter"):
            print(line)
        sys.exit(0)
    else:
        print("failed!")
        sys.exit(2)
