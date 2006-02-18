#
# Unit tests for the bitfield class.
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

from unittest import TestCase
from zvm.bitfield import BitField

class BitFieldTests(TestCase):
    def testCreateInt(self):
        for i in range(0,1024,3):
            bf = BitField(i)
            assert int(bf) == i, \
                   "int(BitField(%d)) -> %d" % (int(bf), i)

    def testCreateString(self):
        i = int(BitField('a'))
        assert i == 97, \
               "int(BitField('a')) -> %d" % i

    def testGetIndex(self):
        bf = BitField(3)
        assert bf[1] == 1
        assert bf[2] == 0
        assert bf[50] == 0

    def testGetSlice(self):
        bf = BitField(42)
        assert bf[3:6] == 5
        assert bf[50:52] == 0

    def testSetIndex(self):
        bf = BitField(42)
        bf[2] = 1
        assert int(bf) == 46

    def testSetSlice(self):
        bf = BitField(42)
        bf[0:3] = 7
        assert int(bf) == 47

    def testShowBitfield(self):
        bf = BitField(42)
        assert bf.to_str(8) == "00101010"
