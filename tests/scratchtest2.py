#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmemory import ZMemory
from zlexer import ZLexer

story = file("../stories/amfv.z4").read()

mem = ZMemory(story)
lexer = ZLexer(mem)

print "Standard dictionary:"
print "   word separators are", lexer._separators
print "   each dict value is", lexer.get_dictionary_entry_length(lexer._dict_addr), "bytes long"
print "   there are", lexer.get_dictionary_num_entries(lexer._dict_addr), "entries in the dictionary"

dict = lexer.get_dictionary(lexer._dict_addr)
print dict
