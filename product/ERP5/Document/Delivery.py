##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from Products.ERP5.ERP5Globals import movement_type_list, default_section_category, current_inventory_state_list
from Products.ERP5Type.XMLMatrix import TempXMLMatrix
from Products.ERP5.Document.DeliveryCell import DeliveryCell
from Acquisition import Explicit, Implicit
from Products.PythonScripts.Utility import allow_class

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

  def newCellContent(self, id):
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
    return self.variation_base_category_list

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
    self.quantity_unit = movement.getQuantityUnit()
    self.resource = movement.getResource()
    self.resource_id = movement.getResourceId()
    self.resource_title = movement.getResourceTitle()
    self.variation_base_category_list = movement.getVariationBaseCategoryList()
    self.total_price = movement.getTotalPrice()
    self.total_quantity = movement.getTotalQuantity()
    self.matrix = XMLMatrix(None)
    self.append(movement)

  def test(self, movement):
    if movement.getResourceId() == self.resource_id and \
      movement.getVariationBaseCategoryList() == self.variation_base_category_list:
      return 1
    else:
      return 0

  def append(self, movement):
    if not movement in self.movement_list:
      self.movement_list.append(movement)

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

InitializeClass(Group)
#allow_class(Group)

class Delivery(XMLObject):
    # CMF Type Definition
    meta_type = 'ERP5 Delivery'
    portal_type = 'Delivery'
    isPortalContent = 1
    isRADContent = 1

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

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
une liste de mouvements..."""
         , 'icon'           : 'delivery_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDelivery'
         , 'immediate_view' : 'delivery_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Movement',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'delivery_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'delivery_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }


#     security.declareProtected(Permissions.AccessContentsInformation, 'getCausalitySate')
#     def getCausalityState(self, id_only=1):
#       """
#         Returns the current state in causality
#       """
#       portal_workflow = getToolByName(self, 'portal_workflow')
#       wf = portal_workflow.getWorkflowById('causality_workflow')
#       return wf._getWorkflowStateOf(self, id_only=id_only)

    security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationSate')
    def getSimulationState(self, id_only=1):
      """
        Returns the current state in simulation
      """
      portal_workflow = getToolByName(self, 'portal_workflow')
      wf = portal_workflow.getWorkflowById('delivery_workflow')
      return wf._getWorkflowStateOf(self, id_only=id_only )

    def expand(self, applied_rule_id):
      """
        Reexpand applied rule
      """
      my_applied_rule = self.portal_simulation.get(applied_rule_id, None)
      if my_applied_rule is not None:
        my_applied_rule.expand()
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

    security.declareProtected(Permissions.ModifyPortalContent, 'invoice')
    def invoice(self):
      """
        This method is called whenever a packing list is being invoiced
      """

    invoice = WorkflowMethod(invoice)

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
      result = self.z_total_price(delivery_uid = self.getUid())
      return result[0][0]

    security.declareProtected(Permissions.AccessContentsInformation, 'getTargetTotalPrice')
    def getTargetTotalPrice(self):
      """
      """
      result = self.z_total_price(delivery_uid = self.getUid())
      return result[0][1]

