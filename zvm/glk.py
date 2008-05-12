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

glsi32 = ctypes.c_int32
glui32 = ctypes.c_uint32

winid_t = ctypes.c_void_p
strid_t = ctypes.c_void_p
frefid_t = ctypes.c_void_p
schanid_t = ctypes.c_void_p

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

evtype_None = 0
evtype_Timer = 1
evtype_CharInput = 2
evtype_LineInput = 3
evtype_MouseInput = 4
evtype_Arrange = 5
evtype_Redraw = 6
evtype_SoundNotify = 7
evtype_Hyperlink = 8

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

style_Normal = 0
style_Emphasized = 1
style_Preformatted = 2
style_Header = 3
style_Subheader = 4
style_Alert = 5
style_Note = 6
style_BlockQuote = 7
style_Input = 8
style_User1 = 9
style_User2 = 10
style_NUMSTYLES = 11

class stream_result_t(ctypes.Structure):
    _fields_ = [("readcount", glui32),
                ("writecount", glui32)]

wintype_AllTypes = 0
wintype_Pair = 1
wintype_Blank = 2
wintype_TextBuffer = 3
wintype_TextGrid = 4
wintype_Graphics = 5

winmethod_Left  = 0x00
winmethod_Right = 0x01
winmethod_Above = 0x02
winmethod_Below = 0x03
winmethod_DirMask = 0x0f

winmethod_Fixed = 0x10
winmethod_Proportional = 0x20
winmethod_DivisionMask = 0xf0

fileusage_Data = 0x00
fileusage_SavedGame = 0x01
fileusage_Transcript = 0x02
fileusage_InputRecord = 0x03
fileusage_TypeMask = 0x0f

fileusage_TextMode   = 0x100
fileusage_BinaryMode = 0x000

filemode_Write = 0x01
filemode_Read = 0x02
filemode_ReadWrite = 0x03
filemode_WriteAppend = 0x05

seekmode_Start = 0
seekmode_Current = 1
seekmode_End = 2

stylehint_Indentation = 0
stylehint_ParaIndentation = 1
stylehint_Justification = 2
stylehint_Size = 3
stylehint_Weight = 4
stylehint_Oblique = 5
stylehint_Proportional = 6
stylehint_TextColor = 7
stylehint_BackColor = 8
stylehint_ReverseColor = 9
stylehint_NUMHINTS = 10

stylehint_just_LeftFlush = 0
stylehint_just_LeftRight = 1
stylehint_just_Centered = 2
stylehint_just_RightFlush = 3

# Function prototypes for the core Glk API.  It is a list of 3-tuples; each
# item in the list represents a function prototype, and each 3-tuple
# is in the form (result_type, function_name, arg_types).

CORE_GLK_LIB_API = [
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
    (strid_t, "glk_window_get_stream", (winid_t,)),
    (None, "glk_window_set_echo_stream", (winid_t, strid_t)),
    (strid_t, "glk_window_get_echo_stream", (winid_t,)),
    (None, "glk_set_window", (winid_t,)),
    (strid_t, "glk_stream_open_file", (frefid_t, glui32, glui32)),
    (strid_t, "glk_stream_open_memory", (ctypes.c_char_p,
                                         glui32, glui32, glui32)),
    (None, "glk_stream_close", (strid_t, ctypes.POINTER(stream_result_t))),
    (strid_t, "glk_stream_iterate", (strid_t, ctypes.POINTER(glui32))),
    (glui32, "glk_stream_get_rock", (strid_t,)),
    (None, "glk_stream_set_position", (strid_t, glsi32, glui32)),
    (glui32, "glk_stream_get_position", (strid_t,)),
    (None, "glk_stream_set_current", (strid_t,)),
    (strid_t, "glk_stream_get_current", ()),
    (None, "glk_put_char", (ctypes.c_ubyte,)),
    (None, "glk_put_char_stream", (strid_t, ctypes.c_ubyte)),
    (None, "glk_put_string", (ctypes.c_char_p,)),
    (None, "glk_put_string_stream", (strid_t, ctypes.c_char_p)),
    (None, "glk_put_buffer", (ctypes.c_char_p, glui32)),
    (None, "glk_put_buffer_stream", (strid_t, ctypes.c_char_p, glui32)),
    (None, "glk_set_style", (glui32,)),
    (None, "glk_set_style_stream", (strid_t, glui32)),
    (glsi32, "glk_get_char_stream", (strid_t,)),
    (glui32, "glk_get_line_stream", (strid_t, ctypes.c_char_p, glui32)),
    (glui32, "glk_get_buffer_stream", (strid_t, ctypes.c_char_p, glui32)),
    (None, "glk_stylehint_set", (glui32, glui32, glui32, glsi32)),
    (None, "glk_stylehint_clear", (glui32, glui32, glui32)),
    (glui32, "glk_style_distinguish", (winid_t, glui32, glui32)),
    (glui32, "glk_style_measure", (winid_t, glui32, glui32,
                                   ctypes.POINTER(glui32))),
    (frefid_t, "glk_fileref_create_temp", (glui32, glui32)),
    (frefid_t, "glk_fileref_create_by_name", (glui32, ctypes.c_char_p,
                                              glui32)),
    (frefid_t, "glk_fileref_create_by_prompt", (glui32, glui32, glui32)),
    (frefid_t, "glk_fileref_create_from_fileref", (glui32, frefid_t,
                                                   glui32)),
    (None, "glk_fileref_destroy", (frefid_t,)),
    (frefid_t, "glk_fileref_iterate", (frefid_t, ctypes.POINTER(glui32))),
    (glui32, "glk_fileref_get_rock", (frefid_t,)),
    (None, "glk_fileref_delete_file", (frefid_t,)),
    (glui32, "glk_fileref_does_file_exist", (frefid_t,)),
    (None, "glk_select", (ctypes.POINTER(event_t),)),
    (None, "glk_select_poll", (ctypes.POINTER(event_t),)),
    (None, "glk_request_timer_events", (glui32,)),
    (None, "glk_request_line_event", (winid_t, ctypes.c_char_p, glui32,
                                      glui32)),
    (None, "glk_request_char_event", (winid_t,)),
    (None, "glk_request_mouse_event", (winid_t,)),
    (None, "glk_cancel_line_event", (winid_t, ctypes.POINTER(event_t))),
    (None, "glk_cancel_char_event", (winid_t,)),
    (None, "glk_cancel_mouse_event", (winid_t,)),
    ]

