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

from Globals import InitializeClass, PersistentMapping
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowMethod
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import TempXMLMatrix
from Products.ERP5Type.Base import Base
from Products.ERP5.Document.DeliveryCell import DeliveryCell
from Acquisition import Explicit, Implicit
from Products.PythonScripts.Utility import allow_class
from DateTime import DateTime
#from Products.ERP5.ERP5Globals import movement_type_list, draft_order_state, planned_order_state

from Products.ERP5.MovementGroup import OrderMovementGroup, PathMovementGroup
from Products.ERP5.MovementGroup import DateMovementGroup, ResourceMovementGroup
from Products.ERP5.MovementGroup import VariantMovementGroup, RootMovementGroup

from zLOG import LOG

class TempDeliveryCell(DeliveryCell):

  def getPrice(self):
    return self.price

  def _setPrice(self, value):
    self.price = value

  def getQuantity(self):
    return self.quantity

  def _setQuantity(self, value):
    self.quantity = value

  def reindexObject(self, *args, **kw):
    pass

  def activate(self):
    return self

class XMLMatrix(TempXMLMatrix):

  def newCellContent(self, id,**kw):
    """
          This method can be overriden
    """
    new_temp_object = TempDeliveryCell(id)
    self._setObject(id, new_temp_object)
    return self.get(id)

class Group(Implicit):
  """
    Hold movements which have the same resource and the same variation.
  """
  # Declarative security
  security = ClassSecurityInfo()
  #security.declareObjectProtected(Permissions.View)
  security.declareObjectPublic()

  # These get methods are workarounds for the Zope security model.
  security.declareProtected(Permissions.AccessContentsInformation, 'getMovementList')
  def getMovementList(self):
    return self.movement_list

  security.declareProtected(Permissions.AccessContentsInformation, 'getResourceId')
  def getResourceId(self):
    return self.resource_id

  security.declareProtected(Permissions.AccessContentsInformation, 'getResourceTitle')
  def getResourceTitle(self):
    return self.resource_title

  security.declareProtected(Permissions.AccessContentsInformation, 'getVariationBaseCategoryList')
  def getVariationBaseCategoryList(self):
    return list(self.variation_base_category_list)

  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
  def getTotalPrice(self):
    return self.total_price

  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
  def getTotalQuantity(self):
    return self.total_quantity

  security.declareProtected(Permissions.AccessContentsInformation, 'getMatrix')
  def getMatrix(self):
    return self.matrix

  def __init__(self, movement):
    self.movement_list = []
    #self.quantity_unit = movement.getQuantityUnit() # This is likely an error JPSforYO
    resource_value = movement.getResourceValue()
    if resource_value is not None:
      self.quantity_unit = resource_value.getDefaultQuantityUnit()
    else:
      self.quantity_unit = movement.getQuantityUnit() # Meaningless XXX ?
    self.resource = movement.getResource()
    self.resource_id = movement.getResourceId()
    self.resource_title = movement.getResourceTitle()
    self.variation_base_category_list = movement.getVariationBaseCategoryList()
    self.variation_category_list = []
    # self.total_price = movement.getTotalPrice() # This is likely an error JPSforYO
    # self.total_quantity = movement.getTotalQuantity() # This is likely an error JPSforYO
    self.total_price = 0.0 # No need to add twice since we add it in append
    self.total_quantity = 0.0 # No need to add twice since we add it in append
    self.matrix = XMLMatrix(None)
    self.append(movement)

  def test(self, movement):
    # Use resource rather than resource_id JPSforYO
    if movement.getResource() == self.resource and \
      movement.getVariationBaseCategoryList() == self.variation_base_category_list:
      return 1
    else:
      return 0

  def append(self, movement):
    if not movement in self.movement_list:
      self.movement_list.append(movement)
      price = movement.getTotalPrice()
      if price is not None:
        self.total_price += price # XXX Something should be done wrt to currency
      # If one order has beed negociated in USD and anotehr in EUR, then there is no
      # way to merge invoices. Multiple invoices must be produced
      # This may require serious extensions to this code
      # ie. N deliveries result in M invoices (1 invoice per currency)
      #self.total_quantity += movement.getTotalQuantity() # This is likely an error JPSforYO
      self.total_quantity += movement.getInventoriatedQuantity()
      for category in movement.getVariationCategoryList():
        if category not in self.variation_category_list:
          self.variation_category_list.append(category)

  def finish(self):
    # Make up a list of cell ranges for setCellRange.
    cell_range_list = []
    for base_category in self.variation_base_category_list:
      cell_range = []
      for movement in self.movement_list:
        for category in movement.getCategoryMembershipList(base_category, base=1):
          if not category in cell_range:
            cell_range.append(category)
      cell_range_list.append(cell_range)

    kw_list = {'base_id' : 'movement'}
    apply(self.matrix._setCellRange, cell_range_list, kw_list)

    # Add every movement into the matrix.
    for movement in self.movement_list:
      # Make sure that the order of the category lists is preserved.
      point = []
      for base_category in self.variation_base_category_list:
        point += movement.getCategoryMembershipList(base_category, base=1)
      cell = apply(self.matrix.getCell, point, kw_list)
      if cell is None:
        cell = apply(self.matrix.newCell, point, kw_list)
        cell.setMappedValuePropertyList(['price', 'quantity'])
        cell._setPrice(movement.getPrice())
        cell._setQuantity(movement.getQuantity())
      else:
        quantity = movement.getQuantity()
        if quantity:
          cell._setPrice(movement.getPrice() * quantity + cell.getPrice()) # Accumulate total price
          cell._setQuantity(quantity + cell.getQuantity())  # Accumulate quantity

    # Normalize price to compute unit price
    for cell in self.matrix.getCellValueList():
      quantity =  cell.getQuantity()
      if quantity:
        cell._setPrice(cell.getPrice() / float(quantity))
      else:
        cell._setPrice(0.0) # if quantity is zero, price is et to 0.0 as a convention
    # Normalize self price also JPSforYO
    quantity = self.total_quantity
    if quantity:
      self.price = self.total_price / float(quantity)
    else:
      self.price = 0.0
    LOG('Group', 0, repr(self.total_price), repr(self.total_quantity))

