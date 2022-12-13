# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2022 Nexedi SA and Contributors. All Rights Reserved.
#                    Xiaowu Zhang <xiaowu.zhang@nexedi.com>
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

from BTrees.OLBTree import OLBTree
from BTrees.LOBTree import LOBTree
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.Document import Document

class DataMapping(Document):
  """
    data mapping is used to map complex data into a single value
    the idea is if an object has complet data to process, like (object, value1, value2, value3,value4....), we can mapping (object, value1, value2, value3,value4....) into a single value X, then we process only X to make it faster
    here is an use case:
    we have two 2D data arrays with 5 columns, the first column is the name of object, the other fours are the differents value of this object
    Data ArrayA:

   | object | value1 | value2 | value3 | value4 |
   | ------ | ------ | ------ | ------ | ------ |
   | X | 1 | 2 | 3 | 4 |
   | Y | 5 |  6 | 7 | 8 |
   | Z | 9 |  10 | 11 | 12 |

   Data ArrayB:

   | object | value1 | value2 | value3 | value4 |
   | ------ | ------ | ------ | ------ | ------ |
   | X | 1 | 2 | 3 | 4 |
   | Y | 5 |  8 | 7 | 8 |
   | Z | 9 |  10 | 192 | 12 |

   now we need to compare data array A to data array B to find which object inside A has different value.
   without data mapping, we need to compare each object's 4 values, the complexity is O(2^n)
   with data mapping:

   we map those values:

   (X, 1, 2, 3, 4)  ==> 1

   (Y, 5, 6, 7, 8)  ==> 2

   (Z, 9, 10, 11,12) ==>3

   (Y, 5, 8, 7, 8) ==> 4

   (Z, 9, 10, 192, 12) ==> 5

   Data ArrayA:

   | object |
   | ------ |
   | 1 |
   | 2 |
   | 3 |

   Data ArrayB:

   | object |
   | ------ |
   | 1 |
   | 4 |
   | 5 |

   then compare 1D array is fast, the complexity is O(n)
  """

  meta_type = 'ERP5 Data Mapping'
  portal_type = 'Data Mapping'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (
    PropertySheet.CategoryCore,
    PropertySheet.SortIndex
  )

  def __init__(self, *args, **kw):
    self._last_value = 0
    self._object_to_index_tree = OLBTree()
    self._index_to_object_tree = LOBTree()
    Document.__init__(self, *args, **kw)


  security.declareProtected(Permissions.AccessContentsInformation, 'addObject')
  def addObject(self, obj):
    if obj in self._object_to_index_tree:
      return self._object_to_index_tree[obj]
    self._object_to_index_tree[obj] = self._last_value
    self._index_to_object_tree[self._last_value] = obj

    self._last_value +=  1
    return self._object_to_index_tree[obj]

  security.declareProtected(Permissions.AccessContentsInformation, 'getValueFromObject')
  def getValueFromObject(self, obj):
    if obj in self._object_to_index_tree:
      return self._object_to_index_tree[obj]
    else:
      return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getObjectFromValue')
  def getObjectFromValue(self, value):
    if value in self._index_to_object_tree:
      return self._index_to_object_tree[value]
    else:
      return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  def getData(self):
    data_list = []
    for obj in self._object_to_index_tree.keys():
      data_list.append((obj, self._object_to_index_tree[obj]))
    return data_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getSize')
  def getSize(self):
    return len(self._object_to_index_tree.keys())

