##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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
from Products.ERP5.Document.DeliveryCell import DeliveryCell
from erp5.component.module.BaobabMixin import BaobabMixin
from zope.interface import implements

class CashDeliveryCell(BaobabMixin, DeliveryCell):
  """
    A Cash Delivery Cell object allows to implement cells
      in Cash Deliveries (packing list, Check payment, Cash Movement, etc.).

    It may include a price (for insurance, for customs, for invoices,
      for orders).
  """
  meta_type = 'ERP5Banking Cash Delivery Cell'
  portal_type = 'Cash Delivery Cell'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  implements( interfaces.IVariated, )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.Arrow
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                      , PropertySheet.ItemAggregation
                      , PropertySheet.VariationRange
                    )

  security.declareProtected(Permissions.View, 'getBaobabSource')
  def getBaobabSource(self, **kw):
    """
    """
    script = self._getTypeBasedMethod('getBaobabSource')
    if script is not None:
      return script(self)
    return self.aq_parent.getBaobabSource(**kw)

  security.declareProtected(Permissions.View, 'getBaobabDestination')
  def getBaobabDestination(self, **kw):
    """
    """
    script = self._getTypeBasedMethod('getBaobabDestination')
    if script is not None:
      return script(self)
    return self.aq_parent.getBaobabDestination(**kw)

  security.declareProtected(Permissions.View, 'getBaobabSourceSection')
  def getBaobabSourceSection(self, **kw):
    """
    """
    return self.aq_parent.getBaobabSourceSection(**kw)

  security.declareProtected(Permissions.View, 'getBaobabDestinationSection')
  def getBaobabDestinationSection(self, **kw):
    """
    """
    return self.aq_parent.getBaobabDestinationSection(**kw)

  security.declareProtected(Permissions.View, 'getBaobabSourceFunction')
  def getBaobabSourceFunction(self, **kw):
    """
    """
    return self.aq_parent.getBaobabSourceFunction(**kw)

  security.declareProtected(Permissions.View, 'getBaobabDestinationFunction')
  def getBaobabDestinationFunction(self, **kw):
    """
    """
    return self.aq_parent.getBaobabDestinationFunction(**kw)

  security.declareProtected(Permissions.View, 'getBaobabSourceProject')
  def getBaobabSourceProject(self, **kw):
    """
    """
    return self.aq_parent.getBaobabSourceProject(**kw)

  security.declareProtected(Permissions.View, 'getBaobabDestinationProject')
  def getBaobabDestinationProject(self, **kw):
    """
    """
    return self.aq_parent.getBaobabDestinationProject(**kw)

  security.declareProtected(Permissions.View, 'getBaobabSourceVariationText')
  def getBaobabSourceVariationText(self, **kw):
    """
    """
    script = self._getTypeBasedMethod('getBaobabSourceVariationText')
    if script is not None:
      return script(self)
    if self.getVariationText() != self.aq_parent.getVariationText():
      return self.getVariationText()
    else:
      # only one cell in a line
      return  self.aq_parent.getBaobabSourceVariationText()

  security.declareProtected(Permissions.View, 'getBaobabDestinationVariationText')
  def getBaobabDestinationVariationText(self, **kw):
    """
    """
    script = self._getTypeBasedMethod('getBaobabDestinationVariationText')
    if script is not None:
      return script(self)
    if self.getVariationText() != self.aq_parent.getVariationText():
      return self.getVariationText()
    else:
      # only one cell in a line
      return  self.aq_parent.getBaobabDestinationVariationText()
