##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from erp5.component.document.CashDeliveryLine import CashDeliveryLine
from Products.ERP5.Document.InventoryLine import InventoryLine
from zope.interface import implements

class CashInventoryLine(InventoryLine, CashDeliveryLine):
  """
    A Cash Inventory Line object allows to implement lines
      in Cash Inventory
  """

  meta_type = 'ERP5Banking Cash Inventory Line'
  portal_type = 'Cash Inventory Line'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  implements( interfaces.IVariated, )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Inventory
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.VariationRange
                    , PropertySheet.ItemAggregation
                    , PropertySheet.CashDeliveryLine
                    )
