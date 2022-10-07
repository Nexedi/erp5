# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

# Required modules - some modules are imported later to prevent circular deadlocks
import persistent
from hashlib import md5

#####################################################
# Avoid importing from (possibly unpatched) Globals
#####################################################

from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import Pdata
from six.moves import cStringIO as StringIO
import transaction

class PdataHelper(persistent.Persistent):
  """Inspired by OFS.Image, this wrapper aim to handle
  long string easily to transform them into Pdata
  """

  def __init__(self, persistent_object, value):
    """Constructor
      - persistent_object: Object contains by storage to access it.
      - value: value to wrapp into Pdata if it is a BaseString or a file.
               It can be also a Pdata object
    """
    self._max_len = 1 << 16
    self._data, self.size = self._read_data(persistent_object, value)
    self.md5sum = None

  def _read_data(self, persistent_object, value):
    """Copied from OFS.Image._read_data
    with some modernisation.

    Returns always a Pdata and its size

      - persistent_object: Object known by storage to access it.
      - value: value to wrapp into Pdata
    """

    n = self._max_len

    if isinstance(value, (str, unicode)):
      if isinstance(value, unicode):
        value = value.encode('utf-8')
      size=len(value)
      if size < n:
        return Pdata(value), size
      # Big string: cut it into smaller chunks
      value = StringIO(value)

    if isinstance(value, FileUpload) and not value:
      raise ValueError('File not specified')

    if isinstance(value, Pdata):
      size = self._read_size_from_pdata(value)
      return value, size

    # Clear md5sum to force refreshing
    self.md5sum = None

    seek=value.seek
    read=value.read

    seek(0,2)
    size=end=value.tell()

    if size <= 2*n:
      seek(0)
      return Pdata(read(size)), size

    # Make sure we have an _p_jar, even if we are a new object, by
    # doing a sub-transaction commit.
    transaction.savepoint(optimistic=True)

    if persistent_object._p_jar is None:
      # Ugh
      seek(0)
      return Pdata(read(size)), size

    # Now we're going to build a linked list from back
    # to front to minimize the number of database updates
    # and to allow us to get things out of memory as soon as
    # possible.
    next_ = None
    while end > 0:
      pos = end-n
      if pos < n:
        pos = 0 # we always want at least n bytes
      seek(pos)

      # Create the object and assign it a next pointer
      # in the same transaction, so that there is only
      # a single database update for it.
      data = Pdata(read(end-pos))
      persistent_object._p_jar.add(data)
      data.next = next_

      # Save the object so that we can release its memory.
      transaction.savepoint(optimistic=True)
      data._p_deactivate()
      # The object should be assigned an oid and be a ghost.
      assert data._p_oid is not None
      assert data._p_state == -1

      next_ = data
      end = pos

    return next_, size

  def _digest_md5_hash_from_pdata(self, pdata):
    """Compute hash part by part
    """
    md5_hash = md5()
    next_ = pdata
    while next_ is not None:
      md5_hash.update(next_.data)
      next_ = next_.next
    return md5_hash.hexdigest()

  def _read_size_from_pdata(self, pdata):
    """Compute size part by part
    """
    size = 0
    next_ = pdata
    while next_ is not None:
      size += len(next_.data)
      next_ = next_.next
    return size

  def __len__(self):
    """Return size of Pdata value
    """
    return self.size

  def __str__(self):
    """Return string concatenation
    of all Pdata parts
    """
    return str(self._data)

  def getContentMd5(self):
    """
    """
    if self.md5sum is not None:
      return self.md5sum
    md5sum = self._digest_md5_hash_from_pdata(self._data)
    self.md5sum = md5sum
    return md5sum

  def __getslice__(self, i, j):
    """XXX Could be improved to avoid loading
    into memory all Pdata objects
    """
    return self.__str__()[i:j]

  def getLastPdata(self):
    """return the last Pdata element
    of a Pdata chains
    """
    pdata = self._data
    next_ = pdata.next

    while next_ is not None:
      pdata = next_
      next_ = pdata.next
    return pdata