InitializeClass(Group)
#allow_class(Group)

class Delivery(XMLObject):
    """
        Each time delivery is modified, it MUST launch a reindexing of
        inventories which are related to the resources contained in the Delivery
    """
    # CMF Type Definition
    meta_type = 'ERP5 Delivery'
    portal_type = 'Delivery'
    isPortalContent = 1
    isRADContent = 1
    isDelivery = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Delivery
                      , PropertySheet.Reference
                      )

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule_id,force=0,**kw):
      """
        Reexpand applied rule
      """
      my_applied_rule = self.portal_simulation.get(applied_rule_id, None)
      LOG('Delivery.expand, force',0,force)
      LOG('Delivery.expand, my_applied_rule',0,my_applied_rule)
      LOG('Delivery.expand, my_applied_rule.expand',0,my_applied_rule.expand)
      if my_applied_rule is not None:
        my_applied_rule.expand(force=force,**kw)
        my_applied_rule.immediateReindexObject()
      else:
        LOG("ERP5 Error:", 100, "Could not expand applied rule %s for delivery %s" % (applied_rule_id, self.getId()))

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return 1

    security.declareProtected(Permissions.ModifyPortalContent, 'plan')
    def plan(self):
      """
        Sets the delivery to planned
      """
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # self.applyToDeliveryRelatedMovement(method_id = 'expand')

    plan = WorkflowMethod(plan)

    security.declareProtected(Permissions.ModifyPortalContent, 'confirm')
    def confirm(self):
      """
        Sets the order to confirmed
      """
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # self.applyToDeliveryRelatedMovement(method_id = 'expand')

    confirm = WorkflowMethod(confirm)

    security.declareProtected(Permissions.ModifyPortalContent, 'start')
    def start(self):
      """
        Starts the delivery
      """
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # self.applyToDeliveryRelatedMovement(method_id = 'expand')

    start = WorkflowMethod(start)

    security.declareProtected(Permissions.ModifyPortalContent, 'stop')
    def stop(self):
      """
        Stops the delivery
      """
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # self.applyToDeliveryRelatedMovement(method_id = 'expand')

    stop = WorkflowMethod(stop)

    security.declareProtected(Permissions.ModifyPortalContent, 'deliver')
    def deliver(self):
      """
        Deliver the delivery
      """
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # self.applyToDeliveryRelatedMovement(method_id = 'expand')

    deliver = WorkflowMethod(deliver)

    security.declareProtected(Permissions.ModifyPortalContent, 'cancel')
    def cancel(self):
      """
        Deliver the delivery
      """
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # self.applyToDeliveryRelatedMovement(method_id = 'expand')

    cancel = WorkflowMethod(cancel)

    security.declareProtected(Permissions.ModifyPortalContent, '_invoice')
    def _invoice(self):
      """
        This method is called whenever a packing list is being invoiced
      """
      # We will make sure that everything is well generated into  the
      # simulation, then we will be able to buid the invoice list.
      # we create an invoice for this delivery
      self.activate(priority=4).buildInvoiceList()

    invoice = WorkflowMethod(_invoice, 'invoice')

    security.declareProtected(Permissions.ModifyPortalContent, 'buildInvoiceList')
    def buildInvoiceList(self):
      """
        Retrieve all invoices lines into the simulation
      """
      reindexable_movement_list = []

      parent_simulation_line_list = []
      for o in self.objectValues():
        parent_simulation_line_list += [x for x in o.getDeliveryRelatedValueList() \
                                        if x.getPortalType()=='Simulation Movement']
      invoice_rule_list = []
      simulation_invoice_line_list = []
      for o in parent_simulation_line_list:
        for rule in o.objectValues():
          invoice_rule_list.append(rule)
          simulation_invoice_line_list += rule.objectValues()
      LOG('buildInvoiceList simulation_invoice_line_list',0,simulation_invoice_line_list)
      from Products.ERP5.MovementGroup import OrderMovementGroup
      from Products.ERP5.MovementGroup import PathMovementGroup
      from Products.ERP5.MovementGroup import DateMovementGroup
      from Products.ERP5.MovementGroup import ResourceMovementGroup
      from Products.ERP5.MovementGroup import VariantMovementGroup
      #class_list = [OrderMovementGroup,PathMovementGroup,DateMovementGroup,ResourceMovementGroup,VariantMovementGroup]
      class_list = [OrderMovementGroup,PathMovementGroup,DateMovementGroup,ResourceMovementGroup]
      root_group = self.portal_simulation.collectMovement(simulation_invoice_line_list,class_list=class_list)
      invoice_list = []

      LOG('buildInvoiceList root_group',0,root_group)
      if root_group is not None:
        LOG('buildInvoiceList root_group.group_list',0,root_group.group_list)
        for order_group in root_group.group_list:
          LOG('buildInvoiceList order_group.order',0,order_group.order)
          if order_group.order is not None:
            # Only build if there is not order yet
            LOG('buildInvoiceList order_group.group_list',0,order_group.group_list)
            for path_group in order_group.group_list :
              invoice_module = self.accounting
              invoice_type = 'Sale Invoice Transaction'
              invoice_line_type = 'Invoice Line'

              LOG('buildInvoiceList path_group.group_list',0,path_group.group_list)
              for date_group in path_group.group_list :

                invoice = invoice_module.newContent(portal_type = invoice_type,
                              start_date = date_group.start_date,
                              stop_date = date_group.stop_date,
                              source = path_group.source,
                              destination = path_group.destination,
                              source_section = path_group.source_section,
                              destination_section = path_group.destination_section,
                              causality_value = self,
                              title = self.getTitle(),
                              description = 'Invoice related to the Delivery %s' % self.getTitle())
                # the new invoice is added to the invoice_list
                invoice_list.append(invoice)
                #for rule in invoice_rule_list : rule.setDeliveryValue(invoice) # This looks strange. Is it okay to do this ?

                for resource_group in date_group.group_list :

                  LOG('buildInvoiceList resource_group.group_list',0,resource_group.group_list)
                  # Create a new Sale Invoice Transaction Line for each resource
                  invoice_line = invoice.newContent(
                        portal_type=invoice_line_type
                      , resource=resource_group.resource)

