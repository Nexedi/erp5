# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
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
from AccessControl import allow_class
from Products.ERP5Type import interfaces

class GeneratedAmountList(list):
  """
    Temporary object needed to aggregate Amount value
    And to calculate some report or total value
  """
  zope.interface.implements(interfaces.IAmountList)

  def getTotalPrice(self):
    """
      Return total base price
    """
    result = 0
    for amount in self:
      total_price = amount.getTotalPrice()
      if total_price:
        result += total_price
    return result

  def getTotalDuration(self):
    """
      Return total duration
    """
    result = 0
    for amount in self:
      duration = amount.getDuration()
      if duration:
        result += duration
    return result

  def aggregate(self):
    # XXX: Do we handle rounding correctly ?
    #      What to do if only total price is rounded ??
    aggregate_dict = {}
    result_list = self.__class__()
    for amount in self:
      key = (amount.getPrice(), amount.getEfficiency(),
             amount.getReference(), amount.categories)
      aggregate = aggregate_dict.get(key)
      if aggregate is None:
        aggregate_dict[key] = [amount, amount.getQuantity()]
        result_list.append(amount)
      else:
        aggregate[1] += amount.getQuantity()
    for amount, quantity in aggregate_dict.itervalues():
      # Before we ignore 'quantity==0' amount here for better performance,
      # but it is not a good idea, especially when the first expand causes
      # non-zero quantity and then quantity becomes zero.
      amount._setQuantity(quantity)
    return result_list

allow_class(GeneratedAmountList)
