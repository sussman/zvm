#
# A class representing the entire user interface of a Z-Machine.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import zaudio
import zscreen
import zstream
import zfilesystem

class ZUI(object):
    """This class encapsulates the entire user interface of a
    Z-Machine, providing access to all functionality that the end-user
    directly experiences or interacts with."""

    def __init__(self, audio, screen, keyboard_input, filesystem):
        """Initializes the ZUI with the given components."""

        assert isinstance(audio, zaudio.ZAudio)
        assert isinstance(screen, zscreen.ZScreen)
        assert isinstance(keyboard_input, zstream.ZInputStream)
        assert isinstance(filesystem, zfilesystem.ZFilesystem)

        # The following are all public attributes of the instance, but
        # should be considered read-only.  In the future, we may want
        # to make them Python properties.

        self.audio = audio
        self.screen = screen
        self.keyboard_input = keyboard_input
        self.filesystem = filesystem
