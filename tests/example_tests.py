#
# Unit tests for the Example class.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from unittest import TestCase
from zvm import zmachine, trivialzui

def make_zmachine():
    # We use Graham Nelson's 'curses' game for our unittests.
    with open("stories/curses.z5", "rb") as story:
      story_image = story.read()
    ui = trivialzui.create_zui()
    return zmachine.ZMachine(story_image, ui, debugmode=True)

class ExampleTest(TestCase):
    def exampleTest(self):
        machine = make_zmachine()
        # Do some useful stuff now
