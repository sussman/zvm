#
# A class which knows how to write and parse 'Quetzal' files, which is
# the standard save-file format for modern Z-machine implementations.
# This allows ZVM's saved games to load in other interpreters, and
# vice versa.
#
# The Quetzal format is documented at:
#    http://www.ifarchive.org/if-archive/infocom/\
#           interpreters/specification/savefile_14.txt
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

# Woohoo!  Python has a module to parse IFF files, which is a generic
# interchange format.  A Quetzal file is in fact a type of IFF file.
import chunk
import os

import bitfield
import zstackmanager
from zlogging import log

# The general format of Queztal is that of a "FORM" IFF file, which is
# a container class for 'chunks'.
#
#   "FORM", 4 bytes of container total-length, "IFZS",
#        4-byte chunkname, 4-byte length, length bytes of data
#        4-byte chunkname, 4-byte length, length bytes of data
#        4-byte chunkname, 4-byte length, length bytes of data
#        ...

class QuetzalError(Exception):
  "General exception for Quetzal classes."
  pass

class QuetzalMalformedChunk(QuetzalError):
  "Malformed chunk detected."

class QuetzalNoSuchSavefile(QuetzalError):
  "Cannot locate save-game file."

class QuetzalUnrecognizedFileFormat(QuetzalError):
  "Not a valid Quetzal file."

class QuetzalIllegalChunkOrder(QuetzalError):
  "IFhd chunk came after Umem/Cmem/Stks chunks (see section 5.4)."

class QuetzalMismatchedFile(QuetzalError):
  "Quetzal file dosen't match current game."

class QuetzalMemoryOutOfBounds(QuetzalError):
  "Decompressed dynamic memory has gone out of bounds."

class QuetzalMemoryMismatch(QuetzalError):
  "Savefile's dynamic memory image is incorrectly sized."

class QuetzalStackFrameOverflow(QuetzalError):
  "Stack frame parsing went beyond bounds of 'Stks' chunk."


