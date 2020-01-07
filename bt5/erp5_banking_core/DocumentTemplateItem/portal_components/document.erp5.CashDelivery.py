##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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
from erp5.component.document.BankingOperation import BankingOperation
from zope.interface import implements

class CashDelivery(BankingOperation):
  """
  """

  meta_type = 'ERP5Banking Cash Delivery'
  portal_type = 'Cash Delivery'
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
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.VariationRange
                    , PropertySheet.ItemAggregation
                    , PropertySheet.BankingOperation
                    )

  security.declareProtected(Permissions.View, 'getBaobabSource')
  def getBaobabSource(self,**kw):
    """
      Returns a calculated source
    """
    script = self._getTypeBasedMethod('getBaobabSource')
    if script is not None:
      return script(self,**kw)
    return self.getSource(**kw)

  security.declareProtected(Permissions.View, 'getBaobabDestination')
  def getBaobabDestination(self,**kw):
    """
      Returns a calculated destination
    """
    script = self._getTypeBasedMethod('getBaobabDestination')
    if script is not None:
      return script(self,**kw)
    return self.getDestination(**kw)
