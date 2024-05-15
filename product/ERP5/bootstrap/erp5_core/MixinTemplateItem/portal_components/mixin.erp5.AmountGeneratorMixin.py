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

from collections import defaultdict, deque
import random
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base, Implicit
from erp5.component.module.GeneratedAmountList import GeneratedAmountList
from Products.ERP5Type import Permissions
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from erp5.component.document.MappedValue import MappedValue
from erp5.component.interface.IAmountGenerator import IAmountGenerator
import six

# XXX What should be done when there is no base_application ?
#     There are 2 options:
#     1. Make the amount generator line always apply, once, which provides an
#        easy way to generate a fixed quantity.
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

  getAmountGeneratorLine__roles__ = None # public
  def getAmountGeneratorLine(self):
    # Use aq_base to avoid additional wrapping.
    return aq_base(self)._amount_generator_line

  def setAmountGeneratorLine(self, amount_generator_line):
    # Use aq_base to keep acquisition context.
    self.aq_base._amount_generator_line = amount_generator_line

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

  def contribute(self, base_amount, variation_category_list, value):
    variated_base_amount = base_amount, variation_category_list
    if variated_base_amount in self._frozen:
      if variation_category_list:
        base_amount = (base_amount,) + variation_category_list
      raise ValueError("Can not contribute to %r because this base_amount is"
        " already applied. This should only happen in you have custom"
        " calculation for some base_amount and your code does not call"
        " getGeneratedAmountQuantity unconditionally for all base_amount"
        " it depends on." % (base_amount,))
    self._dict[variated_base_amount] = \
      self._getQuantity(variated_base_amount) + value

  def _getQuantity(self, variated_base_amount):
    """Get intermediate computed quantity for given base_application"""
    try:
      return self._dict[variated_base_amount]
    except KeyError:
      value = 0
      amount_generator_line = self.aq_base._amount_generator_line
      for base_amount_dict in self._amount_list:
        base_amount_dict.aq_base._amount_generator_line = amount_generator_line
        value += base_amount_dict.getGeneratedAmountQuantity(
          *variated_base_amount)
      self._dict[variated_base_amount] = value
      return value

  getAmountQuantity__roles__ = None # public
  def getAmountQuantity(self, base_amount, variation_category_list=()):
    """Get intermediate computed quantity for given base_application

    Public wrapper to _getQuantity() that can be used directly to apply several
    amount generators one after the other, without having to define a dedicated
    base amount category at each step. Example:
    - movement with quantity*price = 100
    - N discounts of 10%, each one with:
      - base_application=base_amount/cumulative,service_module/discount_<i>
      - base_contribution=base_amount/cumulative
    - with an appriate custom script using this method, you can get an overall
      discount of .1^N
    (with N=3, final price=72.9)
    """
    return self._getQuantity((base_amount, variation_category_list))

  getBaseAmountList__roles__ = None # public
  def getBaseAmountList(self):
    """Return list of amounts that are sub-objects of self

    Returned objects are wrapped like self.
    Example: for a delivery, they are manually created movements.
    """
    return list(self._amount_list)

  getGeneratedAmountQuantity__roles__ = None # public
  def getGeneratedAmountQuantity(self, base_amount, variation_category_list=()):
    """Get final computed quantity for the given base_amount

    If not yet finalized, this method actually calls the (custom) method that
    actually computes the final quantity, which in turn usually calls this
    method again, for the same amount and key: in this case, the returned value
    of this inner call is the last intermediate value just before finalization.
    """
    variated_base_amount = base_amount, variation_category_list
    if variated_base_amount in self._frozen:
      return self._getQuantity(variated_base_amount)
    self._frozen.add(variated_base_amount)
    value = self._dict[variated_base_amount] = \
      self._getGeneratedAmountQuantity(base_amount, variation_category_list)
    return value

  def _getGeneratedAmountQuantity(self, base_amount, variation_category_list):
    try:
      method = self._cache[base_amount]
    except KeyError:
      method = self.aq_base._amount_generator_line._getTypeBasedMethod(
        'getBaseAmountQuantityMethod')
      if method is not None:
        method = method(base_amount)
      if method is None:
        method = self.aq_base._amount_generator_line.getBaseAmountQuantity
      self._cache[base_amount] = method
    if variation_category_list:
      kw = dict(self._method_kw,
                variation_category_list=variation_category_list)
    else:
      kw = self._method_kw
    return method(self, base_amount, **kw)


