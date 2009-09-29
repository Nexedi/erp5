##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Domain import Domain

class ApparelSize(XMLObject, XMLMatrix):
    """
      A matrix which provides customer_size
      for a given size
    """

    meta_type = 'ERP5 Apparel Size'
    portal_type = 'Apparel Size'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.VariationRange
                      , PropertySheet.Arrow
                      , PropertySheet.ApparelSize
                      )

    # XXX this should be done using an interraction workflow
    security.declareProtected(Permissions.ModifyPortalContent, '_updateMatrixCellRange')
    def _updateMatrixCellRange(self):
      lines = self.ApparelSize_asCellRange()[0]
      columns = self.ApparelSize_asCellRange()[1]

      if columns != []:
        self.setCellRange(lines, columns, base_id='size')
      else:
        self.setCellRange(lines, base_id='size')

    # XXX this should be done using an interraction workflow
    security.declareProtected(Permissions.ModifyPortalContent, '_setSizeList')
    def _setSizeList(self,value):
      self._categorySetSizeList(value)
      self._updateMatrixCellRange()

    security.declareProtected(Permissions.ModifyPortalContent, '_setApparelMorphoTypeList')
    def _setApparelMorphoTypeList(self,value):
      self._categorySetApparelMorphoTypeList(value)
      self._updateMatrixCellRange()
