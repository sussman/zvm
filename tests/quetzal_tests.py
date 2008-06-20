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
         [520, 'IFhd', 13, 16, '951024', 19942, 'CMem', 437, 26163, 'Stks', 40])

