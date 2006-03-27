#
# A class for parsing word dictionaries and performing lexical
# analysis of user input.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zstring import ZStringFactory, ZsciiTranslator

class ZLexerError(Exception):
  "General exception for ZLexer class"


class ZLexer(object):

  def __init__(self, mem):

    self._memory = mem
    self._stringfactory = ZStringFactory(self._memory)
    self._zsciitranslator = ZsciiTranslator(self._memory)

    # Load the game's 'standard' dictionary into a python
    # dictionary.  It's safe to do this, because the dictionary
    # exists in static memory; it's a read-only thing.  So let's
    # only parse it ONCE, at start-up.  :-)
    self._dict_addr = self._memory.read_word(0x08)
    self._dict = self.get_dictionary(self._dict_addr)
    self._separators = self.get_dictionary_word_separators (self._dict_addr)

  def _separators_to_ascii_string(self, separators):
    """Convert a list of zscii separator codes into an ascii string."""

    string = ""
    for code in separators:
      string += self._zsciitranslator.ztou(code)
    return string

  def get_dictionary_word_separators(self, address):
    """Return the list of zscii-codes listed as word separators for
    the dictionary at ADDRESS. """

    addr = address
    num_separators = self._memory[addr]
    return self._memory[(addr+1):(addr+num_separators)]

  def get_dictionary_num_entries(self, address):
    """Return the number of entries in the dictionary at ADDRESS."""

    addr = address
    num_separators = self._memory[addr]
    addr += (2 + num_separators)
    return self._memory.read_word(addr)

  def get_dictionary_entry_length(self, address):
    """Return the length of each bytestring value in the dictionary at
    ADDRESS.  """

    addr = address
    num_separators = self._memory[addr]
    addr += (1 + num_separators)
    return self._memory[addr]

  def get_dictionary(self, address):
    """Load a z-machine-format dictionary at ADDRESS -- which maps
    zstrings to bytestrings -- into a python dictionary which maps
    ascii strings to the address of the word in the original
    dictionary.  Return the new dictionary."""

    dict = {}

    # read the header
    addr = address
    num_separators = self._memory[addr]
    addr += (1 + num_separators)
    entry_length = self._memory[addr]
    addr += 1
    num_entries = self._memory.read_word(addr)
    addr += 2

    for i in range(0, num_entries):
      text_key = self._stringfactory.get(addr)
      dict[text_key] = addr
      addr += entry_length

    return dict

  def tokenise_input(self, text_addr, len, dict_addr=None):
    """Given an ascii string at zmemory address TEXT_ADDR of length
    LEN bytes, perform lexical analysis.

    if DICT_ADDR is provided, use the custom dictionary at that
    address to do the analysis, otherwise default to using the game's
    'standard' dictionary.

    Return a list of lists, each list being of the form

       [word,
        byte_address_of_word_in_dictionary (or 0 if not in dictionary),
        number_of_letters_in_word,
        address_of_first_letter_of_word]
    """

    main_list = []
    unicode_input = "" ### convert text_addr/len zcodes to unicode string?

    if dict_addr is None:
      dict = self._dict
      separators = self._separators
    else:
      dict = self.get_dictionary(dict_addr)
      separators = self.get_dictionary_word_separators(dict_addr)

    ### assume we get a tokenized list here somehow, splitting the
    ### string on space and other pre-defined separators.

    for word in token_list:
      if dict.has_key(word):
        byte_addr = dict[word]
      else:
        byte_addr = 0
      word_location = text_addr + unicode_input.find(word)
      main_list.append([word, byte_addr, len(word), word_location])

    return main_list
