#
# A trivial user interface for a Z-Machine that uses stdio for
# everything and supports little to no optional features.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

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
  # TODO: Implement this.
  pass

class TrivialFilesystem(zfilesystem.ZFilesystem):
  def save_game(self, data, suggested_filename=None):
    success = False

    # We don't *have* to use suggested_filename, so we won't.
    filename = raw_input("Enter a name for the saved game " \
                         "(hit enter to cancel): ")
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
