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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.MappedValue import MappedValue
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
from Products.ERP5.Document.TradeCondition import TradeCondition
from Products.ERP5.mixin.amount_generator import AmountGeneratorMixin
import zope.interface

class TradeModelLine(MappedValue, XMLMatrix, Amount, AmountGeneratorMixin):
  """Trade Model Line is a way to represent trade transformation for movements"""
  meta_type = 'ERP5 Trade Model Line'
  portal_type = 'Trade Model Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(
      interfaces.IAmountGenerator,
      interfaces.IVariated
  )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                  , PropertySheet.SimpleItem
                  , PropertySheet.CategoryCore
                  , PropertySheet.Amount
                  , PropertySheet.Price
                  , PropertySheet.TradeModelLine
                  , PropertySheet.Reference
                  , PropertySheet.Predicate
                  , PropertySheet.MappedValue
                  )

  # XXX to be specificied in an interface (IAmountGeneratorLine ?)
  def getAmountProperty(self, amount, base_application, amount_list, rounding):
    """
    Produced amount quantity is needed to initialize transformation
    """
    return amount.getTotalPrice()

  ### Mapped Value Definition
  # Provide default mapped value properties and categories if
  # not defined
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
    return ('price', 'efficiency')

  def getMappedValueBaseCategoryList(self):
    result = self._baseGetMappedValueBaseCategoryList()
    if result:
      return result
    return ('base_contribution', 'trade_phase', )

  #
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPrice')
  def getPrice(self):
    """
    """
    return self._baseGetPrice()
