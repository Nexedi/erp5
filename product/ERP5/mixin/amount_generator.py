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

import random
import zope.interface
from zLOG import LOG, WARNING
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.MappedValue import MappedValue


class AmountGeneratorMixin:
  """
  This class provides a generic implementation of IAmountGenerator.
  It is used by Transformation, Trade Model, Paysheet, etc. It is
  designed to support about any transformation process based
  on IMappedValue interface. The key idea is that the Amount Generator
  Lines and Cell provide either directly or through acquisition the
  methods 'getMappedValuePropertyList' and 'getMappedValueBaseCategoryList'
  to gather the properties and categories to copy from the model
  to the generated amounts.

  NOTE: this is an first prototype of implementation
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IAmountGenerator,)

  # XXX to be specificied in an interface (IAmountGeneratorLine ?)
  def getCellAggregateKey(self, amount_generator_cell):
    """Define a key in order to aggregate amounts at cell level

      Transformed Resource (Transformation)
        key must be None because:
          - quantity and variation are defined in different cells so that the
            user does not need to enter values depending on all axes
          - amount_generator_cell.test should filter only 1 variant
        current key = (acquired resource, acquired variation)

      Assorted Resource (Transformation)
        key = (assorted resource, assorted resource variation)
        usually resource and quantity provided together

      Payroll
        key = (payroll resource, payroll resource variation)

      Tax
        key = (tax resource, tax resource variation)
    """
    return (amount_generator_cell.getResource(),
            amount_generator_cell.getVariationText()) # Variation UID, Hash ?

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getGeneratedAmountList')
  def getGeneratedAmountList(self, amount_list=None, rounding=False,
                             amount_generator_type_list=None):
    """
    Implementation of a generic transformation algorithm which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts without any aggregation.

    TODO:
    - getTargetLevel support
    - is rounding really well supported (ie. before and after aggregation)
      very likely not - proxying before or after must be decided
    """
    # It is the only place we can import this
    from Products.ERP5Type.Document import newTempAmount
    portal = self.getPortalObject()
    getRoundingProxy = portal.portal_roundings.getRoundingProxy
    amount_generator_line_type_list = \
      portal.getPortalAmountGeneratorLineTypeList()
    amount_generator_cell_type_list = \
      portal.getPortalAmountGeneratorCellTypeList()

    # Set empty result by default
    result = []

    # If amount_list is None, then try to collect amount_list from
    # the current context
    if amount_list is None:
      if self.providesIMovementCollection():
        # Amounts are sorted to process deeper objects first.
        movement_portal_type_list = self.getPortalMovementTypeList()
        amount_list = [self]
        amount_index = 0
        while amount_index < len(amount_list):
          amount_list += amount_list[amount_index].objectValues(
              portal_type=movement_portal_type_list)
          amount_index += 1
        # Add only movement which are input (i.e. resource use category
        # is in the normal resource use preference list). Output will
        # be recalculated.
        amount_list = [x for x in amount_list[:0:-1] # skip self
                         if not x.getBaseApplication()] + [self]
      elif self.providesIAmount():
        amount_list = self,
      elif self.providesIAmountList():
        amount_list = self
      else:
        raise ValueError(
          'self must implement IMovementCollection, IAmount or IAmountList')

    def getAmountProperty(amount_generator_line, base_application):
      """Produced amount quantity is needed to initialize transformation"""
      if base_application in base_contribution_set:
        method = amount_generator_line._getTypeBasedMethod('getAmountProperty')
        if method is not None:
          value = method(delivery_amount, base_application, amount_list,
                         rounding)
          if value is not None:
            return value
        return amount_generator_line.getAmountProperty(
            delivery_amount, base_application, amount_list, rounding)

    # First define the method that will browses recursively
    # the amount generator lines and accumulate applicable values
    def accumulateAmountList(self):
      amount_generator_line_list = self.contentValues(
        portal_type=amount_generator_line_type_list)
      # Recursively feed base_amount
      if amount_generator_line_list:
        # Append lines with missing or duplicate int_index
        if self in check_wrong_index_set:
          check_wrong_index_set.update(amount_generator_line_list)
        else:
          index_dict = {}
          for line in amount_generator_line_list:
            index_dict.setdefault(line.getIntIndex(), []).append(line)
          for line_list in index_dict.itervalues():
            if len(line_list) > 1:
              check_wrong_index_set.update(line_list)
        amount_generator_line_list.sort(key=lambda x: (x.getIntIndex(),
                                                       random.random()))
        for amount_generator_line in amount_generator_line_list:
          accumulateAmountList(amount_generator_line)
        return
      elif (self.getPortalType() not in amount_generator_line_type_list):
        return
      # Try to collect cells and aggregate their mapped properties
      # using resource + variation as aggregation key or base_application
      # for intermediate lines
      amount_generator_cell_list = [self] + self.contentValues(
        portal_type=amount_generator_cell_type_list)
      resource_amount_aggregate = {} # aggregates final line information
      value_amount_aggregate = {} # aggregates intermediate line information

      for amount_generator_cell in amount_generator_cell_list:
        if not amount_generator_cell.test(delivery_amount):
          continue
        base_application_list = amount_generator_cell.getBaseApplicationList()
        try:
          base_contribution_list = \
            amount_generator_cell.getBaseContributionList()
        except AttributeError:
          base_contribution_list = ()
        resource = amount_generator_cell.getResource()
        if resource or base_contribution_list: # case 1 & 2
          applied_base_amount_set.update(base_application_list)
        # XXX What should be done when there is no base_application ?
        #     With the following code, it always applies, once, like in
        #     the old implementation, but this is not consistent with
        #     the way we ignore automatically created movements
        #     (see above code when self provides IMovementCollection).
        #     We should either do nothing if there is no base_application,
        #     or find a criterion other than base_application to find
        #     manually created movements.
        for base_application in base_application_list or (None,):
          if base_application not in base_amount:
            value = getAmountProperty(self, base_application)
            if value is None:
              continue
            base_amount[base_application] = value
          # Case 1: the cell defines a final amount of resource
          if resource:
            key = self.getCellAggregateKey(amount_generator_cell)
            property_dict = resource_amount_aggregate.setdefault(key, {})
            # Then collect the mapped properties (net_converted_quantity,
            # resource, quantity, base_contribution_list, base_application...)
            for key in amount_generator_cell.getMappedValuePropertyList():
              # XXX-JPS Make sure handling of list properties can be handled
              property_dict[key] = amount_generator_cell.getProperty(key)
            category_list = amount_generator_cell.getAcquiredCategoryMembershipList(
              amount_generator_cell.getMappedValueBaseCategoryList(), base=1)
            if category_list:
              property_dict.setdefault('category_list',
                                       []).extend(category_list)
            property_dict['resource'] = resource
            # For final amounts, base_application and id MUST be defined
            property_dict.setdefault('base_application_set',
                                     set()).add(base_application)
            #property_dict['trade_phase_list'] = amount_generator_cell.getTradePhaseList() # Required moved to MappedValue
            property_dict.setdefault('causality_value_list',
                                     []).append(amount_generator_cell)
          # Case 2: the cell defines a temporary calculation line
          if base_contribution_list:
            # Define a key in order to aggregate amounts in cells
            #   base_application MUST be defined
            #
            # Single line case: key = base_application
            #
            # Payroll
            #
            #   key = base_application
            #     it is not possible to use cells to add amounts
            #     in intermediate calculation but only to
            #     select one amount
            #
            #   key = (base_application, XXX) would be required
            #
            #  Use of a method to generate keys is probably better.
            #  than hardcoding it here
            property_dict = value_amount_aggregate.setdefault(base_application,
                                                              {})
            # Then collect the mapped properties
            for key in amount_generator_cell.getMappedValuePropertyList():
              property_dict[key] = amount_generator_cell.getProperty(key)
            # For intermediate calculations,
            # base_contribution_list MUST be defined
            property_dict['base_contribution_list'] = base_contribution_list
      for property_dict in resource_amount_aggregate.itervalues():
        base_application_set = property_dict['base_application_set']
        # property_dict should include
        #   resource - VAT service or a Component in MRP
        #   quantity - quantity in component in MRP, (what else XXX)
        #   variation params - color, size, employer share, etc.
        #   price -  empty (like in Transformation) price of a product
        #            (ex. a Stamp) or tax ratio (ie. price per value units)
        #   base_contribution_list - needed to produce reports with
        #                            getTotalPrice
        #
        # Quantity is used as a multiplier (like in transformations for MRP)
        # net_converted_quantity is used preferrably to quantity since we
        # need values converted to the default management unit
        # If no quantity is provided, we consider that the value is 1.0
        # (XXX is it OK ?) XXX-JPS Need careful review with taxes
        quantity = property_dict.pop('net_converted_quantity',
                                     property_dict.get('quantity', 1.0))
        if quantity in (None, ''):
          property_dict['quantity'] = sum(base_amount[x]
                                          for x in base_application_set)
        else:
          property_dict['quantity'] = sum(base_amount[x]
                                          for x in base_application_set) * quantity
        base_application_set.discard(None)
        # XXX Is it correct to generate nothing if the computed quantity is 0 ?
        if not property_dict['quantity']:
          continue
        # Create an Amount object
        # XXX-JPS Could we use a movement for safety ?
        amount = newTempAmount(portal,
          # we only want the id to be unique
          property_dict['causality_value_list'][0]
          .getRelativeUrl().replace('/', '_'))
        amount._setCategoryList(property_dict.pop('category_list', ()))
        amount._edit(
          # XXX If they are several cells, we may have duplicate references.
          reference=self.getReference(),
          # XXX Are title, int_index and description useful ??
          title=self.getTitle(),
          int_index=self.getIntIndex(),
          description=self.getDescription(),
          **property_dict)
        if rounding:
          # We hope here that rounding is sufficient at line level
          amount = getRoundingProxy(amount, context=self)
        result.append(amount)
      for base_application, property_dict in value_amount_aggregate.iteritems():
        # property_dict should include
        #   base_contribution_list - needed to produce reports with
        #                            getTotalPrice
        #   quantity - quantity in component in MRP, (what else XXX)
        #   price -  empty (like in Transformation) price of a product
        #            (ex. a Stamp) or tax ratio (ie. price per value units)
        # XXX Why price ? What about efficiency ?
        value = base_amount[base_application] * \
          (property_dict.get('quantity') or 1.0) * \
          (property_dict.get('price') or 1.0) # XXX-JPS is it really 1.0 ?
          # Quantity is used as a multiplier
          # Price is used as a ratio (also a kind of multiplier)
        for base_key in property_dict['base_contribution_list']:
          if base_key in applied_base_amount_set:
            if self in check_wrong_index_set:
              raise ValueError("Duplicate or missing int_index on Amount"
                               " Generator Lines while processing %r" % self)
            else:
              LOG("getGeneratedAmountList", WARNING, "%r contributes to %r"
                  " but this base_amount was already applied. Order of Amount"
                  " Generator Lines may be wrong." % (self, base_key))
          if base_key not in base_amount:
            base_amount[base_key] = getAmountProperty(self, base_key) or 0
          base_amount[base_key] += value

    is_mapped_value = isinstance(self, MappedValue)

    # Each amount in amount_list creates a new amount to take into account
    # We thus need to start with a loop on amount_list
    for delivery_amount in amount_list:
      if not is_mapped_value:
        self = delivery_amount.asComposedDocument(amount_generator_type_list)
      # XXX It should be possible to keep specific keys in base_amount dict.
      #     This can be done by a preference listing base_amount categories
      #     for which we want to accumulate quantities.
      base_amount = {None: 1}
      base_contribution_set = delivery_amount.getBaseContributionSet()
      # Check that lines are sorted correctly
      applied_base_amount_set = set()
      # Check that lines with missing or duplicate int_index are independant
      check_wrong_index_set = set()
      # Browse recursively the amount generator lines and accumulate
      # applicable values - now execute the method
      accumulateAmountList(self)

    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAggregatedAmountList')
  def getAggregatedAmountList(self, amount_list=None, rounding=False,
                              amount_generator_type_list=None):
    """
    Implementation of a generic transformation algorith which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts with aggregation.

    TODO:
    - make working sample code
    """
    generated_amount_list = self.getGeneratedAmountList(
      amount_list=amount_list, rounding=rounding,
      amount_generator_type_list=amount_generator_type_list)
    aggregated_amount_dict = {}
    result_list = []
    for amount in generated_amount_list:
      key = (amount.getPrice(), amount.getEfficiency(),
             amount.getReference(), amount.categories)
      aggregated_amount = aggregated_amount_dict.get(key)
      if aggregated_amount is None:
        aggregated_amount_dict[key] = amount
        result_list.append(amount)
      else:
        # XXX How to aggregate rounded amounts ?
        #     What to do if the total price is rounded ??
        assert not rounding, "TODO"
        aggregated_amount.quantity += amount.quantity
    if 0:
      print 'getAggregatedAmountList(%r) -> (%s)' % (
        self.getRelativeUrl(),
        ', '.join('(%s, %s, %s)'
                  % (x.getResourceTitle(), x.getQuantity(), x.getPrice())
                  for x in result_list))
    return result_list

    raise NotImplementedError
    # Example of return code
    result = self.getGeneratedAmountList(amount_list=amount_list,
                                         rounding=rounding)
    return SomeMovementGroup(result)
