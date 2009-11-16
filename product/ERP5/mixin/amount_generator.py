# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5.Document.Amount import Amount

class AmountGeneratorMixin:
  """
  This class provides a generic implementation of IAmountGenerator.

  NOTE: very draft placeholder
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IAmountGenerator,)

  security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
  def getAggregatedAmountList(self, context, movement_list=None, rounding=False):
    """
    NOTE: very draft placeholder
    """
    # Generic Transformation Algorithm
    #   the same algorithm should be applied to payroll, taxes and MRP
    #   transformations

    # Set the common arbitrary base amounts in a dictionary
    base_amount = {
      'delivery': 1,
      'employee': 100,
    }

    # Set ungrouped empty result list
    ungrouped_result = []

    # Initialise loop -
    #  movement_list can be for example delivery.contentValues(use='product')
    if movement_list is None:
      movement_list = context.getMovementList()

    # Build the amounts from delivery lines and trade model lines
    for line in movement_list:
      # Set line level base application amounts
      for application in line.getBaseApplicationList(): # Acquired from Resource
        base_amount[application] = total_price=line.getTotalPrice()
      # Set line level arbitrary base amounts
      base_amount.update(dict(
        price=line.getPrice(),
        quantity=line.getQuantity(),
        unit=(line.getQuantityUnit() == 'unit') * line.getQuantity(),
        ton=(line.getQuantityUnit() == 'ton') * line.getQuantity(),
        # more base applications could be set here
      ))
      # Feed the result with trade model (which must be ordered through
      # constraint resolution)
      for trade_model_line in trade_model.contentValues(portal_type="Trade Model Line"):
        if trade_model_line.getResource():
          # This line has a resource, it is an output line
          amount = Amount(resource=trade_model_line.getResource(),
                          # Resource can be a VAT service or a Component in MRP
                          quantity=base_amount[trade_model_line.getBaseApplication()]
                                  *(trade_model_line.getQuantity() or 1.0),
                          # Quantity is used a multiplier (like in transformations for MRP)
                          price=trade_model_line.getPrice(),
                          # Price could be empty here (like in Transformation)
                          # or set to the price of a product (ex. a Stamp)
                          # or set to a tax ratio (ie. price per value units)
                          base_contribution_list=trade_model_line.getBaseContributionList(),
                          # We save here the base contribution so that they can 
                          # be later used by getTotalPrice on the delivery itself
                        )
          ungrouped_result.append(amount)
        else:
          # This line has a no resource, it is an intermediate line
          value = base_amount[trade_model_line.getBaseApplication()] * \
                  (trade_model_line.getQuantity() or 1.0) * \
                  (trade_model_line.getPrice() or 1.0)
                  # Quantity is used as a multiplier
                  # Price is used as a ratio (also a kind of multiplier)
          for key in trade_model_line.getBaseContribution():
            base_amount[key] += value

    # Compute the grouped result - It is still unknown if grouping
    # should happen here and in which way - XXX
    grouped_result = SomeMovementGroup(ungrouped_result)

    # Return result
    return grouped_result


