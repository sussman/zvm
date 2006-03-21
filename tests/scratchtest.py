#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmemory import *
from zopdecoder import *
from zobjectparser import *
from zstring import *

story = file("../stories/amfv.z4").read()
mem = ZMemory(story)
decoder = ZOpDecoder(mem)
objectparser = ZObjectParser(mem)


# Execution starts at the byte address given by the word at address 6
decoder.program_counter = mem.read_word(0x06)

print "initial instruction is at address", decoder.program_counter

print "initial opcode is", mem[decoder.program_counter]


print "decoded instruction is", decoder.get_next_instruction()

print "global variables begin at", mem._global_variable_start
print "global variable 0x10 has value of", mem.read_global(0x10)

for i in range(1, 10):
  print "Shortname of object", i, "is", objectparser.get_shortname(i)
