# The Z-Machine black box. It initializes the whole Z computer, loads
# a story, and starts execution of the cpu.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zmemory import ZMemory
from zopdecoder import ZOpDecoder
from zstackmanager import ZStackManager
from zcpu import ZCpu

class ZMachineError(Exception):
  """General exception for ZMachine class"""

class ZMachine(object):
  """The Z-Machine black box."""

  def __init__(self, story):
    self._pristine_mem = ZMemory(story)
    self._mem = ZMemory(story)
    self._opdecoder = ZOpDecoder(self._mem)
    self._opdecoder.program_counter = self._mem.read_word(0x06)
    self._stackmanager = ZStackManager(self._mem)
    self._cpu = ZCpu(self._mem, self._opdecoder, self._stackmanager)


  def _binary_memory_diff():
    """Helper for Quetzal file format.  Return a compressed binary
    difference between the original 'pristine' state of dynamic memory
    and the current state."""

    # XOR the original game image with the current one
    diffarray = list(self._pristine_mem)
    for index in range(len(self._pristine_mem._total_size)):
      diffarray[index] = self._pristine_mem[index] ^ self._mem[index]

    # Run-length encode the resulting list of 0's and 1's.
    result = []
    zerocounter = 0;
    for index in range(len(diffarray)):
      if diffarray[index] == 0:
        zerocounter += 1
        continue;
      else:
        if zerocounter > 0:
          result.append(0)
          result.append(zerocounter)
          zerocounter = 0
        result.append(diffarray[index])
    return result


  #--------- Public APIs -----------

  def run(self):
    return self._cpu.run()

