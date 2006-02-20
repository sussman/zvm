#
# A ZSCII-to-ASCII Universal Translator.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class Zscii(object):
    # The default Unicode Translation Table that maps to ZSCII codes
    # 155-251. The codes are unicode codepoints for a host of strange
    # characters.
    DEFAULT_UTT = (0xe4, 0xf6, 0xfc, 0xc4, 0xd6, 0xdc,
                   0xdf, 0xbb, 0xab, 0xeb, 0xef, 0xff,
                   0xcb, 0xcf, 0xe1, 0xe9, 0xed, 0xf3,
                   0xfa, 0xfd, 0xc1, 0xc9, 0xcd, 0xd3,
                   0xda, 0xdd, 0xe0, 0xe8, 0xec, 0xf2,
                   0xf9, 0xc0, 0xc8, 0xcc, 0xd2, 0xd9,
                   0xe2, 0xea, 0xee, 0xf4, 0xfb, 0xc2,
                   0xca, 0xce, 0xd4, 0xdb, 0xe5, 0xc5,
                   0xf8, 0xd8, 0xe3, 0xf1, 0xf5, 0xc3,
                   0xd1, 0xd5, 0xe6, 0xc6, 0xe7, 0xc7,
                   0xfe, 0xf0, 0xde, 0xd0, 0xa3, 0x153,
                   0x152, 0xa1, 0xbf)
    # And here is the offset at which the Unicode Translation Table
    # starts.
    UTT_OFFSET = 155

    # This subclass just lists all the "special" character codes that
    # are capturable from an input stream. They're just there so that
    # the user of the virtual machine can give them a nice name.
    class Input(object):
        DELETE = 8
        ESCAPE = 27
        # The cursor pad
        CUR_UP = 129
        CUR_DOWN = 130
        CUR_LEFT = 131
        CUR_RIGHT = 132
        # The Function keys
        F1 = 133
        F2 = 134
        F3 = 135
        F4 = 136
        F5 = 137
        F6 = 138
        F7 = 139
        F8 = 140
        F9 = 141
        F10 = 142
        F11 = 143
        F12 = 144
        # The numpad (keypad) keys.
        KP_0 = 145
        KP_1 = 146
        KP_2 = 147
        KP_3 = 148
        KP_4 = 149
        KP_5 = 150
        KP_6 = 151
        KP_7 = 152
        KP_8 = 153
        KP_9 = 154

    def __init__(self, version, utt=None):
        self._output_table = {
            0 : "",
            13: "\n"
            }
        self._input_table = {
            "\n": 13
            }

        # Prepare the default Unicode Translation Table, if it is
        # needed
        if not utt:
            utt = [unichr(x) for x in self.__class__.DEFAULT_UTT]

        # Populate the input and output tables with the ascii and UTT
        # characters.
        for code,char in [(x,unichr(x)) for x in range(32,127)] + \
                [(self.__class__.UTT_OFFSET + x,utt[x]) for x
                 in range(len(utt))]:
            self._output_table[code] = char
            self._input_table[char] = code

        # Populate the input table with the extra "special" input
        # codes.  The cool trick we use here, is that all these values
        # are in fact numbers, so their key will be available in both
        # dicts, and ztoa will provide the correct code if you pass it
        # a special symbol instead of a character to translate!
        #
        # Oh and we also pull the items from the subclass into this
        # instance, so as to make reference to these special codes
        # easier.
        for name,code in [(c,v) for c,v in self.Input.__dict__.items()
                     if not c.startswith('__')]:
            self._input_table[code] = code
            setattr(self, name, code)

        # The only special support required for ZSCII: ZM v5 defines
        # an extra character code to represent a mouse click. If we're
        # booting a v5 ZM, define this.
        if version == 5:
            setattr(self, "MOUSE_CLICK", 254)
            self._input_table[254] = 254

    def ztou(self, index):
        """Translate the given ZSCII code into the corresponding
        output ASCII character and return it, or raise an exception if
        the requested index has no translation."""
        try:
            return self._output_table[index]
        except KeyError:
            raise IndexError, "No such ZSCII character"

    def utoz(self, char):
        """Translate the given ASCII code into the corresponding input
        ZSCII character and return it, or raise an exception if the
        requested character has no translation."""
        try:
            return self._input_table[char]
        except KeyError:
            raise IndexError, "No such input character"
