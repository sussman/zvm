#
# A template class representing a User Interface.
#
# Third-party programs are expected to subclass ZUI and override all
# the methods, then pass an instance of their class to be driven by
# the main z-machine engine.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#


class ZUI(object):

  def __init__(self):
    "Constructor for UI."

    # The size of the screen.
    self._columns = 80
    self._rows = 24

    # The size of the current font, in characters
    self._fontheight = 1
    self._fontwidth = 1

    # Subclasses must define real values for all the features they
    # support (or don't support).

    self.features = {
      "has_status_line" : True,
      "has_upper_window" : True,
      "has_graphics_font" : False,
      "has_text_colors":  False,
      "has_sound": False,
      "has_mouse": False,
      }

  # Private Routines

  def _set_screen_size(self, rows, columns):
    """Set my own screen size variables."""

    # The UI is responsible for calling this routine whenever the
    # screen-size changes; the z-machine will periodically poll for
    # the screen size via get_screen_size() below.

    # NOTE: be sure to globally-lock self._columns and self._rows
    # before changing their values!!

    pass

  def _set_font_size(self, width, height):
    """Set my own font size variables."""

    # The UI is responsible for calling this routine whenever the font
    # size changes; the z-machine will periodically poll for the
    # screen size via get_font_size() below.

    # NOTE: be sure to globally-lock self.fontwidth and self._fontheight
    # before changing their values!!

    pass


  # File I/O

  def save_game(self, data, suggested_filename=None):
    """Prompt for a filename (possibly using suggested_filename), and
    attempt to write DATA as a saved-game file.  Return True on
    success, False on failure."""

    pass


  def restore_game(self):
    """Prompt for a filename, and return file's contents.  (Presumably
    the interpreter will attempt to use those contents to restore a
    saved game.)"""

    pass


  def open_transcript_file_for_writing(self):
    """Prompt for a filename in which to save either a full game
    transcript or just a list of the user's commands.  Return standard
    python file handle that can be written to."""

    pass


  def open_transcript_file_for_reading(self):
    """Prompt for a filename contain user commands, which can be used
    to drive the interpreter.  Return standard python file handle that
    can be read from."""

    pass


  # Window Management
  #
  # The z-machine has 2 windows for displaying text, "upper" and
  # "lower".  (The upper window has an inital height of 0.)  If
  # visible, the upper window is where the 'status line' typically
  # appears.
  #
  # The UI is responsible for making the lower window scroll properly,
  # as well as wrapping words ("buffering").  The upper window,
  # however, should *never* scroll or wrap words.
  #
  # The UI is also responsible for displaying [MORE] prompts when
  # printing more text than the screen-height can display.  (Note: if
  # the screen height is 255, then it should never prompt [MORE].)

  def get_screen_size(self):
    """Return the current size of the screen as [rows, columns]."""

    return [self._rows, self._columns]


  def select_window(self, number):
    """Select a window to be the 'active' window, and move that
    window's cursor to the upper left."""

    pass


  def split_window(self, height):
    """Make the upper window appear and be HEIGHT lines tall.  To
    'unsplit' a window, call with a height of 0 lines."""

    pass


  def set_cursor_position(self, x, y):
    """Set the cursor to (row, column) coordinates (X,Y) in the
    current window, where (1,1) is the upper-left corner."""

    pass


  def clear_screen(self):
    """Clear the current window of all text."""

    pass


  def erase_window(self, window, color):
    """Erase WINDOW to background COLOR."""

    pass


  # Status Line
  #
  # These routines are only called if the has_status_line capability
  # is set.  Specifically, one of them is called whenever the
  # show_status opcode is executed, and just before input is read from
  # the user.

  def print_status_score_turns(self, text, score, turns):
    """Print a status line in the upper window, as follows:

        On the left side of the status line, print TEXT.
        On the right side of the status line, print SCORE/TURNS.
    """

    pass


  def print_status_time(self, hours, minutes):
    """Print a status line in the upper window, as follows:

        On the left side of the status line, print TEXT.
        On the right side of the status line, print HOURS:MINUTES.
    """

    pass


  # Text Appearances
  #

  def get_font_size(self):
    """Return the current font's size as [width, height]."""

    return [self._fontwidth, self._fontheight]


  def set_font(self, font_number):
    """Set the current window's font to one of

          1 - normal font
          2 - picture font (IGNORE, this means nothing)
          3 - character graphics font
          4 - fixed-width font

    If a font is not available, return None.  Otherwise, set the
    new font, and return the number of the *previous* font.  """

    pass


  def set_text_style(self, style_number):
    """Set the current text style to one of

           0 - Roman
           1 - Reverse video
           2 - Bold
           4 - Italic
           8 - Fixed-width """

    pass


  def set_text_color(self, foreground_color, background_color):
    """Set current text foreground and background color to values in

            0 - current color
            1 - default color
            2 - black,  3 - red, 4 - green, 5 -yellow, 6 - blue,
            7 - magenta, 8 - cyan, 9 - white, 10 - dark grey,
            11- medium grey, 12 - dark grey
     """

    pass


  # Sound Effects
  #
  ### TODO... see section 9 of spec.





#
# What about unicode output??  (print_unicode opcode)
#
#   O1: see section 3.8.5.4 of spec; implementation of O1 must be able
#   to print all unicode chars below 0x100 (ISO 8859-1-Latin chars),
#   or suitable equivalents.  For higher character codes, if there's
#   no glyph, then print a question mark.
#
#   O2:  if the code isn't ascii, use any representation you want.
#
#   O3:  Convert all unicode to zscii.  If not possible, print question mark.
#
#   O4:  Never needs to print non-zscii.
#

