#
# A ZString-to-ASCII Universal Translator.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZStringEndOfString(Exception):
    """No more data left in string."""

class ZStringStream(object):
    """This class takes an address and a ZMemory, and treats that as
    the begginning of a ZString. Subsequent calls to get() will return
    one ZChar code at a time, raising ZStringEndOfString when there is
    no more data."""

    def __init__(self, zmem, addr):
        self._mem = zmem
        self._addr = addr
        self._has_ended = False
        self._get_block()

    def _get_block(self):
        from bitfield import BitField
        chunk = self._mem[self._addr:self._addr+2]
        self._data = BitField(''.join([chr(x) for x in chunk]))
        self._addr += 2
        self._char_in_block = 0

    def get(self, num=1):
        if self._has_ended:
            raise ZStringEndOfString

        # We must read in sequence bits 14-10, 9-5, 4-0.
        offset = (2 - self._char_in_block) * 5
        zchar = self._data[offset:offset+5]

        if self._char_in_block == 2:
            # If end-of-string marker is set...
            if self._data[15] == 1:
                self._has_ended = True
            else:
                self._get_block()
        else:
            self._char_in_block += 1

        return zchar

class ZStringFactory(object):
    """A class that handles the matter of converting a ZString into an
    ASCII string, with all the arcane things such as alphabets
    handled.

    Instances of this class are meant to be long-lived: typical use
    would be attaching an instance of it to the virtual machine, and
    have it do all zstring translations for that machine through its
    xlate_ascii method."""

    # The default alphabet tables for ZChar translation.
    # As the codes 0-5 are special, alphabets start with code 0x6.
    DEFAULT_A0 = "abcdefghijklmnopqrstuvwxyz"
    DEFAULT_A1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # A2 also has 0x6 as special char, so they start at 0x7.
    DEFAULT_A2 = "0123456789.,!?_#'\"/\\<-:()"
    DEFAULT_A2_V5 = "\n0123456789.,!?_#'\"/\\-:()"

    def __init__(self, mem):

        self._mem = mem

        # Build ourselves a zscii translator
        from zscii import Zscii
        self.zscii = Zscii(mem.version)

        self._load_alphabets()

    def _load_alphabets(self):
        """Load a set of alphabet tables, either from a custom memory
        section, or the default tables for the current ZM version."""
        alpha_tables = None

        # If v5, try to load a custom alphabet.
        if self._mem.version == 5:
            if not self._load_custom_alphabet():
                # No custom alphabet, prime for loading default.
                alpha_tables = (self.__class__.DEFAULT_A0,
                                self.__class__.DEFAULT_A1,
                                self.__class__.DEFAULT_A2_V5)
        # Not v5, prime for loading the default alphabet
        else:
            alpha_tables = (self.__class__.DEFAULT_A0,
                            self.__class__.DEFAULT_A1,
                            self.__class__.DEFAULT_A2)

        # If we haven't loaded a default alphabet a this point, crunch
        # the numbers to get our default tables.
        if alpha_tables:
            self.alphabet = []
            for alph in alpha_tables:
                self.alphabet.append([self.zscii.utoz(c) for c in alph])

        print self.alphabet


    def _load_custom_alphabet(self):
        """Check for the existence of a custom alphabet, and load it
        if it does exist. Return True if a custom alphabet was found,
        False otherwise."""
        # The custom alphabet table address is at 0x34 in the memory.
        if self._mem[0x34] == 0:
            return False
        alph_addr = self._mem.byte_addr(self._mem[0x34])

        alphabet = self._mem[alph_addr:alph_addr+78]
        self.alphabet = [alphabet[0:26], alphabet[26:52], alphabet[52:78]]
        return True

    def to_ascii(self, addr):
        return ZString(self._mem, self,
                       ZStringStream(self._mem, addr))

    def get_abbrev(self, subtable, index):
        # The abbreviation table address is at header address 0x18
        abbrev_table_base = self._mem.read_word(0x18)
        # We multiply the result by 2 because each entry is 2 bytes
        # long. The rest is the calculation done as specified in the
        # ZM spec.
        abbrev_table_offset = ((32*subtable)+index)*2
        abbrev_addr = self._mem.word_address(abbrev_table_base +
                                             abbrev_table_offset)
        return ZAbbrev(self._mem, self,
                       ZStringStream(self._mem, abbrev_addr))

class ZString(object):
    def __init__(self, mem, factory, stream):
        self._mem = mem
        self._factory = factory
        self._stream = stream

        # Start on alphabet 0
        self._cur_alph = 0
        self._prev_alph = 0

        self._ascii = []

        try:
            while True:
                c = stream.get()
                ## Special values
                if c in range(1,6):
                    if self._mem.version == 1:
                        a = {
                            1: lambda _: self._ascii.append("\n"),
                            2: lambda _: self._alph_shr(False),
                            3: lambda _: self._alph_shl(False),
                            4: lambda _: self._alph_shr(True),
                            5: lambda _: self._alph_shl(True),
                            }[c](c)
                    elif self._mem.version == 2:
                        a = {
                            1: lambda _: self._get_abbr(0, stream.get()),
                            2: lambda _: self._alph_shr(False),
                            3: lambda _: self._alph_shl(False),
                            4: lambda _: self._alph_shr(True),
                            5: lambda _: self._alph_shl(True),
                            }[c](c)
                    else: # Versions 3-5
                        a = {
                            1: lambda _: self._get_abbr(0, stream.get()),
                            2: lambda _: self._get_abbr(1, stream.get()),
                            3: lambda _: self._get_abbr(2, stream.get()),
                            4: lambda _: self._alph_shr(False),
                            5: lambda _: self._alph_shl(False),
                            }[c](c)

                # Handle the special case of A2/6
                elif self._cur_alph == 2 and c == 6:
                    zscii = (stream.get() << 8) + stream.get()
                    self._ascii.append(factory.zscii.ztou(zscii))

                # All other cases are handled through the alphabet
                # translator.
                else:
                    zscii = factory.alphabet[self._cur_alph][c-6]
                    self._ascii.append(factory.zscii.ztou(zscii))

        except ZStringEndOfString:
            self._end = stream._addr

    def val(self):
        return ''.join(self._ascii)

    def _alph_shr(self, lock):
        """Shift the current alphabet one to the right. If lock is
        True, it will remain permanently active. Else, it will only be
        active for a single character."""
        self._cur_alph = (self._cur_alph + 1) % 3
        if lock:
            self._prev_alph = self._cur_alph

    def _alph_shl(self, lock):
        """Shift the current alphabet one to the right. If lock is
        True, it will remain permanently active. Else, it will only be
        active for a single character."""
        self._cur_alph = (self._cur_alph - 1) % 3
        if lock:
            self._prev_alph = self._cur_alph

    def _get_abbr(self, subtable, index):
        self._ascii += self._factory.get_abbrev(subtable, index).val()

class ZStringAbbrevWithinAbbrev(Exception):
    """An abbreviation tried to refer to another abbreviation."""

class ZAbbrev(ZString):
    def _get_abbr(self, subtable, index):
        raise ZStringAbbrevWithinAbbrev
