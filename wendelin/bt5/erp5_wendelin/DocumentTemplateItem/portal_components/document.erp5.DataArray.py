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
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.BigFile import BigFile
from wendelin.bigarray.array_zodb import ZBigArray
import transaction

class DataArray(BigFile):
  """
  Represents a numpy representation of ndarray
  """

  meta_type = 'ERP5 Data Array'
  portal_type = 'Data Array'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    , PropertySheet.DataArray
                    )

  def initArray(self, shape, dtype):
    """
    Initialise array.
    """
    array = ZBigArray(shape, dtype)
    self._setArray(array)

  def _setArray(self, value):
    """
      Set numpy array to this ERP5 Data Array.
    """
    self.array = value
    
    # ZBigArray requirement: before we can compute it (with subobject
    # .zfile) have to be made explicitly known to connection or current
    # transaction committed (XXX: impossible to use as raises ConflictErrors)
    transaction.commit()