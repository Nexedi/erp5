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
from AccessControl import ClassSecurityInfo
from Acquisition import Implicit
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5.Document.MappedValue import MappedValue

# XXX What should be done when there is no base_application ?
#     There are 2 options:
#     1. Make the amount generator line always apply, once, which provides an
#        easy way to generator a fixed quantity.
#     2. Use this criterion to know if a movement was created manually.
#        This is required to not generate amounts from movements that
#        are already the result of generated amounts.
#     Old simulation implemented both but they conflict.
#     Current code implements the 2nd option: Should we use 'use' instead ?

class BaseAmountDict(Implicit):
  """Dictionary holding accumulated base amounts
  """
  def __init__(self, cache, method_kw):
    self._dict = {}
    self._frozen = set()
    self._amount_list = []
    self._cache = cache
    self._method_kw = method_kw

  def setAmountGeneratorLine(self, amount_generator_line):
    self._amount_generator_line = amount_generator_line

  def recurseMovementList(self, movement_list):
    for amount in movement_list:
      # Add only movement which are input. Output will be recalculated.
      # XXX See above comment about the absence of base_application
      #     (for example, we could check if resource use category is in the
      #     normal resource use preference list).
      if not amount.getBaseApplication():
        amount = self.__class__(self._cache, self._method_kw).__of__(amount)
        self._amount_list.append(amount)
        yield amount
    yield self

  def contribute(self, base_amount, value):
    if base_amount in self._frozen:
      raise ValueError("Can not contribute to %r because this base_amount is"
                       " already applied. Order of Amount Generator Lines is"
                       " wrong." % base_amount)
    self._dict[base_amount] = self._getQuantity(base_amount) + value

  def _getQuantity(self, base_amount):
    """Get intermediate computed quantity for given base_application"""
    try:
      return self._dict[base_amount]
    except KeyError:
      value = 0
      amount_generator_line = self._amount_generator_line
      for base_amount_dict in self._amount_list:
        base_amount_dict._amount_generator_line = amount_generator_line
        value += base_amount_dict.getGeneratedAmountQuantity(base_amount)
      self._dict[base_amount] = value
      return value

  getBaseAmountList__roles__ = None # public
  def getBaseAmountList(self):
    """Return list of amounts that are sub-objects of self

    Returned objects are wrapped like self.
    Example: for a delivery, they are manually created movements.
    """
    return list(self._amount_list)

  getGeneratedAmountQuantity__roles__ = None # public
  def getGeneratedAmountQuantity(self, base_amount):
    """Get final computed quantity for given base_amount

    Note: During a call to getQuantity, this method may be called again by
          getGeneratedAmountQuantity for the same amount and key.
          In this case, the returned value is the last intermediate value just
          before finalization.
    """
    if base_amount in self._frozen:
      return self._getQuantity(base_amount)
    self._frozen.add(base_amount)
    try:
      method = self._cache[base_amount]
    except KeyError:
      method = self._amount_generator_line._getTypeBasedMethod(
        'getBaseAmountQuantityMethod')
      if method is not None:
        method = method(base_amount)
      if method is None:
        method = self._amount_generator_line.getBaseAmountQuantity
      self._cache[base_amount] = method
    value = method(self, base_amount, **self._method_kw)
    self._dict[base_amount] = value
    return value


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
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IAmountGenerator,)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getGeneratedAmountList')
  def getGeneratedAmountList(self, amount_list=None, rounding=False,
                             amount_generator_type_list=None,
                             generate_empty_amounts=False):
    """
    Implementation of a generic transformation algorithm which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts without any aggregation.

    TODO:
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
    result = AggregatedAmountList()

    args = (getTransactionalVariable().setdefault(
              "amount_generator.BaseAmountDict", {}),
            dict(rounding=rounding))
    # If amount_list is None, then try to collect amount_list from
    # the current context
    default_target = None
    if amount_list is None:
      if self.providesIMovementCollection():
        default_target = 'isMovement'
        base_amount_list = BaseAmountDict(*args).__of__(self) \
          .recurseMovementList(self.getMovementList())
      elif self.providesIAmount():
        base_amount_list = BaseAmountDict(*args).__of__(self),
      elif self.providesIAmountList():
        base_amount_list = (BaseAmountDict(*args).__of__(amount)
                            for amount in self)
      else:
        raise ValueError("%r must implement IMovementCollection, IAmount or"
                         " IAmountList" % self)
    else:
      base_amount_list = (BaseAmountDict(*args).__of__(amount)
                          for amount in amount_list)

    # First define the method that will browse recursively
    # the amount generator lines and accumulate applicable values
    def accumulateAmountList(self):
      amount_generator_line_list = self.contentValues(
        portal_type=amount_generator_line_type_list)
      # Recursively feed base_amount
      if amount_generator_line_list:
        amount_generator_line_list.sort(key=lambda x: (x.getIntIndex(),
                                                       random.random()))
        for amount_generator_line in amount_generator_line_list:
          accumulateAmountList(amount_generator_line)
        return
      elif (self.getPortalType() not in amount_generator_line_type_list):
        return
      target_method = self.isTargetDelivery() and 'isDelivery' or default_target
      if target_method and not getattr(delivery_amount, target_method)():
        return
      # Try to collect cells and aggregate their mapped properties
      # using resource + variation as aggregation key or base_application
      # for intermediate lines.
      amount_generator_cell_list = [self] + self.contentValues(
        portal_type=amount_generator_cell_type_list)
      cell_aggregate = {} # aggregates final line information

      for cell in amount_generator_cell_list:
        if not cell.test(delivery_amount):
          if cell is self:
            return
          continue
        key = cell.getCellAggregateKey()
        try:
          property_dict = cell_aggregate[key]
        except KeyError:
          cell_aggregate[key] = property_dict = {
            'base_application_set': set(),
            'base_contribution_set': set(),
            'category_list': [],
            'causality_value_list': [],
            'efficiency': self.getEfficiency(),
            'quantity_unit': self.getQuantityUnit(),
            # XXX If they are several cells, we have duplicate references.
            'reference': self.getReference(),
          }
        # Then collect the mapped values (quantity, price, trade_phase...)
        for key in cell.getMappedValuePropertyList():
          if key in ('net_converted_quantity',
                     'net_quantity', 'converted_quantity'):
            # XXX only 'quantity' is accepted and it is treated
            #     as if it was 'converted_quantity'
            raise NotImplementedError
          # XXX-JPS Make sure handling of list properties can be handled
          property_dict[key] = cell.getProperty(key)
        category_list = cell.getAcquiredCategoryMembershipList(
          cell.getMappedValueBaseCategoryList(), base=1)
        property_dict['category_list'] += category_list
        property_dict['resource'] = cell.getResource()
        # For final amounts, base_application and id MUST be defined
        property_dict['base_application_set'].update(
            cell.getBaseApplicationList())
        # For intermediate calculations, base_contribution_list MUST be defined
        property_dict['base_contribution_set'].update(
            cell.getBaseContributionList())
        property_dict['causality_value_list'].append(cell)

      base_amount.setAmountGeneratorLine(self)
      for property_dict in cell_aggregate.itervalues():
        # Ignore line (i.e. self) if cells produce unrelated amounts.
        # With Transformed Resource (Transformation), line is considered in
        # order to gather common properties and cells are used to describe
        # varianted properties: only 1 amount is produced.
        # In cases like trade, payroll or assorted resources,
        # we want to ignore the line if they are cells.
        # See also implementations of 'getCellAggregateKey'
        causality_value = property_dict['causality_value_list'][-1]
        if causality_value is self and len(cell_aggregate) > 1:
          continue
        base_application_set = property_dict['base_application_set']
        # property_dict may include
        #   resource - VAT service or a Component in MRP
        #              (if unset, the amount will only be used for reporting)
        #   variation params - color, size, employer share, etc.
        #   one of (net_)(converted_)quantity - used as a multiplier
        #     -> in MRP, quantity in component
        #     -> for trade, it provides a way to configure a fixed quantity
        #   price -  empty (like in Transformation) price of a product
        #            (ex. a Stamp) or tax ratio (ie. price per value units)
        #   base_contribution_list - needed to produce reports with
        #                            getTotalPrice
        # 'efficiency' is stored separately in the generated amount,
        # for future simulation of efficiencies.
        # If no quantity is provided, we consider that the value is 1.0
        # (XXX is it OK ?) XXX-JPS Need careful review with taxes
        quantity = float(sum(map(base_amount.getGeneratedAmountQuantity,
                                 base_application_set)))
        for key in 'quantity', 'price', 'efficiency':
          if property_dict.get(key, 0) in (None, ''):
            del property_dict[key]
        quantity *= property_dict.pop('quantity', 1)
        if not (quantity or generate_empty_amounts):
          continue
        # Backward compatibility
        if getattr(self.aq_base, 'create_line', None) == 0:
          property_dict['resource'] = None
        # Create an Amount object
        amount = newTempAmount(portal,
          # we only want the id to be unique so we pick a random causality
          causality_value.getRelativeUrl().replace('/', '_'))
        amount._setCategoryList(property_dict.pop('category_list', ()))
        if amount.getQuantityUnit():
          del property_dict['quantity_unit']
        amount._edit(
          quantity=quantity,
          # XXX Are title, int_index and description useful ??
          title=self.getTitle(),
          int_index=self.getIntIndex(),
          description=self.getDescription(),
          **property_dict)
        # convert to default management unit if possible
        amount._setQuantity(amount.getConvertedQuantity())
        amount._setQuantityUnit(amount.getResourceDefaultQuantityUnit())
        if rounding:
          # We hope here that rounding is sufficient at line level
          amount = getRoundingProxy(amount, context=self)
        result.append(amount)
        # Contribute
        quantity *= property_dict.get('price', 1)
        try:
          quantity /= property_dict.get('efficiency', 1)
        except ZeroDivisionError:
          quantity *= float('inf')
        for base_contribution in property_dict['base_contribution_set']:
          base_amount.contribute(base_contribution, quantity)

    is_mapped_value = isinstance(self, MappedValue)

    for base_amount in base_amount_list:
      delivery_amount = base_amount.getObject()
      if not is_mapped_value:
        self = delivery_amount.asComposedDocument(amount_generator_type_list)
      # Browse recursively the amount generator lines and accumulate
      # applicable values - now execute the method
      accumulateAmountList(self)
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAggregatedAmountList')
  def getAggregatedAmountList(self, amount_list=None, rounding=False,
                              amount_generator_type_list=None,
                              generate_empty_amounts=False):
    """
    Implementation of a generic transformation algorith which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts with aggregation.
    """
    generated_amount_list = self.getGeneratedAmountList(
      amount_list=amount_list, rounding=rounding,
      amount_generator_type_list=amount_generator_type_list,
      generate_empty_amounts=generate_empty_amounts)
    # XXX: Do we handle rounding correctly ?
    #      What to do if only total price is rounded ??
    aggregate_dict = {}
    result_list = AggregatedAmountList()
    for amount in generated_amount_list:
      key = (amount.getPrice(), amount.getEfficiency(),
             amount.getReference(), amount.categories)
      aggregate = aggregate_dict.get(key)
      if aggregate is None:
        aggregate_dict[key] = [amount, amount.getQuantity()]
        result_list.append(amount)
      else:
        aggregate[1] += amount.getQuantity()
    for amount, quantity in aggregate_dict.itervalues():
      if quantity or generate_empty_amounts:
        amount._setQuantity(quantity)
      else:
        result_list.remove(amount)
    if 0:
      print 'getAggregatedAmountList(%r) -> (%s)' % (
        self.getRelativeUrl(),
        ', '.join('(%s, %s, %s)'
                  % (x.getResourceTitle(), x.getQuantity(), x.getPrice())
                  for x in result_list))
    return result_list
