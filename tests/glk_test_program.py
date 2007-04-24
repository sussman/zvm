#
# Test program utilizing the glk module.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#
import sys
import os
import ctypes

# If we're being run from the root directory of our distribution, we
# want said root directory to be on our path so we can import zvm.
sys.path.append(os.getcwd())

import zvm.glk as glk

class CheapGlkLibrary(glk.GlkLib):
    """This class encapsulates the CheapGlk library.  Just instantiate
    it and then call its methods as though it's a ctypes interface to
    a Glk-compliant shared library."""

    def __init__(self):
        if os.name == "nt":
            lib_name = "cheapglk/libcheapglk"
        else:
            lib_name = "cheapglk/libcheapglk.so"
        glk.GlkLib.__init__(self, lib_name)

        # This is a CheapGlk-specific initialization function.
        self._dll.gli_initialize_misc()

def run_test_program(glkLib):
    """Runs the test program with the given Glk library. The given Glk
    library should provide a ctypes interface to a Glk-compliant
    shared library."""

    CharBufArrayType = ctypes.c_char * 256

    mainwin = glkLib.glk_window_open(0, 0, 0, glk.wintype_TextBuffer, 1)
    glkLib.glk_set_window(mainwin)
    glkLib.glk_put_string("Hello, world!\n")
    glkLib.glk_put_string("Type 'quit' to exit.\n")

    commandbuf = CharBufArrayType()
    event = glk.event_t()

    while 1:
        glkLib.glk_put_string("\n> ")
        glkLib.glk_request_line_event(mainwin,
                                      commandbuf,
                                      len(commandbuf)-1,
                                      0)
        gotline = False
        while not gotline:
            glkLib.glk_select(ctypes.pointer(event))
            if (event.type == glk.evtype_LineInput and
                event.win == mainwin):
                gotline = True
        cmdLength = event.val1
        commandbuf[cmdLength] = "\0"

        if commandbuf.value == "quit":
            glkLib.glk_put_string("Goodbye, world!\n")
            glkLib.glk_exit()

if __name__ == "__main__":
    run_test_program(CheapGlkLibrary())