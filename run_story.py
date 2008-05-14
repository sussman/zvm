#!/usr/bin/env python

import sys
import os.path
from zvm import zmachine, trivialzui

def usage():
    print """Usage: %s <story file>

Run a Z-Machine story under ZVM.
""" % sys.argv[0]
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        usage()
    story_file = sys.argv[1]
    if not os.path.isfile(story_file):
        print "%s is not a file." % story_file
        usage()
    try:
        f = file(story_file)
        story_image = f.read()
        f.close()
    except IOError:
        print "Error accessing %s" % story_file
        sys.exit(1)

    machine = zmachine.ZMachine(story_image,
                                ui=trivialzui.create_zui(),
                                debugmode=True)
    machine.run()

if __name__ == '__main__':
    main()