class QuetzalParser(object):
  """A class to read a Quetzal save-file and modify a z-machine."""

  def __init__(self, zmachine):
    log("Creating new instance of QuetzalParser")
    self._zmachine = zmachine
    self._seen_mem_or_stks = False
    self._last_loaded_metadata = {}  # metadata for tests & debugging


  def _parse_ifhd(self, data):
    """Parse a chunk of type IFhd, and check that the quetzal file
    really belongs to the current story (by comparing release number,
    serial number, and checksum.)"""

    # Spec says that this chunk *must* come before memory or stack chunks.
    if self._seen_mem_or_stks:
      raise QuetzalIllegalChunkOrder

    bytes = [ord(x) for x in data]
    if len(bytes) != 13:
      raise QuetzalMalformedChunk

    chunk_release = (ord(data[0]) << 8) + ord(data[1])
    chunk_serial = data[2:8]
    chunk_checksum = (ord(data[8]) << 8) + ord(data[9])
    chunk_pc = (ord(data[10]) << 16) + (ord(data[11]) << 8) + ord(data[12])
    self._zmachine._opdecoder.program_counter = chunk_pc

    log("  Found release number %d" % chunk_release)
    log("  Found serial number %d" % int(chunk_serial))
    log("  Found checksum %d" % chunk_checksum)
    log("  Initial program counter value is %d" % chunk_pc)
    self._last_loaded_metadata["release number"] = chunk_release
    self._last_loaded_metadata["serial number"] = chunk_serial
    self._last_loaded_metadata["checksum"] = chunk_checksum
    self._last_loaded_metadata["program counter"] = chunk_pc

    # Verify the save-file params against the current z-story header
    mem = self._zmachine._mem
    if mem.read_word(2) != chunk_release:
      raise QuetzalMismatchedFile
    serial_bytes = [ord(x) for x in chunk_serial]
    if serial_bytes != mem[0x12:0x18]:
      raise QuetzalMismatchedFile
    mem_checksum = mem.read_word(0x1C)
    if mem_checksum != 0 and (mem_checksum != chunk_checksum):
      raise QuetzalMismatchedFile
    log("  Quetzal file correctly verifies against original story.")


  def _parse_cmem(self, data):
    """Parse a chunk of type Cmem.  Decompress an image of dynamic
    memory, and place it into the ZMachine."""

    log("  Decompressing dynamic memory image")
    self._seen_mem_or_stks = True

    # Just duplicate the dynamic memory block of the pristine story image,
    # and then make tweaks to it as we decode the runlength-encoding.
    pmem = self._zmachine._pristine_mem
    cmem = self._zmachine._mem
    savegame_mem = list(pmem[pmem._dynamic_start:(pmem._dynamic_end + 1)])
    memlen = len(savegame_mem)
    memcounter = 0
    log("  Dynamic memory length is %d" % memlen)
    self._last_loaded_metadata["memory length"] = memlen

    runlength_bytes = [ord(x) for x in data]
    bytelen = len(runlength_bytes)
    bytecounter = 0

    log("  Decompressing dynamic memory image")
    while bytecounter < bytelen:
      byte = runlength_bytes[bytecounter]
      if byte != 0:
        savegame_mem[memcounter] = byte ^ pmem[memcounter]
        memcounter += 1
        bytecounter += 1
        log("   Set byte %d:%d" % (memcounter, savegame_mem[memcounter]))
      else:
        bytecounter += 1
        num_extra_zeros = runlength_bytes[bytecounter]
        memcounter += (1 + num_extra_zeros)
        bytecounter += 1
        log("   Skipped %d unchanged bytes" % (1 + num_extra_zeros))
      if memcounter >= memlen:
        raise QuetzalMemoryOutOfBounds

    # If memcounter finishes less then memlen, that's totally fine, it
    # just means there are no more diffs to apply.

    cmem[cmem._dynamic_start:(cmem._dynamic_end + 1)] = savegame_mem
    log("  Successfully installed new dynamic memory.")


  def _parse_umem(self, data):
    """Parse a chunk of type Umem.  Suck a raw image of dynamic memory
    and place it into the ZMachine."""

    ### TODO:  test this by either finding an interpreter that ouptuts
    ## this type of chunk, or by having own QuetzalWriter class
    ## (optionally) do it.
    log("  Loading uncompressed dynamic memory image")
    self._seen_mem_or_stks = True

    cmem = self._zmachine._mem
    dynamic_len = (cmem._dynamic_end - cmem.dynamic_start) + 1
    log("  Dynamic memory length is %d" % dynamic_len)
    self._last_loaded_metadata["dynamic memory length"] = dynamic_len

    savegame_mem = [ord(x) for x in data]
    if len(savegame_mem) != dynamic_len:
      raise QuetzalMemoryMismatch

    cmem[cmem._dynamic_start:(cmem._dynamic_end + 1)] = savegame_mem
    log("  Successfully installed new dynamic memory.")


  def _parse_stks(self, data):
    """Parse a chunk of type Stks."""

    log("  Begin parsing of stack frames")

    # Our strategy here is simply to create an entirely new
    # ZStackManager object and populate it with a series of ZRoutine
    # stack-frames parses from the quetzal file.  We then attach this
    # new ZStackManager to our z-machine, and allow the old one to be
    # garbage collected.
    stackmanager = zstackmanager.ZStackManager(self._zmachine._mem)

    self._seen_mem_or_stks = True
    bytes = [ord(x) for x in data]
    total_len = len(bytes)
    ptr = 0

    # Read successive stack frames:
    while (ptr < total_len):
      log("  Parsing stack frame...")
      return_pc = (bytes[ptr] << 16) + (bytes[ptr + 1] << 8) + bytes[ptr + 3]
      ptr += 3
      flags_bitfield = bitfield.BitField(bytes[ptr])
      ptr += 1
      varnum = bytes[ptr]  ### TODO: tells us which variable gets the result
      ptr += 1
      argflag = bytes[ptr]
      ptr += 1
      evalstack_size = (bytes[ptr] << 8) + bytes[ptr + 1]
      ptr += 2

      # read anywhere from 0 to 15 local vars
      local_vars = []
      for i in range(flags_bitfield[0:3]):
        var = (bytes[ptr] << 8) + bytes[ptr + 1]
        ptr += 2
        local_vars.append(var)
      log("    Found %d local vars" % len(local_vars))

      # least recent to most recent stack values:
      stack_values = []
      for i in range(evalstack_size):
        val = (bytes[ptr] << 8) + bytes[ptr + 1]
        ptr += 2
        stack_values.append(val)
      log("    Found %d local stack values" % len(stack_values))

      ### Interesting... the reconstructed stack frames have no 'start
      ### address'.  I guess it doesn't matter, since we only need to
      ### pop back to particular return addresses to resume each
      ### routine.

      ### TODO: I can exactly which of the 7 args is "supplied", but I
      ### don't understand where the args *are*??

      routine = zstackmanager.ZRoutine(0, return_pc, self._zmachine._mem,
                                       [], local_vars, stack_values)
      stackmanager.push_routine(routine)
      log("    Added new frame to stack.")

      if (ptr > total_len):
        raise QuetzalStackFrameOverflow

    self._zmachine._stackmanager = stackmanager
    log("  Successfully installed all stack frames.")


  def _parse_intd(self, data):
    """Parse a chunk of type IntD, which is interpreter-dependent info."""

    log("  Begin parsing of interpreter-dependent metadata")
    bytes = [ord(x) for x in data]

    os_id = bytes[0:3]
    flags = bytes[4]
    contents_id = bytes[5]
    reserved = bytes[6:8]
    interpreter_id = bytes[8:12]
    private_data = bytes[12:]
    ### TODO:  finish this


  # The following 3 chunks are totally optional metadata, and are
  # artifacts of the larger IFF standard.  We're not required to do
  # anything when we see them, though maybe it would be nice to print
  # them to the user?

  def _parse_auth(self, data):
    """Parse a chunk of type AUTH.  Display the author."""

    log("Author of file: %s" % data)
    self._last_loaded_metadata["author"] = data

  def _parse_copyright(self, data):
    """Parse a chunk of type (c) .  Display the copyright."""

    log("Copyright: (C) %s" % data)
    self._last_loaded_metadata["copyright"] = data

  def _parse_anno(self, data):
    """Parse a chunk of type ANNO.  Display any annotation"""

    log("Annotation: %s" % data)
    self._last_loaded_metadata["annotation"] = data


  #--------- Public APIs -----------


  def get_last_loaded(self):
    """Return a list of metadata about the last loaded Quetzal file, for
    debugging and test verification."""
    return self._last_loaded_metadata

  def load(self, savefile_path):
    """Parse each chunk of the Quetzal file at SAVEFILE_PATH,
    initializing associated zmachine subsystems as needed."""

    self._last_loaded_metadata = {}

    if not os.path.isfile(savefile_path):
      raise QuetzalNoSuchSavefile

    log("Attempting to load saved game from '%s'" % savefile_path)
    self._file = open(savefile_path)

    # The python 'chunk' module is pretty dumb; it doesn't understand
    # the FORM chunk and the way it contains nested chunks.
    # Therefore, we deliberately seek 12 bytes into the file so that
    # we can start sucking out chunks.  This also allows us to
    # validate that the FORM type is "IFZS".
    header = self._file.read(4)
    if header != "FORM":
      raise QuetzalUnrecognizedFileFormat
    bytestring = self._file.read(4)
    self._len = ord(bytestring[0]) << 24
    self._len += (ord(bytestring[1]) << 16)
    self._len += (ord(bytestring[2]) << 8)
    self._len += ord(bytestring[3])
    log("Total length of FORM data is %d" % self._len)
    self._last_loaded_metadata["total length"] = self._len

    type = self._file.read(4)
    if type != "IFZS":
      raise QuetzalUnrecognizedFileFormat

    try:
      while 1:
        c = chunk.Chunk(self._file)
        chunkname = c.getname()
        chunksize = c.getsize()
        data = c.read(chunksize)
        log("** Found chunk ID %s: length %d" % (chunkname, chunksize))
        self._last_loaded_metadata[chunkname] = chunksize

        if chunkname == "IFhd":
          self._parse_ifhd(data)
        elif chunkname == "CMem":
          self._parse_cmem(data)
        elif chunkname == "UMem":
          self._parse_umem(data)
        elif chunkname == "Stks":
          self._parse_stks(data)
        elif chunkname == "IntD":
          self._parse_intd(data)
        elif chunkname == "AUTH":
          self._parse_auth(data)
        elif chunkname == "(c) ":
          self._parse_copyright(data)
        elif chunkname == "ANNO":
          self._parse_anno(data)
        else:
          # spec says to ignore and skip past unrecognized chunks
          pass

    except EOFError:
      pass

    self._file.close()
    log("Finished parsing Quetzal file.")



