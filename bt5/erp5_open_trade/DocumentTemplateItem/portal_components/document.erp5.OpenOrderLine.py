# -*- coding: utf-8 -*-
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
from erp5.component.document.SupplyLine import SupplyLine

class OpenOrderLine(SupplyLine):
    """
      An Open Order Line is a Supply Line with additional
      properties to define repeatability

    """
    meta_type = 'ERP5 Open Order Line'
    portal_type = 'Open Order Line'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.SupplyLine
                      , PropertySheet.VariationRange
                      , PropertySheet.Path
                      , PropertySheet.FlowCapacity
                      , PropertySheet.Predicate
                      , PropertySheet.Comment
                      )

    def getTotalQuantity(self, default=0):
      """Returns the total quantity for this open order line.
      If the order line contains cells, the total quantity of cells are
      returned.
      """
      if self.hasCellContent(base_id='path'):
        return sum([cell.getQuantity() for cell in
                      self.getCellValueList(base_id='path')])
      return self.getQuantity(default)

    def getTotalPrice(self):
      """Returns the total price for this open order line.
      If the order line contains cells, the total price of cells are
      returned.
      """
      if self.hasCellContent(base_id='path'):
        return sum([cell.getTotalPrice() for cell in
                      self.getCellValueList(base_id='path')])
      return SupplyLine.getTotalPrice(self)


