#
# Unit tests for the zscii class.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
from unittest import TestCase
from zvm import zstring
import mock.zmemory

class BitFieldTests(TestCase):
    def build_translator(self, version, reads=None):
        mem = mock.zmemory.MockZMemory(version, reads)
        return zstring.ZsciiTranslator(mem)

    def testCreateVersions(self):
        """Test that all ZM versions can be created without
        fault. Verify that the v5 has a mouse click input event."""
        # ZM 1-4
        for version in xrange(1,5):
            z = self.build_translator(version)
            self.failUnlessRaises(AttributeError, getattr, z, 'MOUSE_CLICK')
        # ZM 5
        z = self.build_translator(5, [(mock.zmemory.WORD, 0x36, 0)])
        z.utoz(z.MOUSE_CLICK)

    def testGetUnicode(self):
        """Try a couple of zscii-to-unicode conversions, involving
        various ranges of the output spectrum."""
        z = self.build_translator(5, [(mock.zmemory.WORD, 0x36, 0)])
        self.failUnlessEqual(z.ztou(97), u"a")
        self.failUnlessEqual(z.ztou(13), u"\n")
        self.failUnlessEqual(z.ztou(168), u"\xcf")
        self.failUnlessRaises(IndexError, z.ztou, z.CUR_UP)

    def testGetZscii(self):
        """Try a couple of unicode-to-zscii conversions, involving
        various ranges of the input spectrum."""
        z = self.build_translator(5, [(mock.zmemory.WORD, 0x36, 0)])
        self.failUnlessEqual(z.utoz(u"a"), 97)
        self.failUnlessEqual(z.utoz(u"\n"), 13)
        self.failUnlessEqual(z.utoz(u"\xcf"), 168)
        self.failUnlessEqual(z.utoz(z.CUR_UP), 129)
        self.failUnlessEqual(z.utoz(z.MOUSE_CLICK), 254)

