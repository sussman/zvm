#
# This module defines a ctypes foreign function interface to a Glk
# library that has been built as a shared library.  For more information
# on the Glk API, see http://www.eblong.com/zarf/glk/.
#
# Note that the way this module interfaces with a Glk library is
# slightly different from the standard; the standard interface
# actually assumes that a Glk library is in fact not a library, but a
# "front-end" program that is statically linked to a Glk back-end,
# also known as a Glk "program", by calling the back-end's glk_main()
# function.
#
# Instead of this, we assume that the Glk library is actually a shared
# library that is initialized by some external source--be it a Python
# script or a compiled program--and used by this module.  Note that
# this is actually the way some Glk libraries, such as WindowsGlk, are
# made to function.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import os
import ctypes

# These are ctypes-style declarations that reflect the Glk.h file,
# which defines the Glk API, version 0.7.0.  The most recent version
# of Glk.h can be found here:
#
#   http://www.eblong.com/zarf/glk/glk.h
#
# Note that there are ctypes extension libraries that can do this kind
# of thing for us (that is, take a .h file and automatically generate
# a ctypes wrapper from it); however, the only one that exists at the
# time of this writing is ctypeslib, which has dependencies that would
# make our build process quite complex.  Given the relatively small
# size of the Glk API and the freedom we get from hand-coding the
# interface ourselves, we're not using ctypeslib.

wintype_TextBuffer = 3
evtype_LineInput = 3

glui32 = ctypes.c_uint32
winid_t = ctypes.c_void_p

# TRUE, FALSE, and NULL aren't defined in glk.h, but are mentioned in
# Section 1.9 of the Glk spec 0.7.0.
TRUE = 1
FALSE = 0
NULL = ctypes.pointer(glui32(0))

gestalt_Version = 0
gestalt_CharInput = 1
gestalt_LineInput = 2
gestalt_CharOutput = 3
gestalt_CharOutput_CannotPrint = 0
gestalt_CharOutput_ApproxPrint = 1
gestalt_CharOutput_ExactPrint = 2
gestalt_MouseInput = 4
gestalt_Timer = 5
gestalt_Graphics = 6
gestalt_DrawImage = 7
gestalt_Sound = 8
gestalt_SoundVolume = 9
gestalt_SoundNotify = 10
gestalt_Hyperlinks = 11
gestalt_HyperlinkInput = 12
gestalt_SoundMusic = 13
gestalt_GraphicsTransparency = 14
gestalt_Unicode = 15

class event_t(ctypes.Structure):
    _fields_ = [("type", glui32),
                ("win", winid_t),
                ("val1", glui32),
                ("val2", glui32)]

keycode_Unknown  = 0xffffffff
keycode_Left     = 0xfffffffe
keycode_Right    = 0xfffffffd
keycode_Up       = 0xfffffffc
keycode_Down     = 0xfffffffb
keycode_Return   = 0xfffffffa
keycode_Delete   = 0xfffffff9
keycode_Escape   = 0xfffffff8
keycode_Tab      = 0xfffffff7
keycode_PageUp   = 0xfffffff6
keycode_PageDown = 0xfffffff5
keycode_Home     = 0xfffffff4
keycode_End      = 0xfffffff3
keycode_Func1    = 0xffffffef
keycode_Func2    = 0xffffffee
keycode_Func3    = 0xffffffed
keycode_Func4    = 0xffffffec
keycode_Func5    = 0xffffffeb
keycode_Func6    = 0xffffffea
keycode_Func7    = 0xffffffe9
keycode_Func8    = 0xffffffe8
keycode_Func9    = 0xffffffe7
keycode_Func10   = 0xffffffe6
keycode_Func11   = 0xffffffe5
keycode_Func12   = 0xffffffe4
keycode_MAXVAL   = 28

class stream_result_t(ctypes.Structure):
    _fields_ = [("readcount", glui32),
                ("writecount", glui32)]

# Function prototypes for the Glk API.  It is a list of 3-tuples; each
# item in the list represents a function prototype, and each 3-tuple
# is in the form (result_type, function_name, arg_types).

GLK_LIB_API = [
    (None, "glk_set_window", (winid_t,)),
    (None, "glk_put_string", (ctypes.c_char_p,)),
    (None, "glk_request_line_event", (winid_t, ctypes.c_char_p, glui32,
                                      glui32)),
    (None, "glk_select", (ctypes.POINTER(event_t),)),
    (None, "glk_exit", ()),
    (None, "glk_tick", ()),
    (glui32, "glk_gestalt", (glui32, glui32)),
    (glui32, "glk_gestalt_ext", (glui32, glui32, ctypes.POINTER(glui32),
                                 glui32)),
    (winid_t, "glk_window_get_root", ()),
    (winid_t, "glk_window_open", (winid_t, glui32, glui32, glui32, glui32)),
    (None, "glk_window_close", (winid_t, ctypes.POINTER(stream_result_t))),
    (None, "glk_window_get_size", (winid_t, ctypes.POINTER(glui32),
                                   ctypes.POINTER(glui32)) ),
    (None, "glk_window_set_arrangement", (winid_t, glui32, glui32, winid_t)),
    (None, "glk_window_get_arrangement", (winid_t, ctypes.POINTER(glui32),
                                          ctypes.POINTER(glui32),
                                          ctypes.POINTER(winid_t))),
    (winid_t, "glk_window_iterate", (winid_t, ctypes.POINTER(glui32))),
    (glui32, "glk_window_get_rock", (winid_t,)),
    (glui32, "glk_window_get_type", (winid_t,)),
    (winid_t, "glk_window_get_parent", (winid_t,)),
    (winid_t, "glk_window_get_sibling", (winid_t,)),
    (None, "glk_window_clear", (winid_t,)),
    (None, "glk_window_move_cursor", (winid_t, glui32, glui32)),    
    ]

class GlkLib:
    """Encapsulates the ctypes interface to a Glk shared library. When
    instantiated, it wraps the shared library with the appropriate
    function prototypes from the Glk API to reduce the chance of
    mis-calls that may result in segfaults (this effectively simulates
    the strong type-checking a C compiler would perform)."""

    def __init__(self, lib_name):
        """Instantiates the instance, binding it to the given shared
        library (which is referenced by name)."""

        self._dll = ctypes.CDLL(lib_name)

        # Create function prototypes for the Glk API, bind them to
        # functions in our shared library, and then bind the function
        # instances as methods to this object.

        for function_prototype in GLK_LIB_API:
            result_type, function_name, arg_types = function_prototype
            prototype = ctypes.CFUNCTYPE(result_type, *arg_types)
            function = prototype((function_name, self._dll))
            setattr(self, function_name, function)

    def glk_char_to_lower(self, ch):
        raise NotImplementedError("Use unicode.lower() instead.")

    def glk_char_to_upper(self, ch):
        raise NotImplementedError("Use unicode.upper() instead.")
