#
# Unit and integration tests for the glk module.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
import sys
import subprocess
import ctypes
from unittest import TestCase

from . import glk_test_program
import zvm.glk as glk

class AnyGlkTestsMixIn:
    """Integration tests that can be used with any Glk library. Aside
    from serving as integration tests, they also ensure that the Glk
    specification is observed precisely, and as such they can be used
    to validate the integrity of any Glk library in question.

    This is a mix-in class, intended to be mixed-in with an existing
    subclass of unittest.TestCase.  Subclasses should be sure to set
    up the glkLib attribute of the class to point to a Glk library, or
    else lots of AttributeError exceptions will occur."""

    def testGestaltCharInputProvidesValidInformation(self):
        # This tests Section 2.3 of the Glk spec 0.7.0, ensuring that
        # all characters and special key codes are reported to be
        # typable or untypable for single-key input.

        for char in range(0, 1000):
            result = self.glkLib.glk_gestalt(glk.gestalt_CharInput, char)
            assert result == glk.TRUE or result == glk.FALSE

        keycodes = [ getattr(glk, keycode)
                     for keycode in list(glk.__dict__.keys())
                     if keycode.startswith("keycode_") ]

        for keycode in keycodes:
            result = self.glkLib.glk_gestalt(glk.gestalt_CharInput, keycode)
            assert result == glk.TRUE or result == glk.FALSE

    def testGestaltLineInputProvidesValidInformation(self):
        # This tests Section 2.2 of the Glk spec 0.7.0, ensuring that
        # all characters are reported to be either typable or
        # untypable for line input.

        for char in range(0, 1000):
            result = self.glkLib.glk_gestalt(glk.gestalt_LineInput, char)
            assert result == glk.TRUE or result == glk.FALSE

    def testGestaltLineInputReportsAsciiCharsAreTypable(self):
        # This tests Section 2.2 of the Glk spec 0.7.0, ensuring that
        # the ASCII character set is guaranteed to be typable by the
        # end-user for line input.

        for char in range(32, 127):
            result = self.glkLib.glk_gestalt(glk.gestalt_LineInput, char)
            self.assertEqual(result, glk.TRUE)

    def testGestaltLineInputReportsProperCharsAreUntypable(self):
        # This tests Section 2.2 of the Glk spec 0.7.0, ensuring that
        # certain characters are reported to be untypable by the
        # end-user for line input.

        untypableCharacters = (list(range(0, 32)) +
                               list(range(127, 160)) +
                               list(range(256, 1000)))

        for char in untypableCharacters:
            result = self.glkLib.glk_gestalt(glk.gestalt_LineInput, char)
            self.assertEqual(result, glk.FALSE)

    def testGestaltCharOutputReportsProperCharsAreUnprintable(self):
        # This tests Section 2.1 of the Glk spec 0.7.0, ensuring that
        # certain characters are reported to be unprintable.

        unprintableCharacters = (list(range(0, 10)) +
                                 list(range(11, 32)) +
                                 list(range(127, 160)) +
                                 list(range(256, 1000)))

        for char in unprintableCharacters:
            numGlyphs = glk.glui32()
            result = self.glkLib.glk_gestalt_ext(
                glk.gestalt_CharOutput,
                char,
                ctypes.pointer(numGlyphs),
                1
                )

            self.assertEqual(result, glk.gestalt_CharOutput_CannotPrint)

    def testGestaltCharOutputProvidesValidInformation(self):
        # This tests Section 2.1 of the Glk spec 0.7.0, ensuring the
        # integrity of the information provided by the CharOutput
        # gestalt.

        for char in range(0, 1000):
            numGlyphs = glk.glui32()
            result = self.glkLib.glk_gestalt_ext(
                glk.gestalt_CharOutput,
                char,
                ctypes.pointer(numGlyphs),
                1
                )

            # Ensure that the result is a valid value.
            if result == glk.gestalt_CharOutput_CannotPrint:
                pass
            elif result == glk.gestalt_CharOutput_ExactPrint:
                # Any character that can be printed exactly should
                # only be one glyph long.
                self.assertEqual(numGlyphs.value, 1)
            elif result == glk.gestalt_CharOutput_ApproxPrint:
                # Any character that can be printed approximately
                # should be at least one glyph long.
                assert numGlyphs.value >= 1
            else:
                raise AssertionError( "result is invalid." )

    def testGestaltRandomCombinationsWork(self):
        # Section 1.7 of the the Glk spec 0.7.0 says that calling
        # glk_gestalt(x, y) is equivalent to calling
        # glk_gestalt_ext(x, y, NULL, 0), and it also says that it's
        # valid for x and y to be any value, so we will test both of
        # these things here.

        for x in range(0, 100):
            for y in range(0, 100):
                self.assertEqual(
                    self.glkLib.glk_gestalt(x, y),
                    self.glkLib.glk_gestalt_ext(x, y, glk.NULL, 0)
                    )


class CheapGlkTests(TestCase, AnyGlkTestsMixIn):
    """CheapGlk-specific tests."""

    def setUp(self):
        self.glkLib = glk_test_program.CheapGlkLibrary()

    def testGestaltVersionWorks(self):
        CHEAP_GLK_VERSION = 0x705
        self.assertEqual(
            self.glkLib.glk_gestalt(glk.gestalt_Version, 0),
            CHEAP_GLK_VERSION
            )
        self.assertEqual(
            self.glkLib.glk_gestalt_ext(glk.gestalt_Version, 0, glk.NULL, 0),
            CHEAP_GLK_VERSION
            )

    def testGlkProgramWorks(self):
        glk_program = subprocess.Popen(
            args = [sys.executable, glk_test_program.__file__],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            universal_newlines = True
            )
        stdout, stderr = glk_program.communicate("quit\n")
        self.assertEqual(glk_program.returncode, 0)
        assert "Hello, world!" in stdout
        assert "Goodbye, world!" in stdout
        assert len(stderr) == 0
