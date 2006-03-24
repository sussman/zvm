#
# A class for parsing word dictionaries and performing lexical
# analysis of user input.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZLexerError(Exception):
  "General exception for ZLexer class"



class ZLexer(object):

  def __init__(self, mem):
    self._memory = mem

    # Load the game's 'standard' dictionary into a python
    # dictionary.  It's safe to do this, because the dictionary
    # exists in static memory; it's a read-only thing.  So let's
    # only parse it ONCE, at start-up.  :-)
    dict_addr = self._memory.read_word(0x08)
    self._standard_dict = self.get_dictionary(dict_addr)
    self._standard_separators = self.get_dictionary_word_separators(dict_addr)


  def get_dictionary_word_separators(self, address):
    """Return the list of zscii-codes listed as word separators for
    the dictionary at ADDRESS. """

  def get_dictionary_num_entries(self, address):
    """Return the number of entries in the dictionary at ADDRESS."""

  def get_dictionary_entry_length(self, address):
    """Return the length of each bytestring value in the dictionary at
    ADDRESS.  """

  def get_dictionary(self, address):
    """Load a z-machine-format dictionary at ADDRRESS -- which maps
    zstrings to bytestrings -- into a python dictionary which maps
    ascii strings to the address of the word in the original
    dictionary.  Return the new dictionary."""

  def tokenise_input(self, text_buffer, dict_addr=None):
    """Given an ascii string in TEXT_BUFFER, perform lexical analysis.

    if DICT_ADDR is provided, use the custom dictionary at that
    address to do the analysis, otherwise default to using the game's
    'standard' dictionary.

    Return a list of lists, each list being of the form

       [word,
        byte_address_of_word_in_dictionary (or 0 if not in dictionary),
        number_of_letters_in_word,
        position_of_word_in_text_buffer]
    """