#                  line_variation_category_list = []
#                  line_variation_base_category_dict = {}

                  # compute line_variation_base_category_list and
                  # line_variation_category_list for new delivery_line
#                  for variant_group in resource_group.group_list :
#                    for variation_item in variant_group.category_list :
#                      if not variation_item in line_variation_category_list :
#                        line_variation_category_list.append(variation_item)
#                        variation_base_category_items = variation_item.split('/')
#                        if len(variation_base_category_items) > 0 :
#                          line_variation_base_category_dict[variation_base_category_items[0]] = 1

                  # update variation_base_category_list and line_variation_category_list for delivery_line
#                  line_variation_base_category_list = line_variation_base_category_dict.keys()
#                  invoice_line.setVariationBaseCategoryList(line_variation_base_category_list)
#                  invoice_line.setVariationCategoryList(line_variation_category_list)

                  # IMPORTANT : invoice cells are automatically created during setVariationCategoryList

                  #XXX for now, we quickly need this working, without the need of variant_group
                  object_to_update = invoice_line
                  # compute quantity and price for invoice_cell or invoice_line and
                  # build relation between simulation_movement and invoice_cell or invoice_line
                  if object_to_update is not None :
                    quantity = 0
                    total_price = 0
                    for movement in resource_group.movement_list :
                      quantity += movement.getConvertedQuantity()
                      try :
                        total_price += movement.getNetConvertedQuantity() * movement.getPrice() # XXX WARNING - ADD PRICED QUANTITY
                      except :
                        total_price = None
                      # What do we really need to update in the simulation movement ?
                      if movement.getPortalType() == 'Simulation Movement' :
                        movement._setDeliveryValue(object_to_update)
                        reindexable_movement_list.append(movement)

                    if quantity <> 0 and total_price is not None:
                      average_price = total_price/quantity
                    else :
                      average_price = 0

                    LOG('buildInvoiceList edit', 0, repr(( object_to_update, quantity, average_price, )))
                    object_to_update.edit(quantity = quantity,
                                          price = average_price)

                  # update quantity and price for each invoice_cell
                  #XXX for variant_group in resource_group.group_list :
                  if 0 :
                    LOG('Variant_group examin',0,str(variant_group.category_list))
                    object_to_update = None
                    # if there is no variation of the resource, update invoice_line with quantities and price
                    if len(variant_group.category_list) == 0 :
                      object_to_update = invoice_line
                    # else find which invoice_cell is represented by variant_group
                    else :
                      categories_identity = 0
                      #LOG('Before Check cell',0,str(invoice_cell_type))
                      #LOG('Before Check cell',0,str(invoice_line.contentValues()))
                      for invoice_cell in invoice_line.contentValues(filter={'portal_type':'Invoice Cell'}) :
                        #LOG('Check cell',0,str(invoice_cell))
                        #LOG('Check cell',0,str(variant_group.category_list))
                        if len(variant_group.category_list) == len(invoice_cell.getVariationCategoryList()) :
                          #LOG('Parse category',0,str(invoice_cell.getVariationCategoryList()))
                          for category in invoice_cell.getVariationCategoryList() :
                            if not category in variant_group.category_list :
                              #LOG('Not found category',0,str(category))
                              break
                          else :
                            categories_identity = 1

                        if categories_identity :
                          object_to_update = invoice_cell
                          break

                    # compute quantity and price for invoice_cell or invoice_line and
                    # build relation between simulation_movement and invoice_cell or invoice_line
                    if object_to_update is not None :
                      cell_quantity = 0
                      cell_total_price = 0
                      for movement in variant_group.movement_list :
                        cell_quantity += movement.getConvertedQuantity()
                        try :
                          cell_total_price += movement.getNetConvertedQuantity() * movement.getPrice() # XXX WARNING - ADD PRICED QUANTITY
                        except :
                          cell_total_price = None
                        # What do we really need to update in the simulation movement ?
                        if movement.getPortalType() == 'Simulation Movement' :
                          movement._setDeliveryValue(object_to_update)
                          reindexable_movement_list.append(movement)

                      if cell_quantity <> 0 and cell_total_price is not None:
                        average_price = cell_total_price/cell_quantity
                      else :
                        average_price = 0

                      LOG('buildInvoiceList edit', 0, repr(( object_to_update, cell_quantity, average_price, )))
                      object_to_update.edit(quantity = cell_quantity,
                                            price = average_price)
                                            
      # we now reindex the movements we modified
      for movement in reindexable_movement_list :
        movement.immediateReindexObject()
      return invoice_list


    # Pricing methods
    def _getTotalPrice(self, context):
      return 2.0

    def _getDefaultTotalPrice(self, context):
      return 3.0

    def _getSourceTotalPrice(self, context):
      return 4.0

    def _getDestinationTotalPrice(self, context):
      return 5.0

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self):
      """
      """
      result = self.z_total_price(explanation_uid = self.getUid())
      return result[0][0]

