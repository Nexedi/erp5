# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
#                    Fabien Morin <fabien@nexedi.com>
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
from Products.ERP5.Document.AmountGeneratorLine import AmountGeneratorLine

class TradeModelLine(AmountGeneratorLine):
  """Trade Model Line is a way to represent trade transformation for movements"""
  meta_type = 'ERP5 Trade Model Line'
  portal_type = 'Trade Model Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = (PropertySheet.TradeModelLine, )

  @classmethod
  def _getBaseAmountQuantity(cls, delivery_amount):
    return delivery_amount.getTotalPrice()

  ### Mapped Value Definition
  # Provide default mapped value properties and categories if
  # not defined
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMappedValuePropertyList')
  def getMappedValuePropertyList(self):
    """
    """
    result = self._baseGetMappedValuePropertyList()
    if result:
      return result
    # If quantity is defined, then tax works as transformed resource
    if self._baseGetQuantity(None) is not None:
      return ('quantity', 'price', 'step')
    # Else tax provides only a ratio on amount
    return ('price',)

  def getMappedValueBaseCategoryList(self):
    return self._baseGetMappedValueBaseCategoryList() or ('trade_phase', 'use',)
