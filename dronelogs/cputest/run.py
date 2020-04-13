#!/usr/bin/env python

import sys
from os import environ
import random


def init():
    in_square = in_circle = pi = 0
    for i in range(10000000):
        x = random.random()
        y = random.random()
        dist = (x * x + y * y) ** 0.5

        in_square += 1
        if dist <= 1.0:
            in_circle += 1

    pi = 4 * in_circle / in_square
    print(pi)


if __name__ == "__main__":
    for num in range(10):
        init()
    sys.exit(0)
