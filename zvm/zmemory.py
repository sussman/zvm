#
# A class which represents the z-machine's main memory bank.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import bitfield
from zlogging import log

# This class that represents the "main memory" of the z-machine.  It's
# readable and writable through normal indexing and slice notation,
# just like a typical python 'sequence' object (e.g. mem[342] and
# mem[22:90]).  The class validates memory layout, enforces read-only
# areas of memory, and also the ability to return both word-addresses
# and 'packed' addresses.


class ZMemoryError(Exception):
  "General exception for ZMemory class"
  pass

class ZMemoryIllegalWrite(ZMemoryError):
  "Tried to write to a read-only part of memory"
  def __init__(self, address):
    super(ZMemoryIllegalWrite, self).__init__(
      "Illegal write to address %d" % address)

class ZMemoryBadInitialization(ZMemoryError):
  "Failure to initialize ZMemory class"
  pass

class ZMemoryOutOfBounds(ZMemoryError):
  "Accessed an address beyond the bounds of memory."
  pass

class ZMemoryBadMemoryLayout(ZMemoryError):
  "Static plus dynamic memory exceeds 64k"
  pass

class ZMemoryBadStoryfileSize(ZMemoryError):
  "Story is too large for Z-machine version."
  pass

class ZMemoryUnsupportedVersion(ZMemoryError):
  "Unsupported version of Z-story file."
  pass


