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

class ZObjectIllegalPropertyNumber(ZObjectError):
  "Illegal property number given."
  pass

class ZObjectIllegalPropertySet(ZObjectError):
  "Illegal set of a property whose size is not 1 or 2."
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

  def _get_default_property_addr(self, propnum):
    """Return address of default value for property PROPNUM."""

    addr = self._propdefaults_addr

    if 1 <= self._memory.version <= 3:
      if not (1 <= propnum <= 31):
        raise ZObjectIllegalPropertyNumber
    elif 4 <= self._memory.version <= 5:
      if not (1 <= propnum <= 63):
        raise ZObjectIllegalPropertyNumber
    else:
      raise ZObjectIllegalVersion

    return (addr + (2 * (propnum - 1)))


  #--------- Public APIs -----------

  def get_attribute(self, objectnum, attrnum):
    """Return value (0 or 1) of attribute number ATTRNUM of object
    number OBJECTNUM."""

    object_addr = self._get_object_addr(objectnum)

    if 1 <= self._memory.version <= 3:
      if not (0 <= attrnum <= 31):
        raise ZObjectIllegalAttributeNumber
      bf = BitField(self._memory[object_addr + (attrnum / 8)])

    elif 4 <= self._memory.version <= 5:
      if not (0 <= attrnum <= 47):
        raise ZObjectIllegalAttributeNumber
      bf = BitField(self._memory[object_addr + (attrnum / 8)])

    else:
      raise ZObjectIllegalVersion

    return bf[7 - (attrnum % 8)]


  def get_all_attributes(self, objectnum):
    """Return a list of all attribute numbers that are set on object
    OBJECTNUM"""

    if 1 <= self._memory.version <= 3:
      max = 32
    elif 4 <= self._memory.version <= 5:
      max = 48
    else:
      raise ZObjectIllegalVersion

    # really inefficient, but who cares?
    attrs = []
    for i in range (0, max):
      if self.get_attribute(objectnum, i):
        attrs.append(i)
    return attrs


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


  def get_prop_addr_len(self, objectnum, propnum):
    """Return address & length of value for property number PROPNUM of
    object number OBJECTNUM.  If object has no such property, then
    return the address & length of the 'default' value for the property."""

    # start at the beginning of the object's proptable
    addr = self._get_proptable_addr(objectnum)
    # skip past the shortname of the object
    addr += (2 * self._memory[addr])
    pnum = 0

    if 1 <= self._memory.version <= 3:

      while self._memory[addr] != 0:
        bf = BitField(self._memory[addr])
        addr += 1
        pnum = bf[4:0]
        size = bf[7:5] + 1
        if pnum == propnum:
          return (addr, size)
        addr += size

    elif 4 <= self._memory.version <= 5:

      while self._memory[addr] != 0:
        bf = BitField(self._memory[addr])
        addr += 1
        pnum = bf[5:0]
        if bf[7]:
          bf2 = BitField(self._memory[addr])
          addr += 1
          size = bf2[5:0]
        else:
          if bf[6]:
            size = 2
          else:
            size = 1
        if pnum == propnum:
          return (addr, size)
        addr += size

    else:
      raise ZObjectIllegalVersion

    # property list ran out, so return default propval instead.
    default_value_addr = self._get_default_property_addr(propnum)
    return (default_value_addr, 2)


  def get_all_properties(self, objectnum):
    """Return a dictionary of all properties listed in the property
    table of object OBJECTNUM.  (Obviously, this discounts 'default'
    property values.).  The dictionary maps property numbers to (addr,
    len) propval tuples."""

    proplist = {}

    # start at the beginning of the object's proptable
    addr = self._get_proptable_addr(objectnum)
    # skip past the shortname of the object
    shortname_length = self._memory[addr]
    addr += 1
    addr += (2*shortname_length)

    if 1 <= self._memory.version <= 3:
      while self._memory[addr] != 0:
        bf = BitField(self._memory[addr])
        addr += 1
        pnum = bf[4:0]
        size = bf[7:5] + 1
        proplist[pnum] = (addr, size)
        addr += size

    elif 4 <= self._memory.version <= 5:
      while self._memory[addr] != 0:
        bf = BitField(self._memory[addr])
        addr += 1
        pnum = bf[0:6]
        if bf[7]:
          bf2 = BitField(self._memory[addr])
          addr += 1
          size = bf2[0:6]
          if size == 0:
            size = 64
        else:
          if bf[6]:
            size = 2
          else:
            size = 1
        proplist[pnum] = (addr, size)
        addr += size

    else:
      raise ZObjectIllegalVersion

    return proplist

  def set_property(self, objectnum, propnum, value):
    """Set a property on an object."""
    proplist = self.get_all_properties(objectnum)
    if propnum not in proplist:
      raise ZObjectIllegalPropertyNumber

    addr, size = proplist[propnum]
    if size == 1:
      self._memory[addr] = (value & 0xFF)
    elif size == 2:
      self._memory.write_word(addr, value)
    else:
      raise ZObjectIllegalPropertySet

  def describe_object(self, objectnum):
    """For debugging purposes, pretty-print everything known about
    object OBJECTNUM."""

    print "Object number:", objectnum
    print "    Short name:", self.get_shortname(objectnum)
    print "    Parent:", self.get_parent(objectnum),
    print " Sibling:", self.get_sibling(objectnum),
    print " Child:", self.get_child(objectnum)
    print "    Attributes:", self.get_all_attributes(objectnum)
    print "    Properties:"

    proplist = self.get_all_properties(objectnum)
    for key in proplist.keys():
      (addr, len) = proplist[key]
      print "       [%2d] :" % key,
      for i in range(0, len):
        print "%02X" % self._memory[addr+i],
      print

