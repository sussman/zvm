#
# A helper class to access individual bits of a bitfield in a Pythonic
# way.
#
# Inspired from a recipe at:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/113799
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class BitField(object):
    """An bitfield gives read/write access to the individual bits of a
    value, in array and slice notation.

    Conversion back to an int value is also supported, and a method is
    provided to print the value in binary for debug purposes.

    For all indexes, 0 is the LSB (Least Significant Bit)."""

    def __init__(self, value=0):
        """Initialize a bitfield object from a number or string value."""
        if isinstance(value, str):
            self._d = ord(value)
        else:
            self._d = value

    def __getitem__(self, index):
        """Get the value of a single bit or slice."""
        if isinstance(index, slice):
            start, stop = index.start, index.stop
            if start > stop:
                (start, stop) = (stop, start)
            mask = (1<<(stop - start)) -1
            return (self._d >> start) & mask
        else:
            return (self._d >> index) & 1

    def __setitem__(self, index, value):
        """Set the value of a single bit or slice."""
        if isinstance(value, str):
            value = ord(value)
        if isinstance(index, slice):
            start, stop = index.start, index.stop
            mask = (1<<(stop - start)) -1
            value = (value & mask) << start
            mask = mask << start
            self._d = (self._d & ~mask) | value
            return (self._d >> start) & mask
        else:
            value = (value) << index
            mask = (1) << index
            self._d  = (self._d & ~mask) | value

    def __int__(self):
        """Return the whole bitfield as an integer."""
        return self._d

    def to_str(self, len):
        """Print the binary representation of the bitfield."""
        return ''.join(["%d" % self[i]
                        for i in range(len-1,-1,-1)])
