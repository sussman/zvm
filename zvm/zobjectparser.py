#
# A class which knows how to parse objects in the object tree.
# Implements section 12 of Z-code specification.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from bitfield import BitField
from zmemory import ZMemory

class ZObjectError(Exception):
  "General exception for ZObject class"
  pass

class ZObjectIllegalObjectNumber(ZObjectError):
  "Illegal object number given."
  pass

class ZObjectIllegalVersion(ZObjectError):
  "Unsupported z-machine version."
  pass



# Again, the interpreter should only need exactly one instance of this class.

class ZObjectParser(object):

  def __init__(self, zmem):

    self._memory = zmem
    self._propdefaults_addr = ?  # at word $0A
    self._objecttree_addr = ?  # size of header depends on z version


  def _get_object_addr(self, objectnum):
    """Return address of object number OBJECTNUM."""

    if 1 <= self._memory.version <= 3:
      if not (1 <= objectnum <= 255):
        raise ZObjectIllegalObjectNumber
      return self._objecttree_addr + (9 * (objectnum - 1))

    elif 4 <= self._memory.version <= 5:
      if not (1 <= objectnum <= 65535):
        raise ZObjectIllegalObjectNumber
      return self._objecttree_addr + (14 * (objectnum - 1))

    else:
      raise ZObjectIllegalVersion


  def get_attribute(self, objectnum, attrnum):
    """Return value of attribute number ATTRNUM of object number OBJECTNUM."""

    pass


  def get_property(self, objectnum, propnum):
    """Return value of property number PROPNUM of object number OBJECTNUM."""

    # don't forget to use the 'propdefaults' table if the property
    # doesn't exist.


  def get_parent(self, objectnum):
    """Return object number of parent of object number OBJECTNUM."""

    pass


  def get_child(self, objectnum):
    """Return object number of child of object number OBJECTNUM."""

    pass


  def get_sibling(self, objectnum):
    """Return object number of sibling of object number OBJECTNUM."""

    pass


  def get_shortname(self, objectnum):
    """Return 'short name' of object number OBJECTNUM as ascii string."""

    pass
