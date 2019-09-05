
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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
"""
Products.ERP5.interfaces.amount
"""

from Products.ERP5.interfaces.amount_core import IAmountCore
from Products.ERP5.interfaces.amount_conversion import IAmountConversion
from Products.ERP5.interfaces.amount_price import IAmountPrice
from Products.ERP5.interfaces.amount_arithmetic import IAmountArithmetic

class IAmount(IAmountCore, IAmountConversion, IAmountPrice, IAmountArithmetic):
  """Amount interface specification

    An amount represents a quantity of a given resource
    in a given quantity unit. Optional efficiency can be
    specified in order to represent a loss ratio to take
    into account in calculations. Loss ratio is normally
    used only in Path.

    The Amount interface is useful each time
    one needs to add or substract amounts of resources
    independently of a movement. This is the case for example
    for all Transformation related classes.

    TODO-XXX:
      1. Try to merge IAmountPrice and IPriceable
         interface (used for deliveried)
      2. remove profit_quantity and target_quantity everywhere
      3. consider how to make Interface compatible
         with accessor generation (ex. getResource,
         getQuantity, etc.)
  """
