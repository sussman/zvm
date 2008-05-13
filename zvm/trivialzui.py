#
# A trivial user interface for a Z-Machine that uses (mostly) stdio for
# everything and supports little to no optional features.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

# TODO: There are a few edge-cases in this UI implementation in
# regards to word-wrapping.  For example, if keyboard input doesn't
# terminate in a newline, then word-wrapping can be temporarily thrown
# off; the text I/O performed by the audio and filesystem doesn't
# really communicate with the screen object, which means that
# operations performed by them can temporarily throw off word-wrapping
# as well.

import sys

import zaudio
import zscreen
import zstream
import zfilesystem
import zui
from zlogging import log

class TrivialAudio(zaudio.ZAudio):
  def __init__(self):
    zaudio.ZAudio.__init__(self)
    self.features = {
      "has_more_than_a_bleep": False,
      }

  def play_bleep(self, bleep_type):
    if bleep_type == zaudio.BLEEP_HIGH:
      sys.stdout.write("AUDIO: high-pitched bleep\n")
    elif bleep_type == zaudio.BLEEP_LOW:
      sys.stdout.write("AUDIO: low-pitched bleep\n")
    else:
      raise AssertionError("Invalid bleep_type: %s" % str(bleep_type))

class TrivialScreen(zscreen.ZScreen):
  def __init__(self):
    zscreen.ZScreen.__init__(self)
    self.__styleIsAllUppercase = False

    # Current column of text being printed.
    self.__curr_column = 0

    # Number of rows displayed since we last took input; needed to
    # keep track of when we need to display the [MORE] prompt.
    self.__rows_since_last_input = 0

  def split_window(self, height):
    log("TODO: split window here to height %d" % height)

  def select_window(self, window_num):
    log("TODO: select window %d here" % window_num)

  def set_cursor_position(self, x, y):
    log("TODO: set cursor position to (%d,%d) here" % (x,y))

  def erase_window(self, window=zscreen.WINDOW_LOWER,
                   color=zscreen.COLOR_CURRENT):
    for row in range(self._rows):
      sys.stdout.write("\n")
    self.__curr_column = 0
    self.__rows_since_last_input = 0

  def set_font(self, font_number):
    if font_number == zscreen.FONT_NORMAL:
      return font_number
    else:
      # We aren't going to support anything but the normal font.
      return None

  def set_text_style(self, style):
    # We're pretty much limited to stdio here; even if we might be
    # able to use terminal hackery under Unix, supporting styled text
    # in a Windows console is problematic [1].  The closest thing we
    # can do is have our "bold" style be all-caps, so we'll do that.
    #
    # [1] http://mail.python.org/pipermail/tutor/2004-February/028474.html

    if style == zscreen.STYLE_BOLD:
      self.__styleIsAllUppercase = True
    else:
      self.__styleIsAllUppercase = False

  def __show_more_prompt(self):
    """Display a [MORE] prompt, wait for the user to press a key, and
    then erase the [MORE] prompt, leaving the cursor at the same
    position that it was at before the call was made."""

    assert self.__curr_column == 0, \
           "Precondition: current column must be zero."

    MORE_STRING = "[MORE]"
    sys.stdout.write(MORE_STRING)
    _read_char()
    # Erase the [MORE] prompt and reset the cursor position.
    sys.stdout.write("\r%s\r" % (" " * len(MORE_STRING)))
    self.__rows_since_last_input = 0

  def on_input_occurred(self, newline_occurred=False):
    """Callback function that should be called whenever keyboard input
    has occurred; this is so we can keep track of when we need to
    display a [MORE] prompt."""

    self.__rows_since_last_input = 0
    if newline_occurred:
      self.__curr_column = 0

  def __unbuffered_write(self, string):
    """Write the given string, inserting newlines at the end of
    columns as appropriate, and displaying [MORE] prompts when
    appropriate.  This function does not perform word-wrapping."""

    for char in string:
      newline_printed = False
      sys.stdout.write(char)

      if char == "\n":
        newline_printed = True
      else:
        self.__curr_column += 1

      if self.__curr_column == self._columns:
        sys.stdout.write("\n")
        newline_printed = True

      if newline_printed:
        self.__rows_since_last_input += 1
        self.__curr_column = 0
        if (self.__rows_since_last_input == self._rows and
            self._rows != zscreen.INFINITE_ROWS):
          self.__show_more_prompt()

  def write(self, string):
    if self.__styleIsAllUppercase:
      # Apply our fake "bold" transformation.
      string = string.upper()

    if self.buffer_mode:
      # This is a hack to get words to wrap properly, based on our
      # current cursor position.

      # First, add whitespace padding up to the column of text that
      # we're at.
      string = (" " * self.__curr_column) + string

      # Next, word wrap our current string.
      string = _word_wrap(string, self._columns-1)

      # Now remove the whitespace padding.
      string = string[self.__curr_column:]

    self.__unbuffered_write(string)

