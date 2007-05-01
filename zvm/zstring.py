#
# A ZString-to-Unicode Universal Translator.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

import itertools


class ZStringEndOfString(Exception):
    """No more data left in string."""

class ZStringIllegalAbbrevInString(Exception):
    """String abbreviation encountered within a string in a context
    where it is not allowed."""


class ZStringTranslator(object):
    def __init__(self, zmem):
        self._mem = zmem

    def get(self, addr):
        from bitfield import BitField
        pos = (addr, BitField(self._mem.read_word(addr)), 0)

        s = []
        try:
            while True:
                s.append(self._read_char(pos))
                pos = self._next_pos(pos)
        except ZStringEndOfString:
            return s

    def _read_char(self, pos):
        offset = (2 - pos[2]) * 5
        return pos[1][offset:offset+5]

    def _is_final(self, pos):
        return pos[1][15] == 1

    def _next_pos(self, pos):
        from bitfield import BitField

        offset = pos[2] + 1
        # Overflowing from current block?
        if offset == 3:
            # Was last block?
            if self._is_final(pos):
                # Kill processing.
                raise ZStringEndOfString
            # Get and return the next block.
            return (pos[0] + 2,
                    BitField(self._mem.read_word(pos[0] + 2)),
                    0)

        # Just increment the intra-block counter.
        return (pos[0], pos[1], offset)


