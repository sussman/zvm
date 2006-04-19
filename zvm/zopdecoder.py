#
# A class which represents the Program Counter and decodes instructions
# to be executed by the ZPU.  Implements section 4 of Z-code specification.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from bitfield import BitField
from zmemory import ZMemory

class ZOperationError(Exception):
  "General exception for ZOperation class"
  pass


# Depending on the opcode, the list of operands that follow can be
# extremely varied, and are stored in weird and different ways.  This
# class parses both opcodes and operands, and manages the program
# counter.  The ZPU merely needs to call
# ZOpDecoder.get_next_instruction(), and a list of [opcode, [operand,
# operand, ...]] will be returned and the program counter
# automatically incremented.  Depending on the opcode, the ZPU may
# also need to fetch "extra" operands related to variable storage,
# branch offsets, and zstrings to print.  Those are available by
# calling the public functions at the end of the class.


class ZOpDecoder(object):

  def __init__(self, zmem):
    ""
    self._memory = zmem
    self._parse_map = {}
    self.program_counter = 0

    # Create a dictionary that maps initial instruction bytes
    # to functions that properly parse the opcode and operands.
    for i in range(0x0, 0x1f+1):
      self._parse_map[i] = self._long_2op_small_small
    for i in range(0x20, 0x3f+1):
      self._parse_map[i] = self._long_2op_small_var
    for i in range(0x40, 0x5f+1):
      self._parse_map[i] = self._long_2op_var_small
    for i in range(0x60, 0x7f+1):
      self._parse_map[i] = self._long_2op_var_var
    for i in range(0x80, 0x8f+1):
      self._parse_map[i] = self._short_1op_large
    for i in range(0x90, 0x9f+1):
      self._parse_map[i] = self._short_1op_small
    for i in range(0xa0, 0xaf+1):
      self._parse_map[i] = self._short_1op_var
    for i in range(0xb0, 0xbf+1):
      self._parse_map[i] = self._short_0op
    for i in range(0xc0, 0xdf+1):
      self._parse_map[i] = self._variable_2op
    for i in range(0xe0, 0xff+1):
      self._parse_map[i] = self._variable_var

    if self._memory.version == 5:  # for z5, opcode 0xbe is 'special'
      self._parse_map[0xbe] = self._extended_var


  def get_next_instruction(self):
    """Decode the opcode & operands currently pointed to by the
    program counter, and appropriately increment the program counter
    afterwards. A decoded operation is returned to the caller in the form:

       [opcode-number, [operand, operand, operand, ...]]

    If opcode has no operands, then [opcode-number, []] is returned."""

    opcode = self._memory[self.program_counter]
    self.program_counter += 1
    return self._parse_map[opcode](opcode)


  # Helper funcs that actually parse opcode-numbers and operands.
  # They all examine the address pointed to by the Program Counter,
  # parse bytes, return [opcode-number, [operand, ...]], and increment
  # the Program Counter as needed.

  # The following routines all read two 1-byte operands:
  def _read_two_bytes(self, opcode):
    operand1 = self._memory[self.program_counter]
    operand2 = self._memory[self.program_counter + 1]
    self.program_counter += 2
    return [opcode, [operand1, operand2]]

  def _long_2op_small_small(self, opcode):
    return self._read_two_bytes(opcode)

  def _long_2op_small_var(self, opcode):
    return self._read_two_bytes(opcode)

  def _long_2op_var_small(self, opcode):
    return self._read_two_bytes(opcode)

  def _long_2op_var_var(self, opcode):
    return self._read_two_bytes(opcode)

  # This routine reads a single 2-byte operand:
  def _short_1op_large(self, opcode):
    operand = self._memory.read_word(self.program_counter)
    self.program_counter += 2
    return [opcode, [operand]]

  # And these read a single 1-byte operand:
  def _read_one_byte(self, opcode):
    operand = self._memory[self.program_counter]
    self.program_counter += 1
    return [opcode, [operand]]

  def _short_1op_small(self, opcode):
    return self._read_one_byte(opcode)

  def _short_1op_var(self, opcode):
    return self._read_one_byte(opcode)

  # No operands at all
  def _short_0op(self, opcode):
    return [opcode, []]

  # The last few routines need to examine a bunch if bit-pairs to
  # figure out the 'type' (size) of a variable number of operands.

  def _get_operand_types(self, byte):
    """Parse BYTE value and leturn a list containing only 1's or 2's,
    indicating both the number of operands to read, and the size of each."""

    type_list = []
    bf = BitField(byte)
    field_list = [bf[6:8], bf[4:6], bf[2:4], bf[0:2]]
    for value in field_list:
      if value == 0:
        type_list.append(2)
      elif 1<= value <= 2:
        type_list.append(1)
    return type_list

  def _variable_2op(self, opcode):
    type_list = self._get_operand_types(self._memory[self.program_counter])
    self.program_counter += 1

    if len(type_list) != 2:
      raise ZOperationError # sanity check

    operands = []
    for size in type_list:
      if size == 1:
        operand = self._memory[self.program_counter]
      elif size == 2:
        operand = self._memory.read_word(self.program_counter)
      operands.append(operand)
      self.program_counter += size

    return [opcode, operands]

  def _variable_var(self, opcode):
    type_list = self._get_operand_types(self._memory[self.program_counter])
    self.program_counter += 1

    # Two opcodes are 'special' in that they have a whole extra byte
    # of operand-types to parse.  (They can use up to 8 operands.)
    if opcode == 236 or opcode == 250:
      type_list2 = self._get_operand_types(self._memory[self.program_counter])
      self.program_counter += 1
      type_list += type_list2

    operands = []
    for size in type_list:
      if size == 1:
        operand = self._memory[self.program_counter]
      elif size == 2:
        operand = self._memory.read_word(self.program_counter)
      operands.append(operand)
      self.program_counter += size

    return [opcode, operands]


  # For z5, opcode 0xbe is weird.  The "true" opcode is given in
  # subsequent byte, followed by variable number of operands.
  def _extended_var(self, opcode):
    actual_opcode = self._memory[self.program_counter]
    self.program_counter += 1

    type_list = self._get_operand_types(self._memory[self.program_counter])
    self.program_counter += 1

    operands = []
    for size in type_list:
      if size == 1:
        operand = self._memory[self.program_counter]
      elif size == 2:
        operand = self._memory.read_word(self.program_counter)
      operands.append(operand)
      self.program_counter += size

    # Return the actual opcode + 255, so that we can tell it apart
    # from the usual, non-extended funcs.
    return [0x100 + actual_opcode, operands]


  # Public funcs that the ZPU may also need to call, depending on the
  # opcode being executed:

  def get_zstring(self):
    """For string opcodes, return the zstring pointed to by the PC.
    Increment PC just past the text.  (The caller is responsible for
    converting the bytes into ascii.)"""

    start_addr = self.program_counter
    bf = BitField(0)

    while True:
      bf.__init__(self._memory.read_word(self.program_counter))
      program_counter += 2
      if bf[15] == 1:
        break

    return self._memory[start:self.program_counter]


  def get_store_address(self):
    """For store opcodes, read byte pointed to by PC and return the
    variable number in which the operation result should be stored.
    Increment the PC as necessary."""

    variable_num = self._memory[self.program_counter]
    self.program_counter += 1
    return variable_num


  def get_branch_offset(self):
    """For branching opcodes, examine address pointed to by PC, and
    return two values: first, either True or False (indicating whether
    to branch if true or branch if false), and second, the address to
    jump to.  Increment the PC as necessary."""

    bf = BitField(self._memory.read_word(self.program_counter))
    if bf[14] == 1:
      self.program_counter += 1
      return bf[15], bf[8:14]
    else:
      self.program_counter += 2
      return bf[15], bf[0:14]