#     security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
#     def getTotalPrice(self, context=None, REQUEST=None, **kw):
#       """
#       """
#       return self._getTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultTotalPrice')
    def getDefaultTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDefaultTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getSourceTotalPrice')
    def getSourceTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getSourceTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationTotalPrice')
    def getDestinationTotalPrice(self, context=None, REQUEST=None, **kw):
      """
      """
      return self._getDestinationTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    # Pricing
    security.declareProtected( Permissions.ModifyPortalContent, 'updatePrice' )
    def updatePrice(self):
      for c in self.objectValues():
        if hasattr(aq_base(c), 'updatePrice'):
          c.updatePrice()

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
    def getTotalPrice(self,  src__=0, **kw):
      """
        Returns the total price for this order
      """
      kw['explanation_uid'] = self.getUid()
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      if src__:
        return self.Delivery_zGetTotal(src__=1, **kw)
      aggregate = self.Delivery_zGetTotal(**kw)[0]
      return aggregate.total_price or 0

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
    def getTotalQuantity(self, src__=0, **kw):
      """
        Returns the quantity if no cell or the total quantity if cells
      """      
      kw['explanation_uid'] = self.getUid()
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      if src__:
        return self.Delivery_zGetTotal(src__=1, **kw)
      aggregate = self.Delivery_zGetTotal(**kw)[0]
      return aggregate.total_quantity or 0

    security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryUid')
    def getDeliveryUid(self):
      return self.getUid()

    security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryValue')
    def getDeliveryValue(self):
      """
      Deprecated, we should use getRootDeliveryValue instead
      """
      return self

    security.declareProtected(Permissions.AccessContentsInformation, 'getRootDeliveryValue')
    def getRootDeliveryValue(self):
      """
      This method returns the delivery, it is usefull to retrieve the delivery
      from a line or a cell
      """
      return self

    security.declareProtected(Permissions.AccessContentsInformation, 'getDelivery')
    def getDelivery(self):
      return self.getRelativeUrl()

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementList')
    def getMovementList(self, portal_type=None):
      """
        Return a list of movements.
      """
      if portal_type is None:
        portal_type = self.getPortalMovementTypeList()
      movement_list = []
      for m in self.contentValues(filter={'portal_type': portal_type}):
        if m.hasCellContent():
          for c in m.contentValues(filter={'portal_type': portal_type}):
            movement_list.append(c)
        else:
          movement_list.append(m)
      return movement_list

    security.declareProtected(Permissions.AccessContentsInformation, 'getSimulatedMovementList')
    def getSimulatedMovementList(self):
      """
        Return a list of simulated movements.
        This does not contain Container Line or Container Cell.
      """
      return self.getMovementList(portal_type=self.getPortalSimulatedMovementTypeList())

    security.declareProtected(Permissions.AccessContentsInformation, 'getInvoiceMovementList')
    def getInvoiceMovementList(self):
      """
        Return a list of simulated movements.
        This does not contain Container Line or Container Cell.
      """
      return self.getMovementList(portal_type=self.getPortalInvoiceMovementTypeList())

    security.declareProtected(Permissions.AccessContentsInformation, 'getContainerList')
    def getContainerList(self):
      """
        Return a list of root containers.
        This does not contain sub-containers.
      """
      container_list = []
      for m in self.contentValues(filter={'portal_type': self.getPortalContainerTypeList()}):
        container_list.append(m)
      return container_list

    def applyToDeliveryRelatedMovement(self, portal_type='Simulation Movement', method_id = 'expand'):
      for my_simulation_movement in self.getDeliveryRelatedValueList(
                                                portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement.getObject(), method_id)()
      for m in self.contentValues(filter={'portal_type': self.getPortalMovementTypeList()}):
        # Find related in simulation
        for my_simulation_movement in m.getDeliveryRelatedValueList(
                                                portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement.getObject(), method_id)()
        for c in m.contentValues(filter={'portal_type': 'Delivery Cell'}):
          for my_simulation_movement in c.getDeliveryRelatedValueList(
                                                portal_type = 'Simulation Movement'):
            # And apply
            getattr(my_simulation_movement.getObject(), method_id)()


    #######################################################
    # Causality computation
    security.declareProtected(Permissions.View, 'isConvergent')
    def isConvergent(self):
      """
        Returns 0 if the target is not met
      """
      return not self.isDivergent()

    security.declareProtected(Permissions.View, 'isSimulated')
    def isSimulated(self):
      """
        Returns 1 if all movements have a delivery or order counterpart
        in the simulation
      """
      LOG('Delivery.isSimulated getMovementList',0,self.getMovementList())
      for m in self.getMovementList():
        LOG('Delivery.isSimulated m',0,m.getPhysicalPath())
        LOG('Delivery.isSimulated m.isSimulated',0,m.isSimulated())
        if not m.isSimulated():
          LOG('Delivery.isSimulated m.getQuantity',0,m.getQuantity())
          LOG('Delivery.isSimulated m.getSimulationQuantity',0,m.getSimulationQuantity())
          if m.getQuantity() != 0.0 or m.getSimulationQuantity() != 0:
            return 0
          # else Do we need to create a simulation movement ? XXX probably not
      return 1

    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self):
      """
        Returns 1 if the target is not met according to the current information
        After and edit, the isOutOfTarget will be checked. If it is 1,
        a message is emitted

        emit targetUnreachable !
      """
      if len(self.Delivery_zIsDivergent(uid=self.getUid())) > 0:
        return 1
      # Check if the total quantity equals the total of each simulation movement quantity
      for movement in self.getMovementList():
        d_quantity = movement.getQuantity()
        simulation_quantity = 0.
        for simulation_movement in movement.getDeliveryRelatedValueList():
          simulation_quantity += float(simulation_movement.getCorrectedQuantity())
        if d_quantity != simulation_quantity:
          return 1
      return 0

    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self, dsolver, tsolver):
      """
        Solves a delivery with a Solver
        Only delivery level matter should be modified (not movements)
      """
      dsolver.solveDelivery(self)
      tsolver.solveDelivery(self)

    #######################################################
    # Defer indexing process
    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      if self.isIndexable:
        # Reindex children
        self.activate().recursiveImmediateReindexObject()
        # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
        # Make sure expanded simulation is still OK (expand and reindex)
        # self.activate().applyToDeliveryRelatedMovement(method_id = 'expand')

    #######################################################
    # Stock Management
    def _getMovementResourceList(self):
      resource_dict = {}
      for m in self.contentValues(filter={'portal_type': self.getPortalMovementTypeList()}):
        r = m.getResource()
        if r is not None:
          resource_dict[r] = 1
      return resource_dict.keys()

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventory')
    def getInventory(self, **kw):
      """
      Returns inventory
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - deliverable)
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getAvailableInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns inventory at infinite
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryList')
    def getInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryList')
    def getCurrentInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryStat')
    def getInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryChart')
    def getInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryList')
    def getInventoryHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryHistoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryList')
    def getMovementHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getMovementHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryStat')
    def getMovementHistoryStat(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['category'] = self._getMovementResourceList()
      return self.portal_simulation.getMovementHistoryStat(**kw)


    security.declareProtected(Permissions.AccessContentsInformation, 'collectMovement')
    def collectMovement(self, movement_list):
      """
        Collect all movements into a list of group objects.
      """
      from Globals import InitializeClass

      # Collect each delivery cell into a delivery line.
      group_list = []
      for movement in movement_list:
        movement_in_group = 0
        for group in group_list:
          if group.test(movement):
            group.append(movement)
            movement_in_group = 1
            break
        if not movement_in_group:
          group_list.append(Group(movement).__of__(self))

      # This is required to build a matrix.
      for group in group_list:
        group.finish()

      return group_list

    # XXX this should be moved to Invoice
    security.declareProtected(Permissions.AccessContentsInformation, 'buildInvoiceLineList')
    def buildInvoiceLineList(self, movement_group):
      """
        Build invoice lines from a list of movements.
      """
      invoice_line_list = []

      if movement_group is not None:
        for group in movement_group:
          # Create each invoice_line in the new invoice
          # but only if quantity > 0
          if group.total_quantity > 0 :
            invoice_line = self.newContent(portal_type = 'Invoice Line',
                                          resource = group.resource,
                                          quantity_unit = group.quantity_unit) # FIXME: more args
            invoice_line_list.append(invoice_line)

            # Make sure that the order is always preserved.
            variation_base_category_list = list(group.variation_base_category_list)
            variation_base_category_list.sort()
            invoice_line.setVariationBaseCategoryList(variation_base_category_list)
            #LOG('buildInvoiceLineList', 0, "group.variation_base_category_list = %s" % str(group.variation_base_category_list))
            variation_category_list = []
            for cell_key in group.matrix.getCellKeyList(base_id='movement'):
              for variation_category in cell_key:
                if variation_category not in variation_category_list:
                  variation_category_list.append(variation_category)
            invoice_line.setVariationCategoryList(variation_category_list)
            # IMPORTANT : delivery cells are automatically created during setVariationCategoryList

            #LOG('buildInvoiceLineList', 0, "invoice_line.contentValues() = %s" % str(invoice_line.contentValues()))
            if len(variation_category_list) > 0:
              for invoice_cell in invoice_line.contentValues(filter={'portal_type':'Invoice Cell'}):
                category_list = invoice_cell.getVariationCategoryList()
                # XXX getVariationCategoryList does not return the same order as setVariationBaseCategoryList
                point = []
                for base_category in group.variation_base_category_list:
                  for category in category_list:
                    if category.startswith(base_category + '/'):
                      point.append(category)
                      break
                kw_list = {'base_id' : 'movement'}
                cell = apply(group.matrix.getCell, point, kw_list)
                #LOG('buildInvoiceLineList', 0,
                #    "point = %s, cell = %s" % (str(point), str(cell)))
                if cell is not None:
                  #LOG('buildInvoiceLineList', 0,
                  #    "quentity = %s, price = %s" % (str(cell.getQuantity()), str(cell.getPrice())))
                  invoice_cell.edit(quantity = cell.getQuantity(),
                                    price = cell.getPrice(),
                                    force_update = 1)
            else:
              # There is no variation category.
              invoice_line.edit(quantity = group.total_quantity,
                                price = group.price,
                                force_update = 1) # Use unit price JPSforYO

      return invoice_line_list

    # Simulation consistency propagation
    security.declareProtected(Permissions.ModifyPortalContent, 'updateFromSimulation')
    def updateFromSimulation(self, update_target = 0):
      """
      Update all lines of this transaction based on movements in the simulation
      related to this transaction.
      """
      # XXX update_target no more used
      transaction_type = self.getPortalType()
      line_type = transaction_type + " Line"
      to_aggregate_movement_list = []
      to_reindex_list = []
      source_section = self.getSourceSection()
      destination_section = self.getDestinationSection()
      resource = self.getResource()
      start_date = self.getStartDate()
      
      def updateLineOrCell(c):
        quantity = 0
        source = c.getSource()
        destination = c.getDestination()
        for m in c.getDeliveryRelatedValueList():
          m_source_section = m.getSourceSection()
          m_destination_section = m.getDestinationSection()
          m_resource = m.getResource()
          m_start_date = m.getStartDate()
          m_source = m.getSource()
          m_destination = m.getDestination()
          m_quantity = m.getCorrectedQuantity()
          if m_source_section == source_section and m_destination_section == destination_section \
              and m_resource == resource and m_start_date == start_date:
            if m_source == source and m_destination == destination:
              # The path is the same, only the quantity may have changed
              if m_quantity:
                quantity += m_quantity
            else:
              # Source and/or destination have changed. The Simulation Movement has
              # to be linked to a new TransactionLine
              m.setDelivery('')
              to_aggregate_movement_list.append(m)
            to_reindex_list.append(m)
          else:
            # Source_section and/or destination_section and/or date and/or resource differ
            # The Simulation Movement has to be linked to a new Transaction (or an existing one)
            m.setDelivery('')
            to_aggregate_movement_list.append(m)
            to_reindex_list.append(m)
        # Recalculate delivery ratios for the remaining movements in this line
        c.setQuantity(quantity)
        c.updateSimulationDeliveryProperties()
      
      # Update the transaction from simulation
      for l in self.contentValues(filter={'portal_type':self.getPortalDeliveryMovementTypeList()}):
        if l.hasCellContent():
          for c in l.contentValues(filter={'portal_type':self.getPortalDeliveryMovementTypeList()}):
            updateLineOrCell(c)
        else:
          updateLineOrCell(l)
          
      # Re-aggregate the disconnected movements
      # XXX Dirty ; it should use DeliveryBuilder when it will be available
      if len(to_aggregate_movement_list) > 0:
        applied_rule_type = to_aggregate_movement_list[0].getRootAppliedRule().getSpecialiseId()
        if applied_rule_type == "default_amortisation_rule":
          self.portal_simulation.buildDeliveryList( self.portal_simulation.collectMovement(to_aggregate_movement_list,
                                                        [ResourceMovementGroup, DateMovementGroup, PathMovementGroup] ) )
        
      # Touch the Transaction to make an automatic converge
      self.edit() 

    security.declareProtected(Permissions.ModifyPortalContent, 'propagateResourceToSimulation')
    def propagateResourceToSimulation(self):
      """
        Propagates any changes on resources or variations to the simulation
        by disconnecting simulation movements refering to another resource/variation,
        creating DeliveryRules for new resources and setting target_quantity to 0 for resources
        which are no longer delivered

        propagateResourceToSimulation has priority (ie. must be executed before) over updateFromSimulation
      """
      if self.getPortalType() == 'Amortisation Transaction':
        return
      unmatched_simulation_movement = []
      unmatched_delivery_movement = []
      LOG('propagateResourceToSimulation, ',0,'starting')
      for l in self.contentValues(filter={'portal_type':self.getPortalDeliveryMovementTypeList()}):
        LOG('propagateResourceToSimulation, l.getPhysicalPath()',0,l.getPhysicalPath())
        LOG('propagateResourceToSimulation, l.objectValues()',0,l.objectValues())
        LOG('propagateResourceToSimulation, l.hasCellContent()',0,l.hasCellContent())
        LOG('propagateResourceToSimulation, l.showDict()',0,l.showDict())
        if l.hasCellContent():
          for c in l.contentValues(filter={'portal_type':self.getPortalDeliveryMovementTypeList()}):
            LOG('propagateResourceToSimulation, c.getPhysicalPath()',0,c.getPhysicalPath())
            for s in c.getDeliveryRelatedValueList():
              LOG('propagateResourceToSimulation, s.getPhysicalPath()',0,s.getPhysicalPath())
              LOG('propagateResourceToSimulation, c.getResource()',0,c.getResource())
              LOG('propagateResourceToSimulation, s.getResource()',0,s.getResource())
              if s.getResource() != c.getResource() or s.getVariationText() != c.getVariationText(): # We should use here some day getVariationValue and __cmp__
                unmatched_delivery_movement.append(c)
                unmatched_simulation_movement.append(s)
                s.setDelivery(None) # Disconnect
                l._setQuantity(0.0)
        else:
          for s in l.getDeliveryRelatedValueList():
            if s.getResource() != l.getResource() or s.getVariationText() != l.getVariationText():
              unmatched_delivery_movement.append(l)
              unmatched_simulation_movement.append(s)
              s.setDelivery(None) # Disconnect
              l._setQuantity(0.0)
      LOG('propagateResourceToSimulation, unmatched_simulation_movement',0,unmatched_simulation_movement)
      # Build delivery list with unmatched_simulation_movement
      root_group = self.portal_simulation.collectMovement(unmatched_simulation_movement)
      new_delivery_list = self.portal_simulation.buildDeliveryList(root_group)
      simulation_state = self.getSimulationState()
      if simulation_state == 'confirmed':
        for new_delivery in new_delivery_list:
          new_delivery.confirm()

      LOG('propagateResourceToSimulation, new_delivery_list',0,new_delivery_list)
      # And merge into us
      if len(new_delivery_list)>0:
        list_to_merge = [self]
        list_to_merge.extend(new_delivery_list)
        LOG('propagateResourceToSimulation, list_to_merge:',0,list_to_merge)
        self.portal_simulation.mergeDeliveryList(list_to_merge)

    security.declareProtected(Permissions.ModifyPortalContent, 'propagateArrowToSimulation')
    def propagateArrowToSimulation(self):
      """
        Propagates any changes on arrow to the simulation 
        
        propagateArrowToSimulation has priority (ie. must be executed before) over updateFromSimulation        
      """
      LOG('propagateArrowToSimulation, ',0,'starting')
      for l in self.contentValues(filter={'portal_type':delivery_movement_type_list}):
        LOG('propagateArrowToSimulation, l.getPhysicalPath()',0,l.getPhysicalPath())
        LOG('propagateArrowToSimulation, l.objectValues()',0,l.objectValues())
        LOG('propagateArrowToSimulation, l.hasCellContent()',0,l.hasCellContent())
        LOG('propagateArrowToSimulation, l.showDict()',0,l.showDict())
        if l.hasCellContent():
          for c in l.contentValues(filter={'portal_type':delivery_movement_type_list}):
            LOG('propagateArrowToSimulation, c.getPhysicalPath()',0,c.getPhysicalPath())
            for s in c.getDeliveryRelatedValueList():
              LOG('propagateArrowToSimulation, s.getPhysicalPath()',0,s.getPhysicalPath())
              LOG('propagateArrowToSimulation, c.getDestination()',0,c.getDestination())
              LOG('propagateArrowToSimulation, s.getDestination()',0,s.getDestination())
              if c.getTargetSource() != s.getSource() \
                or c.getTargetDestination() != s.getDestination() \
                or c.getTargetSourceSection() != s.getSourceSection() \
                or c.getTargetDestinationSection() != s.getDestinationSection():
                  s.setSource(c.getTargetSource())
                  s.setDestination(c.getTargetDestination())
                  s.setSourceSection(c.getTargetSourceSection())
                  s.setDestinationSection(c.getTargetDestinationSection())
                  s.activate().expand()
        else:
          for s in l.getDeliveryRelatedValueList():
            if l.getTargetSource() != s.getSource() \
              or l.getTargetDestination() != s.getDestination() \
              or l.getTargetSourceSection() != s.getSourceSection() \
              or l.getTargetDestinationSection() != s.getDestinationSection():
                s.setSource(l.getTargetSource())
                s.setDestination(l.getTargetDestination())
                s.setSourceSection(l.getTargetSourceSection())
                s.setDestinationSection(l.getTargetDestinationSection())
                s.activate().expand()

    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, **kw):
      """
      call propagateArrowToSimulation
      """
      XMLObject._edit(self,REQUEST=REQUEST,force_update=force_update,**kw)
      #self.propagateArrowToSimulation()
      # We must expand our applied rule only if not confirmed
      #if self.getSimulationState() in planned_order_state:
      #  self.updateAppliedRule() # This should be implemented with the interaction tool rather than with this hard coding

    security.declareProtected(Permissions.ModifyPortalContent, 'notifySimulationChange')
    def notifySimulationChange(self):
      """
        WorkflowMethod used to notify the causality workflow that the simulation
        has changed, so we have to check if the delivery is divergent or not
      """
      pass
    notifySimulationChange = WorkflowMethod(notifySimulationChange)

    def updateSimulationDeliveryProperties(self, movement_list = None, delivery = None):
      """
      Set properties delivery_ratio and delivery_error for each simulation movement
      in movement_list (all movements by default), according to this delivery calculated quantity
      """
      if movement_list is None:
        movement_list = delivery.getDeliveryRelatedValueList()
      # First find the calculated quantity
      delivery_quantity = 0
      for m in delivery.getDeliveryRelatedValueList():
        m_quantity = m.getCorrectedQuantity()
        if m_quantity is not None:
          delivery_quantity += m_quantity
      # Then set the properties
      if delivery_quantity != 0:
        for m in movement_list:
          m.setDeliveryRatio(m.getCorrectedQuantity() / delivery_quantity)
          m.setDeliveryError(delivery_quantity * m.getDeliveryRatio() - m.getCorrectedQuantity())
      else:
        for m in movement_list:
          m.setDeliveryError(m.getCorrectedQuantity())
          m.setProfitQuantity(m.getQuantity())
      # Finally, reindex the movements to update their divergence property
      for m in delivery.getDeliveryRelatedValueList():
        m.immediateReindexObject()
