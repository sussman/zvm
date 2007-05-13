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

          1 - a high-pitched bleep
          2 - a low-pitched bleep
      """

      pass

    def play_sound_effect(self, id, effect, volume, repeats,
                          routine=None):
    """The given effect happens to the given sound number.  The id
    must be 3 or above is supplied by the ZAudio object for the
    particular game in question.

    The effect can be:
    
        1 - prepare
        2 - start
        3 - stop
        4 - finish

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
    """

    pass