# Function prototypes for the optional Unicode extension of the Glk
# API.
UNICODE_GLK_LIB_API = [
    (None, "glk_put_char_uni", (glui32,)),
    (None, "glk_put_string_uni", (ctypes.POINTER(glui32),)),
    (None, "glk_put_buffer_uni", (ctypes.POINTER(glui32), glui32)),
    (None, "glk_put_char_stream_uni", (strid_t, glui32)),
    (None, "glk_put_string_stream_uni", (strid_t, ctypes.POINTER(glui32))),
    (None, "glk_put_buffer_stream_uni", (strid_t, ctypes.POINTER(glui32),
                                         glui32)),
    (glsi32, "glk_get_char_stream_uni", (strid_t,)),
    (glui32, "glk_get_buffer_stream_uni", (strid_t, ctypes.POINTER(glui32),
                                           glui32)),
    (glui32, "glk_get_line_stream_uni", (strid_t, ctypes.POINTER(glui32),
                                         glui32)),
    (strid_t, "glk_stream_open_file_uni", (frefid_t, glui32, glui32)),
    (strid_t, "glk_stream_open_memory_uni", (ctypes.POINTER(glui32),
                                             glui32, glui32, glui32)),
    (None, "glk_request_char_event_uni", (winid_t,)),
    (None, "glk_request_line_event_uni", (winid_t, ctypes.POINTER(glui32),
                                          glui32, glui32))
    ]

class GlkLib(object):
    """Encapsulates the ctypes interface to a Glk shared library. When
    instantiated, it wraps the shared library with the appropriate
    function prototypes from the Glk API to reduce the chance of
    mis-calls that may result in segfaults (this effectively simulates
    the strong type-checking a C compiler would perform)."""

    def __init__(self, lib_name):
        """Instantiates the instance, binding it to the given shared
        library (which is referenced by name)."""

        self._dll = ctypes.CDLL(lib_name)

        self.__bind_prototypes(CORE_GLK_LIB_API)

        if self.glk_gestalt(gestalt_Unicode, 0) == 1:
            self.__bind_prototypes(UNICODE_GLK_LIB_API)
        else:
            self.__bind_not_implemented_prototypes(UNICODE_GLK_LIB_API)

    def __bind_prototypes(self, function_prototypes):
        """Create function prototypes from the given list of 3-tuples
        of the form (result_type, function_name, arg_types), bind them
        to functions in our shared library, and then bind the function
        instances as methods to this object."""

        for function_prototype in function_prototypes:
            result_type, function_name, arg_types = function_prototype
            prototype = ctypes.CFUNCTYPE(result_type, *arg_types)
            function = prototype((function_name, self._dll))
            setattr(self, function_name, function)

    def __bind_not_implemented_prototypes(self, function_prototypes):
        """Create functions with the names from the given list of
        3-tuples of the form (result_type, function_name, arg_types)
        that simply raise NotImplementedError, and bind them to this
        object.  This should be used when a Glk library doesn't
        support some optional extension of the Glk API."""

        def notImplementedFunction(*args, **kwargs):
            raise NotImplementedError( "Function not implemented " \
                                       "by this Glk library." )

        for function_prototype in function_prototypes:
            _, function_name, _ = function_prototype
            setattr(self, function_name, notImplementedFunction)

    def glk_char_to_lower(self, ch):
        raise NotImplementedError("Use unicode.lower() instead.")

    def glk_char_to_upper(self, ch):
        raise NotImplementedError("Use unicode.upper() instead.")

    def glk_buffer_to_lower_case_uni(self, buf, len, numchars):
        raise NotImplementedError("Use unicode.lower() instead.")

    def glk_buffer_to_upper_case_uni(self, buf, len, numchars):
        raise NotImplementedError("Use unicode.upper() instead.")

    def glk_buffer_to_title_case_uni(self, buf, len, numchars, lowerrest):
        raise NotImplementedError("Use unicode.title() instead.")