class ZMemory(object):

  # A list of 64 tuples describing who's allowed to tweak header-bytes.
  # Index into the list is the header-byte being tweaked.
  # List value is a tuple of the form
  #
  #         [minimum_z_version, game_allowed, interpreter_allowed]
  #
  # Note: in section 11.1 of the spec, we should technically be
  # enforcing authorization by *bit*, not by byte.  Maybe do this
  # someday.

  HEADER_PERMS = ([1,0,0], [3,0,1], None, None,
                  [1,0,0], None, [1,0,0], None,
                  [1,0,0], None, [1,0,0], None,
                  [1,0,0], None, [1,0,0], None,
                  [1,1,1], [1,1,1], None, None,
                  None, None, None, None,
                  [2,0,0], None, [3,0,0], None,
                  [3,0,0], None, [4,1,1], [4,1,1],
                  [4,0,1], [4,0,1], [5,0,1], None,
                  [5,0,1], None, [5,0,1], [5,0,1],
                  [6,0,0], None, [6,0,0], None,
                  [5,0,1], [5,0,1], [5,0,0], None,
                  [6,0,1], None, [1,0,1], None,
                  [5,0,0], None, [5,0,0], None,
                  None, None, None, None,
                  None, None, None, None)

  def __init__(self, initial_string):
    """Construct class based on a string that represents an initial
    'snapshot' of main memory."""
    if initial_string is None:
      raise ZMemoryBadInitialization

    # Copy string into a _memory sequence that represents main memory.
    self._total_size = len(initial_string)
    self._memory = [ord(x) for x in initial_string]

    # Figure out the different sections of memory
    self._static_start = self.read_word(0x0e)
    self._static_end = min(0x0ffff, self._total_size)
    self._dynamic_start = 0
    self._dynamic_end = self._static_start - 1
    self._high_start = self.read_word(0x04)
    self._high_end = self._total_size
    self._global_variable_start = self.read_word(0x0c)

    # Dynamic + static must not exceed 64k
    dynamic_plus_static = ((self._dynamic_end - self._dynamic_start)
                           + (self._static_end - self._static_start))
    if dynamic_plus_static > 65534:
      raise ZMemoryBadMemoryLayout

    # What z-machine version is this story file?
    self.version = self._memory[0]

    # Validate game size
    if 1 <= self.version <= 3:
      if self._total_size > 131072:
        raise ZMemoryBadStoryfileSize
    elif 4 <= self.version <=  5:
      if self._total_size > 262144:
        raise ZMemoryBadStoryfileSize
    else:
      raise ZMemoryUnsupportedVersion

    log("Memory system initialized, map follows")
    log("  Dynamic memory: %x - %x" % (self._dynamic_start, self._dynamic_end))
    log("  Static memory: %x - %x" % (self._static_start, self._static_end))
    log("  High memory: %x - %x" % (self._high_start, self._high_end))
    log("  Global variable start: %x" % self._global_variable_start)

  def _check_bounds(self, index):
    if not (0 <= index < self._total_size):
      raise ZMemoryOutOfBounds

  def _check_static(self, index):
    """Throw error if INDEX is within the static-memory area."""
    if self._static_start <= index <= self._static_end:
      raise ZMemoryIllegalWrite(index)

  def print_map(self):
    """Pretty-print a description of the memory map."""
    print "Dynamic memory: ", self._dynamic_start, "-", self._dynamic_end
    print " Static memory: ", self._static_start, "-", self._static_end
    print "   High memory: ", self._high_start, "-", self._high_end

  def __getitem__(self, index):
    """Return the byte value stored at address INDEX.."""
    self._check_bounds(index)
    return self._memory[index]

  def __setitem__(self, index, value):
    """Set VALUE in memory address INDEX."""
    self._check_bounds(index)
    self._check_static(index)
    self._memory[index] = value

  def __getslice__(self, start, end):
    """Return a sequence of bytes from memory."""
    self._check_bounds(start)
    self._check_bounds(end)
    return self._memory[start:end]

  def __setslice__(self, start, end, sequence):
    """Set a range of memory addresses to SEQUENCE."""
    self._check_bounds(start)
    self._check_bounds(end - 1)
    self._check_static(start)
    self._check_static(end - 1)
    self._memory[start:end] = sequence

  def word_address(self, address):
    """Return the 'actual' address of word address ADDRESS."""
    if address < 0 or address > (self._total_size / 2):
      raise ZMemoryOutOfBounds
    return address*2

  def packed_address(self, address):
    """Return the 'actual' address of packed address ADDRESS."""
    if 1 <= self.version <= 3:
      if address < 0 or address > (self._total_size / 2):
        raise ZMemoryOutOfBounds
      return address*2
    elif 4 <= self.version <=  5:
      if address < 0 or address > (self._total_size / 4):
        raise ZMemoryOutOfBounds
      return address*4
    else:
      raise ZMemoryUnsupportedVersion

  def read_word(self, address):
    """Return the 16-bit value stored at ADDRESS, ADDRESS+1."""
    if address < 0 or address >= (self._total_size - 1):
      raise ZMemoryOutOfBounds
    return (self._memory[address] << 8) + self._memory[(address + 1)]

  def write_word(self, address, value):
    """Write the given 16-bit value at ADDRESS, ADDRESS+1."""
    if address < 0 or address >= (self._total_size - 1):
      raise ZMemoryOutOfBounds
    # Handle writing of a word to the game headers. If write_word is
    # used for this, we assume that it's the game that is setting the
    # header. The interpreter should use the specialized method.
    value_msb = (value >> 8) & 0xFF
    value_lsb = value & 0xFF
    if 0 <= address < 64:
      self.game_set_header(address, value_msb)
      self.game_set_header(address+1, value_lsb)
    else:
      self._memory[address] = value_msb
      self._memory[address+1] = value_lsb

  # Normal sequence syntax cannot be used to set bytes in the 64-byte
  # header.  Instead, the interpreter or game must call one of the
  # following APIs.

  def interpreter_set_header(self, address, value):
    """Possibly allow the interpreter to set header ADDRESS to VALUE."""
    if address < 0 or address > 63:
      raise ZMemoryOutOfBounds
    perm_tuple = self.HEADER_PERMS[address]
    if perm_tuple is None:
      raise ZMemoryIllegalWrite(address)
    if self.version >= perm_tuple[0] and perm_tuple[2]:
      self._memory[address] = value
    else:
      raise ZMemoryIllegalWrite(address)

  def game_set_header(self, address, value):
    """Possibly allow the game code to set header ADDRESS to VALUE."""
    if address < 0 or address > 63:
      raise ZMemoryOutOfBounds
    perm_tuple = self.HEADER_PERMS[address]
    if perm_tuple is None:
      raise ZMemoryIllegalWrite(address)
    if self.version >= perm_tuple[0] and perm_tuple[1]:
      self._memory[address] = value
    else:
      raise ZMemoryIllegalWrite(address)

  # The ZPU will need to read and write global variables.  The 240
  # global variables are located at a place determined by the header.

  def read_global(self, varnum):
    """Return 16-bit value of global variable VARNUM.  Incoming VARNUM
    must be between 0x10 and 0xFF."""
    if not (0x10 <= varnum <= 0xFF):
      raise ZMemoryOutOfBounds
    actual_address = self._global_variable_start + ((varnum - 0x10) * 2)
    return self.read_word(actual_address)

  def write_global(self, varnum, value):
    """Write 16-bit VALUE to global variable VARNUM.  Incoming VARNUM
    must be between 0x10 and 0xFF."""
    if not (0x10 <= varnum <= 0xFF):
      raise ZMemoryOutOfBounds
    if not (0x00 <= value <= 0xFFFF):
      raise ZMemoryIllegalWrite(address)
    log("Write %d to global variable %d" % (value, varnum))
    actual_address = self._global_variable_start + ((varnum - 0x10) * 2)
    bf = bitfield.BitField(value)
    self._memory[actual_address] = bf[8:15]
    self._memory[actual_address + 1] = bf[0:7]

  # The 'verify' opcode and the QueztalWriter class both need to have
  # a checksum of memory generated.

  def generate_checksum(self):
    """Return a checksum value which represents all the bytes of
    memory added from $0040 upwards, modulo $10000."""
    count = 0x40
    total = 0
    while count < self._total_size:
      total += self._memory[count]
      count += 1
    return (total % 0x10000)
