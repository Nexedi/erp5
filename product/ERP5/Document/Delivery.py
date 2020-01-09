# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import zope.interface

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager, \
    setSecurityManager, newSecurityManager
from AccessControl.User import nobody
from AccessControl.PermissionRole import PermissionRole
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.ImmobilisationDelivery import ImmobilisationDelivery
from Products.ERP5.mixin.amount_generator import AmountGeneratorMixin
from Products.ERP5.mixin.composition import CompositionMixin
from Products.ERP5.mixin.rule import SimulableMixin
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod, \
    unrestricted_apply
from zLOG import LOG, PROBLEM

class Delivery(XMLObject, ImmobilisationDelivery, SimulableMixin,
               CompositionMixin, AmountGeneratorMixin):
    """
        Each time delivery is modified, it MUST launch a reindexing of
        inventories which are related to the resources contained in the Delivery
    """
    # CMF Type Definition
    meta_type = 'ERP5 Delivery'
    portal_type = 'Delivery'
    isDelivery = ConstantGetter('isDelivery', value=True)

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

    # Declarative interfaces
    zope.interface.implements(interfaces.IAmountGenerator,
                              interfaces.IDivergenceController,
                              interfaces.IMovementCollection)

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      return 1

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getTotalPrice')
    def getTotalPrice(self, fast=0, src__=0, base_contribution=None, rounding=False, **kw):
      """ Returns the total price for this order

        if the `fast` argument is set to a true value, then it use
        SQLCatalog to compute the price, otherwise it sums the total
        price of objects one by one.

        So if the order is not in the catalog, getTotalPrice(fast=1)
        will return 0, this is not a bug.

        base_contribution must be a relative url of a category. If passed, then
        fast parameter is ignored.
      """
      if 'portal_type' not in kw:
        kw['portal_type'] = self.getPortalObject() \
          .getPortalDeliveryMovementTypeList()
      if base_contribution is None:
        if fast:
          # XXX fast ignores base_contribution for now, but it should be possible
          # to use a related key
          kw['section_uid'] = self.getDestinationSectionUid()
          kw['stock.explanation_uid'] = self.getUid()
          return self.getPortalObject()\
            .portal_simulation.getInventoryAssetPrice(**kw)

        result = sum([ line.getTotalPrice(fast=0) for line in
                       self.objectValues(**kw) ])
      else:
        # Find amounts from movements in the delivery.
        if isinstance(base_contribution, (tuple, list)):
          base_contribution_list = base_contribution
        else:
          base_contribution_list = (base_contribution,)
        base_contribution_value_list = []
        portal_categories = self.portal_categories
        for relative_url in base_contribution_list:
          base_contribution_value = portal_categories.getCategoryValue(relative_url)
          if base_contribution_value is not None:
            base_contribution_value_list.append(base_contribution_value)
        if not base_contribution_value_list:
          # We cannot find any amount so that the result is 0.
          result = 0
        else:
          matched_movement_list = [
              movement
              for movement in self.getMovementList()
              if set(movement.getBaseContributionValueList()).intersection(base_contribution_value_list)]
          if rounding:
            portal_roundings = self.portal_roundings
            matched_movement_list = [
                portal_roundings.getRoundingProxy(movement)
                for movement in matched_movement_list]
          result = sum([movement.getTotalPrice()
                        for movement in matched_movement_list])

      method = self._getTypeBasedMethod('convertTotalPrice')
      if method is not None:
        return method(result)
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTotalNetPrice')
    def getTotalNetPrice(self, fast=0, src__=0, **kw):
      """
        Same as getTotalPrice, but including Tax and Discount (from legacy
        simulation).

        This method is deprecated because it uses deprecated Tax & Discount
        portal types. You should use getTotalPrice(base_contribution=) instead.
      """
      total_price = self.getTotalPrice(fast=fast, src__=src__, **kw)
      kw['portal_type'] = self.getPortalObject().getPortalTaxMovementTypeList()
      return total_price + self.getTotalPrice(fast=fast, src__=src__, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTotalQuantity')
    def getTotalQuantity(self, fast=0, src__=0, **kw):
      """ Returns the total quantity of this order.

        if the `fast` argument is set to a true value, then it use
        SQLCatalog to compute the quantity, otherwise it sums the total
        quantity of objects one by one.

        So if the order is not in the catalog, getTotalQuantity(fast=1)
        will return 0, this is not a bug.
      """
      if 'portal_type' not in kw:
        kw['portal_type'] = self.getPortalObject() \
          .getPortalDeliveryMovementTypeList()
      if fast:
        kw['section_uid'] = self.getDestinationSectionUid()
        kw['stock.explanation_uid'] = self.getUid()
        return self.getPortalObject().portal_simulation.getInventory(**kw)
      return sum([ line.getTotalQuantity(fast=0) for line in
                      self.objectValues(**kw) ])

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
                             '_getMovementList')
    def _getMovementList(self, portal_type=None, **kw):
      """
      Return a list of movements
      """
      movement_portal_type_set = set(
        self.getPortalObject().getPortalMovementTypeList())
      movement_list = self.objectValues(
        portal_type=movement_portal_type_set, **kw)
      if movement_list:

        if isinstance(portal_type, str):
          portal_type = portal_type,
        elif isinstance(portal_type, (list, tuple)):
          portal_type = set(portal_type)

        # Browse lines recursively and collect leafs.
        stack = [iter(movement_list)]
        movement_list = []
        while stack:
          for sub_object in stack[-1]:
            content_list = sub_object.objectValues(
              portal_type=movement_portal_type_set, **kw)
            if sub_object.hasCellContent():
              cell_list = sub_object.getCellValueList()
              if len(cell_list) != len(content_list):
                content_list = set(content_list).difference(cell_list)
                if content_list:
                  stack.append(iter(content_list))
                  break
              else:
                movement_list.extend(x for x in content_list
                  if portal_type is None or x.getPortalType() in portal_type)
            elif content_list:
              stack.append(iter(content_list))
              break
            elif portal_type is None or \
                 sub_object.getPortalType() in portal_type:
              movement_list.append(sub_object)
          else:
            del stack[-1]

      return movement_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getMovementList')
    def getMovementList(self, portal_type=None, **kw):
      """
       Return a list of movements.
      """
      return self._getMovementList(portal_type=portal_type, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getSimulatedMovementList')
    def getSimulatedMovementList(self):
      """
        Return a list of simulated movements.
        This does not contain Container Line or Container Cell.
      """
      return self.getMovementList(portal_type=
        self.getPortalObject().getPortalSimulatedMovementTypeList())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInvoiceMovementList')
    def getInvoiceMovementList(self):
      """
        Return a list of simulated movements.
        This does not contain Container Line or Container Cell.
      """
      return self.getMovementList(portal_type=
        self.getPortalObject().getPortalInvoiceMovementTypeList())

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainerList')
    def getContainerList(self):
      """
        Return a list of root containers.
        This does not contain sub-containers.
      """
      return self.objectValues(portal_type=
        self.getPortalObject().getPortalContainerTypeList())

    #######################################################
    # Causality computation
    security.declareProtected(Permissions.AccessContentsInformation, 'isConvergent')
    def isConvergent(self,**kw):
      """
        Returns 0 if the target is not met
      """
      return bool(not self.isDivergent(**kw))

    security.declareProtected(Permissions.AccessContentsInformation, 'isSimulated')
    def isSimulated(self):
      """
        Returns 1 if all non-null movements have a delivery counterpart
        in the simulation
      """
      for m in self.getMovementList():
        if m.getQuantity() and not m.isSimulated():
          return 0
      return 1

    security.declareProtected(Permissions.AccessContentsInformation, 'isDivergent')
    def isDivergent(self, fast=0, **kw):
      """Return True if this movement diverges from the its simulation.
      """
      ## Note that fast option was removed. Now, fast=1 is ignored.

      # Check if the total quantity equals the total of each simulation movement quantity
      for simulation_movement in self._getAllRelatedSimulationMovementList():
        if simulation_movement.isDivergent():
          return True
      return False

    security.declareProtected(Permissions.AccessContentsInformation, 'getDivergenceList')
    def getDivergenceList(self, **kw):
      """
      Return a list of messages that contains the divergences
      """
      divergence_list = []
      for simulation_movement in self._getAllRelatedSimulationMovementList():
         divergence_list.extend(simulation_movement.getDivergenceList())
      return divergence_list

    security.declareProtected(Permissions.AccessContentsInformation, 'updateCausalityState')
    @UnrestrictedMethod
    def updateCausalityState(self, solve_automatically=True, **kw):
      """
      This is often called as an activity, it will check if the
      deliver is convergent, and if so it will put the delivery
      in a solved state, if not convergent in a diverged state
      """
      isTransitionPossible = \
          self.getPortalObject().portal_workflow.isTransitionPossible
      if isTransitionPossible(self, 'diverge') and \
          isTransitionPossible(self, 'converge'):
        if self.isDivergent(**kw):
          if solve_automatically and \
              isTransitionPossible(self, 'solve_automatically'):
            self.solveAutomatically()
          else:
            self.diverge()
        else:
          self.converge()

    def updateSimulation(self, calculate=False, **kw):
      if calculate:
        path = self.getPath()
        self.activate(
          after_tag='build:'+path,
          after_path_and_method_id=(path, '_localBuild'),
          ).updateCausalityState()
      if kw:
        super(Delivery, self).updateSimulation(**kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'splitAndDeferMovementList')
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
      if start_date is not None or stop_date is not None:
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
      kw = {'after_tag': tag_list[:], 'tag': expand_tag}
      for s_m in deferred_simulation_movement_list:
        s_m.expand('deferred', activate_kw=kw)
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
      # do not reexpand simulation: this is a task for DSolver / TSolver

    #######################################################
    # Stock Management
    def _getMovementResourceList(self):
      resource_set = {m.getResource()
        for m in self.objectValues(portal_type=
          self.getPortalObject().getPortalMovementTypeList())}
      resource_set.discard(None)
      return list(resource_set)

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

    ##########################################################################
    # Applied Rule stuff

    security.declareProtected(Permissions.AccessContentsInformation,
                              'localBuild')
    def localBuild(self, activity_kw=()):
      """Activate builders for this delivery

      The generated activity will find all buildable business links for this
      delivery, and call related builders, which will select all simulation
      movements part of the same explanation(s) as the delivery.

      XXX: Consider moving it to SimulableMixin if it's useful for
           Subscription Items.
      """
      # XXX: Previous implementation waited for expand activities of related
      #      documents and even suggested to look at explanation tree,
      #      instead of causalities. Is it required ?
      kw = {'priority': 3}
      kw.update(activity_kw)
      after_tag = kw.pop('after_tag', None)
      if isinstance(after_tag, basestring):
        after_tag = [after_tag]
      else:
        after_tag = list(after_tag) if after_tag else []
      after_tag.append('build:' + self.getPath())
      sm = getSecurityManager()
      newSecurityManager(None, nobody)
      try:
        unrestricted_apply(self.activate(after_tag=after_tag, **kw)._localBuild)
      finally:
        setSecurityManager(sm)

    def _localBuild(self):
      """Do an immediate local build for this delivery"""
      return self.asComposedDocument().build(explanation=self)

    def _createRootAppliedRule(self):
      # Only create RAR if we are not in a "too early" or "too late" state.
      state = self.getSimulationState()
      if (state != 'deleted' and
          state not in self.getPortalObject().getPortalDraftOrderStateList()):
        return super(Delivery, self)._createRootAppliedRule()

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRootCausalityValueList')
    def getRootCausalityValueList(self):
      """
        Returns the initial causality value for this movement.
        This method will look at the causality and check if the
        causality has already a causality
      """
      seen_set = set()
      def recursive(self):
        if self in seen_set:
          return []

        seen_set.add(self)
        causality_value_list = self.getCausalityValueList()
        if causality_value_list:
          initial_list = []
          for causality in causality_value_list:
            # The causality may be something which has not this method
            # (e.g. item)
            if getattr(causality, 'getRootCausalityValueList', None) is None:
                continue

            assert causality != self
            initial_list += [x for x in recursive(causality)
                             if x not in initial_list]
          return initial_list
        return [self]

      return recursive(self)

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

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getBuilderList')
    def getBuilderList(self):
      """Returns appropriate builder list."""
      return self._getTypeBasedMethod('getBuilderList')()
      # XXX - quite a hack, since no way to know...
      #       propper implementation should use business path definition
      #       however, the real question is "is this really necessary"
      #       since the main purpose of this method is superceded
      #       by IDivergenceController

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRootSpecialiseValue')
    def getRootSpecialiseValue(self, portal_type_list):
      """Returns first specialise value matching portal type"""
      def findSpecialiseValue(context):
        if context.getPortalType() in portal_type_list:
          return context
        if getattr(context, 'getSpecialiseValueList', None) is not None:
          for specialise in context.getSpecialiseValueList():
            specialise_value = findSpecialiseValue(specialise)
            if specialise_value is not None:
              return specialise_value
        return None
      return findSpecialiseValue(self)

    security.declareProtected( Permissions.ModifyPortalContent,
                               'disconnectSimulationMovementList')
    def disconnectSimulationMovementList(self, movement_list=None):
      """Disconnects simulation movements from delivery's lines

      If movement_list is passed only those movements will be disconnected
      from simulation.

      If movements in movement_list do not belong to current
      delivery they are silently ignored.

      Returns list of disconnected Simulation Movements.

      Known issues and open questions:
       * how to protect disconnection from completed delivery?
       * what to do if movements from movement_list do not belong to delivery?
       * it is required to remove causality relation from delivery or delivery
         lines??
      """
      delivery_movement_value_list = self.getMovementList()
      if movement_list is not None:
        movement_value_list = [self.restrictedTraverse(movement) for movement
            in movement_list]
        # only those how are in this delivery
        movement_value_list = [movement_value for movement_value in
            movement_value_list if movement_value
            in delivery_movement_value_list]
      else:
        movement_value_list = delivery_movement_value_list

      disconnected_simulation_movement_list = []
      for movement_value in movement_value_list:
        # Note: Relies on fact that is invoked, when simulation movements are
        # indexed properly
        for simulation_movement in movement_value \
            .getDeliveryRelatedValueList(portal_type='Simulation Movement'):
          simulation_movement.edit(
            delivery = None,
            delivery_ratio = None
          )
          disconnected_simulation_movement_list.append(
              simulation_movement.getRelativeUrl())

      return disconnected_simulation_movement_list

    def _getAllRelatedSimulationMovementList(self):
      result = []
      for movement in self.getMovementList():
        result += movement.getDeliveryRelatedValueList()
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getDivergentTesterAndSimulationMovementList')
    def getDivergentTesterAndSimulationMovementList(self):
      """
      This method returns a list of (tester, simulation_movement) for each divergence.
      """
      divergent_tester_list = []
      for simulation_movement in self._getAllRelatedSimulationMovementList():
        simulation_movement = simulation_movement.getObject()
        rule = simulation_movement.getParentValue().getSpecialiseValue()
        for tester in rule._getDivergenceTesterList(exclude_quantity=False):
          if tester.explain(simulation_movement) not in (None, []):
            divergent_tester_list.append((tester, simulation_movement))
      return divergent_tester_list

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
