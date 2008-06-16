#
# A class which represents the i/o streams of the Z-Machine and their
# current state of selection.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

# Constants for output streams.  These are human-readable names for
# the stream ID numbers as described in sections 7.1.1 and 7.1.2
# of the Z-Machine Standards Document.
OUTPUT_SCREEN = 1
OUTPUT_TRANSCRIPT = 2
OUTPUT_MEMORY = 3
OUTPUT_PLAYER_INPUT = 4

# Constants for input streams.  These are human-readable names for the
# stream ID numbers as described in section 10.2 of the Z-Machine
# Standards Document.
INPUT_KEYBOARD = 0
INPUT_FILE = 1

class ZOutputStreamManager(object):
  """Manages output streams for a Z-Machine."""

  def __init__(self, zmem, zui):
    # TODO: Actually set/create the streams as necessary.

    self._selectedStreams = []
    self._streams = {}

  def select(self, stream):
    """Selects the given stream ID for output."""

    if stream not in self._selectedStreams:
      self._selectedStreams.append(stream)

  def unselect(self, stream):
    """Unselects the given stream ID for output."""

    if stream in self._selectedStreams:
      self._selectedStreams.remove(stream)

  def get(self, stream):
    """Retrieves the given stream ID."""

    return self._streams[stream]

  def write(self, string):
    """Writes the given unicode string to all currently selected output
    streams."""

    # TODO: Implement section 7.1.2.2 of the Z-Machine Standards
    # Document, so that while stream 3 it is selected, no text is
    # sent to any other output streams which are selected. (However,
    # they remain selected.).

    # TODO: Implement section 7.1.2.2.1, so that newlines are written to
    # output stream 3 as ZSCII 13.

    # TODO: Implement section 7.1.2.3, so that whiles stream 4 is
    # selected, the only text printed to it is that of the player's
    # commands and keypresses (as read by read_char). This may not
    # ultimately happen via this method.

    for stream in self._selectedStreams:
      self._streams[stream].write(string)

class ZInputStreamManager(object):
  """Manages input streams for a Z-Machine."""

  def __init__(self, zui):
    # TODO: Actually set/create the streams as necessary.

    self._selectedStream = None
    self._streams = {}

  def select(self, stream):
    """Selects the given stream ID as the currently active input stream."""

    # TODO: Ensure section 10.2.4, so that while stream 1 is selected,
    # the only text printed to it is that of the player's commands and
    # keypresses (as read by read_char). Not sure where this logic
    # will ultimately go, however.

    self._selectedStream = stream

  def getSelected(self):
    """Returns the input stream object for the currently active input
    stream."""

    return self._streams[self._selectedStream]
