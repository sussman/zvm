#
# A class which represents the Program Counter and decodes instructions
# to be executed by the ZPU.
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

  doublevar_opcodes = (12, 26)

  store_opcodes = ()

  branch_opcodes = ()

  text_opcodes = ()


  def __init__(self, zmem):
    ""
    self._memory = zmem
    self._disassembly_map = {}
    self.program_counter = 0

    # Create a fast lookup table that maps initial instruction bytes
    # to functions that properly parse the opcode and operands.
    for i in range(0x0, 0x1f+1):
      self._disassembly_map[i] = self._long_2op_small_small
    for i in range(0x20, 0x3f+1):
      self._disassembly_map[i] = self._long_2op_small_var
    for i in range(0x40, 0x5f+1):
      self._disassembly_map[i] = self._long_2op_var_small
    for i in range(0x60, 0x7f+1):
      self._disassembly_map[i] = self._long_2op_var_var
    for i in range(0x80, 0x8f+1):
      self.-disassembly_map[i] = self._short_1op_large
    for i in range(0x90, 0x9f+1):
      self._disassembly_map[i] = self._short_1op_small
    for i in range(0xa0, 0xaf+1):
      self._disassembly_map[i] = self._short_1op_var
    for i in range(0xb0, 0xbf+1):
      self._disassembly_map[i] = self._short_0op
    for i in range(0xc0, 0xdf+1):
      self._disassembly_map[i] = self._variable_2op
    for i in range(0xe0, 0xff+1):
      self._disassembly_map[i] = self._variable_var

    if self._zmemory.version == 5:  # for z5, opcode 0xbe is 'special'
      self._disassembly_map[0xbe] = self._extended_var


  def seek_beyond_string(self, str_addr):
    """Beginning at STR_ADDR, scan an encoded zstring to the end.
       When finished, STR_ADDR points to the address immediately
       following the zstring."""

    bf = BitField(0)
    while True:
      bf.__init__(self._memory.read_word(str_addr))
      str_addr += 2
      if bf[15] == 1:
        return str_addr

  def get_next_instruction(self):
    """Decode the instruction currently pointed to by the program
    counter, and appropriately increment the program counter
    afterwards.

    A decoded instruction is returned to the caller in the form:

    [opcode-number,
     [operand, operand, operand, ...],
     store-variable (or None),
     [1|0, branch-offset] (or None),
     "string" (or None)]

    This structure should contain everything the CPU needs to execute
    an instruction.

    """
    # Begin by parsing out the opcode and operands
    instruction = self._disassembly_map[self._memory[self.program_counter]]()

    # So now we have [opcode, [operand ...]]. Let's play 20 questions!

    # Is it a 'doublevar' opcode?
    if instruction[0] in doublevar_opcodes:
      self._get_extra_operands(instruction)

    # Is it a 'store' opcode?
    if instruction[0] in store_opcodes:
      pass

    # Is it a 'branch' opcode?
    if instruction[0] in branch_opcodes:
      pass

    # Is it a 'text' opcode?
    if instruction[0] in text_opcodes:
      pass

    return instruction


  # Helper funcs that actually parse opcode-numbers and operands.

  def _long_2op_small_small(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _long_2op_small_var(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _long_2op_var_small(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _long_2op_var_var(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _short_1op_large(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _short_1op_small(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _short_1op_var(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _short_0op(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _extended_var(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _variable_2op(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _variable_var(self):
    """Starting at program counter, parse byte(s) and return
    [opcode-number, [operand, operand, ...]]"""
    pass

  def _get_extra_operands(self, instruction):
    """For 'doublevar' opcodes, parse the extra operands and append
    them into INSTRUCTION."""
    pass
