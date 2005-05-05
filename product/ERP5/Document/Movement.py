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
  security.declareObjectProtected(Permissions.View)

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
    if type(price) in (type(1.0), type(1)) and type(quantity) in (type(1.0), type(1)):
      return quantity * price
    else:
      return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
  def getPrice(self, context=None, REQUEST=None, **kw):
    """
    """
    local_price = self._baseGetPrice()
    if local_price is None:
      # We must find a price for this delivery line
      local_price = self._getPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))
      # And store it localy
      if local_price is not None: self.setPrice(local_price)
    return local_price

  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
  def getTotalPrice(self, context=None, REQUEST=None, **kw):
    """
    """
    return self._getTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
  def getTotalQuantity(self):
    """
      Returns the quantity if no cell or the total quantity if cells
    """
    return self.getQuantity()

  # Industrial price API
  security.declareProtected(Permissions.AccessContentsInformation, 'getIndustrialPrice')
  def getIndustrialPrice(self):
    """
      Calculates industrial price in context of this movement
    """
    resource = self.getResourceValue()
    if resource is not None:
      return resource.getIndustrialPrice(context=self)
    return None

  # Asset price calculation
  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceTotalAssetPrice')
  def getSourceTotalAssetPrice(self):
    """
      Returns a price which can be used to calculate stock value (asset)
    """
    try:
      price = self.getSourceAssetPrice()
      if price is None:
        return None
      quantity = self.getQuantity()
      if quantity is None:
        return None
      return quantity * price
    except:
      return None

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationTotalAssetPrice')
  def getDestinationTotalAssetPrice(self):
    """
      Returns a price which can be used to calculate stock value (asset)
    """
    try:
      price = self.getDestinationAssetPrice()
      if price is None:
        return None
      quantity = self.getQuantity()
      if quantity is None:
        return None
      return quantity * price
    except:
      return None

  # Causality computation
  security.declareProtected(Permissions.View, 'isConvergent')
  def isConvergent(self):
    """
      Returns 0 if the target is not met
    """
    return not self.isDivergent()

  security.declareProtected(Permissions.View, 'isDivergent')
  def isDivergent(self):
    """
      Returns 1 if the target is not met according to the current information
      After and edit, the isOutOfTarget will be checked. If it is 1,
      a message is emitted

      emit targetUnreachable !
    """
    if self.getStartDate() is None or self.getTargetStartDate() is None \
            or self.getStopDate() is None or self.getTargetStopDate() is None:
      return 1
    # This is uggly but required due to python2.2/2.3 Zope 2.6/2.7 inconsistency in _millis calculation
    return self.getQuantity() != self.getTargetQuantity() or \
           self.getStartDate().Date() != self.getTargetStartDate().Date() or \
           self.getStopDate().Date() != self.getTargetStopDate().Date()

  # Solver
  def solve(self, dsolver, tsolver):
    if dsolver is not None:
      self.applyDeliverySolver(dsolver)
    if tsolver is not None:
      self.applyTargetSolver(tsolver)

  security.declareProtected(Permissions.ModifyPortalContent, 'applyDeliverySolver')
  def applyDeliverySolver(self, solver):
    self.portal_simulation.applyDeliverySolver(self, solver)

  security.declareProtected(Permissions.ModifyPortalContent, 'applyTargetSolver')
  def applyTargetSolver(self, solver):
    self.portal_simulation.applyTargetSolver(self, solver)

  security.declareProtected(Permissions.AccessContentsInformation, 'getExplanation')
  def getExplanation(self):
    """
      This method allows to group Delivery movements and Simulation movements in a different way
    """
    return self.getDelivery()

  security.declareProtected(Permissions.AccessContentsInformation, 'getExplanationUid')
  def getExplanationUid(self):
    """
      This method allows to group Delivery movements and Simulation movements in a different way
    """
    return self.getDeliveryUid()

  security.declareProtected(Permissions.AccessContentsInformation, 'getExplanationValue')
  def getExplanationValue(self):
    """
      This method allows to group Delivery movements and Simulation movements in a different way
    """
    return self.getDeliveryValue()

  # Simulation
  security.declareProtected(Permissions.View, 'isSimulated')
  def isSimulated(self):
    return len(self.getDeliveryRelatedValueList()) > 0 or len(self.getOrderRelatedValueList()) > 0

  # New Causality API          
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderQuantity')
  def getOrderQuantity(self):
    """
      Returns the quantity of related order(s)
    """
    return self.getQuantity()
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryQuantity')
  def getDeliveryQuantity(self):
    """
      Returns the quantity of related delivery(s)
    """
    return self.getQuantity()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationQuantity')
  def getSimulationQuantity(self):
    """
      Returns the sum of quantities in related simulation movements
    """
    return self.getQuantity()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderStartDateList')
  def getOrderStartDateList(self):
    """
      Returns the start date of related order(s)
    """
    return [self.getStartDate()]
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryStartDateList')
  def getDeliveryStartDateList(self):
    """
      Returns the start date of related delivery(s)
    """
    return [self.getStartDate()]
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationStartDateList')
  def getSimulationStartDateList(self):
    """
      Returns the of start date related simulation movements
    """
    return [self.getStartDate()]
  
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderStopDateList')
  def getOrderStopDateList(self):
    """
      Returns the stop date of related order(s)
    """
    return [self.getStopDate()]
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryStopDateList')
  def getDeliveryStopDateList(self):
    """
      Returns the stop date of related delivery(s)
    """
    return [self.getStopDate()]
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationStopDateList')
  def getSimulationStopDateList(self):
    """
      Returns the of stop date related simulation movements
    """
    return [self.getStopDate()]
  
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderSourceList')
  def getOrderSourceList(self):
    """
      Returns the source of related orders
    """
    return self.getSourceList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliverySourceList')
  def getDeliverySourceList(self):
    """
      Returns the source of related deliveries
    """
    return self.getSourceList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationSourceList')
  def getSimulationSourceList(self):
    """
      Returns the source of related simulation movements
    """
    return self.getSourceList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderDestinationList')
  def getOrderDestinationList(self):
    """
      Returns the destination of related orders
    """
    return self.getDestinationList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryDestinationList')
  def getDeliveryDestinationList(self):
    """
      Returns the destination of related deliveries
    """
    return self.getDestinationList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationDestinationList')
  def getSimulationDestinationList(self):
    """
      Returns the destination of related simulation movements
    """
    return self.getDestinationList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderSourceSectionList')
  def getOrderSourceSectionList(self):
    """
      Returns the source_section of related orders
    """
    return self.getSourceSectionList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliverySourceSectionList')
  def getDeliverySourceSectionList(self):
    """
      Returns the source_section of related deliveries
    """
    return self.getSourceSectionList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationSourceSectionList')
  def getSimulationSourceSectionList(self):
    """
      Returns the source_section of related simulation movements
    """
    return self.getSourceSectionList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getOrderDestinationSectionList')
  def getOrderDestinationSectionList(self):
    """
      Returns the destination_section of related orders
    """
    return self.getDestinationSectionList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryDestinationSectionList')
  def getDeliveryDestinationSectionList(self):
    """
      Returns the destination_section of related deliveries
    """
    return self.getDestinationSectionList()    
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationDestinationSectionList')
  def getSimulationDestinationSectionList(self):
    """
      Returns the destination_section of related simulation movements
    """
    return self.getDestinationSectionList()    
    
  
  # Debit and credit methods
  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceDebit')
  def getSourceDebit(self):
    """
      Return the quantity
    """
    quantity = self.getQuantity()

    try:
      quantity = float(quantity)
    except:
      quantity = 0.0

    if quantity < 0:
      return - quantity
    else:
      return 0.0

  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceCredit')
  def getSourceCredit(self):
    """
      Return the quantity
    """
    quantity = self.getQuantity()

    try:
      quantity = float(quantity)
    except:
      quantity = 0.0

    if quantity < 0:
      return 0.0
    else:
      return quantity

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationDebit')
  getDestinationDebit = getSourceCredit

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationCredit')
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
    except:
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
    except:
      source_credit = 0.0
    self.setQuantity(source_credit)

  security.declareProtected(Permissions.ModifyPortalContent, 'setDestinationDebit')
  def setDestinationDebit(self, destination_debit):
    """
      Temp
    """
    return

  security.declareProtected(Permissions.ModifyPortalContent, 'setDestinationCredit')
  def setDestinationCredit(self, destination_credit):
    """
      Temp
    """
    return

  # SKU vs. CU
  security.declareProtected(Permissions.AccessContentsInformation, 'getSourceStandardInventoriatedQuantity')
  def getSourceStandardInventoriatedQuantity(self):
    """
      The inventoriated quantity converted in a default unit
      
      For assortments, returns the inventoriated quantity in terms of number of items
      in the assortemnt.
      
      For accounting, returns the quantity converted in a default unit
    """
    return self.getStandardInventoriatedQuantity()        
    
  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationStandardInventoriatedQuantity')
  def getDestinationStandardInventoriatedQuantity(self):
    """
      The inventoriated quantity converted in a default unit
      
      For assortments, returns the inventoriated quantity in terms of number of items
      in the assortemnt.
      
      For accounting, returns the quantity converted in a default unit
    """
    return self.getStandardInventoriatedQuantity()        
