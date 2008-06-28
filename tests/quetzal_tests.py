#
# Unit tests for the two quetzal classes.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
from unittest import TestCase
from zvm import zmachine, trivialzui
from zvm import quetzal

def make_zmachine():
    # We use Graham Nelson's 'curses' game for our unittests.
    story_image = file("stories/curses.z5").read()
    ui = trivialzui.create_zui()
    return zmachine.ZMachine(story_image, ui, debugmode=True)

class QuetzalWriterTest(TestCase):
  def testWriteQuetzalFile(self):
    machine = make_zmachine()
    writer = quetzal.QuetzalWriter(machine)
    writer.write("tests/test_savefile")

class QuetzalParserTest(TestCase):
  def testLoadCurses(self):
    "Try loading a specific curses save-file, verify expected metadata."
    machine = make_zmachine()
    parser = quetzal.QuetzalParser(machine)
    parser.load("stories/curses.save1")
    savefile_metadata = parser.get_last_loaded()
    self.assertEquals(savefile_metadata,\
        {'total length': 520, \
         'memory length': 26163, \
         'checksum': 19942, \
         'release number': 16, \
         'serial number': '951024', \
         'program counter': 176149, \
         'CMem': 437, 'Stks': 40, 'IFhd': 13})