#     security.declareProtected(Permissions.AccessContentsInformation, 'getTotalPrice')
#     def getTotalPrice(self, context=None, REQUEST=None, **kw):
#       """
#       """
#       return self._getTotalPrice(self.asContext(context=context, REQUEST=REQUEST, **kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'getDefaultTotalprice')
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
    def getTotalPrice(self):
      """
        Returns the total price for this order
      """
      aggregate = self.Delivery_zGetTotal()[0]
      return aggregate.total_price

    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
    def getTotalQuantity(self):
      """
        Returns the quantity if no cell or the total quantity if cells
      """
      aggregate = self.Delivery_zGetTotal()[0]
      return aggregate.total_quantity

    security.declareProtected(Permissions.AccessContentsInformation, 'getTargetTotalQuantity')
    def getTargetTotalQuantity(self):
      """
        Returns the quantity if no cell or the total quantity if cells
      """
      aggregate = self.Delivery_zGetTotal()[0]
      return aggregate.target_total_quantity

    security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryUid')
    def getDeliveryUid(self):
      return self.getUid()

    security.declareProtected(Permissions.AccessContentsInformation, 'getDeliveryValue')
    def getDeliveryValue(self):
      return self

    security.declareProtected(Permissions.AccessContentsInformation, 'getDelivery')
    def getDelivery(self):
      return self.getRelativeUrl()

    def getMovementList(self):
      movement_list = []
      for m in self.contentValues(filter={'portal_type': movement_type_list}):
        if m.hasCellContent():
          for c in m.contentValues(filter={'portal_type': movement_type_list}):
            movement_list.append(c)
        else:
          movement_list.append(m)
      return movement_list

    def applyToDeliveryRelatedMovement(self, portal_type='Simulation Movement', method_id = 'expand'):
      for my_simulation_movement in self.getDeliveryRelatedValueList(
                                                portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement.getObject(), method_id)()
      for m in self.contentValues(filter={'portal_type': movement_type_list}):
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

    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self):
      """
        Returns 1 if the target is not met according to the current information
        After and edit, the isOutOfTarget will be checked. If it is 1,
        a message is emitted

        emit targetUnreachable !
      """
      from DateTime import DateTime
      # This is uggly but required due to python2.2/2.3 Zope 2.6/2.7 inconsistency in _millis calculation
      if self.getStartDate().Date() != self.getTargetStartDate().Date()  or \
         self.getStopDate().Date() != self.getTargetStopDate().Date():
        LOG("isDivergent getStartDate", 0, repr(self.getStartDate()))
        LOG("isDivergent getTargetStartDate", 0, repr(self.getTargetStartDate()))
        LOG("isDivergent getStopDate", 0, repr(self.getStopDate()))
        LOG("isDivergent getTargetStopDate", 0, repr(self.getTargetStopDate()))

        LOG("isDivergent getStartDate", 0, repr(self.getStartDate()))
        LOG("isDivergent getTargetStartDate", 0, repr(self.getTargetStartDate()))
        LOG("isDivergent getStopDate", 0, repr(self.getStopDate()))
        LOG("isDivergent getTargetStopDate", 0, repr(self.getTargetStopDate()))
        LOG("isDivergent getStartDate", 0, repr(self.getStartDate()._millis))
        LOG("isDivergent getTargetStartDate", 0, repr(self.getTargetStartDate()._millis))
        LOG("isDivergent getStopDate", 0, repr(self.getStopDate()._millis))
        LOG("isDivergent getTargetStopDate", 0, repr(self.getTargetStopDate()._millis))
        LOG("isDivergent class getStartDate", 0, repr(self.getStartDate().__class__))
        LOG("isDivergent class getTargetStartDate", 0, repr(self.getTargetStartDate().__class__))
        LOG("isDivergent class getStopDate", 0, repr(self.getStopDate().__class__))
        LOG("isDivergent class getTargetStopDate", 0, repr(self.getTargetStopDate().__class__))
        LOG("isDivergent", 0, repr(type(self.getStartDate())))
        LOG("isDivergent", 0, repr(type(self.getTargetStartDate())))
        LOG("isDivergent ==", 0, str(self.getStartDate() == self.getTargetStartDate()))
        LOG("isDivergent !=", 0, str(self.getStartDate() != self.getTargetStartDate()))
        LOG("isDivergent", 0, str(self.getStopDate() != self.getTargetStopDate()))
        return 1

      for line in self.contentValues(filter={'portal_type': movement_type_list}):
        if line.isDivergent():
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
      for m in self.contentValues(filter={'portal_type': movement_type_list}):
        r = m.getResource()
        if r is not None:
          resource_dict[r] = 1
      return resource_dict.keys()

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventory')
    def getInventory(self, at_date = None, section = None, node = None,
            node_category=None, section_category=default_section_category, simulation_state=None,
            ignore_variation=0, **kw):
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      resource_dict = {}
      for m in self.contentValues(filter={'portal_type': movement_type_list}):
        resource_dict[m.getResource()] = 1
      result = self.Resource_zGetInventory(  resource = self._getMovementResourceList(),
                                             to_date=at_date,
                                             section=section, node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state=simulation_state)
      if len(result) > 0:
        return result[0].inventory
      return 0.0

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventory')
    def getFutureInventory(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns inventory at infinite
      """
      return self.getInventory(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventory')
    def getCurrentInventory(self, section = None, node = None,
             node_category=None, section_category=default_section_category, ignore_variation=0, **kw):
      """
        Returns current inventory
      """
      return self.getInventory(section=section, node=node,
                  node_category=node_category, section_category=section_category,
                  simulation_state=current_inventory_state_list, **kw)
      #return self.getInventory(section=section, node=node,
      #            node_category=node_category, section_category=section_category,
      #            simulation_state='delivered', **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableInventory')
    def getAvailableInventory(self, section = None, node = None,
               node_category=None, section_category=default_section_category,
               ignore_variation=0, **kw):
      """
        Returns available inventory, ie. current inventory - deliverable
      """
      return self.getInventory(at_date=DateTime(), section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryList')
    def getInventoryList(self, at_date = None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      resource_dict = {}
      for m in self.contentValues(filter={'portal_type': movement_type_list}):
        resource_dict[m.getResource()] = 1
      result = self.Resource_zGetInventoryList(resource = resource_dict.keys(),
                                               to_date=at_date,
                                               section=section, node=node,
                                               node_category=node_category,
                                               section_category=section_category, **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryList')
    def getFutureInventoryList(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      return self.getInventoryList(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryList')
    def getCurrentInventoryList(self, section = None, node = None,
                            node_category=None, section_category=default_section_category,
                            ignore_variation=0, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      return self.getInventoryList(simulation_state=current_inventory_state_list, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)
      #return self.getInventoryList(at_date=DateTime(), section=section, node=node,
      #                       node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryStat')
    def getInventoryStat(self, at_date = None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns statistics of inventory list grouped by section or site
      """
      resource_dict = {}
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      for m in self.contentValues(filter={'portal_type': movement_type_list}):
        resource_dict[m.getResource()] = 1
      result = self.Resource_zGetInventory(resource = resource_dict.keys(),
                                             to_date=at_date,
                                             section=section, node=node,
                                             node_category=node_category,
                                             section_category=section_category, **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryStat')
    def getFutureInventoryStat(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns statistics of future inventory list grouped by section or site
      """
      return self.getInventoryStat(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, section = None, node = None,
                            node_category=None, section_category=default_section_category,
                            ignore_variation=0, **kw):
      """
        Returns statistics of current inventory list grouped by section or site
      """
      return self.getInventoryStat(simulation_state='delivered', section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)
      #return self.getInventoryStat(at_date=DateTime(), section=section, node=node,
      #                       node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryChart')
    def getInventoryChart(self, at_date = None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      if type(simulation_state) is type('a'):
        simulation_state = [simulation_state]
      result = self.getInventoryList(at_date=at_date, section=section, node=node,
                       node_category=node_category, section_category=section_category,
                       simulation_state=simulation_state, ignore_variation=ignore_variation, **kw)
      return map(lambda r: (r.node_title, r.inventory), result)

    security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryChart')
    def getFutureInventoryChart(self, section = None, node = None,
             node_category=None, section_category=default_section_category, simulation_state=None,
             ignore_variation=0, **kw):
      """
        Returns list of future inventory grouped by section or site
      """
      return self.getInventoryChart(at_date=None, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)

    security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, section = None, node = None,
                            node_category=None, section_category=default_section_category,
                            ignore_variation=0, **kw):
      """
        Returns list of current inventory grouped by section or site
      """
      return self.getInventoryChart(simulation_state=current_inventory_state_list, section=section, node=node,
                             node_category=node_category, section_category=section_category, **kw)
      # return self.getInventoryChart(at_date=DateTime(), section=section, node=node,
      #                       node_category=node_category, section_category=section_category, **kw)


    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryList')
    def getMovementHistoryList(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      result = self.Resource_zGetMovementHistoryList(resource = self._getMovementResourceList(),
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category, **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getMovementHistoryStat')
    def getMovementHistoryStat(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      result = self.Resource_zGetInventory(resource = self._getMovementResourceList(),
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category, **kw)
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryList')
    def getInventoryHistoryList(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      # Get Movement List
      result = self.Resource_getInventoryHistoryList(  resource = self._getMovementResourceList(),
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state = simulation_state,
                                              **kw)
      return result


    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, from_date = None, to_date=None, section = None, node = None,
              node_category=None, section_category=default_section_category, simulation_state=None,
              ignore_variation=0, **kw):
      """
        Returns list of inventory grouped by section or site
      """
      # Get Movement List
      result = self.Resource_getInventoryHistoryChart(  resource = self._getMovementResourceList(),
                                             from_date=from_date,
                                             to_date=to_date,
                                             section=section,
                                             node=node,
                                             node_category=node_category,
                                             section_category=section_category,
                                             simulation_state = simulation_state,
                                              **kw)
      return result

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
          # Create each invoice_line in the new invoice.
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
                                price = cell.getPrice(),)

      return invoice_line_list
