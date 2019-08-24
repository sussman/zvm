#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmachine import ZMachine

story = open("../stories/zork.z3", "rb").read()

machine = ZMachine(story)

machine.run()
