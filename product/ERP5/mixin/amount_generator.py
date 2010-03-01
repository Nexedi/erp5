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

  NOTE: this is an early prototype of implementation
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IAmountGenerator,)

  def _getGlobalPropertyDict(self, context, amount_list=None, rounding=False):
    """
    This method can be overridden to define global
    properties involved in trade model line calculation
    """
    raise NotImplementedError
    return {
      'delivery': 1,
      'employee': 100,
    }

  def _getAmountPropertyDict(self, amount, amount_list=None, rounding=False):
    """
    This method can be overridden to define local
    properties involved in trade model line calculation
    """
    raise NotImplementedError
    return dict(
        price=amount.getPrice(),
        quantity=amount.getQuantity(),
        unit=(amount.getQuantityUnit() == 'unit') * amount.getQuantity(),
        ton=(amount.getQuantityUnit() == 'ton') * amount.getQuantity(),
        # more base applications could be set here
      )

  security.declareProtected(Permissions.AccessContentsInformation, 'getGeneratedAmountList')
  def getGeneratedAmountList(self, context, amount_list=None, rounding=False):
    """ 
    Implementation of a generic transformation algorithm which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts without any aggregation.

    TODO:
    - getTargetLevel support
    - is rounding really well supported (ie. before and after aggregation)
      very likely not - proxying before or after must be decided
    """
    # Initialize base_amount global properties (which can be modified
    # during the calculation process)
    base_amount = self._getGlobalPropertyDict(context, amount_list=amount_list, rounding=rounding)
    portal_roundings = self.portal_roundings

    # Set empty result by default
    result = []

    # If amount_list is None, then try to collect amount_list from 
    # the current context
    if amount_list is None: 
      if context.providesIMovementCollection():
        amount_list = context.getMovementList()
      elif context.providesIAmount():
        amount_list = [context]
      elif context.providesIAmountList():
        amount_list = context
      else:
        raise ValueError('amount_list must implement IMovementCollection, IAmount or IAmountList')

    # Each amount in amount_list creates a new amount to take into account
    # We thus need to start with a loop on amount_list
    for amount in amount_list:
      # Initialize base_amount with per amount properties
      amount_propert_dict = self._getAmountPropertyDict(amount, amount_list=amount_list, rounding=rounding)
      base_amount.update(amount_propert_dict)

      # Initialize base_amount with total_price for each amount applications
      for application in amount.getBaseApplicationList(): # Acquired from Resource
        base_amount[application] = amount.getTotalPrice()
    
      # Browse recursively the trade model and accumulate
      # applicable values - first define the recursive method
      def accumulateAmountList(amount_generator_line):
        amount_generator_line_list = amount_generator_line.contentValues(portal_type=self.getPortalAmountGeneratorLineTypeList())
        # Recursively feed base_amount
        if len(amount_generator_line_list):
          amount_generator_line_list = amount_generator_line_list.sort(key=lambda x: x.getIntIndex())
          for amount_generator_line in amount_generator_line_list:
            accumulateAmountList(amount_generator_line)
          return 
        # Try to collect cells and aggregate their mapped properties
        # using resource + variation as aggregation key or base_application
        # for intermediate lines
        amount_generator_cell_list = amount_generator_line.contentValues(portal_type=self.getPortalAmountGeneratorCellTypeList())
        if not amount_generator_cell_list: 
          # Consider the line as the unique cell
          amount_generator_cell_list = [amount_generator_line]
        resource_amount_aggregate = {} # aggregates final line information
        value_amount_aggregate = {} # aggregates intermediate line information
        for amount_generator_cell in amount_generator_cell_list:
          if amount_generator_cell.test(amount): # XXX-JPS getTargetLevel not supported
            # Case 1: the cell defines a final amount of resource 
            if amount_generator_cell.getResource():
              # We must aggregate per resource, variation
              key = (amount_generator_cell.getResource(), amount_generator_cell.getVariationText()) # Variation UID, Hash ?
              resource_amount_aggregate.setdefault(key, {})
              # Then collect the mapped properties (resource, quantity, net_converted_quantity, base_contribution_list, base_application, etc.)
              for property_key in amount_generator_cell.getMappedValuePropertyList():
                # Handling of property lists ? XXX?
                resource_amount_aggregate[key][property_key] = amount_generator_cell.getProperty(property_key)
              resource_amount_aggregate[key]['category_list'] = amount_generator_cell.getCategoryMembershipList(
                 amount_generator_cell.getMappedValueBaseCategoryList())
            # Case 2: the cell defines a temporary calculation line
            else:
              # We must aggregate per base_application
              key = amount_generator_cell.getBaseApplication()
              value_amount_aggregate.setdefault(key, {})
              # Then collect the mapped properties
              for property_key in amount_generator_cell.getMappedValuePropertyList():
                value_amount_aggregate[key][property_key] = amount_generator_cell.getProperty(property_key)
              value_amount_aggregate[key]['category_list'] = amount_generator_cell.getCategoryMembershipList(
                 amount_generator_cell.getMappedValueBaseCategoryList())
        if resource_amount_aggregate:
          for key, property_dict in resource_amount_aggregate.items():
            resource, variation_text = key
            if property_dict.get('category_list', None) is not None:
              category_list = property_dict['category_list']
              del property_dict['category_list']
            else:
              category_list = None
            base_application = property_dict['base_application']
            # property_dict should include
            #   resource - VAT service or a Component in MRP
            #   quantity - quantity in component in MRP, (what else XXX)
            #   variation params - color, size, employer share, etc.
            #   price -  empty (like in Transformation) price of a product (ex. a Stamp)
            #            or tax ratio (ie. price per value units)
            #   base_contribution_list - needed to produce reports with getTotalPrice
            #
            # Quantity is used as a multiplier (like in transformations for MRP)
            # net_converted_quantity is used preferrably to quantity since we need
            # values converted to the default management unit
            # If not quantity is provided, we consider that the value is 1.0 (XXX is it OK ?)
            property_dict['quantity'] = base_amount[amount_generator_line.getBaseApplication()] * \
                (property_dict.get('net_converted_quantity', property_dict.get('quantity')), 1.0)
            # We should not keep net_converted_quantity
            if property_dict.get('net_converted_quantity', None) is not None:
              del property_dict['net_converted_quantity']
            # Create an Amount object
            amount = Amount() # XXX-JPS we could use a movement for safety
            if category_list: amount._setCategoryList(category_list)
            amount._edit(**property_dict)
            if rounding:
              # We hope here that rounding is sufficient at line level
              amount = portal_roundings.getRoundingProxy(amount, context=amount_generator_line)
            result.append(amount)
        if value_amount_aggregate:
          for base_application, property_dict in value_amount_aggregate.items():            
            # property_dict should include
            #   base_contribution_list - needed to produce reports with getTotalPrice
            #   quantity - quantity in component in MRP, (what else XXX)
            #   price -  empty (like in Transformation) price of a product (ex. a Stamp)
            #            or tax ratio (ie. price per value units)
            base_contribution_list = property_dict['base_contribution_list']
            value = base_amount[base_application] * \
                      (property_dict.get('quantity', None) or 1.0) * \
                      (property_dict.get('price', None) or 1.0)       # XXX-JPS is it really 1.0 ?
                      # Quantity is used as a multiplier
                      # Price is used as a ratio (also a kind of multiplier)
            for base_key in base_contribution_list:
              base_amount[base_key] += value

      # Browse recursively the trade model and accumulate
      # applicable values - now execute the method
      accumulateAmountList(self)

      # Purge base_amount of amount applications
      for application in amount_propert_dict.keys():
        del base_amount[application]

    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAggregatedAmountList')
  def getAggregatedAmountList(self, context, movement_list=None, rounding=False):
    """
    Implementation of a generic transformation algorith which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts with aggregation.
    """
    raise NotImplementedError
    result = self.getGeneratedAmountList(context, movement_list=movement_list, rounding=rounding)
    return SomeMovementGroup(result)
