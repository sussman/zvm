#
# A ZString-to-ASCII Universal Translator.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZStringEndOfString(Exception):
    """No more data left in string."""

class ZStringStream(object):
    """This class takes an address and a ZMemory, and treats that as
    the begginning of a ZString. Subsequent calls to get() will return
    one ZChar code at a time, raising ZStringEndOfString when there is
    no more data."""

    def __init__(self, zmem, addr):
        self._mem = zmem
        self._addr = addr
        self._has_ended = False
        self._get_block()

    def _get_block(self):
        from bitfield import BitField
        chunk = self._mem[self._addr:self._addr+2]
        self._data = BitField(''.join([chr(x) for x in chunk]))
        self._addr += 2
        self._char_in_block = 0

    def get(self, num=1):
        if self._has_ended:
            raise ZStringEndOfString

        # We must read in sequence bits 14-10, 9-5, 4-0.
        offset = (2 - self._char_in_block) * 5
        zchar = self._data[offset:offset+5]

        if self._char_in_block == 2:
            # If end-of-string marker is set...
            if self._data[15] == 1:
                self._has_ended = True
            else:
                self._get_block()
        else:
            self._char_in_block += 1

        return zchar
