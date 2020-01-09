# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

import zope.interface
from warnings import warn
from AccessControl import ClassSecurityInfo
from AccessControl.PermissionRole import PermissionRole

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Base import Base

#from Products.ERP5.Core import MetaNode, MetaResource

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply
from Products.ERP5.mixin.amount_generator import AmountGeneratorMixin
from Products.ERP5.mixin.composition import CompositionMixin
from Products.ERP5.Document.Amount import Amount
from Products.ERP5Type.Cache import transactional_cached

from zLOG import LOG, WARNING

@transactional_cached()
def getExchangeRate(currency_value, section_currency, date):
  currency = currency_value.getRelativeUrl()
  if currency != section_currency:
    from Products.ERP5Type.Document import newTempAccountingTransactionLine
    return currency_value.getPrice(context=newTempAccountingTransactionLine(
      currency_value.getPortalObject(),
      "accounting_line",
      resource=currency,
      start_date=date,
      price_currency=section_currency
    ))

class Movement(XMLObject, Amount, CompositionMixin, AmountGeneratorMixin):
  """
    The Movement class allows to implement ERP5 universal accounting model.

    Movement instances are used in different situations:

    - Orders: Movement instances are use as a documentary object
      to define quantities in orders

    - Deliveries: movements track the actual transfer of resources
      in the past (accounting) or in the future (planning / budgetting)

    For example, the following objects are Orders:

    - a purchase order (the document we send to a supplier
      when we need some goods)

    - a sales order (the document we ask our customer
      to sign to confirm a sale)

    - a production order (the document we send to the workshop
      to confirm we need some operation / service to be achieved)

    Orders allow to describe a target, but can not be used to account
    the reality of actual transfered quantities.

    This is not the case for Deliveries:

    - an invoice (a delivery of money between abstract accounts)

    - a packing list (ie. a delivery of goods shipped)

    - a delivery report (ie. a delivery of goods received)

    - a production report (ie. a delivery of service)

    - a T/T report (a delivery of money between reals accounts)


    For planning, the following approach is used:

    1- Movements from an order are never modified once the order
       is confirmed. This is a rule. An Order is like a contract.
       It can only be amended, if all parties agree.

    2- Movements in a delivery may exist on their own
       (ex. an accounting transaction). Past movements
       can not be modified. Future movements may or may
       not be modified

    When an order is confirmed, the list of "order" movements
    it contains is copied into "delivery" movements. Each delivery
    movement contains a "causality" reference to the order
    it. This allows delivery to be completely different from order
    (ex. different resource, different date, different quantity)
    and allows to keep track of the causal relation between
    a delivery and an order.

    A delivery document (actually a delivery line) then points to one or more of
    the "delivery" movements in the simulation. It is possible to know
    which items have been delivered by making sure each movement in the simulation
    is associated to a "delivery document".

    By looking at all "simulation"

    Delivery movements can be applied the following transformations:

    - split : one movement is cut into 2 or more movements

    - submovements : one movement "generates" many other movements.
      For example, a delivery of goods from the workshop to the stock,
      will result in a "pull" calculation which generates operations
      and sourcing based on a BOM document. The causality of each
      delivery is the "applied rule" which was used to generate submovements

    One should note that

    - movements are never joined (because it would break causality and
      tracability)

    - movements acquire some context information from their causality

    Some submovements need no order to be "confirmed". Some submovements
    need an order to be "confirmed". For example

    - a submovement which allows to compute the CO2 emissions
      of a production facility needs no order confirmation
      (this kind of movement is mostly ised for reporting)

    - a submovement which takes some goods in a stock and
      brings them to a workshop needs some "stock movement"
      order to be "confirmed"

    - a submovement which requires someone to take his time
      for some operation nees a "service order" to be confirmed

    This means that the simulation process must make a distinction
    between different workflows applicable to a movement. For
    movements which require an order to be confirmed, the workflow
    involves the following steps:

    - an order is automaticaly generated, with "order movements"
      which become "causalities" for delivery movements (XXX
      this sound strange...)

    - each order movement is associated to one of the delivery

    As a result, a delivery movement which requires an order may
    have 2 causalities

    - one causality (ie. application of a rule)

    - another causality (ie. confirmation in an order)

    Each causality may define its own context. One context
    may be related for example to a customer request, another context
    may be related to an "internal customer" request (eg. the production manager).
    Context may eventually conflict each other.

    In a customer oriented company, movements should probably
    always be stored within the customer order and acquire
    from the order all context information.

    In a mass production facility, context may be defined in more
    than one location. This is an incentive for putting
    all movements in a simulation "box".

    The second approach is chosen for documentary consistency approach :
      in ERP5, documents rules, can be synchronized. Simulation can not be
      synchronized

    TODO:
    - consider creating a class GeneratedMovement
      and move some superfluous code to it
  """
  meta_type = 'ERP5 Movement'
  portal_type = 'Movement'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IAmountGenerator,
                            interfaces.IVariated,
                            interfaces.IMovement)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Reference
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.Simulation  # XXX-JPS property should be moved to GeneratedMovement class

                    )
  def isPropertyRecorded(self, k): # XXX-JPS method should be moved to GeneratedMovement class
    return False

  security.declareProtected(Permissions.AccessContentsInformation, 'isMovement')
  def isMovement(self):
    return 1

  security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
  def isAccountable(self):
    return True

  security.declareProtected(Permissions.AccessContentsInformation,
                      'isMovingItem')
  def isMovingItem(self, item):
    type_based_script = self._getTypeBasedMethod('isMovingItem')
    if type_based_script:
      return type_based_script(item)
    return False

  security.declareProtected(Permissions.AccessContentsInformation, 'getMovedItemUidList')
  def getMovedItemUidList(self):
    """This method returns an uid list of items
    """
    return [item.getUid() for item in self.getAggregateValueList() \
      if self.isMovingItem(item)]

  # Pricing methods
  def _getPrice(self, context):
    context = self.asContext(context=context,
                             quantity=self.getConvertedQuantity())
    operand_dict = self.getPriceCalculationOperandDict(context=context)
    if operand_dict is not None:
      price = operand_dict['price']
      resource = self.getResourceValue()
      quantity_unit = self.getQuantityUnit()
      if price is not None and quantity_unit and resource is not None:
        return resource.convertQuantity(price, quantity_unit,
                                        resource.getDefaultQuantityUnit(),
                                        self.getVariationCategoryList())
      return price

  def _getTotalPrice(self, default=None, context=None, fast=0, **kw):
    price = self.getPrice(context=context)
    quantity = self.getQuantity()
    if isinstance(price, (int, float)) and \
      isinstance(quantity, (int, float)):
      return quantity * price
    else:
      return default

  def _getBaseUnitPrice(self, context):
    # Override Amount._getBaseUnitPrice to use Movement's
    # getPriceCalculationOperandDict instead of Resource's.
    operand_dict = context.getPriceCalculationOperandDict(context=context)
    if operand_dict is not None:
      base_unit_price = operand_dict.get('base_unit_price', None)
      return base_unit_price

  security.declareProtected(Permissions.AccessContentsInformation,
          'getPriceCalculationOperandDict')
  def getPriceCalculationOperandDict(self, default=None, context=None, **kw):
    """Return a dict object which contains operands used for price
    calculation. The returned items depend on a site configuration,
    because this will invoke a custom script at the end. The only
    assumption is that the dict must contain a key 'price'
    which represents the final result of the price calculation.

    The purpose is to obtain descriptive information to notify the user
    of how a price is calculated in details, in particular, for invoices
    and quotations. So a script which is eventually called should provide
    all values required for generating such reports (e.g. a price,
    a price without a discount, and a discount).
    """
    # First, try a type-based method, and if not present, use
    # the good-old-days way (which only returns a final result).
    if context is None:
      context = self
    method = context._getTypeBasedMethod('getPriceCalculationOperandDict')
    if method is None:
      # Try this, because when the context is an instance of a derived
      # class of Movement, Movement_getPriceCalculationOperandDict is
      # not searched.
      method = getattr(context, 'Movement_getPriceCalculationOperandDict', None)
    if method is not None:
      operand_dict = unrestricted_apply(method, kw=kw)
      if operand_dict is None:
        return default
      assert 'price' in operand_dict
      return operand_dict
    return {'price': context.Movement_lookupPrice()}

  security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
  def getPrice(self, default=None, context=None, evaluate=1, **kw):
    """
      Get the Price in the context.

      If price is not stored locally, lookup a price and store it.

      FIXME: Don't trust this docstring, this method is not at all using the
      passed context, but uses this movement as context.
    """
    # XXX As all accessors can recieve the default value as first positional
    # argument, so we changed the first positional argument from context to
    # default. Here we try to provide backward compatibility for scripts
    # passing the context as first positional argument, and advice them to use:
    #   context.getPrice(context=context)
    # instead of:
    #   context.getPrice(context)
    if isinstance(default, Base):
      msg = 'getPrice first argument is supposed to be the default value'\
            ' accessor, the context should be passed as with the context='\
            ' keyword argument'
      warn(msg, DeprecationWarning)
      LOG('ERP5', WARNING, msg)
      context = default
      default = None

    if len(kw):
      warn('Passing keyword arguments to Movement.getPrice has no effect',
           DeprecationWarning)

    local_price = self._baseGetPrice()
    if local_price is None and evaluate:
      # We must find a price for this movement
      local_price = self._getPrice(context=self)
    return local_price

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getTotalPrice')
  def getTotalPrice(self, default=0.0, context=None, REQUEST=None, fast=None,
                    **kw):
    """Return the total price in the context.

    The optional parameter "fast" is for compatibility, and will be ignored.
    """
    # see getPrice
    if isinstance(default, Base) and context is None:
      msg = 'getTotalPrice first argument is supposed to be the default value'\
            ' accessor, the context should be passed as with the context='\
            ' keyword argument'
      warn(msg, DeprecationWarning)
      LOG('ERP5', WARNING, msg)
      context = default
      default = None

    tmp_context = self.asContext(context=context, REQUEST=REQUEST, **kw)
    result = self._getTotalPrice(default=default, context=tmp_context, fast=fast, **kw)
    method = self._getTypeBasedMethod('convertTotalPrice')
    if method is None:
      return result
    return method(result)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getTotalQuantity')
  def getTotalQuantity(self, default=0.0):
    """
      Returns the quantity if no cell or the total quantity if cells
    """
    return self.getQuantity(default=default)

  # Industrial price API
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getIndustrialPrice')
  def getIndustrialPrice(self):
    """
      Calculates industrial price in context of this movement
    """
    resource = self.getResourceValue()
    if resource is not None:
      return resource.getIndustrialPrice(context=self)
    return None

  # Asset price calculation
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceInventoriatedTotalAssetPrice')
  def getSourceInventoriatedTotalAssetPrice(self):
    """
      Returns a price which can be used to calculate stock value (asset)

      Asset price is used for calculation of inventory asset value
      and for accounting

      If the asset price is specified (as in accounting for multi-currency),
      then it is returned. If no asset price is specified, then we use
      the price as defined on the line, but only for incoming quantities
      (purchase price, industrial price, etc.).

      For outgoing quantities, it is the responsability of database
      to calculate asset prices based on calculation rules (FIFO,
      LIFO, AVERAGE, etc.).
    """
    # This is what we use for accounting
    result = self.getSourceTotalAssetPrice()
    if result is not None:
      return result
    quantity = self.getQuantity()
    if quantity :
      source_asset_price = self.getSourceAssetPrice()
      if source_asset_price :
        return source_asset_price * - quantity
    return None

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceInventoriatedTotalAssetDebit')
  def getSourceInventoriatedTotalAssetDebit(self) :
    """
      Returns the debit part of inventoriated source total asset price.
    """
    result = self.getSourceInventoriatedTotalAssetPrice()
    if result is not None :
      if (result > 0) ^ bool(self.isCancellationAmount()):
        return result
    return 0.0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceInventoriatedTotalAssetCredit')
  def getSourceInventoriatedTotalAssetCredit(self) :
    """
      Returns the credit part of inventoriated source total asset price.
    """
    result = self.getSourceInventoriatedTotalAssetPrice()
    if result is not None :
      if (result < 0) ^ bool(self.isCancellationAmount()):
        return -result
    return 0.0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationInventoriatedTotalAssetPrice')
  def getDestinationInventoriatedTotalAssetPrice(self):
    """
      Returns a price which can be used to calculate stock value (asset)

      Asset price is used for calculation of inventory asset value
      and for accounting
    """
    # This is what we use for accounting
    result = self.getDestinationTotalAssetPrice()
    if result is not None:
      return result
    quantity = self.getQuantity()
    if quantity :
      destination_asset_price = self.getDestinationAssetPrice()
      if destination_asset_price :
        return destination_asset_price * quantity
    return None

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationInventoriatedTotalAssetDebit')
  def getDestinationInventoriatedTotalAssetDebit(self) :
    """
      Returns the debit part of inventoriated destination total asset price.
    """
    result = self.getDestinationInventoriatedTotalAssetPrice()
    if result is not None :
      if (result > 0) ^ bool(self.isCancellationAmount()):
        return result
    return 0.0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationInventoriatedTotalAssetCredit')
  def getDestinationInventoriatedTotalAssetCredit(self) :
    """
      Returns the credit part of inventoriated destination total asset price.
    """
    result = self.getDestinationInventoriatedTotalAssetPrice()
    if result is not None :
      if (result < 0) ^ bool(self.isCancellationAmount()):
        return -result
    return 0.0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceAssetPrice')
  def getSourceAssetPrice(self):
    """
      Returns the price converted to the currency of the source section

      This will be implemeted by calling currency conversion on currency resources
    """
    type_based_script = self._getTypeBasedMethod('getSourceAssetPrice')
    if type_based_script:
      return type_based_script()
    return self._getAssetPrice(section = self.getSourceSectionValue(), date = self.getStartDate())

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationAssetPrice')
  def getDestinationAssetPrice(self):
    """
      Returns the price converted to the currency of the destination section
    """
    type_based_script = self._getTypeBasedMethod('getDestinationAssetPrice')
    if type_based_script:
      return type_based_script()
    return self._getAssetPrice(section = self.getDestinationSectionValue(), date = self.getStopDate())

  def _getAssetPrice(self,section,date):
    price = self.getPrice()
    if section is None or not price or getattr(
      section.aq_base, 'getPriceCurrencyValue', None
    ) is None:
      return price
    currency_value = self.getPriceCurrencyValue()
    if currency_value:
      section_currency = section.getPriceCurrency()
      if section_currency:
        exchange_rate = getExchangeRate(
          currency_value, section_currency, date)
        if exchange_rate:
          return exchange_rate * price
    return price

  # Causality computation
  security.declareProtected( Permissions.AccessContentsInformation,
                             'isConvergent')
  def isConvergent(self):
    """
      Returns true if movement is not divergent
    """
    return bool(not self.isDivergent())

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isDivergent')
  def isDivergent(self):
    """Return True if this movement diverges from the its simulation.
    """
    for simulation_movement in self.getDeliveryRelatedValueList():
      if simulation_movement.isDivergent():
        return True
    return False

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDivergenceList')
  def getDivergenceList(self):
    """
    Return a list of messages that contains the divergences
    """
    divergence_list = []
    for simulation_movement in self.getDeliveryRelatedValueList():
      divergence_list.extend(simulation_movement.getDivergenceList())

    return divergence_list

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanation')
  def getExplanation(self):
    """
      Returns the relative_url of the explanation of this movement.
    """
    explanation = self.getExplanationValue()
    if explanation is not None:
      return explanation.getRelativeUrl()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationUid')
  def getExplanationUid(self):
    """
      Returns the uid of the explanation of this movement.
    """
    explanation = self.getExplanationValue()
    if explanation is not None:
      return explanation.getUid()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationValue')
  def getExplanationValue(self):
    """
      Returns the object explanation of this movement.
    """
    try:
      return self.getRootDeliveryValue()
    except AttributeError:
      return None

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationTitle')
  def getExplanationTitle(self, default=''):
    """
      Returns the title of the explanation of this movement.
    """
    explanation_value = self.getExplanationValue()
    if explanation_value is not None:
      return explanation_value.getTitle()
    return default

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationReference')
  def getExplanationReference(self, default=''):
    """
      Returns the reference of the explanation of this movement.
    """
    explanation_value = self.getExplanationValue()
    if explanation_value is not None:
      return explanation_value.getReference()
    return default

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRootCausalityValueList')
  def getRootCausalityValueList(self):
    """
      Returns the initial causality value for this movement.
      This method will look at the causality and check if the
      causality has already a causality
    """
    return self.getExplanationValue().getRootCausalityValueList()


  # Simulation
  security.declareProtected( Permissions.AccessContentsInformation,
                             'isSimulated')
  def isSimulated(self):
    # 'order' category is deprecated. it is kept for compatibility.
    return (len(self.getDeliveryRelatedValueList()) > 0) or\
           (len(self.getOrderRelatedValueList()) > 0)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isGeneratedBySimulation')
  def isGeneratedBySimulation(self):
    """
      Returns true if the movement is linked to a simulation movement whose
      parent is not a root applied rule, even if the movement is being built.

      Otherwise, this means the movement is or should be linked to a root
      simulation movement.
    """
    simulation_movement = self.getDeliveryRelatedValue()
    return simulation_movement is not None and \
       not simulation_movement.getParentValue().isRootAppliedRule()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSimulationQuantity')
  def getSimulationQuantity(self):
    """Computes the quantities in the simulation.
    """
    return sum(m.getQuantity() for m in self.getDeliveryRelatedValueList())

  # Debit and credit methods
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceDebit')
  def getSourceDebit(self):
    """
      Return the quantity
    """
    quantity = self.getQuantity()
    try:
      quantity = float(quantity)
    except TypeError:
      quantity = 0.0
    if (quantity < 0) ^ bool(self.isCancellationAmount()):
      return - quantity
    return 0.0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceCredit')
  def getSourceCredit(self):
    """
      Return the quantity
    """
    quantity = self.getQuantity()
    try:
      quantity = float(quantity)
    except TypeError:
      quantity = 0.0
    if (quantity < 0) ^ bool(self.isCancellationAmount()):
      return 0.0
    return quantity

  security.declareProtected( Permissions.AccessContentsInformation,
                    'getDestinationDebit', 'getDestinationCredit')
  getDestinationDebit = getSourceCredit
  getDestinationCredit = getSourceDebit

  security.declareProtected(Permissions.ModifyPortalContent, 'setSourceDebit')
  def setSourceDebit(self, source_debit):
    """
      Set the quantity
    """
    if source_debit in (None, ''):
      return
    try:
      source_debit = float(source_debit)
    except TypeError:
      source_debit = 0.0
    self.setCancellationAmount(source_debit < 0)
    self.setQuantity(- source_debit)

  security.declareProtected(Permissions.ModifyPortalContent, 'setSourceCredit')
  def setSourceCredit(self, source_credit):
    """
      Set the quantity
    """
    if source_credit in (None, ''):
      return
    try:
      source_credit = float(source_credit)
    except TypeError:
      source_credit = 0.0
    self.setCancellationAmount(source_credit < 0)
    self.setQuantity(source_credit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDestinationDebit', 'setDestinationCredit' )
  setDestinationDebit = setSourceCredit
  setDestinationCredit = setSourceDebit

  security.declarePrivate('_edit')
  def _edit(self, edit_order=(), **kw):
    """Overloaded _edit to support setting debit and credit at the same time,
    which is required for the GUI.
    Also sets the variation category list and property dict at the end, because
    _setVariationCategoryList and _setVariationPropertyDict needs the resource
    to be set.
    """
    quantity = 0
    if 'source_debit' in kw and 'source_credit' in kw:
      source_credit = kw.pop('source_credit') or 0
      source_debit = kw.pop('source_debit') or 0
      quantity += (source_credit - source_debit)
      kw['quantity'] = quantity
      kw['cancellation_amount'] = (source_credit < 0 or source_debit < 0)
    if 'destination_debit' in kw and 'destination_credit' in kw:
      destination_credit = kw.pop('destination_credit') or 0
      destination_debit = kw.pop('destination_debit') or 0
      quantity += (destination_debit - destination_credit)
      kw['quantity'] = quantity
      kw['cancellation_amount'] = (destination_credit < 0 or destination_debit < 0)

    # If both asset debit and asset credit are passed, we have to take care not
    # to erase the asset price if one of them is unset.
    if kw.get('source_asset_debit') or kw.get('source_asset_credit'):
      if kw.get('source_asset_debit') in (None, ''):
        kw.pop('source_asset_debit', None)
      if kw.get('source_asset_credit') in (None, ''):
        kw.pop('source_asset_credit', None)
    if kw.get('destination_asset_debit') or kw.get('destination_asset_credit'):
      if kw.get('destination_asset_debit') in (None, ''):
        kw.pop('destination_asset_debit', None)
      if kw.get('destination_asset_credit') in (None, ''):
        kw.pop('destination_asset_credit', None)

    if not edit_order:
      edit_order = ('variation_category_list', 'variation_property_dict',)
    return XMLObject._edit(self, edit_order=edit_order, **kw)

  # Debit and credit methods for asset
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceAssetDebit' )
  def getSourceAssetDebit(self):
    """
      Return the debit part of the source total asset price.

      This is the same as getSourceDebit where quantity is replaced
      by source_total_asset_price.
      This method returns 0 if the total asset price is not set.
    """
    quantity = self.getSourceTotalAssetPrice()
    try:
      quantity = float(quantity)
    except TypeError:
      quantity = 0.0
    if (quantity < 0) ^ bool(self.isCancellationAmount()):
      return 0.0
    return quantity

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSourceAssetCredit' )
  def getSourceAssetCredit(self):
    """
      Return the credit part of the source total asset price.

      This is the same as getSourceCredit where quantity is replaced
      by source_total_asset_price.
      This method returns 0 if the total asset price is not set.
    """
    quantity = self.getSourceTotalAssetPrice()
    try:
      quantity = float(quantity)
    except TypeError:
      quantity = 0.0
    if (quantity < 0) ^ bool(self.isCancellationAmount()):
      return - quantity
    return 0.0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationAssetDebit' )
  def getDestinationAssetDebit(self):
    """
      Return the debit part of the destination total asset price.

      This is the same as getDestinationDebit where quantity is replaced
      by destination_total_asset_price.
      This method returns 0 if the total asset price is not set.
    """
    quantity = self.getDestinationTotalAssetPrice()
    try:
      quantity = float(quantity)
    except TypeError:
      quantity = 0.0
    if (quantity < 0) ^ bool(self.isCancellationAmount()):
      return 0.0
    return quantity

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationAssetCredit' )
  def getDestinationAssetCredit(self):
    """
      Return the credit part of the destination total asset price.

      This is the same as getDestinationCredit where quantity is replaced
      by destination_total_asset_price.
      This method returns 0 if the total asset price is not set.
    """
    quantity = self.getDestinationTotalAssetPrice()
    try:
      quantity = float(quantity)
    except TypeError:
      quantity = 0.0
    if (quantity < 0) ^ bool(self.isCancellationAmount()):
      return - quantity
    return 0.0

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setSourceAssetDebit' )
  def setSourceAssetDebit(self, source_debit):
    """
      Set the source total asset price
    """
    if source_debit in (None, ''):
      self.setSourceTotalAssetPrice(None)
      return
    try:
      source_debit = float(source_debit)
    except TypeError:
      source_debit = 0.0
    self.setCancellationAmount(source_debit < 0)
    self.setSourceTotalAssetPrice(source_debit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setSourceAssetCredit' )
  def setSourceAssetCredit(self, source_credit):
    """
      Set the source total asset price
    """
    if source_credit in (None, ''):
      self.setSourceTotalAssetPrice(None)
      return
    try:
      source_credit = float(source_credit)
    except TypeError:
      source_credit = 0.0
    self.setCancellationAmount(source_credit < 0)
    self.setSourceTotalAssetPrice( - source_credit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDestinationAssetDebit' )
  def setDestinationAssetDebit(self, destination_debit):
    """
      Set the destination total asset price
    """
    if destination_debit in (None, ''):
      self.setDestinationTotalAssetPrice(None)
      return
    try:
      destination_debit = float(destination_debit)
    except TypeError:
      destination_debit = 0.0
    self.setCancellationAmount(destination_debit < 0)
    self.setDestinationTotalAssetPrice(destination_debit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDestinationAssetCredit' )
  def setDestinationAssetCredit(self, destination_credit):
    """
      Set the destination total asset price
    """
    if destination_credit in (None, ''):
      self.setDestinationTotalAssetPrice(None)
      return
    try:
      destination_credit = float(destination_credit)
    except TypeError:
      destination_credit = 0.0
    self.setCancellationAmount(destination_credit < 0)
    self.setDestinationTotalAssetPrice( - destination_credit)

  # Item Access (tracking)
  security.declareProtected(Permissions.AccessContentsInformation,
      'getTrackedItemUidList')
  def getTrackedItemUidList(self):
    """
      Return a list of uid for related items
    """
    ### XXX We should filter by portal type here
    return self.getAggregateUidList()

  # Helper methods to display total quantities as produced / consumed
  security.declareProtected(Permissions.AccessContentsInformation,
      'getProductionTotalQuantity')
  def getProductionTotalQuantity(self):
    """
      Return the produced quantity
    """
    quantity = self.getTotalQuantity()
    return self.getProductionQuantity(quantity=quantity)

  security.declareProtected(Permissions.AccessContentsInformation,
      'getConsumptionTotalQuantity')
  def getConsumptionTotalQuantity(self):
    """
      Return the produced quantity
    """
    quantity = self.getTotalQuantity()
    return self.getConsumptionQuantity(quantity=quantity)

  security.declareProtected(Permissions.AccessContentsInformation,
      'getSubVariationText')
  def getSubVariationText(self,**kw):
    """
    Provide a string representation of XXX
    """
    base_category_list = self.getPortalSubVariationBaseCategoryList()
    portal_type_list = self.getPortalSubVariationTypeList()
    return_list = []
    for base_category in base_category_list:
      variation_list = self.getAcquiredCategoryMembershipList(base_category,
          portal_type=portal_type_list,base=1)
      return_list.extend(variation_list)
    return "\n".join(return_list)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getParentExplanationValue')
  def getParentExplanationValue(self):
    """
      This method should be removed as soon as movement groups
      will be rewritten. It is a temp hack
    """
    return self.getParentValue().getExplanationValue()


  # SKU vs. CU
#   security.declareProtected(Permissions.AccessContentsInformation, 'getSourceStandardInventoriatedQuantity')
#   def getSourceStandardInventoriatedQuantity(self):
#     """
#       The inventoriated quantity converted in a default unit
#
#       For assortments, returns the inventoriated quantity in terms of number of items
#       in the assortemnt.
#
#       For accounting, returns the quantity converted in a default unit
#     """
#     return self.getStandardInventoriatedQuantity()

#   security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationStandardInventoriatedQuantity')
#   def getDestinationStandardInventoriatedQuantity(self):
#     """
#       The inventoriated quantity converted in a default unit
#
#       For assortments, returns the inventoriated quantity in terms of number of items
#       in the assortemnt.
#
#       For accounting, returns the quantity converted in a default unit
#     """
#     return self.getStandardInventoriatedQuantity()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'asMovementList')
  def asMovementList(self):
    """
    Placeholder method called when indexing a movement.

    It can be overloaded to generate multiple movements
    from a single one.
    It is used for cataloging a movement multiple time in
    the movement/stock tables.

    Ex: a movement have multiple destinations.
    asMovementList returns a list a movement context with different
    single destination.
    """
    return (self, )

  # XXX: Dirty but required for erp5_banking_core
  getBaobabSourceUid = lambda x: x.getSourceUid()
  getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

  getBaobabDestinationUid = lambda x: x.getDestinationUid()
  getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

  getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
  getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

  getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
  getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

  getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
  getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

  getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
  getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

  getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
  getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

  getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
  getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

  getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
  getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

  getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
  getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)
