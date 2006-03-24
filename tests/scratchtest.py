#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmachine import ZMachine

story = file("../stories/amfv.z4").read()

machine = ZMachine(story)

machine.run()
