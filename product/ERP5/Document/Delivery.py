##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Type.Base import Base
from Products.ERP5.Document.DeliveryCell import DeliveryCell
from Acquisition import Explicit, Implicit
from Products.PythonScripts.Utility import allow_class
from DateTime import DateTime

from zLOG import LOG

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

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return 1

    # Pricing methods
    def _getTotalPrice(self, context):
      return 2.0

    def _getDefaultTotalPrice(self, context):
      return 3.0

    def _getSourceTotalPrice(self, context):
      return 4.0

    def _getDestinationTotalPrice(self, context):
      return 5.0

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

    security.declareProtected(Permissions.AccessContentsInformation,
                             'getMovementList')
    def getMovementList(self, portal_type=None, **kw):
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
      return int(not self.isDivergent())

    security.declareProtected(Permissions.View, 'isSimulated')
    def isSimulated(self):
      """
        Returns 1 if all movements have a delivery or order counterpart
        in the simulation
      """
      #LOG('Delivery.isSimulated getMovementList',0,self.getMovementList())
      for m in self.getMovementList():
        #LOG('Delivery.isSimulated m',0,m.getPhysicalPath())
        #LOG('Delivery.isSimulated m.isSimulated',0,m.isSimulated())
        if not m.isSimulated():
          #LOG('Delivery.isSimulated m.getQuantity',0,m.getQuantity())
          #LOG('Delivery.isSimulated m.getSimulationQuantity',0,m.getSimulationQuantity())
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

    #######################################################
    # Defer indexing process
    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      self.recursiveReindexObject()
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

# XXX FIXME: to be deleted
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
      #LOG('propagateResourceToSimulation, ',0,'starting')
      for l in self.contentValues(filter={'portal_type':self.getPortalDeliveryMovementTypeList()}):
        #LOG('propagateResourceToSimulation, l.getPhysicalPath()',0,l.getPhysicalPath())
        #LOG('propagateResourceToSimulation, l.objectValues()',0,l.objectValues())
        #LOG('propagateResourceToSimulation, l.hasCellContent()',0,l.hasCellContent())
        #LOG('propagateResourceToSimulation, l.showDict()',0,l.showDict())
        if l.hasCellContent():
          for c in l.contentValues(filter={'portal_type':self.getPortalDeliveryMovementTypeList()}):
            #LOG('propagateResourceToSimulation, c.getPhysicalPath()',0,c.getPhysicalPath())
            for s in c.getDeliveryRelatedValueList():
              #LOG('propagateResourceToSimulation, s.getPhysicalPath()',0,s.getPhysicalPath())
              #LOG('propagateResourceToSimulation, c.getResource()',0,c.getResource())
              #LOG('propagateResourceToSimulation, s.getResource()',0,s.getResource())
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

      #LOG('propagateResourceToSimulation, new_delivery_list',0,new_delivery_list)
      # And merge into us
      if len(new_delivery_list)>0:
        list_to_merge = [self]
        list_to_merge.extend(new_delivery_list)
        #LOG('propagateResourceToSimulation, list_to_merge:',0,list_to_merge)
        self.portal_simulation.mergeDeliveryList(list_to_merge)

# XXX FIXME: to be deleted
    security.declareProtected(Permissions.ModifyPortalContent, 'propagateArrowToSimulation')
    def propagateArrowToSimulation(self):
      """
        Propagates any changes on arrow to the simulation

        propagateArrowToSimulation has priority (ie. must be executed before) over updateFromSimulation
      """
      #LOG('propagateArrowToSimulation, ',0,'starting')
      for l in self.contentValues(filter={'portal_type':delivery_movement_type_list}):
        #LOG('propagateArrowToSimulation, l.getPhysicalPath()',0,l.getPhysicalPath())
        #LOG('propagateArrowToSimulation, l.objectValues()',0,l.objectValues())
        #LOG('propagateArrowToSimulation, l.hasCellContent()',0,l.hasCellContent())
        #LOG('propagateArrowToSimulation, l.showDict()',0,l.showDict())
        if l.hasCellContent():
          for c in l.contentValues(filter={'portal_type':delivery_movement_type_list}):
            #LOG('propagateArrowToSimulation, c.getPhysicalPath()',0,c.getPhysicalPath())
            for s in c.getDeliveryRelatedValueList():
              #LOG('propagateArrowToSimulation, s.getPhysicalPath()',0,s.getPhysicalPath())
              #LOG('propagateArrowToSimulation, c.getDestination()',0,c.getDestination())
              #LOG('propagateArrowToSimulation, s.getDestination()',0,s.getDestination())
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

# XXX FIXME: to be deleted
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

    ##########################################################################
    # Applied Rule stuff
    def updateAppliedRule(self, rule_id):
      """
        Create a new Applied Rule is none is related, or call expand
        on the existing one.
      """
      if (rule_id is not None) and\
         (self.getSimulationState() not in \
                                       self.getPortalDraftOrderStateList()):
        # Nothing to do if we are already simulated
        self._createAppliedRule(rule_id)

    def _createAppliedRule(self, rule_id):
      """
        Create a new Applied Rule is none is related, or call expand
        on the existing one.
      """
      # Return if draft or cancelled simulation_state
      if self.getSimulationState() in ('cancelled',):
        # The applied rule should be cleaned up 
        # ie. empty all movements which have no confirmed children
        return
      # Otherwise, expand
      # Look up if existing applied rule
      my_applied_rule_list = self.getCausalityRelatedValueList(\
                                            portal_type='Applied Rule')
      if len(my_applied_rule_list) == 0:
        if self.isSimulated(): 
          # No need to create a DeliveryRule 
          # if we are already in the simulation process
          return 
        # Create a new applied order rule (portal_rules.order_rule)
        portal_rules = getToolByName(self, 'portal_rules')
        portal_simulation = getToolByName(self, 'portal_simulation')
        my_applied_rule = portal_rules[rule_id].\
                                    constructNewAppliedRule(portal_simulation)
        # Set causality
        my_applied_rule.setCausalityValue(self)
        # We must make sure this rule is indexed
        # now in order not to create another one later
        my_applied_rule.immediateReindexObject()
      elif len(my_applied_rule_list) == 1:
        # Re expand the rule if possible
        my_applied_rule = my_applied_rule_list[0]
      else:
        raise "SimulationError", 'Delivery %s has more than one applied\
                                rule.' % self.getRelativeUrl()

      # We are now certain we have a single applied rule
      # It is time to expand it
      self.activate().expand(my_applied_rule.getId())

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule_id, force=0,**kw):
      """
        Reexpand applied rule
      """
      my_applied_rule = self.portal_simulation.get(applied_rule_id, None)
      if my_applied_rule is not None:
        my_applied_rule.expand(force=force,**kw)
        # XXX Why reindexing the applied rule ?
        my_applied_rule.immediateReindexObject()
      else:
        LOG("ERP5 Error:", 100, 
            "Could not expand applied rule %s for delivery %s" %\
                (applied_rule_id, self.getId()))
