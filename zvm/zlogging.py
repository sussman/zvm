#
# Logging assistance. This provides a logging facility for the rest of
# the Z-Machine. As a Z-Machine is inherently I/O intensive, dumb screen
# dumping is no longer adequate. This logging facility, based on
# python's logging module, provides file logging.
#

import logging

# Top-level initialization
logging.getLogger().setLevel(logging.DEBUG)

# Create the logging objects regardless.  If debugmode is False, then
# they won't actually do anything when used.
mainlog = logging.FileHandler('debug.log', 'a')
mainlog.setLevel(logging.DEBUG)
mainlog.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
logging.getLogger('mainlog').addHandler(mainlog)

# We'll store the disassembly in a separate file, for better
# readability.
disasm = logging.FileHandler('disasm.log', 'a')
disasm.setLevel(logging.DEBUG)
disasm.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('disasm').addHandler(disasm)

mainlog = logging.getLogger('mainlog')
mainlog.info('*** Log reopened ***')
disasm = logging.getLogger('disasm')
disasm.info('*** Log reopened ***')

# Pubilc routines used by other modules
def set_debug(state):
  if state:
    logging.getLogger().setLevel(logging.DEBUG)
  else:
    logging.getLogger().setLevel(logging.CRITICAL)

def log(msg):
  mainlog.debug(msg)

def log_disasm(pc, opcode_type, opcode_num, opcode_name, args):
  disasm.debug("%06x  %s:%02x %s %s" % (pc, opcode_type, opcode_num,
                                        opcode_name, args))
