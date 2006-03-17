#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmemory import *
from zopdecoder import *
from zobjectparser import *
from zstring import *

story = file("../stories/trinity.z4").read()
mem = ZMemory(story)
decoder = ZOpDecoder(mem)
objectparser = ZObjectParser(mem)
stringfactory = ZStringFactory(mem)


# Execution starts at the byte address given by the word at address 6
decoder.program_counter = mem.read_word(0x06)

print "initial instruction is at address", decoder.program_counter

print "initial opcode is", mem[decoder.program_counter]


print "decoded instruction is", decoder.get_next_instruction()

print "global variables begin at", mem._global_variable_start
print "global variable 0x10 has value of", mem.read_global(0x10)

print "Shortname of object 1 is ", objectparser.get_shortname(1)
