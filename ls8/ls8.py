#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) != 2:
    print("usage: ls8.py 'programname'\nExiting...")
    sys.exit(1)
    
program = []
try:
    with open(sys.argv[1]) as f:
        for line in f:
            x = line.split()
            if len(x) == 0 or x[0] == "#":
                continue

            try:
                program.append(int(x[0], 2))
            except ValueError:
                print(f"Invalid value: {x[0]}")
    # print(program)
    cpu.load(program)
    cpu.run()
except FileNotFoundError:
    print(f"Couldn't open file: {sys.argv[1]}")
    sys.exit(2)
