#
# A class for parsing word dictionaries and performing lexical
# analysis of user input.  (See section 13 of the z-machine spec.)
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import re
from zstring import ZStringFactory, ZsciiTranslator

class ZLexerError(Exception):
  "General exception for ZLexer class"

# Note that the specification describes tokenisation as a process
# whereby the user's input is divided into words, each word converted
# to a z-string, then searched for in the 'standard' dictionary.  This
# is really inefficient.  Therefore, because the standard dictionary
# is immutable (lives in static memory), this class parses and loads
# it *once* into a private python dictionary.  We can then forever do
# O(1) lookups of unicode words, rather than O(N) lookups of
# zscii-encoded words.

# Note that the main API here (tokenise_input()) can work with any
# dictionary, not just the standard one.

class ZLexer(object):

  def __init__(self, mem):

    self._memory = mem
    self._stringfactory = ZStringFactory(self._memory)
    self._zsciitranslator = ZsciiTranslator(self._memory)

    # Load and parse game's 'standard' dictionary from static memory.
    dict_addr = self._memory.read_word(0x08)
    self._num_entries, self._entry_length, self._separators, entries_addr = \
                       self._parse_dict_header(dict_addr)
    self._dict = self.get_dictionary(dict_addr)


  def _parse_dict_header(self, address):
    """Parse the header of the dictionary at ADDRESS.  Return the
    number of entries, the length of each entry, a list of zscii
    word separators, and an address of the beginning the entries."""

    addr = address
    num_separators = self._memory[addr]
    separators = self._memory[(addr + 1):(addr + num_separators)]
    addr += (1 + num_separators)
    entry_length = self._memory[addr]
    addr += 1
    num_entries = self._memory.read_word(addr)
    addr += 2

    return num_entries, entry_length, separators, addr


  def _tokenise_string(self, string, separators):
     """Split unicode STRING into a list of words, and return the list.
    Whitespace always counts as a word separator, but so do any
    unicode characters provided in the list of SEPARATORS.  Note,
    however, that instances of these separators caunt as words
    themselves."""

     # re.findall(r'[,.;]|\w+', 'abc, def')
     sep_string = ""
     for sep in separators:
       sep_string += sep
     if sep_string == "":
       regex = r"\w+"
     else:
       regex = r"[%s]|\w+" % sep_string

     return re.findall(regex, string)


  #--------- Public APIs -----------


  def get_dictionary(self, address):
    """Load a z-machine-format dictionary at ADDRESS -- which maps
    zstrings to bytestrings -- into a python dictionary which maps
    unicode strings to the address of the word in the original
    dictionary.  Return the new dictionary."""

    dict = {}

    num_entries, entry_length, separators, addr = \
                 self._parse_dict_header(address)

    for i in range(0, num_entries):
      text_key = self._stringfactory.get(addr)
      dict[text_key] = addr
      addr += entry_length

    return dict


  def parse_input(self, string, dict_addr=None):
    """Given a unicode string, parse it into words based on a dictionary.

    if DICT_ADDR is provided, use the custom dictionary at that
    address to do the analysis, otherwise default to using the game's
    'standard' dictionary.

    The dictionary plays two roles: first, it specifies separator
    characters beyond the usual space character.  Second, we need to
    look up each word in the dictionary and return the address.

    Return a list of lists, each list being of the form

       [word, byte_address_of_word_in_dictionary (or 0 if not in dictionary)]
    """

    if dict_addr is None:
      zseparators = self._separators
      dict = self._dict
    else:
      num_entries, entry_length, zseparators, addr = \
                   self._parse_dict_header(dict_addr)
      dict = self.get_dictionary(dict_addr)

    # Our list of word separators are actually zscii codes that must
    # be converted to unicode before we can use them.
    separators = []
    for code in zseparators:
      separators.append(self._zsciitranslator.ztou(code))

    token_list = self._tokenise_string(string, separators)

    final_list = []
    for word in token_list:
      if dict.has_key(word):
        byte_addr = dict[word]
      else:
        byte_addr = 0
      final_list.append([word, byte_addr])

    return final_list