#------------------------------------------------------------------------------


class QuetzalWriter(object):
  """A class to write the current state of a z-machine into a
  Quetzal-format file."""

  def __init__(self, zmachine):
    log("Creating new instance of QuetzalWriter")
    self._zmachine = zmachine

  def _generate_ifhd_chunk(self):
    """Return a chunk of type IFhd, containing metadata about the
    zmachine and story being played."""

    ### TODO: write this.  payload must be *exactly* 13 bytes, even if
    ### it means padding the program counter.

    ### Some old infocom games don't have checksums stored in header.
    ### If not, generate it from the *original* story file memory
    ### image and put it into this chunk.  See ZMemory.generate_checksum().
    pass

    return "0"


  def _generate_cmem_chunk(self):
    """Return a compressed chunk of data representing the compressed
    image of the zmachine's main memory."""

    ### TODO:  debug this when ready
    return "0"

    # XOR the original game image with the current one
    diffarray = list(self._zmachine._pristine_mem)
    for index in range(len(self._zmachine._pristine_mem._total_size)):
      diffarray[index] = self._zmachine._pristine_mem[index] \
                         ^ self._zmachine._mem[index]
    log("XOR array is %s" % diffarray)

    # Run-length encode the resulting list of 0's and 1's.
    result = []
    zerocounter = 0;
    for index in range(len(diffarray)):
      if diffarray[index] == 0:
        zerocounter += 1
        continue;
      else:
        if zerocounter > 0:
          result.append(0)
          result.append(zerocounter)
          zerocounter = 0
        result.append(diffarray[index])
    return result


  def _generate_stks_chunk(self):
    """Return a stacks chunk, describing the stack state of the
    zmachine at this moment."""

    ### TODO:  write this
    return "0"


  def _generate_anno_chunk(self):
    """Return an annotation chunk, containing metadata about the ZVM
    interpreter which created the savefile."""

    ### TODO:  write this
    return "0"


  #--------- Public APIs -----------


  def write(self, savefile_path):
    """Write the current zmachine state to a new Quetzal-file at
    SAVEFILE_PATH."""

    log("Attempting to write game-state to '%s'" % savefile_path)
    self._file = open(savefile_path, 'w')

    ifhd_chunk = self._generate_ifhd_chunk()
    cmem_chunk = self._generate_cmem_chunk()
    stks_chunk = self._generate_stks_chunk()
    anno_chunk = self._generate_anno_chunk()

    total_chunk_size = len(ifhd_chunk) + len(cmem_chunk) \
                       + len(stks_chunk) + len(anno_chunk)

    # Write main FORM chunk to hold other chunks
    self._file.write("FORM")
    ### TODO: self._file_write(total_chunk_size) -- spread it over 4 bytes
    self._file.write("IFZS")

    # Write nested chunks.
    for chunk in (ifhd_chunk, cmem_chunk, stks_chunk, anno_chunk):
      self._file.write(chunk)
      log("Wrote a chunk.")
    self._file.close()
    log("Done writing game-state to savefile.")
