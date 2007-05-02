#
# A class which knows how to both write and parse 'Quetzal' files,
# which is the standard save-file format for all well-behaved
# Z-machine implementatinos.
#
# The format is documented at:
#    http://ifarchive.giga.or.at/if-archive/infocom/\
#           interpreters/specification/savefile_14.txt
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

# Woohoo!  Python has a module to parse IFF files, which is a generic
# interchange format.  A Quetzal file is in fact a type of IFF file.
import chunk

# The general format of Queztal is that of a "FORM" IFF file, which is
# a container class for 'chunks'.
#
#   "FORM", 4 bytes showing container length, 4-byte ID "IFZS",
#        4-byte chunkname, 4-byte length, length bytes of data
#        4-byte chunkname, 4-byte length, length bytes of data
#        4-byte chunkname, 4-byte length, length bytes of data
#        ...


class QuetzalError(Exception):
  "General exception for Quetzal classes."
  pass

class QuetzalUnrecognizedFileFormat(QuetzalError):
  "Not a valid Quetzal file."


class QuetzalParser(object):

  def __init__(self, filename, zmachine=None):
    """Parse Quetzal save-file FILENAME, handling each of the known
    Quetzal chunk types as they are discovered.  Each chunk type
    handler is responsible for initializing some portion of
    ZMACHINE."""

    self._file = open(filename)

    # The python 'chunk' module is pretty dumb;  it doesn't understand
    # the FORM chunk and the way it contains nested chunks.
    # Therefore, first we validate the FORM type is "IFZS", then we
    # deliberately seek 12 bytes into the file so the module can start
    # sucking out sequential chunks.

    header = self._file.read(4)
    if header != "FORM":
      raise QuetzalUnrecognizedFileFormat

    bytestring = self._file.read(4)
    self._total_length = 3 ### how to convert '\x00\x00\x02\x08' to decimal?

    type = self._file.read(4)
    if type != "IFZS":
      raise QuetzalUnrecognizedFileFormat

    try:
      while 1:
        c = chunk.Chunk(self._file)
        print "Found chunk with ID", c.getname()
        print "   whose length is", c.getsize()
        c.skip()
    except EOFError:
      pass

    print "All done parsing."
    
