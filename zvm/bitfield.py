#
# A helper class to access individual bits of a bitfield in a Pythonic
# way.
#
# Inspired from a recipe at:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/113799
#
# Copyright 2006 David Anderson <david.anderson@calixo.net>
#                Ben Collins-Sussman <sussman@red-bean.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided
#   with the distribution.
#
#   * Neither the name of the <ORGANIZATION> nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#  OF THE POSSIBILITY OF SUCH DAMAGE.
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
            self._d = 0
            for i,v in zip(range(0,8*len(value),8),
                           [ord(s) for s in value[::-1]]):
                self[i:i+8] = v
        else:
            self._d = value

    def __getitem__(self, index):
        """Get the value of a single bit."""
        return (self._d >> index) & 1

    def __setitem__(self, index, value):
        """Set the value of a single bit."""
        value    = (value&1L)<<index
        mask     = (1L)<<index
        self._d  = (self._d & ~mask) | value

    def __getslice__(self, start, end):
        """Get the integer value of a slice of bits."""
        mask = 2L**(end - start) -1
        return (self._d >> start) & mask

    def __setslice__(self, start, end, value):
        """Set the binary value of a slice of the field, using the
        bits of the given integer."""
        mask = 2L**(end - start) -1
        value = (value & mask) << start
        mask = mask << start
        self._d = (self._d & ~mask) | value
        return (self._d >> start) & mask

    def __int__(self):
        """Return the whole bitfield as an integer."""
        return self._d

    def to_str(self, len):
        """Print the binary representation of the bitfield."""
        return ''.join(["%d" % self[i]
                        for i in range(len-1,-1,-1)])
