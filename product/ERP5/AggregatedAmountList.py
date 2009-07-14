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

from UserList import UserList

import zope.interface
from Globals import InitializeClass
from Products.PythonScripts.Utility import allow_class
from AccessControl import ClassSecurityInfo

from Products.ERP5.interfaces.transformation import IAggregatedAmountList

class AggregatedAmountList(UserList):
  """
    Temporary object needed to aggregate Amount value
    And to calculate some report or total value
  """
  zope.interface.implements(IAggregatedAmountList)

  meta_type = "AggregatedAmountList"
  security = ClassSecurityInfo()
#  security.declareObjectPublic()

  security.declarePublic('getTotalPrice')
  def getTotalPrice(self):
    """
      Return total base price
    """
    result = sum(filter(lambda y: y is not None,
                        map(lambda x: x.getTotalPrice(), self)))
    return result

  security.declarePublic('getTotalDuration')
  def getTotalDuration(self):
    """
      Return total duration
    """
    result = sum(filter(lambda y: y is not None, 
                        map(lambda x: x.getDuration(), self)))
    return result

  def multiplyQuantity(self,context=None):
    """
      Take into account the quantity of the 
      context. Change the quantity of each element.
    """
    quantity = None
    if context is not None:
      if context.getQuantity() is not None:
        quantity = context.getQuantity()
    if quantity is not None:
      for x in self:
        previous_quantity = x.getQuantity()
        if previous_quantity is not None:
          x.edit(quantity=context.getQuantity()*previous_quantity)

InitializeClass(AggregatedAmountList)
allow_class(AggregatedAmountList)
