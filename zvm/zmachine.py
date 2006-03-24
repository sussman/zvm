# The Z-Machine black box. It initializes the whole Z computer, loads
# a story, and starts execution of the cpu.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zmemory import ZMemory
from zopdecoder import ZOpDecoder
from zcpu import ZCpu

class ZMachineError(Exception):
    """General exception for ZMachine class"""

class ZMachine(object):
    """The Z-Machine black box."""

    def __init__(self, story):
        self._mem = ZMemory(story)
        self._opdecoder = ZOpDecoder(self._mem)
        self.program_counter = self._mem.read_word(0x06)
        self._cpu = ZCpu(self._mem, self._opdecoder)

    def run(self):
        return self._cpu.run()