class BaseAmountResolver(BaseAmountDict):

  class _node(set):

    contribution_dict = None

    def __init__(self, property_dict, contribution_dict): # pylint: disable=super-init-not-called
      self.property_dict = property_dict
      self.contribution_dict = contribution_dict

    def __call__(self):
      if self.contribution_dict:
        contribution_dict_get = self.contribution_dict.get
        del self.contribution_dict
        for application in list(self):
          for node in contribution_dict_get(application, ()):
            self |= node()
      return self

  def __init__(self, cache, method_kw): # pylint: disable=super-init-not-called
    self._dict = cache.setdefault(None, {})
    self._cache = cache
    self._method_kw = method_kw

  def __call__(self, delivery_amount, property_dict_list):
    if property_dict_list:
      recurseApplicationDependencies = \
        self.__of__(delivery_amount).getGeneratedAmountQuantity
      contribution_dict = defaultdict(list)
      node_list = []
      for property_dict in property_dict_list:
        node = self._resolving = self._node(property_dict, contribution_dict)
        node_list.append(node)
        self._amount_generator_line = property_dict[None]
        for variated_base_amount in property_dict['_application']:
          recurseApplicationDependencies(*variated_base_amount)
        for variated_base_amount in property_dict['_contribution']:
          contribution_dict[variated_base_amount].append(node)
      del self._resolving, property_dict_list[:]
      # O(n^2) sorting !! Yeah, shame on me but is it possible to do better
      # when there are pairs of items that can't be compared (e.g. A & C in
      # A -> B <- C), and original order shoud be preserved if possible ?
      # Anyway, there are usually very few objects.
      for node in reversed(node_list):
        isdisjoint = node().isdisjoint
        for i, property_dict in enumerate(property_dict_list):
          if not isdisjoint(property_dict['_contribution']):
            property_dict_list.insert(i, node.property_dict)
            break
        else:
          property_dict_list.append(node.property_dict)
      property_dict_list.reverse()

  def getBaseAmountList(self):
    return ()

  def _getQuantity(self, variated_base_amount):
    return 0

  def getGeneratedAmountQuantity(self, base_amount, variation_category_list=()):
    variated_base_amount = base_amount, variation_category_list
    resolving = self._resolving
    if variated_base_amount not in self._dict:
      self._resolving = self._dict[variated_base_amount] = \
        {variated_base_amount}
      self._getGeneratedAmountQuantity(base_amount, variation_category_list)
      self._resolving = resolving
    resolving |= self._dict[variated_base_amount]
    return 0


