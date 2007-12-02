#
# A class which manages both (1) the general purpose stack ("data
# stack") used by the story code to store temporary data, and (2) the
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

# Helper class used by ZStackManager; a 'routine' object which
# includes its own privae stack of data.
class ZRoutine(object):

  def __init__(self, start_addr, return_addr, zmem, args,
               local_vars=None, stack=None):
    """Initialize a routine object beginning at START_ADDR in ZMEM,
    with initial argument values in list ARGS.  If LOCAL_VARS is None,
    then parse them from START_ADDR."""

    self.start_addr = start_addr
    self.return_addr = return_addr
    self.program_counter = 0    # used when execution interrupted

    if stack is None:
      self.stack = []
    else:
      self.stack = stack[:]

    if local_vars is not None:
      self.local_vars = local_vars[:]
    else:
      num_local_vars = zmem[self.start_addr]
      if not (0 <= num_local_vars <= 15):
        log("num local vars is %d" % num_local_vars)
        raise ZStackError
      self.start_addr += 1

      # Initialize the local vars in the ZRoutine's dictionary. This is
      # only needed on machines v1 through v4. In v5 machines, all local
      # variables are preinitialized to zero.
      self.local_vars = [0 for _ in range(15)]
      if 1 <= zmem.version <= 4:
        for i in range(num_local_vars):
          self.local_vars[i] = zmem.read_word(self.start_addr)
          self.start_addr += 2
      elif zmem.version != 5:
        raise ZStackUnsupportedVersion

    # Place call arguments into local vars, if available
    for i in range(0, len(args)):
      self.local_vars[i] = args[i]


  def pretty_print(self):
    "Display a ZRoutine nicely, for debugging purposes."

    log("ZRoutine:        start address: %d" % self.start_addr)
    log("ZRoutine: return value address: %d" % self.return_addr)
    log("ZRoutine:      program counter: %d" % self.program_counter)
    log("ZRoutine:      local variables: %d" % self.local_vars)


class ZStackBottom(object):

  def __init__(self):
    self.program_counter = 0  # used as a cache only


class ZStackManager(object):

  def __init__(self, zmem):

    self._memory = zmem
    self._stackbottom = ZStackBottom()
    self._call_stack = [self._stackbottom]


  def get_local_variable(self, varnum):
    """Return value of local variable VARNUM from currently-running
    routine.  VARNUM must be a value between 0 and 15, and must
    exist."""

    if self._call_stack[-1] == self._stackbottom:
      raise ZStackNoRoutine

    if not 0 <= varnum <= 15:
      raise ZStackNoSuchVariable

    current_routine = self._call_stack[-1]

    return current_routine.local_vars[varnum]


  def set_local_variable(self, varnum, value):
    """Set value of local variable VARNUM to VALUE in
    currently-running routine.  VARNUM must be a value between 0 and
    15, and must exist."""

    if self._call_stack[1] == self._stackbottom:
      raise ZStackNoRoutine

    if not 0 <= varnum <= 15:
      raise ZStackNoSuchVariable

    current_routine = self._call_stack[-1]

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


  # Used by quetzal save-file parser to reconstruct stack-frames.
  def push_routine(self, routine):
    """Blindly push a ZRoutine object to the call stack.
    WARNING: do not use this unless you know what you're doing; you
    probably want the more full-featured start_routine() belowe
    instead."""

    self._call_stack.append(routine)


  # ZPU should call this whenever it decides to call a new routine.
  def start_routine(self, routine_addr, return_addr,
                    program_counter, args):
    """Save the state of the currenly running routine (by examining
    the current value of the PROGRAM_COUNTER), and prepare for
    execution of a new routine at ROUTINE_ADDR with list of initial
    arguments ARGS."""

    new_routine = ZRoutine(routine_addr, return_addr,
                           self._memory, args)
    current_routine = self._call_stack[-1]
    current_routine.program_counter = program_counter
    self._call_stack.append(new_routine)

    return new_routine.start_addr


  # ZPU should call this whenever it decides to return from current
  # routine.
  def finish_routine(self, return_value):
    """Toss the currently running routine from the call stack, and
    toss any leftover values pushed to the data stack by said routine.
    Return the previous routine's program counter address, so that
    execution can resume where from it left off."""

    exiting_routine = self._call_stack.pop()
    current_routine = self._call_stack[-1]

    # Depending on many things, return stuff.
    if exiting_routine.return_addr != None:
      if exiting_routine.return_addr == 0: # Push to stack
        self.push_stack(return_value)
      elif 0 < exiting_routine.return_addr < 10: # Store in local var
        self.set_local_variable(exiting_routine.return_addr,
                                return_value)
      else: # Store in global var
        self._memory.write_global(exiting_routine.return_addr,
                                  return_value)

    return current_routine.program_counter

