#
# A class which represents the Program Counter and decodes operation
# to be executed by the ZPU
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from bitfield import BitField
from zmemory import ZMemory

class ZOperationError(Exception):
  "General exception for ZOperation class"
  pass



class ZOpDecoder(object):

  def __init__(self, zmem):
    ""
    self._memory = zmem
    self._program_counter = 0

  def seek_after_string(self, str_addr):
    """Beginning at STR_ADDR, scan an encoded zstring to the end.
       When finished, STR_ADDR points to the address immediately
       following the zstring."""

    bf = BitField(0)
    while True:
      bf.__init__(self._memory.read_word(str_addr))
      str_addr += 2
      if bf[15] == 1:
        return str_addr

  def get_op(self):
    """Decode the operation currently pointed to by the program
    counter, and appropriately increment the program counter
    afterwards.

    A decoded operation is returned to the caller in the form:

    [opcode-number,
     [operand, operand, operand, ...],
     store-variable (or None),
     branch-offset (or None),
     "string" (or None)]

    """

