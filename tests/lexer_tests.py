#
# Unit tests for the ZLexer class.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
from unittest import TestCase
from zvm.zmemory import ZMemory
from zvm.zlexer import ZLexer

phrase1 = "the quick brown fox"
phrase2 = "the quick, brown,;fox\t might,,be   fe;el.ing ;; odd, .today"
phrase3 = "the fish, house, and bird are odd and round, no?"

class ZLexerTests(TestCase):
  def setUp(self):
    # We use Graham Nelson's 'curses' game for our unittests.
    storydata = open("stories/curses.z5", "rb").read()
    self.mem = ZMemory(storydata)

  def testParseDictionary(self):
    # load game's 'standard' dictionary into a python dictionary
    lexer = ZLexer(self.mem)
    num_keys = len(list(lexer._dict.keys()))
    assert num_keys == lexer._num_entries, \
           "lexer didn't parse all dictionary entries"

  def testTokenisation(self):
    lexer = ZLexer(self.mem)
    separators = (',', ';', '.')

    tokens = lexer._tokenise_string(phrase1, separators)
    assert tokens == ['the', 'quick', 'brown', 'fox']

    tokens = lexer._tokenise_string(phrase2, separators)
    assert tokens == ['the', 'quick', ',', 'brown', ',', ';', 'fox', \
                      'might', ',', ',', 'be', 'fe', ';', 'el', '.', 'ing', \
                      ';', ';', 'odd', ',', '.', 'today']

  def testParseInput(self):
    lexer = ZLexer(self.mem)

    results = lexer.parse_input(phrase3)
    assert results == [['the', 40278], ['fish', 33150], [',', 0], \
                       ['house', 34572], [',', 0], ['and', 29874], \
                       ['bird', 30576], ['are', 0], ['odd', 36525], \
                       ['and', 29874], ['round', 38361], [',', 0], \
                       ['no', 36300]]
