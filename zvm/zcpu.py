#
# A class which represents the CPU itself, the brain of the virtual
# machine. It ties all the systems together and runs the story.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZCpuError(Exception):
    "General exception for Zcpu class"
    pass


class ZCpu(object):

    _opcodes = {}

    def __init__(self, zmem):
        self._memory = zmem

        print self._opcodes

    def _get_handler(self, opcode):
        return getattr(self, _opcodes[opcode])

    def test_opcode(self, zop):
        """This is a test opcode."""
    test_opcode._opcode = 0x20

    # This is the "automagic" opcode handler registration system.
    # After each function that is an opcode handler, we assign the
    # function object an _opcode attribute, giving the numeric opcode
    # the function implements.
    #
    # Then, the following code iterates back over all items in the
    # class, and registers all objects with that attribute in the
    # _opcodes dictionary.
    #
    # Then, at runtime, the _get_handler method can be invoked to
    # retrieve the function implementing a given opcode.  Pretty cool
    # voodoo if you ask me.
    for k,v in vars().items():
        if hasattr(v, "_opcode"):
            _opcodes[v._opcode] = k
