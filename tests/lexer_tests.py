#
# Unit tests for the ZLexer class.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
from unittest import TestCase
from zvm.zmemory import ZMemory
from zvm.zlexer import ZLexer

phrase1 = u"the quick brown fox"
phrase2 = u"the quick, brown,;fox\t might,,be   fe;el.ing ;; odd, .today"
phrase3 = u"the fish, house, and bird are odd and round, no?"

class ZLexerTests(TestCase):
  def setUp(self):
    # We use Graham Nelson's 'curses' game for our unittests.
    storydata = file("stories/curses.z5").read()
    self.mem = ZMemory(storydata)

  def testParseDictionary(self):
    # load game's 'standard' dictionary into a python dictionary
    lexer = ZLexer(self.mem)
    num_keys = len(lexer._dict.keys())
    assert num_keys == lexer._num_entries, \
           "lexer didn't parse all dictionary entries"

  def testTokenisation(self):
    lexer = ZLexer(self.mem)
    separators = (u',', u';', u'.')

    tokens = lexer._tokenise_string(phrase1, separators)
    assert tokens == ['the', 'quick', 'brown', 'fox']

    tokens = lexer._tokenise_string(phrase2, separators)
    assert tokens == ['the', 'quick', ',', 'brown', ',', ';', 'fox', \
                      'might', ',', ',', 'be', 'fe', ';', 'el', '.', 'ing', \
                      ';', ';', 'odd', ',', '.', 'today']

  def testParseInput(self):
    lexer = ZLexer(self.mem)

    results = lexer.parse_input(phrase3)
    assert results == [[u'the', 40278], [u'fish', 33150], [u',', 0], \
                       [u'house', 34572], [u',', 0], [u'and', 29874], \
                       [u'bird', 30576], [u'are', 0], [u'odd', 36525], \
                       [u'and', 29874], [u'round', 38361], [u',', 0], \
                       [u'no', 36300]]
