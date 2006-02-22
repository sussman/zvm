#
# A class which represents the z-machine's main memory bank.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#


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
  pass

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

    # Dynamic + static must not exceed 64k
    dynamic_plus_static = ((self._dynamic_end - self._dynamic_start)
                           + (self._static_end - self._static_start))
    if dynamic_plus_static > 65534:
      raise ZMemoryBadMemoryLayout

    # What z-machine version is this story file?
    self.version = ord(self._memory[0])

    # Validate game size
    if self.version >= 1 and self.version <= 3:
      if self._total_size > 131072:
        raise ZMemoryBadStoryfileSize
    elif self.version == 4 or self.version == 5:
      if self._total_size > 262144:
        raise ZMemoryBadStoryfileSize
    else:
      raise ZMemoryUnsupportedVersion



  def _check_bounds(self, index):
    if index < 0 or index >= self._total_size:
      raise ZMemoryOutOfBounds

  def _check_static(self, index):
    if index >= self._static_start and index <= self._static_end:
      raise ZMemoryIllegalWrite

  def _bytes_to_16bit_int(self, byte1, byte2):
    """Convert two bytes into a 16-bit integer."""
    return (ord(byte1) << 8) + ord(byte2)

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
    self._check_bounds(end)
    self._check_static(start)
    self._check_static(end)
    self._memory[start:end] = sequence

  def word_address(self, address):
    """Return the 'actual' address of word address ADDRESS."""
    if address < 0 or address > (self._total_size / 2):
      raise ZMemoryOutOfBounds
    return address*2

  def packed_address(self, address):
    """Return the 'actual' address of packed address ADDRESS."""
    if self.version >= 1 and self.version <= 3:
      if address < 0 or address > (self._total_size / 2):
        raise ZMemoryOutOfBounds
      return address*2
    elif self.version == 4 or self.version == 5:
      if address < 0 or address > (self._total_size / 4):
        raise ZMemoryOutOfBounds
      return address*4
    else:
      raise ZMemoryUnsupportedVersion

  def read_word(self, address):
    """Return the 16-bit value stored at ADDRESS, ADDRESS+1."""
    if address < 0 or address >= (self._total_size - 1):
      raise ZMemoryOutOfBounds
    return self._bytes_to_16bit_int(self._memory[address],
                                    self._memory[(address + 1)])



