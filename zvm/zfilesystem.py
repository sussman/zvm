#
# A template class representing the interactions that the end-user has
# with the filesystem in a z-machine.
#
# Third-party programs are expected to subclass ZFilesystem and
# override all the methods, then pass an instance of their class to be
# driven by the main z-machine engine.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZFilesystem(object):
  """Encapsulates the interactions that the end-user has with the
  filesystem."""

  def save_game(self, data, suggested_filename=None):
    """Prompt for a filename (possibly using suggested_filename), and
    attempt to write DATA as a saved-game file.  Return True on
    success, False on failure.

    Note that file-handling errors such as 'disc corrupt' and 'disc
    full' should be reported directly to the player by the method in
    question method, and they should also cause this function to
    return False.  If the user clicks 'cancel' or its equivalent,
    this function should return False."""

    raise NotImplementedError()


  def restore_game(self):
    """Prompt for a filename, and return file's contents.  (Presumably
    the interpreter will attempt to use those contents to restore a
    saved game.)  Returns None on failure.

    Note that file-handling errors such as 'disc corrupt' and 'disc
    full' should be reported directly to the player by the method in
    question method, and they should also cause this function to
    return None. The error 'file not found' should cause this function
    to return None.  If the user clicks 'cancel' or its equivalent,
    this function should return None."""

    raise NotImplementedError()


  def open_transcript_file_for_writing(self):
    """Prompt for a filename in which to save either a full game
    transcript or just a list of the user's commands.  Return standard
    python file object that can be written to.

    If an error occurs, or if the user clicks 'cancel' or its
    equivalent, return None."""

    raise NotImplementedError()


  def open_transcript_file_for_reading(self):
    """Prompt for a filename contain user commands, which can be used
    to drive the interpreter.  Return standard python file object that
    can be read from.

    If an error occurs, or if the user clicks 'cancel' or its
    equivalent, return None."""

    raise NotImplementedError()
