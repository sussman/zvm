#
# A trivial user interface for a Z-Machine that uses (mostly) stdio for
# everything and supports little to no optional features.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import sys

import zaudio
import zscreen
import zstream
import zfilesystem
import zui

class TrivialAudio(zaudio.ZAudio):
  def __init__(self):
    self.features = {
      "has_more_than_a_bleep": False,
      }

  def play_bleep(self, bleep_type):
    if bleep_type == zaudio.BLEEP_HIGH:
      print "AUDIO: high-pitched bleep"
    elif bleep_type == zaudio.BLEEP_LOW:
      print "AUDIO: low-pitched bleep"
    else:
      raise AssertionError("Invalid bleep_type: %s" % str(bleep_type))

class TrivialScreen(zscreen.ZScreen):
  # TODO: Implement this.
  pass

class TrivialKeyboardInputStream(zstream.ZInputStream):
  def __init__(self):
    self.features = {
      "has_timed_input" : False,
      }

  def read_line(self, original_text=None, max_length=0,
                terminating_characters=None,
                timed_input_routine=None, timed_input_interval=0):
    result = _read_line(original_text, terminating_characters)
    if max_length > 0:
      result = result[:max_length]
    return unicode(result)

  def read_char(self, timed_input_routine=None,
                timed_input_interval=0):
    return _read_char()

class TrivialFilesystem(zfilesystem.ZFilesystem):
  def save_game(self, data, suggested_filename=None):
    success = False

    sys.stdout.write("Enter a name for the saved game " \
                     "(hit enter to cancel): ")
    filename = _read_line(suggested_filename)
    if filename:
      try:
        file_obj = open(filename, "wb")
        file_obj.write(data)
        file_obj.close()
        success = True
      except IOError, e:
        print "FILESYSTEM: An error occurred: %s" % e

    return success

  def restore_game(self):
    data = None

    filename = raw_input("Enter the name of the saved game to restore " \
                         "(hit enter to cancel): ")
    if filename:
      try:
        file_obj = open(filename, "rb")
        data = file_obj.read()
        file_obj.close()
      except IOError, e:
        print "FILESYSTEM: An error occurred: %s" % e

    return data

  def open_transcript_file_for_writing(self):
    file_obj = None

    filename = raw_input("Enter a name for the transcript file " \
                         "(hit enter to cancel): ")
    if filename:
      try:
        file_obj = open(filename, "w")
      except IOError, e:
        print "FILESYSTEM: An error occurred: %s" % e

    return file_obj

  def open_transcript_file_for_reading(self):
    file_obj = None

    filename = raw_input("Enter the name of the transcript file to read " \
                         "(hit enter to cancel): ")
    if filename:
      try:
        file_obj = open(filename, "r")
      except IOError, e:
        print "FILESYSTEM: An error occurred: %s" % e

    return file_obj

def create_zui():
  """Creates and returns a ZUI instance representing a trivial user
  interface."""

  return zui.ZUI(
    TrivialAudio(),
    TrivialScreen(),
    TrivialKeyboardInputStream(),
    TrivialFilesystem()
    )

# Keyboard input functions

_INTERRUPT_CHAR = chr(3)
_BACKSPACE_CHAR = chr(8)
_DELETE_CHAR = chr(127)

def _win32_read_char():
  """Win32-specific function that reads a character of input from the
  keyboard and returns it without printing it to the screen."""

  import msvcrt

  return unicode(msvcrt.getch())

def _unix_read_char():
  """Unix-specific function that reads a character of input from the
  keyboard and returns it without printing it to the screen."""

  # This code was excised from:
  # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/134892

  import tty
  import termios

  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
  finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  return unicode(ch)

def _read_char():
  """Reads a character of input from the keyboard and returns it
  without printing it to the screen."""

  if sys.platform == "win32":
    _platform_read_char = _win32_read_char
  else:
    # We're not running on Windows, so assume we're running on Unix.
    _platform_read_char = _unix_read_char

  char = _platform_read_char()
  if char == _INTERRUPT_CHAR:
    raise KeyboardInterrupt()
  else:
    return char

def _read_line(original_text=None, terminating_characters=None):
  """Reads a line of input with the given unicode string of original
  text, which is editable, and the given unicode string of terminating
  characters (used to terminate text input).  By default,
  terminating_characters is a string containing the carriage return
  character ('\r')."""
  
  if original_text == None:
    original_text = u""
  if not terminating_characters:
    terminating_characters = u"\r"

  assert isinstance(original_text, unicode)
  assert isinstance(terminating_characters, unicode)

  chars_entered = len(original_text)
  sys.stdout.write(original_text)
  string = original_text
  finished = False
  while not finished:
    char = _read_char()

    if char in (_BACKSPACE_CHAR, _DELETE_CHAR):
      if chars_entered > 0:
        chars_entered -= 1
        string = string[:-1]
      else:
        continue
    elif char in terminating_characters:
      finished = True
    else:
      string += char
      chars_entered += 1

    if char == "\r":
      char_to_print = "\n"
    elif char == _BACKSPACE_CHAR:
      char_to_print = "%s %s" % (_BACKSPACE_CHAR, _BACKSPACE_CHAR)
    else:
      char_to_print = char

    sys.stdout.write(char_to_print)
  return string
