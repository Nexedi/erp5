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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Core import MetaNode, MetaResource

from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5.Document.Amount import Amount

from zLOG import LOG

class Movement(XMLObject, Amount):
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

    For simple planning, we use a simple approach. Deliveries contain
    a reference to an order (causality) 2 quantities:

    - a quantity value

    - a target_quantity value

    When quantity and target_quantity, the delivery can be closed.
    When quantity and target_quantity is different, a new delivery is created
    with 0 quantity and target_quantity = target_quantity - quantity.
    This simple system allows to delivery goods of a single order in
    multiple times, and to keep track of deliveries without any complex
    planning system. It is the basis of ERP5 trade module.

    If we need to implement more complex planning, such as in a production
    workshop, we can not use such a simple model. We have to implement a
    planning system. The approach in ERP5 is based on "simulation".

    In this case, target_quantity becomes meaningless.

    For complex planning, the following approach is used instead.

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

    A delivery document (actuall a delivery line) then points to one or more of
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

    - movements are never joined (because it would breack causality and
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
  """
  meta_type = 'ERP5 Movement'
  portal_type = 'Movement'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isMovement = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = ( Interface.Variated, )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    )

  # Pricing methods
  # _getPrice is defined in the order / delivery
  # Pricing mehod
  def _getPrice(self, context):
    # Call a script on the context
    return context.Movement_lookupPrice()

  def _getTotalPrice(self, context):
    price = self.getPrice(context=context)
    quantity = self.getQuantity()
    if type(price) in (type(1.0), type(1)) and \
        type(quantity) in (type(1.0), type(1)):
      return quantity * price
    else:
      return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
  def getPrice(self, context=None, REQUEST=None, **kw):
    """
      Get the Price in the context.

      If price is not stored locally, lookup a price and store it.
    """
    local_price = self._baseGetPrice()
    if local_price is None:
      # We must find a price for this movement
      local_price = self._getPrice(self.asContext(
                            context=context, REQUEST=REQUEST, **kw))
      # And store it localy
      if local_price is not None: self.setPrice(local_price)
    return local_price

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getTotalPrice')
  def getTotalPrice(self, context=None, REQUEST=None, **kw):
    """
      Get the Total Price in the context.
    """
    return self._getTotalPrice(self.asContext(context=context,
                                REQUEST=REQUEST, **kw))

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getTotalQuantity')
  def getTotalQuantity(self):
    """
      Returns the quantity if no cell or the total quantity if cells
    """
    return self.getQuantity()

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
      FILO, AVERAGE, etc.).
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
                             'getSourceAssetPrice')
  def getSourceAssetPrice(self):
    """
      Returns the price converted to the currency of the source section

      This will be implemeted by calling currency conversion on currency resources
    """
    return self.getPrice() # XXX Not implemented yet TODO

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDestinationAssetPrice')
  def getDestinationAssetPrice(self):
    """
      Returns the price converted to the currency of the destination section
    """
    return self.getPrice() # XXX Not implemented yet TODO

  # Causality computation
  security.declareProtected( Permissions.AccessContentsInformation,
                             'isConvergent')
  def isConvergent(self):
    """
      Returns 0 if the target is not met
    """
    return int(not self.isDivergent())

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isDivergent')
  def isDivergent(self):
    """
      XXX documentation out of sync with actual use
      Returns 1 if the target is not met according to the current information
      After and edit, the isOutOfTarget will be checked. If it is 1,
      a message is emitted

      emit targetUnreachable !
    """
    for simulation_movement in self.getDeliveryRelatedValueList():
      if simulation_movement.isDivergent():
        return 1
    return 0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanation')
  def getExplanation(self):
    """
      Returns the relative_url of the explanation of this movement.
    """
    return self.getDelivery()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationUid')
  def getExplanationUid(self):
    """
      Returns the uid of the explanation of this movement.
    """
    return self.getDeliveryUid()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationValue')
  def getExplanationValue(self):
    """
      Returns the object explanation of this movement.
    """
    return self.getDeliveryValue()

  # Simulation
  security.declareProtected( Permissions.AccessContentsInformation,
                             'isSimulated')
  def isSimulated(self):
    return (len(self.getDeliveryRelatedValueList()) > 0) or\
           (len(self.getOrderRelatedValueList()) > 0)

  # New Causality API
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderQuantity')
  def getOrderQuantity(self):
    """
      Returns the quantity of related order(s)
    """
    return self.getQuantity()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryQuantity')
  def getDeliveryQuantity(self):
    """
      Returns the quantity of related delivery(s)
    """
    return self.getQuantity()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationQuantity')
  def getSimulationQuantity(self):
    """
      Returns the sum of quantities in related simulation movements
    """
    return self.getQuantity()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderStartDateList')
  def getOrderStartDateList(self):
    """
      Returns the list of start date of related order(s)
    """
    return [self.getStartDate()]

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryStartDateList')
  def getDeliveryStartDateList(self):
    """
      Returns the list of start date of related delivery(s)
    """
    return [self.getStartDate()]

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationStartDateList')
  def getSimulationStartDateList(self):
    """
      Returns the list of start date related simulation movements
    """
    return [self.getStartDate()]

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderStopDateList')
  def getOrderStopDateList(self):
    """
      Returns the list of stop date of related order(s)
    """
    return [self.getStopDate()]

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryStopDateList')
  def getDeliveryStopDateList(self):
    """
      Returns the list of stop date of related delivery(s)
    """
    return [self.getStopDate()]

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationStopDateList')
  def getSimulationStopDateList(self):
    """
      Returns the list of stop date related simulation movements
    """
    return [self.getStopDate()]

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderSourceList')
  def getOrderSourceList(self):
    """
      Returns the source of related orders
    """
    return self.getSourceList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliverySourceList')
  def getDeliverySourceList(self):
    """
      Returns the source of related deliveries
    """
    return self.getSourceList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationSourceList')
  def getSimulationSourceList(self):
    """
      Returns the source of related simulation movements
    """
    return self.getSourceList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderDestinationList')
  def getOrderDestinationList(self):
    """
      Returns the destination of related orders
    """
    return self.getDestinationList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryDestinationList')
  def getDeliveryDestinationList(self):
    """
      Returns the destination of related deliveries
    """
    return self.getDestinationList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationDestinationList')
  def getSimulationDestinationList(self):
    """
      Returns the destination of related simulation movements
    """
    return self.getDestinationList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderSourceSectionList')
  def getOrderSourceSectionList(self):
    """
      Returns the source_section of related orders
    """
    return self.getSourceSectionList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliverySourceSectionList')
  def getDeliverySourceSectionList(self):
    """
      Returns the source_section of related deliveries
    """
    return self.getSourceSectionList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationSourceSectionList')
  def getSimulationSourceSectionList(self):
    """
      Returns the source_section of related simulation movements
    """
    return self.getSourceSectionList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderDestinationSectionList')
  def getOrderDestinationSectionList(self):
    """
      Returns the destination_section of related orders
    """
    return self.getDestinationSectionList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryDestinationSectionList')
  def getDeliveryDestinationSectionList(self):
    """
      Returns the destination_section of related deliveries
    """
    return self.getDestinationSectionList()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationDestinationSectionList')
  def getSimulationDestinationSectionList(self):
    """
      Returns the destination_section of related simulation movements
    """
    return self.getDestinationSectionList()

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
    if quantity < 0:
      return - quantity
    else:
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
    if quantity < 0:
      return 0.0
    else:
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
      return 0.0
    try:
      source_debit = float(source_debit)
    except TypeError:
      source_debit = 0.0
    self.setQuantity(- source_debit)

  security.declareProtected(Permissions.ModifyPortalContent, 'setSourceCredit')
  def setSourceCredit(self, source_credit):
    """
      Set the quantity
    """
    if source_credit in (None, ''):
      return 0.0
    try:
      source_credit = float(source_credit)
    except TypeError:
      source_credit = 0.0
    self.setQuantity(source_credit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDestinationDebit', 'setDestinationCredit' )
  setDestinationDebit = setSourceCredit
  setDestinationCredit = setSourceDebit

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
    if quantity < 0:
      return 0.0
    else:
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
    if quantity < 0:
      return - quantity
    else:
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
    if quantity < 0:
      return 0.0
    else:
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
    if quantity < 0:
      return -quantity
    else:
      return 0.0
  
  security.declareProtected( Permissions.ModifyPortalContent,
                             'setSourceAssetDebit' )
  def setSourceAssetDebit(self, source_debit):
    """
      Set the source total asset price
    """
    if source_debit in (None, ''):
      return
    try:
      source_debit = float(source_debit)
    except TypeError:
      source_debit = 0.0
    self.setSourceTotalAssetPrice(source_debit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setSourceAssetCredit' )
  def setSourceAssetCredit(self, source_credit):
    """
      Set the source total asset price
    """
    if source_credit in (None, ''):
      return
    try:
      source_credit = float(source_credit)
    except TypeError:
      source_credit = 0.0
    self.setSourceTotalAssetPrice( - source_credit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDestinationAssetDebit' )
  def setDestinationAssetDebit(self, destination_debit):
    """
      Set the destination total asset price
    """
    if destination_debit in (None, ''):
      return
    try:
      destination_debit = float(destination_debit)
    except TypeError:
      destination_debit = 0.0
    self.setDestinationTotalAssetPrice(destination_debit)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDestinationAssetCredit' )
  def setDestinationAssetCredit(self, destination_credit):
    """
      Set the destination total asset price
    """
    if destination_credit in (None, ''):
      return
    try:
      destination_credit = float(destination_credit)
    except TypeError:
      destination_credit = 0.0
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
