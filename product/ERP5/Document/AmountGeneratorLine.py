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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.MappedValue import MappedValue
from Products.ERP5.mixin.amount_generator import AmountGeneratorMixin


class AmountGeneratorLine(MappedValue, XMLMatrix, Amount,
                          AmountGeneratorMixin):
  """Abstract class to represent amount transformation for movements"""
  meta_type = 'ERP5 Amount Generator Line'
  portal_type = 'Amount Generator Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IAmountGeneratorLine)

  # Declarative properties
  property_sheets = (PropertySheet.AmountGeneratorLine, )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCellAggregateKey')
  def getCellAggregateKey(self):
    """Define a key in order to aggregate amounts at cell level"""
    return (self.getResource(),
            self.getVariationText()) # Variation UID, Hash ?

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBaseAmountQuantity')
  @classmethod
  def getBaseAmountQuantity(cls, delivery_amount, base_application, rounding):
    """Default method to compute quantity for the given base_application"""
    value = delivery_amount.getGeneratedAmountQuantity(base_application)
    if base_application in delivery_amount.getBaseContributionList():
      value += cls._getBaseAmountQuantity(delivery_amount)
    return value

  @classmethod
  def _getBaseAmountQuantity(cls, delivery_amount):
    """Get default quantity contributed by the input amount"""
    raise NotImplementedError
