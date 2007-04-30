#
# A class which represents the z-machine's main memory bank.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import zvm.bitfield
import collections


class MockZMemoryExpectationError(Exception):
  """Effective access did not match expectations."""


# Constants for the different types of memory accesses.
BYTE = 0 # 1 byte
WORD = 1 # 2-byte word

# Mappings of these constants to strings.
_access_type_str = {
    BYTE: 'byte',
    WORD: 'word',
    }


class MockZMemory(object):
    def __init__(self, version, reads=None):
        self.version = version
        self._expected_reads = collections.deque(reads or [])

    def add_expected_reads(self, reads):
        """Add expected reads to the end of the expected sequence. The
        argument should be a list of (type, address, value) tuples."""
        self._expected_reads.extend(reads)

    def checked_memory_read(self, access_type, address):
        """Make sure that the requested memory read was expected, and
        return the preprogrammed value if it was. Return"""
        try:
            expected = self._expected_reads.popleft()
        except IndexError:
            raise MockZMemoryExpectationError(
                'Unexpected %s read of 0x%X' % (_access_type_str[access_type],
                                                address))

        if expected[0] != access_type or expected[1] != address:
            raise MockZMemoryExpectationError(
                'Expected %s read of 0x%X, got %s read of 0x%X' %
                (_access_type_str[expected[0]], expected[1],
                 _access_type_str[access_type], address))

        return expected[2]

    # Follows the implemented parts of the ZVM API.
    def read_word(self, address):
        return self.checked_memory_read(WORD, address)
