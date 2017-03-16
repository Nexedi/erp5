# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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
import hashlib
from BTrees.OOBTree import OOBTree
from AccessControl import ClassSecurityInfo
from Products.ERP5.Document.Document import Document
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.BTreeData import PersistentString

class DataBucketStream(Document):
  """
  Represents data stored in many small files.
  """

  meta_type = 'ERP5 Data Bucket Stream'
  portal_type = 'Data Bucket Stream'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    )


  def __init__(self, id, **kw):
    self.initTree()
    Document.__init__(self, id, **kw)
    
  def initTree(self):
    """
      Initialize the Tree
    """
    self._tree = OOBTree()
    
  def _getOb(self,id, *args, **kw):
    return None
    
  def getBucket(self, key):
    """
      Get one bucket
    """
    return self._tree[key].value
    
  def insertBucket(self, key, value):
    """
      Insert one bucket
    """
    return self._tree.insert(key, PersistentString(value))
    
  def popBucket(self, key):
    """
      Remove one Bucket
    """
    return self._tree.pop(key)
  
  def itervalues(self, min_key=None, count=None):
    """
      Yield complete buckets of data.
    """
    for i, chunk in enumerate(self._tree.itervalues(min_key)):
      if count is not None and i > count - 1:
        break
      out = chunk.value
      # Free memory used by chunk. Helps avoiding thrashing connection
      # cache by discarding chunks earlier.
      chunk._p_deactivate()
      yield out

  def readBucketList(self, min_key=None, count=None):
    """
      Get complete buckets of data.
    """
    return [bucket for bucket in self.itervalues(min_key, count)]
    
  def getItemList(self):
    """
      Return a list of all key, value pairs
    """
    return [item for item in self._tree.items()]
    
  def getKeyList(self):
    """
      Return a list of all keys
    """
    return [key for key in self._tree.keys()]
    
  def getMd5sum(self, key):
    """
      Get hexdigest of bucket.
    """
    h = hashlib.md5()
    h.update(self.getBucket(key))
    return h.hexdigest()
