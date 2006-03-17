#
# A class which knows how to parse objects in the object tree.
# Implements section 12 of Z-code specification.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from bitfield import BitField
from zmemory import ZMemory
from zstring import ZStringFactory


class ZObjectError(Exception):
  "General exception for ZObject class"
  pass

class ZObjectIllegalObjectNumber(ZObjectError):
  "Illegal object number given."
  pass

class ZObjectIllegalAttributeNumber(ZObjectError):
  "Illegal attribute number given."
  pass

class ZObjectIllegalVersion(ZObjectError):
  "Unsupported z-machine version."
  pass



# The interpreter should only need exactly one instance of this class.

class ZObjectParser(object):

  def __init__(self, zmem):

    self._memory = zmem
    self._propdefaults_addr = zmem.read_word(0x0a)
    self._stringfactory = ZStringFactory(self._memory)

    if 1 <= self._memory.version <= 3:
      self._objecttree_addr = self._propdefaults_addr + 62
    elif 4 <= self._memory.version <= 5:
      self._objecttree_addr = self._propdefaults_addr + 126
    else:
      raise ZObjectIllegalVersion


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

  def _get_parent_sibling_child(self, objectnum):
    """Return [parent, sibling, child] object numbers of object OBJECTNUM."""

    addr = self._get_object_addr(objectnum)

    if 1 <= self._memory.version <= 3:
      addr += 4  # skip past attributes
      return self._memory[addr:addr+3]

    elif 4 <= self._memory.version <= 5:
      addr += 6  # skip past attributes
      return [self._memory.read_word(addr),
              self._memory.read_word(addr + 2),
              self._memory.read_word(addr + 4)]
    else:
      raise ZObjectIllegalVersion

  def _get_proptable_addr(self, objectnum):
    """Return address of property table of object OBJECTNUM."""

    addr = self._get_object_addr(objectnum)

    # skip past attributes and relatives
    if 1 <= self._memory.version <= 3:
      addr += 7
    elif 4 <= self._memory.version <= 5:
      addr += 12
    else:
      raise ZObjectIllegalVersion

    return self._memory.read_word(addr)


  #--------- Public API -----------

  def get_attribute(self, objectnum, attrnum):
    """Return value (0 or 1) of attribute number ATTRNUM of object
    number OBJECTNUM."""

    object_addr = self._get_object_addr(objectnum)

    if 1 <= self._memory.version <= 3:
      if not (0 <= attrnum <= 31):
        raise ZObjectIllegalAttributeNumber
      bf = Bitfield(self._memory[object_addr + (attrnum / 8)])

    elif 4 <= self._memory.version <= 5:
      if not (0 <= attrnum <= 47):
        raise ZObjectIllegalAttributeNumber
      bf = Bitfield(self._memory[object_addr + (attrnum / 8)])

    else:
      raise ZObjectIllegalVersion

    return bf[7 - (attrum % 8)]


  def get_parent(self, objectnum):
    """Return object number of parent of object number OBJECTNUM."""

    [parent, sibling, child] = self._get_parent_sibling_child(objectnum)
    return parent


  def get_child(self, objectnum):
    """Return object number of child of object number OBJECTNUM."""

    [parent, sibling, child] = self._get_parent_sibling_child(objectnum)
    return child


  def get_sibling(self, objectnum):
    """Return object number of sibling of object number OBJECTNUM."""

    [parent, sibling, child] = self._get_parent_sibling_child(objectnum)
    return sibling


  def get_shortname(self, objectnum):
    """Return 'short name' of object number OBJECTNUM as ascii string."""

    addr = self._get_proptable_addr(objectnum)
    return self._stringfactory.get(addr+1)


  def get_property(self, objectnum, propnum):
    """Return value of property number PROPNUM of object number OBJECTNUM."""

    # don't forget to use the 'propdefaults' table if the property
    # doesn't exist.
