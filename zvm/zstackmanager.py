#
# A class which manages both (1) the general purpose stack ("data
# stack") used by he story code to store temporary data, and (2) the
# interpreter-private stack of routines ("call stack") and their local
# variables.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

class ZStackError(Exception):
  "General exception for stack or routine-related errors"
  pass

class ZStackUnsupportedVersion(ZStackError):
  "Unsupported version of Z-story file."
  pass

class ZStackNoRoutine(ZStackError):
  "No routine is being executed."
  pass

class ZStackNoSuchVariable(ZStackError):
  "Trying to access non-existent local variable."
  pass

class ZStackPopError(ZStackError):
  "Nothing to pop from stack!"
  pass


# Helper class used by ZStackManager.  Nobody else should need to use it.
class ZRoutine(object):

  def __init__(self, start_addr, zmem, args):
    """Initialize a routine object beginning at START_ADDR in ZMEM,
    with initial argument values in list ARGS."""

    self.start_addr = start_addr
    self.program_counter = 0    # used when execution interrupted
    self.local_vars = {}
    self.stack = []

    # First byte of routine is number of local variables
    ptr = start_addr
    num_local_vars = zmem[ptr]
    if not (0 <= num_local_vars <= 15):
      print "num local vars is", num_local_vars
      raise ZStackError
    ptr += 1

    # Initialize the local vars in the ZRoutine's dictionary
    if 1 <= zmem.version <= 4:
      for i in range(num_local_vars):
        self.local_vars[i] = zmem.read_word(ptr)
        ptr += 2

    elif zmem.version == 5:
      for i in range(num_local_vars):
        self.local_vars[i] = 0

    else:
      raise ZStackUnsupportedVersion

    # Place call arguments into local vars, if available
    for i in range(0, len(args)):
      if self.local_vars.has_key(i):
        self.local_vars[i] = args[i]

  def pretty_print(self):
    "Display a ZRoutine nicely, for debugging purposes."

    print "ZRoutine:   start address:", self.start_addr
    print "ZRoutine: program counter:", self.program_counter
    print "ZRoutine: local variables:", self.local_vars



class ZStackManager(object):


  def __init__(self):

    self._memory = zmem
    self._call_stack = [self.STACK_DELIMITER]


  def get_local_variable(self, varnum):
    """Return value of local variable VARNUM from currently-running
    routine.  VARNUM must be a value between 0 and 15, and must
    exist."""

    if self._call_stack[-1] == self.STACK_DELIMITER
      raise ZStackNoRoutine

    current_routine = self._call_stack[-1]
    if not current_routine.local_vars.has_key(varnum):
      raise ZStackNoSuchVariable

    return current_routine.local_vars[varnum]


  def set_local_variable(self, varnum, value):
    """Set value of local variable VARNUM to VALUE in
    currently-running routine.  VARNUM must be a value between 0 and
    15, and must exist."""

    if self._call_stack[1] == self.STACK_DELIMITER:
      raise ZStackNoRoutine

    current_routine = self._call_stack[-1]
    if not current_routine.local_vars.has_key(varnum):
      raise ZStackNoSuchVariable

    current_routine.local_vars[varnum] = value


  def push_stack(self, value):
    "Push VALUE onto the top of the current routine's data stack."

    current_routine = self._call_stack[-1]
    current_routine.stack.append(value)


  def pop_stack(self):
    "Remove and return value from the top of the data stack."

    current_routine = self._call_stack[-1]
    return current_routine.stack.pop()


  def get_stack_frame_index(self):
    "Return current stack frame number.  For use by 'catch' opcode."

    return len(self._call_stack) - 1
  

  # ZPU should call this whenever it decides to call a new routine.
  def start_routine(self, routine_addr, program_counter, args):
    """Save the state of the currenly running routine (by examining
    the current value of the PROGRAM_COUNTER), and prepare for
    execution of a new routine at ROUTINE_ADDR with list of initial
    arguments ARGS."""

    new_routine = ZRoutine(routine_addr, self._memory, args)
    current_routine = self._call_stack[-1]
    current_routine.program_counter = program_counter
    self._call_stack.append(new_routine)


  # ZPU should call this whenever it decides to return from current routine.
  def finish_routine(self):
    """Toss the currently running routine from the call stack, and
    toss any leftover values pushed to the data stack by said routine.
    Return the previous routine's program counter address, so that
    execution can resume where from it left off."""

    self._call_stack.pop()
    current_routine = self._call_stack[-1]
    return current_routine.program_counter