class ZCharTranslator(object):

    # The default alphabet tables for ZChar translation.
    # As the codes 0-5 are special, alphabets start with code 0x6.
    DEFAULT_A0 = [ord(x) for x in "abcdefghijklmnopqrstuvwxyz"]
    DEFAULT_A1 = [ord(x) for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    # A2 also has 0x6 as special char, so they start at 0x7.
    DEFAULT_A2 = [ord(x) for x in "0123456789.,!?_#'\"/\\<-:()"]
    DEFAULT_A2_V5 = [ord(x) for x in "\n0123456789.,!?_#'\"/\\-:()"]

    ALPHA = (DEFAULT_A0, DEFAULT_A1, DEFAULT_A2)
    ALPHA_V5 = (DEFAULT_A0, DEFAULT_A1, DEFAULT_A2_V5)

    def __init__(self, zmem):
        self._mem = zmem

        # Initialize the alphabets
        if self._mem.version == 5:
            self._alphabet = self._load_custom_alphabet() or self.ALPHA_V5
        else:
            self._alphabet = self.ALPHA

        # Initialize the special state handlers
        self._load_specials()

        # Initialize the abbreviations (if supported)
        self._load_abbrev_tables()

    def _load_custom_alphabet(self):
        """Check for the existence of a custom alphabet, and load it
        if it does exist. Return the custom alphabet if it was found,
        None otherwise."""
        # The custom alphabet table address is at 0x34 in the memory.
        if self._mem[0x34] == 0:
            return None

        alph_addr = self._mem.read_word(0x34)
        alphabet = self._mem[alph_addr:alph_addr+78]
        return [alphabet[0:26], alphabet[26:52], alphabet[52:78]]

    def _load_abbrev_tables(self):
        self._abbrevs = {}

        # If the ZM doesn't do abbrevs, just return an empty dict.
        if self._mem.version == 1:
            return

        # Build ourselves a ZStringTranslator for the abbrevs.
        xlator = ZStringTranslator(self._mem)

        def _load_subtable(num, base):
            for i,zoff in [(i,base+(num*64)+(i*2))
                            for i in range(0, 32)]:
                zaddr = self._mem.read_word(zoff)
                zstr = xlator.get(self._mem.word_address(zaddr))
                zchr = self.get(zstr, allow_abbreviations=False)
                self._abbrevs[(num, i)] = zchr

        abbrev_base = self._mem.read_word(0x18)
        _load_subtable(0, abbrev_base)

        # Does this ZM support the extended abbrev tables?
        if self._mem.version >= 3:
            _load_subtable(1, abbrev_base)
            _load_subtable(2, abbrev_base)

    def _load_specials(self):
        """Load the special character code handlers for the current
        machine version.
        """
        # The following three functions define the three possible
        # special character code handlers.
        def newline(state):
            """Append ZSCII 13 (newline) to the output."""
            state['zscii'].append(13)

        def shift_alphabet(state, direction, lock):
            """Shift the current alphaber up or down. If lock is
            False, the alphabet will revert to the previous alphabet
            after outputting 1 character. Else, the alphabet will
            remain unchanged until the next shift.
            """
            state['curr_alpha'] = (state['curr_alpha'] + direction) % 3
            if lock:
                state['prev_alpha'] = state['curr_alpha']

        def abbreviation(state, abbrev):
            """Insert the given abbreviation from the given table into
            the output stream.

            This character was an abbreviation table number. The next
            character will be the offset within that table of the
            abbreviation. Set up a state handler to intercept the next
            character and output the right abbreviation."""
            def write_abbreviation(state, c, subtable):
                state['zscii'] += self._abbrevs[(subtable, c)]
                del state['state_handler']

            # If we're parsing an abbreviation, there should be no
            # nested abbreviations. So this is just a sanity check for
            # people feeding us bad stories.
            if not state['allow_abbreviations']:
                raise ZStringIllegalAbbrevInString

            state['state_handler'] = lambda s,c: write_abbreviation(s, c,
                                                                    abbrev)

        # Register the specials handlers depending on machine version.
        if self._mem.version == 1:
            self._specials = {
                1: lambda s: newline(s),
                2: lambda s: shift_alphabet(s, +1, False),
                3: lambda s: shift_alphabet(s, -1, False),
                4: lambda s: shift_alphabet(s, +1, True),
                5: lambda s: shift_alphabet(s, -1, True),
                }
        elif self._mem.version == 2:
            self._specials = {
                1: lambda s: abbreviation(s, 0),
                2: lambda s: shift_alphabet(s, +1, False),
                3: lambda s: shift_alphabet(s, -1, False),
                4: lambda s: shift_alphabet(s, +1, True),
                5: lambda s: shift_alphabet(s, -1, True),
                }
        else: # ZM v3-5
            self._specials = {
                1: lambda s: abbreviation(s, 0),
                2: lambda s: abbreviation(s, 1),
                3: lambda s: abbreviation(s, 2),
                4: lambda s: shift_alphabet(s, +1, False),
                5: lambda s: shift_alphabet(s, -1, False),
                }

    def _special_zscii(self, state, char):
        if 'zscii_char' not in state.keys():
            state['zscii_char'] = char
        else:
            zchar = (state['zscii_char'] << 5) + char
            state['zscii'].append(zchar)
            del state['zscii_char']
            del state['state_handler']

    def get(self, zstr, allow_abbreviations=True):
        state = {
            'curr_alpha': 0,
            'prev_alpha': 0,
            'zscii': [],
            'allow_abbreviations': allow_abbreviations,
            }

        for c in zstr:
            if 'state_handler' in state.keys():
                # If a special handler has registered itself, then hand
                # processing over to it.
                state['state_handler'](state, c)
            elif c in self._specials.keys():
                # Hand off per-ZM version special char handling.
                self._specials[c](state)
            elif state['curr_alpha'] == 2 and c == 6:
                # Handle the strange A2/6 character
                state['state_handler'] = self._special_zscii
            else:
                # Do the usual Thing: append a zscii code to the
                # decoded sequence and revert to the "previous"
                # alphabet (or not, if it hasn't recently changed or
                # was locked)
                if c == 0:
                    # Append a space.
                    z = 32
                elif state['curr_alpha'] == 2:
                    # The symbol alphabet table only has 25 chars
                    # because of the A2/6 special char, so we need to
                    # adjust differently.
                    z = self._alphabet[state['curr_alpha']][c-7]
                else:
                    z = self._alphabet[state['curr_alpha']][c-6]
                state['zscii'].append(z)
                state['curr_alpha'] = state['prev_alpha']

        return state['zscii']


class ZsciiTranslator(object):
    # The default Unicode Translation Table that maps to ZSCII codes
    # 155-251. The codes are unicode codepoints for a host of strange
    # characters.
    DEFAULT_UTT = [unichr(x) for x in
                   (0xe4, 0xf6, 0xfc, 0xc4, 0xd6, 0xdc,
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
                   0x152, 0xa1, 0xbf)]
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

    def __init__(self, zmem):
        self._mem = zmem
        self._output_table = {
            0 : "",
            10: "\n"
            }
        self._input_table = {
            "\n": 10
            }

        self._load_unicode_table()

        # Populate the input and output tables with the ASCII and UTT
        # characters.
        for code,char in [(x,unichr(x)) for x in range(32,127)]:
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
        if self._mem.version == 5:
            setattr(self, "MOUSE_CLICK", 254)
            self._input_table[254] = 254

    def _load_unicode_table(self):
        if self._mem.version == 5:
            # Read the header extension table address
            ext_table_addr = self._mem.read_word(0x36)

            # If:
            #  - The extension header's address is non-null
            #  - There are at least 3 words in the extension header
            #    (the unicode translation table is the third word)
            #  - The 3rd word (unicode translation table address) is
            #    non-null
            #
            # Then there is a unicode translation table other than the
            # default that needs loading.
            if (ext_table_addr != 0 and
                self._mem.read_word(ext_table_addr) >= 3 and
                self._mem.read_word(ext_table_addr+6) != 0):

                # The first byte is the number of unicode characters
                # in the table.
                utt_len = self._mem[ext_table_addr]

                # Build the range of addresses to load from, and build
                # the unicode translation table as a list of unicode
                # chars.
                utt_range = xrange(ext_table+1, ext_table+1+(utt_len*2), 2)
                utt = [unichr(self._mem.read_word(i)) for i in utt_range]
            else:
                utt = self.DEFAULT_UTT

            # One way or another, we have a unicode translation
            # table. Add all the characters in it to the input and
            # output translation tables.
            for zscii, unichar in itertools.izip(itertools.count(155), utt):
                self._output_table[zscii] = unichar
                self._input_table[unichar] = zscii

    def ztou(self, index):
        """Translate the given ZSCII code into the corresponding
        output Unicode character and return it, or raise an exception if
        the requested index has no translation."""
        try:
            return self._output_table[index]
        except KeyError:
            raise IndexError, "No such ZSCII character"

    def utoz(self, char):
        """Translate the given Unicode code into the corresponding
        input ZSCII character and return it, or raise an exception if
        the requested character has no translation."""
        try:
            return self._input_table[char]
        except KeyError:
            raise IndexError, "No such input character"

    def get(self, zscii):
        return ''.join([self.ztou(c) for c in zscii])


class ZStringFactory(object):
    def __init__(self, zmem):
        self._mem = zmem
        self.zstr = ZStringTranslator(zmem)
        self.zchr = ZCharTranslator(zmem)
        self.zscii = ZsciiTranslator(zmem)

    def get(self, addr):
        zstr = self.zstr.get(addr)
        zchr = self.zchr.get(zstr)
        return self.zscii.get(zchr)
