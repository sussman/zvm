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

wintype_TextBuffer = 3
evtype_LineInput = 3

glui32 = ctypes.c_uint32
winid_t = ctypes.c_void_p

class event_t(ctypes.Structure):
    _fields_ = [("type", glui32),
                ("win", winid_t),
                ("val1", glui32),
                ("val2", glui32)]

# Function prototypes for the Glk API.  It is a list of 3-tuples; each
# item in the list represents a function prototype, and each 3-tuple
# is in the form (result_type, function_name, arg_types).

GLK_LIB_API = [
    (winid_t, "glk_window_open", (winid_t, glui32, glui32, glui32, glui32)),
    (None, "glk_set_window", (winid_t,)),
    (None, "glk_put_string", (ctypes.c_char_p,)),
    (None, "glk_request_line_event", (winid_t, ctypes.c_char_p, glui32,
                                      glui32)),
    (None, "glk_select", (ctypes.POINTER(event_t),)),
    (None, "glk_exit", ()),
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
