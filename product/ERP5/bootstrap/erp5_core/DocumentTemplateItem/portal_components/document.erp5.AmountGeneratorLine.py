# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLMatrix import XMLMatrix
from erp5.component.document.Amount import Amount
from erp5.component.document.MappedValue import MappedValue
from erp5.component.mixin.AmountGeneratorMixin import AmountGeneratorMixin
from erp5.component.interface.IAmountGeneratorLine import IAmountGeneratorLine

@zope.interface.implementer(IAmountGeneratorLine)
class AmountGeneratorLine(MappedValue, XMLMatrix, Amount,
                          AmountGeneratorMixin):
  """Abstract class to represent amount transformation for movements"""
  meta_type = 'ERP5 Amount Generator Line'
  portal_type = 'Amount Generator Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (PropertySheet.DublinCore,
                     PropertySheet.AmountGeneratorLine)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCellAggregateKey')
  def getCellAggregateKey(self):
    """Define a key in order to aggregate amounts at cell level"""
    resource = self.getResource()
    if resource:
      return (resource, self.getVariationText()) # Variation UID, Hash ?
    # For a pure intermediate line, we need another way to prevent merging:
    # do not merge if base_application or base_contribution is variated.
    return frozenset(self.getBaseApplicationList() +
                     self.getBaseContributionList())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBaseAmountQuantity')
  @classmethod
  def getBaseAmountQuantity(cls, delivery_amount, base_application,
                            variation_category_list=(), **kw):
    """Default method to compute quantity for the given base_application"""
    value = delivery_amount.getGeneratedAmountQuantity(
      base_application, variation_category_list)
    delivery_amount = delivery_amount.getObject()
    if base_application in delivery_amount.getBaseContributionList():
      assert not variation_category_list
      value += cls._getBaseAmountQuantity(delivery_amount)
    return value

  @classmethod
  def _getBaseAmountQuantity(cls, delivery_amount):
    """Get default quantity contributed by the input amount"""
    raise NotImplementedError
