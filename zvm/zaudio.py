#
# A template class representing the audio interface of a z-machine.
#
# Third-party programs are expected to subclass ZAudio and override
# all the methods, then pass an instance of their class to be driven
# by the main z-machine engine.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

# Constants for simple bleeps. These are human-readable names for the
# first two sound effect numbers for the Z-Machine's 'sound_effect'
# opcode.
BLEEP_HIGH = 1
BLEEP_LOW = 2

# Constants for sound effects. These are human-readable names for
# the 'effect' operand of the Z-Machine's 'sound_effect' opcode.
EFFECT_PREPARE = 1
EFFECT_START = 2
EFFECT_STOP = 3
EFFECT_FINISH = 4

class ZAudio(object):
  def __init__(self):
    """Constructor of the audio system."""

    # Subclasses must define real values for all the features they
    # support (or don't support).

    self.features = {
      "has_more_than_a_bleep": False,
      }

  def play_bleep(self, bleep_type):
    """Plays a bleep sound of the given type:

        BLEEP_HIGH - a high-pitched bleep
        BLEEP_LOW - a low-pitched bleep
    """

    raise NotImplementedError()

  def play_sound_effect(self, id, effect, volume, repeats,
                        routine=None):
    """The given effect happens to the given sound number.  The id
    must be 3 or above is supplied by the ZAudio object for the
    particular game in question.

    The effect can be:

        EFFECT_PREPARE - prepare a sound effect for playing
        EFFECT_START - start a sound effect
        EFFECT_STOP - stop a sound effect
        EFFECT_FINISH - finish a sound effect

    The volume is an integer from 1 to 8 (8 being loudest of
    these). The volume level -1 means 'loudest possible'.

    The repeats specify how many times for the sound to repeatedly
    play itself, if it is provided.

    The routine, if supplied, is a Python function that will be called
    once the sound has finished playing.  Note that this routine may
    be called from any thread.  The routine should have the following
    form:

        def on_sound_finished(id)

    where 'id' is the id of the sound that finished playing.

    This method should only be implemented if the
    has_more_than_a_bleep feature is enabled."""

    raise NotImplementedError()
