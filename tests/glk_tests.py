#
# Unit and integration tests for the glk module.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
import sys
import subprocess
from unittest import TestCase

import glk_test_program

class GlkTests(TestCase):
    def testGlkProgramWorks(self):
        glk_program = subprocess.Popen(
            args = [sys.executable, glk_test_program.__file__],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
            )
        glk_program.stdin.write("quit\n")
        glk_program.wait()
        self.assertEquals(glk_program.returncode, 0)
        text = glk_program.stdout.read()
        assert "Hello, world!" in text
        assert "Goodbye, world!" in text
