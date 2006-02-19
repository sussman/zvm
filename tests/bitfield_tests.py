#
# Unit tests for the bitfield class.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
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
