#
# A class which represents the CPU itself, the brain of the virtual
# machine. It ties all the systems together and runs the story.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from zopdecoder import ZOpDecoder

class ZCpuError(Exception):
    "General exception for Zcpu class"

class ZCpuOpcodeOverlap(ZCpuError):
    "Overlapping opcodes registered"

class ZCpuIllegalInstruction(ZCpuError):
    "Illegal instruction encountered"

def declare_opcode(func, optype, opcode, version=(1,2,3,4,5)):
    """Helper function used for declaring functions implementing
    opcodes."""
    func._optype = optype
    func._opcode = opcode
    func._opversion = version

class ZCpu(object):

    _opcodes = {}

    def __init__(self, zmem, zopdecoder):
        self._memory = zmem
        self._opdecoder = zopdecoder

        print self._opcodes

    def _get_handler(self, optype, opcode):
        try:
            print "Opcode key:", (optype, opcode, self._memory.version)
            return getattr(self, self._opcodes[(optype, opcode,
                                                self._memory.version)])
        except KeyError:
            print "Unknown instruction (%s, 0x%X)" % (optype, opcode)
            raise ZCpuIllegalInstruction

    def run(self):
        while True:
            (optype, opcode, operands) = self._opdecoder.get_next_instruction()
            self._get_handler(optype, opcode)(*operands)

    def op_add(a, b):
        """16-bit signed addition"""
        print a,'+',b,'=',a+b
    declare_opcode(op_add, "2OP", 0x14)

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
        if hasattr(v, "_optype"):
            for ver in v._opversion:
                opkey = (v._optype, v._opcode, ver)

                if opkey in _opcodes.keys():
                    raise ZCpuOpcodeOverlap

                _opcodes[opkey] = k
