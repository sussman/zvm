#
# Template classes representing input/output streams of a z-machine.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZOutputStream(object):
  """Abstract class representing an output stream for a z-machine."""

  def write(self, string):
    """Prints the given unicode string to the output stream."""

    raise NotImplementedError()


class ZBufferableOutputStream(ZOutputStream):
  """Abstract class representing a buffered output stream for a
  z-machine, which can be optionally configured at run-time to provide
  'buffering', also known as word-wrap."""

  def __init__(self):
    # This is a public variable that determines whether buffering is
    # enabled for this stream or not.  Subclasses can make it a
    # Python property if necessary.
    self.buffer_mode = False


class ZInputStream(object):
  """Abstract class representing an input stream for a z-machine."""

  def __init__(self):
    """Constructor for the input stream."""
    # Subclasses must define real values for all the features they
    # support (or don't support).

    self.features = {
      "has_timed_input" : False,
      }

  def read_line(self, original_text=None, max_length=0,
                terminating_characters=None,
                timed_input_routine=None, timed_input_interval=0):
    """Reads from the input stream and returns a unicode string
    representing the characters the end-user entered.  The characters
    are displayed to the screen as the user types them.

    original_text, if provided, is pre-filled-in unicode text that the
    end-user may delete or otherwise modify if they so choose.

    max_length is the maximum length, in characters, of the text that
    the end-user may enter.  Any typing the end-user does after these
    many characters have been entered is ignored.  0 means that there
    is no practical limit to the number of characters the end-user can
    enter.

    terminating_characters is a string of unicode characters
    representing the characters that can signify the end of a line of
    input.  If not provided, it defaults to a string containing a
    carriage return character ('\r').  The terminating character is
    not contained in the returned string.

    timed_input_routine is a function that will be called every
    time_input_interval milliseconds.  This function should be of the
    form:

        def timed_input_routine(interval)

    where interval is simply the value of timed_input_interval that
    was passed in to read_line().  The function should also return
    True if input should continue to be collected, or False if input
    should stop being collected; if False is returned, then
    read_line() will return a unicode string representing the
    characters typed so far.

    The timed input routine will be called from the same thread that
    called read_line().

    Note, however, that supplying a timed input routine is only useful
    if the has_timed_input feature is supported by the input stream.
    If it is unsupported, then the timed input routine will not be
    called."""

    raise NotImplementedError()

  def read_char(self, timed_input_routine=None,
                timed_input_interval=0):
    """Reads a single character from the stream and returns it as a
    unicode character.

    timed_input_routine and timed_input_interval are the same as
    described in the documentation for read_line().

    TODO: Should the character be automatically printed to the screen?
    The Z-Machine documentation for the read_char opcode, which this
    function is meant to ultimately implement, doesn't specify."""

    raise NotImplementedError()