class TrivialKeyboardInputStream(zstream.ZInputStream):
  def __init__(self, screen):
    zstream.ZInputStream.__init__(self)
    self.__screen = screen
    self.features = {
      "has_timed_input" : False,
      }

  def read_line(self, original_text=None, max_length=0,
                terminating_characters=None,
                timed_input_routine=None, timed_input_interval=0):
    result = _read_line(original_text, terminating_characters)
    if max_length > 0:
      result = result[:max_length]

    # TODO: The value of 'newline_occurred' here is not accurate,
    # because terminating_characters may include characters other than
    # carriage return.
    self.__screen.on_input_occurred(newline_occurred=True)

    return unicode(result)

  def read_char(self, timed_input_routine=None,
                timed_input_interval=0):
    result = _read_char()
    self.__screen.on_input_occurred()
    return result

class TrivialFilesystem(zfilesystem.ZFilesystem):
  def __report_io_error(self, exception):
    sys.stdout.write("FILESYSTEM: An error occurred: %s\n" % exception)

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
        self.__report_io_error(e)

    return success

  def restore_game(self):
    data = None

    sys.stdout.write("Enter the name of the saved game to restore " \
                     "(hit enter to cancel): ")
    filename = _read_line()
    if filename:
      try:
        file_obj = open(filename, "rb")
        data = file_obj.read()
        file_obj.close()
      except IOError, e:
        self.__report_io_error(e)

    return data

  def open_transcript_file_for_writing(self):
    file_obj = None

    sys.stdout.write("Enter a name for the transcript file " \
                     "(hit enter to cancel): ")
    filename = _read_line()
    if filename:
      try:
        file_obj = open(filename, "w")
      except IOError, e:
        self.__report_io_error(e)

    return file_obj

  def open_transcript_file_for_reading(self):
    file_obj = None

    sys.stdout.write("Enter the name of the transcript file to read " \
                     "(hit enter to cancel): ")
    filename = _read_line()
    if filename:
      try:
        file_obj = open(filename, "r")
      except IOError, e:
        self.__report_io_error(e)

    return file_obj

def create_zui():
  """Creates and returns a ZUI instance representing a trivial user
  interface."""

  audio = TrivialAudio()
  screen = TrivialScreen()
  keyboard_input = TrivialKeyboardInputStream(screen)
  filesystem = TrivialFilesystem()

  return zui.ZUI(
    audio,
    screen,
    keyboard_input,
    filesystem
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

# Word wrapping helper function

def _word_wrap(text, width):
  """
  A word-wrap function that preserves existing line breaks
  and most spaces in the text. Expects that existing line
  breaks are posix newlines (\n).
  """

  # This code was taken from:
  # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061

  return reduce(lambda line, word, width=width: '%s%s%s' %
                (line,
                 ' \n'[(len(line)-line.rfind('\n')-1
                       + len(word.split('\n',1)[0]
                            ) >= width)],
                 word),
                text.split(' ')
               )
