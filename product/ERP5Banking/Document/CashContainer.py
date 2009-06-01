##############################################################################
#
# Copyright (c) 2005-2006 Nexedi SARL and Contributors. All Rights Reserved.
#               Aurelien Calonne <aurel@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Container import Container


class CashContainer(Container):
  """
    A Cash DeliveryLine object allows to implement lines
      in Cash Deliveries (packing list, Check payment, Cash Movement, etc.).

    It may include a price (for insurance, for customs, for invoices,
      for orders).
  """

  meta_type = 'ERP5Banking Cash Container'
  portal_type = 'Cash Container'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.VariationRange
                    , PropertySheet.ItemAggregation
                    , PropertySheet.Container
                    , PropertySheet.CashContainer
                    , PropertySheet.Reference
                    )

  security.declareProtected(Permissions.View, 'getBaobabSource')
  def getBaobabSource(self):
    """
      Returns a calculated source
    """
    script = self._getTypeBasedMethod('getBaobabSource')
    if script is not None:
      return script(self)      
    return self.getSource()

  security.declareProtected(Permissions.View, 'getBaobabDestination')
  def getBaobabDestination(self):
    """
      Returns a calculated destination
    """
    script = self._getTypeBasedMethod('getBaobabDestination')
    if script is not None:
      return script(self)
    return self.getDestination()
