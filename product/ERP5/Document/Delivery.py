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

from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Base import WorkflowMethod
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Movement import Movement
from Products.ERP5.Document.ImmobilisationDelivery import ImmobilisationDelivery

from zLOG import LOG
from zLOG import PROBLEM

class Delivery(XMLObject, ImmobilisationDelivery):
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
    security.declareObjectProtected(Permissions.AccessContentsInformation)

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
                      , PropertySheet.Price
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

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getTotalPrice')
    def getTotalPrice(self, fast=1, src__=0, **kw):
      """ Returns the total price for this order
        if the `fast` argument is set to a true value, then it use
        SQLCatalog to compute the price, otherwise it sums the total
        price of objects one by one.

        So if the order is not in the catalog, getTotalPrice(fast=1)
        will return 0, this is not a bug.
      """
      if not fast :
        kw.setdefault( 'portal_type',
                       self.getPortalDeliveryMovementTypeList())
        return sum([ line.getTotalPrice(fast=0) for line in
                        self.objectValues(**kw) ])
      kw['explanation_uid'] = self.getUid()
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      if src__:
        return self.Delivery_zGetTotal(src__=1, **kw)
      aggregate = self.Delivery_zGetTotal(**kw)[0]
      return aggregate.total_price or 0

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getTotalQuantity')
    def getTotalQuantity(self, fast=1, src__=0, **kw):
      """ Returns the total quantity of this order.
        if the `fast` argument is set to a true value, then it use
        SQLCatalog to compute the quantity, otherwise it sums the total
        quantity of objects one by one.

        So if the order is not in the catalog, getTotalQuantity(fast=1)
        will return 0, this is not a bug.
      """
      if not fast :
        kw.setdefault('portal_type',
                      self.getPortalDeliveryMovementTypeList())
        return sum([ line.getTotalQuantity(fast=0) for line in
                        self.objectValues(**kw) ])
      kw['explanation_uid'] = self.getUid()
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      if src__:
        return self.Delivery_zGetTotal(src__=1, **kw)
      aggregate = self.Delivery_zGetTotal(**kw)[0]
      return aggregate.total_quantity or 0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDeliveryUid')
    def getDeliveryUid(self):
      return self.getUid()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDeliveryValue')
    def getDeliveryValue(self):
      """
      Deprecated, we should use getRootDeliveryValue instead
      """
      return self

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getRootDeliveryValue')
    def getRootDeliveryValue(self):
      """
      This method returns the delivery, it is usefull to retrieve the delivery
      from a line or a cell
      """
      return self

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDelivery')
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
      add_movement = movement_list.append
      extend_movement = movement_list.extend
      sub_object_list = self.contentValues(filter={'portal_type': portal_type})
      extend_sub_object = sub_object_list.extend
      append_sub_object = sub_object_list.append
      while sub_object_list:
        sub_object = sub_object_list.pop()
        content_list = sub_object.contentValues(
                          filter={'portal_type': portal_type})
        if sub_object.hasCellContent():
          cell_list = sub_object.getCellValueList()
          if len(cell_list) != len(content_list):
            for x in content_list:
              if x not in cell_list:
                append_sub_object(x)
          else:
            extend_movement(content_list)
        elif content_list:
          extend_sub_object(content_list)
        else:
          add_movement(sub_object)
      return movement_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getSimulatedMovementList')
    def getSimulatedMovementList(self):
      """
        Return a list of simulated movements.
        This does not contain Container Line or Container Cell.
      """
      return self.getMovementList(portal_type=
                          self.getPortalSimulatedMovementTypeList())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInvoiceMovementList')
    def getInvoiceMovementList(self):
      """
        Return a list of simulated movements.
        This does not contain Container Line or Container Cell.
      """
      return self.getMovementList(portal_type=
                            self.getPortalInvoiceMovementTypeList())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainerList')
    def getContainerList(self):
      """
        Return a list of root containers.
        This does not contain sub-containers.
      """
      container_list = []
      for m in self.contentValues(filter={'portal_type':
                                  self.getPortalContainerTypeList()}):
        container_list.append(m)
      return container_list

    def applyToDeliveryRelatedMovement(self, portal_type='Simulation Movement',
        method_id = 'expand',**kw):
      for my_simulation_movement in self.getDeliveryRelatedValueList(
                                      portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement.getObject(), method_id)(**kw)
      for m in self.contentValues(filter={'portal_type':
                                      self.getPortalMovementTypeList()}):
        # Find related in simulation
        for my_simulation_movement in m.getDeliveryRelatedValueList(
                                  portal_type = 'Simulation Movement'):
          # And apply
          getattr(my_simulation_movement.getObject(), method_id)(**kw)
        for c in m.contentValues(filter={'portal_type':
                                        self.getPortalMovementTypeList()}):
          for my_simulation_movement in c.getDeliveryRelatedValueList(
                                  portal_type = 'Simulation Movement'):
            # And apply
            getattr(my_simulation_movement.getObject(), method_id)(**kw)


    #######################################################
    # Causality computation
    security.declareProtected(Permissions.View, 'isConvergent')
    def isConvergent(self,**kw):
      """
        Returns 0 if the target is not met
      """
      return int(not self.isDivergent(**kw))

    security.declareProtected(Permissions.View, 'isSimulated')
    def isSimulated(self):
      """
        Returns 1 if all movements have a delivery or order counterpart
        in the simulation
      """
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
    def isDivergent(self, fast=0, **kw):
      """
        Returns 1 if the target is not met according to the current information
        After and edit, the isOutOfTarget will be checked. If it is 1,
        a message is emitted

        emit targetUnreachable !
      """
      # Delivery_zIsDivergent only works when object and simulation is
      # reindexed, so if an user change the delivery, he must wait
      # until everything is indexed, this is not acceptable for users
      # so we should not use it by default (and may be we should remove)
      if fast==1 and len(self.Delivery_zIsDivergent(uid=self.getUid())) > 0:
        return 1
      # Check if the total quantity equals the total of each simulation movement quantity
      for movement in self.getMovementList():
        if movement.isDivergent():
          return 1
      return 0

    security.declareProtected(Permissions.View, 'getDivergenceList')
    def getDivergenceList(self, **kw):
      """
      Return a list of messages that contains the divergences
      """
      divergence_list = []
      for movement in self.getMovementList():
         divergence_list.extend(movement.getDivergenceList())
      return divergence_list

    def updateCausalityState(self,**kw):
      """
      This is often called as an activity, it will check if the
      deliver is convergent, and if so it will put the delivery
      in a solved state, if not convergent in a diverged state
      """
      if getattr(self, 'diverge', None) is not None \
            and getattr(self, 'converge', None) is not None:
        if self.isDivergent(**kw):
          self.diverge()
        else:
          self.converge()

    def splitAndDeferMovementList(self, start_date=None, stop_date=None,
        movement_uid_list=[], delivery_solver=None,
        target_solver='CopyToTarget', delivery_builder=None):
      """
      this method will unlink and delete movements in movement_uid_list and
      rebuild a new Packing List with them.
      1/ change date in simulation, call TargetSolver and expand
      2/ detach simulation movements from to-be-deleted movements
      3/ delete movements
        XXX make sure that all detached movements are deleted at the same
        time, else the interaction workflow would reattach them to a delivery
        rule.
      4/ call builder
      """
      tag_list = []
      movement_list = [x for x in self.getMovementList() if x.getUid() in
          movement_uid_list]
      if not movement_list: return

      deferred_simulation_movement_list = []
      # defer simulation movements
      if start_date != None or stop_date != None:
        for movement in movement_list:
          start_date = start_date or movement.getStartDate()
          stop_date = stop_date or movement.getStopDate()
          for s_m in movement.getDeliveryRelatedValueList():
            if s_m.getStartDate() != start_date or \
                s_m.getStopDate() != stop_date:
              s_m.edit(start_date=start_date, stop_date=stop_date)
              deferred_simulation_movement_list.append(s_m)

      solver_tag = '%s_splitAndDefer_solver' % self.getRelativeUrl()
      expand_tag = '%s_splitAndDefer_expand' % self.getRelativeUrl()
      detach_tag = '%s_splitAndDefer_detach' % self.getRelativeUrl()
      build_tag = '%s_splitAndDefer_build' % self.getRelativeUrl()
      # call solver and expand on deferrd movements
      for movement in movement_list:
        movement.activate(tag=solver_tag).Movement_solveMovement(
            delivery_solver, target_solver)
      tag_list.append(solver_tag)
      for s_m in deferred_simulation_movement_list:
        s_m.activate(after_tag=tag_list[:], tag=expand_tag).expand()
      tag_list.append(expand_tag)

      detached_movement_url_list = []
      deleted_movement_uid_list = []
      #detach simulation movements
      for movement in movement_list:
        movement_url = movement.getRelativeUrl()
        movement_uid = getattr(movement,'uid',None)
        if movement_uid: deleted_movement_uid_list.append(movement_uid)
        for s_m in movement.getDeliveryRelatedValueList():
          delivery_list = \
              [x for x in s_m.getDeliveryList() if x != movement_url]
          s_m.activate(after_tag=tag_list[:], tag=detach_tag).setDeliveryList(
              delivery_list)
          detached_movement_url_list.append(s_m.getRelativeUrl())
      tag_list.append(detach_tag)

      #delete delivery movements
      # deleteContent uses the uid as a activity tag
      self.activate(after_tag=tag_list[:]).deleteContent([movement.getId() for
          movement in movement_list])
      tag_list.extend(deleted_movement_uid_list)

      # update causality state on self, after deletion
      self.activate(after_tag=tag_list[:],
          activity='SQLQueue').updateCausalityState()

      # call builder on detached movements
      builder = getattr(self.portal_deliveries, delivery_builder)
      builder.activate(after_tag=tag_list[:], tag=build_tag).build(
          movement_relative_url_list=detached_movement_url_list)


    #######################################################
    # Defer indexing process
    def reindexObject(self, *k, **kw):
      """
        Reindex children and simulation
      """
      self.recursiveReindexObject(*k, **kw)
      # NEW: we never rexpand simulation - This is a task for DSolver / TSolver
      # Make sure expanded simulation is still OK (expand and reindex)
      # self.activate().applyToDeliveryRelatedMovement(method_id = 'expand')

    #######################################################
    # Stock Management
    def _getMovementResourceList(self):
      resource_dict = {}
      for m in self.contentValues(filter={
                      'portal_type': self.getPortalMovementTypeList()}):
        r = m.getResource()
        if r is not None:
          resource_dict[r] = 1
      return resource_dict.keys()

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventory')
    def getInventory(self, **kw):
      """
      Returns inventory
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventory')
    def getCurrentInventory(self, **kw):
      """
      Returns current inventory
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getAvailableInventory')
    def getAvailableInventory(self, **kw):
      """
      Returns available inventory
      (current inventory - deliverable)
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getAvailableInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventory')
    def getFutureInventory(self, **kw):
      """
      Returns inventory at infinite
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventory(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryList')
    def getInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventoryList')
    def getCurrentInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventoryList')
    def getFutureInventoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryStat')
    def getInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventoryStat')
    def getCurrentInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventoryStat')
    def getFutureInventoryStat(self, **kw):
      """
      Returns statistics of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventoryStat(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryChart')
    def getInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getCurrentInventoryChart')
    def getCurrentInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getCurrentInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getFutureInventoryChart')
    def getFutureInventoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getFutureInventoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryHistoryList')
    def getInventoryHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getInventoryHistoryChart')
    def getInventoryHistoryChart(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getInventoryHistoryChart(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getMovementHistoryList')
    def getMovementHistoryList(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getMovementHistoryList(**kw)

    security.declareProtected(Permissions.AccessContentsInformation, 
                              'getMovementHistoryStat')
    def getMovementHistoryStat(self, **kw):
      """
      Returns list of inventory grouped by section or site
      """
      kw['resource'] = self._getMovementResourceList()
      return self.portal_simulation.getMovementHistoryStat(**kw)





# JPS: We must still decide if getInventoryAssetPrice is part of the Delivery API

#     security.declareProtected(Permissions.AccessContentsInformation, 'getInventoryAssetPrice')
#     def getInventoryAssetPrice(self, **kw):
#       """
#         Returns asset at infinite
#       """
#       kw['category'] = self._getMovementResourceList()
#       return self.portal_simulation.getInventoryAssetPrice(**kw)
# 
#     security.declareProtected(Permissions.AccessContentsInformation, 'getFutureInventoryAssetPrice')
#     def getFutureInventoryAssetPrice(self, **kw):
#       """
#         Returns asset at infinite
#       """
#       kw['category'] = self._getMovementResourceList()
#       return self.portal_simulation.getFutureInventoryAssetPrice(**kw)
# 
#     security.declareProtected(Permissions.AccessContentsInformation, 'getCurrentInventoryAssetPrice')
#     def getCurrentInventoryAssetPrice(self, **kw):
#       """
#         Returns asset at infinite
#       """
#       kw['category'] = self._getMovementResourceList()
#       return self.portal_simulation.getCurrentInventoryAssetPrice(**kw)
# 
#     security.declareProtected(Permissions.AccessContentsInformation, 'getAvailableInventoryAssetPrice')
#     def getAvailableInventoryAssetPrice(self, **kw):
#       """
#         Returns asset at infinite
#       """
#       kw['category'] = self._getMovementResourceList()
#       return self.portal_simulation.getAvailableInventoryAssetPrice(**kw)

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

    ##########################################################################
    # Applied Rule stuff
    def updateAppliedRule(self, rule_reference=None, rule_id=None, force=0,
                          **kw):
      """
      Create a new Applied Rule if none is related, or call expand
      on the existing one.

      The chosen applied rule will be the validated rule with reference ==
      rule_reference, and the higher version number.

      If no rule is found, simply pass rule_reference to _createAppliedRule,
      to keep compatibility vith the previous behaviour
      """
      if rule_id is not None:
        from warnings import warn
        warn('rule_id to updateAppliedRule is deprecated; use rule_reference instead',
             DeprecationWarning)
        rule_reference = rule_id

      if rule_reference is None:
        return

      portal_rules = getToolByName(self, 'portal_rules')
      res = portal_rules.searchFolder(reference=rule_reference,
          validation_state="validated", sort_on='version',
          sort_order='descending') # XXX validated is Hardcoded !

      if len(res) > 0:
        rule_id = res[0].getId()
      else:
        rule_id = rule_reference

      if (self.getSimulationState() not in
          self.getPortalDraftOrderStateList()):
        # Nothing to do if we are already simulated
        self._createAppliedRule(rule_id, force=force, **kw)

    def _createAppliedRule(self, rule_id, force=0, activate_kw=None, **kw):
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
      my_applied_rule_list = self.getCausalityRelatedValueList(
          portal_type='Applied Rule')
      my_applied_rule = None
      if len(my_applied_rule_list) == 0:
        if self.isSimulated(): 
          # No need to create a DeliveryRule 
          # if we are already in the simulation process
          pass
        else:
          # Create a new applied order rule (portal_rules.order_rule)
          portal_rules = getToolByName(self, 'portal_rules')
          portal_simulation = getToolByName(self, 'portal_simulation')
          my_applied_rule = portal_rules[rule_id].\
              constructNewAppliedRule(portal_simulation)
          # Set causality
          my_applied_rule.setCausalityValue(self)
          # We must make sure this rule is indexed
          # now in order not to create another one later
          my_applied_rule.reindexObject(activate_kw=activate_kw, **kw)
      elif len(my_applied_rule_list) == 1:
        # Re expand the rule if possible
        my_applied_rule = my_applied_rule_list[0]
      else:
        raise "SimulationError", 'Delivery %s has more than one applied'\
            ' rule.' % self.getRelativeUrl()

      my_applied_rule_id = None
      expand_activate_kw = {}
      if my_applied_rule is not None:
        my_applied_rule_id = my_applied_rule.getId()
        expand_activate_kw['after_path_and_method_id'] = (
            my_applied_rule.getPath(),
            ['immediateReindexObject', 'recursiveImmediateReindexObject'])
      # We are now certain we have a single applied rule
      # It is time to expand it
      self.activate(activate_kw=activate_kw, **expand_activate_kw).expand(
          applied_rule_id=my_applied_rule_id, force=force,
          activate_kw=activate_kw, **kw)

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule_id=None, force=0, activate_kw=None,**kw):
      """
        Reexpand applied rule
        
        Also reexpand all rules related to movements
      """
      excluded_rule_path_list = []
      if applied_rule_id is not None:
        my_applied_rule = self.portal_simulation.get(applied_rule_id, None)
        if my_applied_rule is not None:
          excluded_rule_path_list.append(my_applied_rule.getPath())
          my_applied_rule.expand(force=force, activate_kw=activate_kw,**kw)
          # once expanded, the applied_rule must be reindexed
          # because some simulation_movement may change even
          # if there are not edited (acquisition)
          my_applied_rule.recursiveReindexObject(activate_kw=activate_kw)
        else:
          LOG("ERP5", PROBLEM,
              "Could not expand applied rule %s for delivery %s" %\
                  (applied_rule_id, self.getId()))
      self.expandRuleRelatedToMovement(
                  excluded_rule_path_list=excluded_rule_path_list,
                  force=force,
                  activate_kw=activate_kw,
                  **kw)

    security.declareProtected(Permissions.ModifyPortalContent,
        'expandRuleRelatedToMovement')
    def expandRuleRelatedToMovement(self,excluded_rule_path_list=None,
                                    activate_kw=None,**kw):
      """
      Some delivery movement may be related to another applied rule than
      the one related to the delivery. Delivery movements may be related
      to many simulation movements from many different root applied rules,
      so it is required to expand the applied rule parent to related
      simulation movements.

      exclude_rule_path : do not expand this applied rule (or children
                          applied rule)
      """
      if excluded_rule_path_list is None:
        excluded_rule_path_list = []
      to_expand_list = []
      # we might use a zsql method, because it can be very slow
      for m in self.getMovementList():
        if m.isSimulated():
          sim_movement_list = m.getDeliveryRelatedValueList()
          for sim_movement in sim_movement_list:
            if sim_movement.getRootAppliedRule().getPath() \
                not in excluded_rule_path_list:
              parent_value = sim_movement.getParentValue()
              if parent_value not in to_expand_list:
                to_expand_list.append(parent_value)
      for rule in to_expand_list:
        rule.expand(activate_kw=activate_kw,**kw)
        rule.recursiveReindexObject(activate_kw=activate_kw)

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRootCausalityValueList')
    def getRootCausalityValueList(self):
      """
        Returns the initial causality value for this movement.
        This method will look at the causality and check if the
        causality has already a causality
      """
      causality_value_list = [x for x in self.getCausalityValueList()
                                if x is not self]
      initial_list = []
      if len(causality_value_list)==0:
        initial_list = [self]
      else:
        for causality in causality_value_list:
          # The causality may be something which has not this method
          # (e.g. item)
          if hasattr(causality, 'getRootCausalityValueList'):
            tmp_causality_list = causality.getRootCausalityValueList()
            initial_list.extend([x for x in tmp_causality_list 
                                 if x not in initial_list])
      return initial_list


    # XXX Temp hack, should be removed has soon as the structure of
    # the order/delivery builder will be reviewed. It might
    # be reviewed if we plan to configure movement groups in the zmi
    security.declareProtected( Permissions.ModifyPortalContent,
                               'setRootCausalityValueList')
    def setRootCausalityValueList(self,value):
      """
      This is a hack
      """
      pass

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getParentExplanationValue')
    def getParentExplanationValue(self):
      """
        This method should be removed as soon as movement groups
        will be rewritten. It is a temp hack
      """
      return self

    # XXX Temp hack, should be removed has soon as the structure of
    # the order/delivery builder will be reviewed. It might
    # be reviewed if we plan to configure movement groups in the zmi
    security.declareProtected( Permissions.ModifyPortalContent,
                               'setParentExplanationValue')
    def setParentExplanationValue(self,value):
      """
      This is a hack
      """
      pass

