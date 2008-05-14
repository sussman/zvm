# The Z-Machine black box. It initializes the whole Z computer, loads
# a story, and starts execution of the cpu.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zstring import ZStringFactory
from zmemory import ZMemory
from zopdecoder import ZOpDecoder
from zstackmanager import ZStackManager
from zobjectparser import ZObjectParser
from zcpu import ZCpu
import zlogging

class ZMachineError(Exception):
  """General exception for ZMachine class"""

class ZMachine(object):
  """The Z-Machine black box."""

  def __init__(self, story, ui, debugmode=False):
    zlogging.set_debug(debugmode)
    self._pristine_mem = ZMemory(story) # the original memory image
    self._mem = ZMemory(story) # the memory image which changes during play
    self._stringfactory = ZStringFactory(self._mem)
    self._objectparser = ZObjectParser(self._mem)
    self._stackmanager = ZStackManager(self._mem)
    self._opdecoder = ZOpDecoder(self._mem, self._stackmanager)
    self._opdecoder.program_counter = self._mem.read_word(0x06)
    self._ui = ui
    self._cpu = ZCpu(self._mem, self._opdecoder, self._stackmanager,\
                     self._objectparser, self._stringfactory, self._ui)

  #--------- Public APIs -----------

  def run(self):
    return self._cpu.run()
