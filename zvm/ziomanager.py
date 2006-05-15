#
# A class for managing the z-machines various input/output streams.
# Acts as the abstraction layer between the ZCPU and an instance of
# ZUI class that's able to print to the screen.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zmemory import ZMemory
from zstring import ZStringFactory
from zui import ZUI


#  Zmachine itself manages a 'list of streams' that are can be
#  independently switched on and off by the game.
#
#   OUTPUT STREAMS:
#
#     O1:  screen
#     O2:  transcript of whole game (sent to printer or file)
#     O3:  (z3+) dynamic memory
#     O4:  (z3+) transcript of user input only
#
#  Player input is *always* echoed to O1 and O2.  O1 and O2 are
#  allowed to buffer text so as to implement word-wrapping in lower
#  window.  Buffering is always on in z1-z3, but can be turned off in
#  z4+ via buffer_mode opcode.
#
#  When implementing O2, only ask for filename *once*, not everytime
#  it's switched on or off.
#
#  If O3 is 'on', then it *exclusively* receives output; no other
#  streams recerive output, even if they're also on.
#
#      -> data goes to ?table? address when on
#      -> newlines recorded as zscii 13
#      -> when off, address should contain length-word, then data.
#      -> recursive to 16 levels: each 'selection' of O3 writes to new
#         table address, then 'deselection' paps back to previous table
#
#  O4:  if selected, *only* write user's keypresses (from read_char).
#       Commands are written atomically, after they finish
#
#
#
# Code to select/deselect output streams:
#
#   z1-z2:  O1 always on, O2 selected by toggling bit 0 of 'flags2'
#     z3+:  output_stream opcode twiddles all 4 streams, OR flogs2 can still
#           be twiddled for O2... AND flogs2 must *always* represent the
#           latest O2 state no matter what.
#
# INPUT STREAMS:
#
#  z1, z2:  keyboard is only source of input.
#     z3+:  input comes from current "input stream"
#
#            I0:  keyboard
#            I1:  file of commands  (as produced by O4)
#



# These two stream classes are wholly managed by ZIOManager; nobody
# else should need to see them or use them.

class ZOutputStream(object):

  def __init__(self):

    # Whether the stream is printing output or not.
    self.active = False

    # "Buuffering" just means the stream is  wrapping words.
    self.buffering = False

    #?? current font, style, etc?


class ZInputStream(object):

  def __init__(self):
    pass




class ZIOManager(object):

  def __init__(self, zmem, zui):

    self._memory = zmem
    self._ui = zui
    self._input_stream = ??
    self._output_streams = []

    ### set up initial streams based on z-version...

    ### examine self._ui.features and adjust self._memory header flags
    ### appropriately.  This tells the game-program which opcodes are
    ### safe to use or not.


  # Only one input stream is active at a time.

  def select_input_stream(self, stream_number):
    """Activate input stream STREAM_NUMBER."""

    ### todo: if input stream 1 is selected, we must ask self._ui to
    ### ask the user to open a file, and then read from the file
    ### stream.
    pass


  # Any number of output streams can be active at once.

  def select_output_stream(self, stream_number):
    """Activate output stream STREAM_NUMBER."""

    ### do weird side-effect stuff here, such as automatically turning
    ### other streams on/off.
    pass


  def deselect_output_stream(self, stream_number):
    """Deactivate output stream STREAM_NUMBER."""

    ### do weird side-effect stuff here, such as automatically turning
    ### other streams on/off.
    pass


  def get_active_output_streams(self):
    """Return a list of numbers representing active output streams."""

    pass


  def set_output_buffering(self, stream_number, ):
    """If inactive, have the STREAM_NUMBER's lower window start
    buffering text and performing word-wrapping.  If already active,
    turn off buffering."""

    pass


  def show_status_line(self):
    """Display the latest status line."""

    ### Check for self._ui.features["has_status_line"].
    ### Look at self._mem flags to see if it's a 'score' or 'time' game,
    ### and call one of the two ZUI status functions.


  def print(self, text):
    """Print text to all active output streams."""

    pass


  def read(self):
    """Read a line of input from the user, from the current input stream."""

    pass





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
