#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) > 1:
    program = []
    with open(sys.argv[1]) as f:
        for line in f:
            x = line.split()
            if len(x) > 0 and x[0] != "#":
                program.append(int(x[0], 2))
    cpu.load(program)
    cpu.run()
else:
    print("No program specified! Exiting...")
