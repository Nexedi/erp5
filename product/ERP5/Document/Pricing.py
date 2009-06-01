##############################################################################
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix

from Products.ERP5.Document.Resource import Resource
from Products.ERP5.Document.MappedValue import MappedValue

class Pricing(MappedValue, XMLMatrix):
    """
      Un element de tarif est un prix pour un ensemble de conditions d'application...
    """

    meta_type = 'ERP5 Pricing'
    portal_type = 'Pricing'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Price
                      , PropertySheet.Pricing
                      )

    security.declareProtected(Permissions.ModifyPortalContent, '_setQuantityRangeList')
    def _setQuantityRangeList(self, category_list):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on
      """
      self._setCategoryMembership('quantity_range', category_list, base=0)
      self.setCellRange((None,), category_list, base_id = 'destination_base_price')

    security.declareProtected(Permissions.ModifyPortalContent, 'setQuantityRangeList')
    def setQuantityRangeList(self, category_list):
      self._setQuantityRangeList(category_list)
      self.reindexObject()