@zope.interface.implementer(IAmountGenerator,)
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getGeneratedAmountList')
  def getGeneratedAmountList(self, amount_list=None, rounding=False,
                             amount_generator_type_list=None,
                             generate_empty_amounts=True):
    """
    Implementation of a generic transformation algorithm which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts without any aggregation.

    TODO:
    - is rounding really well supported (ie. before and after aggregation)
      very likely not - proxying before or after must be decided
    """
    # pylint:disable=self-cls-assignment,possibly-used-before-assignment
    # It is the only place where we can import this
    portal = self.getPortalObject()
    getRoundingProxy = portal.portal_roundings.getRoundingProxy
    amount_generator_line_type_list = \
      portal.getPortalAmountGeneratorLineTypeList()
    amount_generator_cell_type_list = \
      portal.getPortalAmountGeneratorCellTypeList()

    # Set empty result by default
    result = GeneratedAmountList()

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

    def getLineSortKey(line):
      int_index = line.getIntIndex()
      return (line.getFloatIndex() if int_index is None else int_index,
              random.random())

    is_mapped_value = isinstance(self, MappedValue)
    recurse_queue = deque()
    resolver = BaseAmountResolver(*args)

    for base_amount in base_amount_list:
      delivery_amount = base_amount.getObject()
      recurse_queue.append(self if is_mapped_value
        else delivery_amount.asComposedDocument(amount_generator_type_list))
      property_dict_list = []
      # If several amount generator lines have same reference, the first
      # (sorted by int_index or float_index) matching one will mask the others.
      # Note that this is possible when a model (i.e. Trade Condition) contains
      # several lines with same reference; Composition only does masking by
      # reference between lines from different parents.
      reference_set = set()
      while recurse_queue:
        self = recurse_queue.popleft()
        amount_generator_line_list = self.objectValues(
          portal_type=amount_generator_line_type_list)
        # Recursively feed base_amount
        if amount_generator_line_list:
          # First sort so that a line can mask other of same reference.
          # We will sort again later to satisfy dependencies between
          # base_application & base_contribution.
          amount_generator_line_list.sort(key=getLineSortKey)
          recurse_queue += amount_generator_line_list
          continue
        if self.getPortalType() not in amount_generator_line_type_list:
          continue
        target_method = 'isDelivery' if self.isTargetDelivery() \
          else default_target
        if target_method and not getattr(delivery_amount, target_method)():
          continue
        if not self.test(delivery_amount):
          continue
        self = self.asPredicate()
        reference = self.getReference()
        if reference:
          if reference in reference_set:
            continue
          reference_set.add(reference)
        # Try to collect cells and aggregate their mapped properties
        # using resource + variation as aggregation key or base_application
        # for intermediate lines.
        amount_generator_cell_list = [self] + self.objectValues(
          portal_type=amount_generator_cell_type_list)
        cell_aggregate = {} # aggregates final line information

        base_application_list = self.getBaseApplicationList()
        base_contribution_list = self.getBaseContributionList()
        for cell in amount_generator_cell_list:
          if cell is not self:
            if not cell.test(delivery_amount):
              continue
            cell = cell.asPredicate()
          aggregate_key = cell.getCellAggregateKey()
          try:
            property_dict = cell_aggregate[aggregate_key]
          except KeyError:
            cell_aggregate[aggregate_key] = property_dict = {
              None: self,
              'base_application_set': set(base_application_list),
              'base_contribution_set': set(base_contribution_list),
              'category_list': [],
              'causality_value_list': [],
              'efficiency': self.getEfficiency(),
              'quantity_unit': self.getQuantityUnit(),
              # The trade model rule often matches by reference and fails if
              # getAggregatedAmountList returns amounts with same reference.
              'reference': cell.getReference() or reference,
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
          if cell is self:
            self_key = aggregate_key
          else:
            # cells inherit base_application and base_contribution from line
            property_dict['base_application_set'].update(
              cell.getBaseApplicationList())
            property_dict['base_contribution_set'].update(
              cell.getBaseContributionList())
          property_dict['causality_value_list'].append(cell)

        # Ignore line (i.e. self) if cells produce unrelated amounts.
        # With Transformed Resource (Transformation), line is considered in
        # order to gather common properties and cells are used to describe
        # variated properties: only 1 amount is produced.
        # In cases like trade, payroll or assorted resources,
        # we want to ignore the line if they are cells.
        # See also implementations of 'getCellAggregateKey'
        if len(cell_aggregate) > 1 and \
           len(cell_aggregate[self_key]['causality_value_list']) == 1:
          del cell_aggregate[self_key]

        # Allow base_application & base_contribution to be variated.
        for property_dict in six.itervalues(cell_aggregate):
          base_amount_set = property_dict['base_application_set']
          variation_list = tuple(sorted(x for x in base_amount_set
                                          if not x.startswith('base_amount/')))
          base_amount_set.difference_update(variation_list)
          # Before we ignored 'quantity=0' amount here for better performance,
          # but it makes expand unstable (e.g. when the first expand causes
          # non-zero quantity and then quantity becomes zero).
          # Ignore only if there's no base_application.
          if not base_amount_set:
            continue
          property_dict['_application'] = [(x, variation_list)
            for x in base_amount_set]
          base_amount_set = property_dict['base_contribution_set']
          variation_list = tuple(sorted(x for x in base_amount_set
                                          if not x.startswith('base_amount/')))
          property_dict['_contribution'] = [(x, variation_list)
            for x in base_amount_set.difference(variation_list)]
          property_dict_list.append(property_dict)

      # Sort amount generators according to
      # base_application & base_contribution dependencies.
      resolver(delivery_amount, property_dict_list)

      # Accumulate applicable values.
      for property_dict in property_dict_list:
        self = property_dict.pop(None)
        base_amount.setAmountGeneratorLine(self)
        contribution_list = property_dict.pop('_contribution')
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
        quantity = float(sum(base_amount.getGeneratedAmountQuantity(*x)
                             for x in property_dict.pop('_application')))
        for key in 'quantity', 'price', 'efficiency':
          if property_dict.get(key, 0) in (None, ''):
            del property_dict[key]
        quantity *= property_dict.pop('quantity', 1)

        # Backward compatibility
        if getattr(self.aq_base, 'create_line', None) == 0:
          property_dict['resource'] = None
        # Create an Amount object
        amount = portal.newContent(temp_object=True, portal_type='Amount',
          # we only want the id to be unique so we pick a random causality
          id=property_dict['causality_value_list'][-1]
            .getRelativeUrl().replace('/', '_'),
          notify_workflow=False)
        amount._setCategoryList(property_dict.pop('category_list', ()))
        if amount.getQuantityUnit():
          del property_dict['quantity_unit']
        amount._setQuantity(quantity)
        amount._setTitle(self.getTitle())
        amount._setDescription(self.getDescription())
        for x in six.iteritems(property_dict):
          amount._setProperty(*x)
        # convert to default management unit if possible
        amount._setQuantity(amount.getConvertedQuantity())
        amount._setQuantityUnit(amount.getResourceDefaultQuantityUnit())
        if rounding:
          # We hope here that rounding is sufficient at line level
          amount = getRoundingProxy(amount, context=self)
        amount._base = delivery_amount
        result.append(amount)
        # Contribute
        quantity *= property_dict.get('price', 1)
        try:
          quantity /= property_dict.get('efficiency', 1)
        except ZeroDivisionError:
          quantity *= float('inf')
        for base_contribution, variation_category_list in contribution_list:
          base_amount.contribute(base_contribution, variation_category_list,
                                 quantity)

    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAggregatedAmountList')
  def getAggregatedAmountList(self, *args, **kw):
    """
    Implementation of a generic transformation algorith which is
    applicable to payroll, tax generation and BOMs. Return the
    list of amounts with aggregation.
    """
    return self.getGeneratedAmountList(*args, **kw).aggregate()

InitializeClass(AmountGeneratorMixin)
