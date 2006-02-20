#
# A class which represents the z-machine's main memory bank.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#


# This class that represents the "main memory" of the z-machine.  It's
# readable and writable through normal indexing and slice notation,
# just like a typical python 'sequence' object (e.g. mem[342] and
# mem[22:90]).  It enforces read-only areas of memory, and also the
# ability to return 2-byte word-addresses.

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



class ZMemory(object):

  def __init__(self, initial_string):
    """Construct class based on a string that represents an initial
    'snapshot' of main memory."""
    if initial_string is None:
      raise ZMemoryBadInitialization

    self._total_size = len(initial_string)
    self._memory = [x for x in initial_string]

    self._static_start = self.get_word_value(0x0e)
    self._static_end = min(0x0ffff, self._total_size)
    self._dynamic_start = 0
    self._dynamic_end = self._static_start - 1
    self._high_start = self.get_word_value(0x04)
    self._high_end = self._total_size

  ### implement sequence funcs:
  ### http://python.org/doc/2.4.2/ref/sequence-types.html

  def _bytes_to_16bit_int(self, byte1, byte2):
    """Convert two bytes into a 16-bit integer."""
    return (ord(byte1) << 8) + ord(byte2)

  def get_word_value(self, index):
    """Return the 16-bit value stored at INDEX, INDEX+1."""
    if index < 0 or index >= (self._total_size - 1):
      raise ZMemoryOutOfBounds
    return self._bytes_to_16bit_int(self._memory[index],
                                    self._memory[(index + 1)])

  def print_map(self):
    """Pretty-print a description of the memory map."""
    print "Dynamic memory: ", self._dynamic_start, "-", self._dynamic_end
    print " Static memory: ", self._static_start, "-", self._static_end
    print "   High memory: ", self._high_start, "-", self._high_end

  def __getitem__(self, index):
    """Return the byte value stored at address INDEX.."""
    if index < 0 or index >= self._total_size:
      raise ZMemoryOutOfBounds
    return self._memory[index]

  def __setitem__(self, index, value):
    """Set VALUE in memory address INDEX."""
    if index < 0 or index >= self._total_size:
      raise ZMemoryOutOfBounds
    if index >= self._static_start and index <= self._static_end:
      raise ZMemoryIllegalWrite
    self._memory[index] = value


