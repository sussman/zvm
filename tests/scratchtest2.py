#!/usr/bin/env python

import sys
sys.path.append("../zvm")

from zmemory import ZMemory
from zlexer import ZLexer

story = file("../stories/zork.z1").read()

mem = ZMemory(story)
lexer = ZLexer(mem)

print "This story is z version", mem.version

print "Standard dictionary:"
print "   word separators are", lexer._separators
print "   each dict value is", lexer.get_dictionary_entry_length(lexer._dict_addr), "bytes long"
print "   there are", lexer.get_dictionary_num_entries(lexer._dict_addr), "entries in the dictionary"

dict = lexer.get_dictionary(lexer._dict_addr)
print dict

print

print "dictionary has", len(dict.keys()), "items"

print lexer._dict

def lex_split(str, separators):
    split_str = []
    prev_i = 0
    i = 0
    while i < len(str):
        if str[i] in separators:
            split_str.append(str[prev_i:i])
            split_str.append(str[i])
            prev_i = i+1
        i = i+1
