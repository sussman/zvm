#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmachine import ZMachine

story = file("../stories/zork.z3").read()

machine = ZMachine(story)

machine.run()
