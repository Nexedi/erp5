##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.SupplyCell import SupplyCell

class OpenOrderCell(SupplyCell):
    """
      An Open Order Cell allows to define specific properties
      for each variation of a resource in an Open Order Line.
    """
    meta_type = 'ERP5 Open Order Cell'
    portal_type = 'Open Order Cell'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.SupplyLine
                      , PropertySheet.Discount
                      , PropertySheet.Path
                      , PropertySheet.FlowCapacity
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                      , PropertySheet.Reference
                      )

    def getTotalPrice(self):
      """Returns the total price for this open order cell.
      Unlike Amount, we do not calculate a price implicitly if not defined.
      Actually, I (jerome) think amount behaviour itself if wrong.
      """
      return (self.getQuantity() or 0) * (self.getPrice() or 0)

