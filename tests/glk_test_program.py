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
    it and then use it like you would any other glk.GlkLib instance."""

    def __init__(self):
        if sys.platform.startswith( "win" ) or sys.platform == "darwin":
            lib_name = "cheapglk/libcheapglk"
        else:
            lib_name = "cheapglk/libcheapglk.so"
        glk.GlkLib.__init__(self, lib_name)

        # This is a CheapGlk-specific initialization function.
        self._dll.gli_initialize_misc()

class WindowsGlkLibrary(glk.GlkLib):
    """This class encapsulates the WindowsGlk library.  Just
    instantiate it and then use it like you would any other glk.GlkLib
    instance.

    Note that WindowsGlk's Glk.dll file needs to be located in a
    directory that is somewhere on the DLL search order.  (You should
    be fine if you just put the DLL in the current working directory.)

    The WindowsGlk distribution can be found here:

      http://www.eblong.com/zarf/glk/

    Just do a search for 'WindowsGlk' and you'll find a link."""

    def __init__( self ):
        glk.GlkLib.__init__(self, "Glk")
        
        GLK_VERSION = 0x00000601

        if self._dll.InitGlk(GLK_VERSION) == 0:
            raise RuntimeError( "InitGlk() failed." )

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
