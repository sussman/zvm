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

    def __init__(self, zmem):
        ""
        self._memory = zmem
        self._opcode_handlers = {}

        # Introspect ourselves, discover all functions that look like
        # opcode handlers, and add them to our mapper
        for func in self.__class__.__dict__:
            print "Considering %s" % func
            instance_func = getattr(self, func)
            if instance_func != None:
                doc_head = instance_func.__doc__.split('\n')[0]
                print "Potential candidate, docstring is %s" % doc_head

                if doc_head.startswith("ZOPCODE "):
                    opcode_num = int(doc_head[8:], 16)
                    self._opcode_handlers[opcode_num] = instance_func

        print self._opcode_handlers

    def test_opcode(self, zop):
        """ZOPCODE 0x20

        This is a test opcode."""
