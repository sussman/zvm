#
# A class which represents the CPU itself, the brain of the virtual
# machine. It ties all the systems together and runs the story.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZCpuError(Exception):
    "General exception for Zcpu class"

class ZCpuIllegalInstruction(ZCpuError):
    "Illegal instruction encountered"

class ZCpu(object):

    _opcodes = {}

    def __init__(self, zmem, zopdecoder):
        self._memory = zmem
        self._opdecoder = zopdecoder

        print self._opcodes

    def _get_handler(self, opcode):
        try:
            return getattr(self, self._opcodes[opcode])
        except KeyError:
            raise ZCpuIllegalInstruction

    def run(self):
        while True:
            (type, opcode, operands) = self._opdecoder.get_next_instruction()
            self._get_handler(opcode)(*operands)


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
