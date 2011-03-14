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

import transaction
import zope.interface
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from Products.ERP5.Document.Movement import Movement

from zLOG import LOG, WARNING

from Acquisition import aq_base

from Products.ERP5.Document.AppliedRule import TREE_DELIVERED_CACHE_KEY, TREE_DELIVERED_CACHE_ENABLED
from Products.ERP5.mixin.property_recordable import PropertyRecordableMixin
from Products.ERP5.mixin.explainable import ExplainableMixin

# XXX Do we need to create groups ? (ie. confirm group include confirmed, getting_ready and ready

parent_to_movement_simulation_state = {
  'cancelled'        : 'cancelled',
  'draft'            : 'draft',
  'auto_planned'     : 'auto_planned',
  'planned'          : 'planned',
  'ordered'          : 'planned',
  'confirmed'        : 'planned',
  'getting_ready'    : 'planned',
  'ready'            : 'planned',
  'started'          : 'planned',
  'stopped'          : 'planned',
  'delivered'        : 'planned',
  'invoiced'         : 'planned',
}

class SimulationMovement(PropertyRecordableMixin, Movement, ExplainableMixin):
  """
      Simulation movements belong to a simulation workflow which includes
      the following steps

      - planned

      - ordered

      - confirmed (the movement is now confirmed in qty or date)

      - started (the movement has started)

      - stopped (the movement is now finished)

      - delivered (the movement is now archived in a delivery)

      The simulation worklow uses some variables, which are
      set by the template

      - is_order_required

      - is_delivery_required


      XX
      - is_problem_checking_required ?

      Other flag
      (forzen flag)

      NEW: we do not use DCWorklow so that the simulation process
      can be as much as possible independent of a Zope / CMF implementation.
  """
  meta_type = 'ERP5 Simulation Movement'
  portal_type = 'Simulation Movement'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Simulation
                    # Need industrial_phase
                    , PropertySheet.TransformedResource
                    , PropertySheet.AppliedRule
                    , PropertySheet.ItemAggregation
                    , PropertySheet.Reference
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IPropertyRecordable, )

  def tpValues(self) :
    """ show the content in the left pane of the ZMI """
    return self.objectValues()

  # Price should be acquired
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getPrice')
  def getPrice(self, default=None, context=None, REQUEST=None, **kw):
    """
    """
    return self._baseGetPrice(default) # Call the price method

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCausalityState')
  def getCausalityState(self):
    """
      Returns the current state in causality
    """
    return getattr(aq_base(self), 'causality_state', 'solved')

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setCausalityState')
  def setCausalityState(self, value):
    """
      Change causality state
    """
    self.causality_state = value

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getSimulationState')
  def getSimulationState(self, id_only=1):
    """Returns the current state in simulation

      Inherit from delivery or parent (using a conversion table to make orders
      planned when parent is confirmed).
      
      In the case of simulation coming from an item, the simulation state is
      delegated to the item.

      XXX: movements in zero stock rule can not acquire simulation state
    """
    delivery = self.getDeliveryValue()
    if delivery is not None:
      return delivery.getSimulationState()
    # 'order' category is deprecated. it is kept for compatibility.
    order = self.getOrderValue()
    if order is not None:
      return order.getSimulationState()

    try:
      parent_state = None
      try:
        parent_state = self.getParentValue().getSimulationState()
      except AttributeError:
        item = self.getParentValue().getCausalityValue(
                portal_type=self.getPortalItemTypeList())
        if interfaces.IExpandableItem.providedBy(item):
          return item.getSimulationMovementSimulationState(self)
        raise
      return parent_to_movement_simulation_state[parent_state]
    except (KeyError, AttributeError):
      LOG('SimulationMovement.getSimulationState', WARNING,
          'Could not acquire simulation state from %s'
          % self.getRelativeUrl(), error=True)
      return None

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getTranslatedSimulationStateTitle')
  def getTranslatedSimulationStateTitle(self):
    """Returns translated simulation state title, for user interface, such as
    stock browser.
    """
    delivery = self.getDeliveryValue()
    if delivery is not None:
      return delivery.getTranslatedSimulationStateTitle()
    # 'order' category is deprecated. it is kept for compatibility.
    order = self.getOrderValue()
    if order is not None:
      return order.getTranslatedSimulationStateTitle()
    # The simulation_state of a simulation movement is calculated by a
    # mapping, there's no reliable way of getting the translated title from a
    # simulation state ID, so we just return the state ID because we got
    # nothing better to return.
    return self.getSimulationState()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isCompleted')
  def isCompleted(self):
    """Lookup business path and, if any, return True whenever
    simulation_state is in of completed state list defined on business path
    """
    # only available in BPM, so fail totally in case of working without BPM
    business_link =  self.getCausalityValue(
                         portal_type=self.getPortalBusinessLinkTypeList())
    if business_link is None:
      return False
    return self.getSimulationState() in business_link.getCompletedStateList()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isFrozen')
  def isFrozen(self):
    """Lookup business path and, if any, return True whenever
    simulation_state is in one of the frozen states defined on business path
    """
    business_link =  self.getCausalityValue(
                         portal_type=self.getPortalBusinessLinkTypeList())
    if business_link is None:
      # Legacy support - this should never happen
      # XXX-JPS ADD WARNING
      if self.getSimulationState() in ('stopped', 'delivered', 'cancelled'):
        return True
      if self._baseIsFrozen() == 0:
        self._baseSetFrozen(None)
      return self._baseGetFrozen() or False
    return self.getSimulationState() in business_link.getFrozenStateList()

  security.declareProtected( Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self):
    """
      Returns 1 if this needs to be accounted
      Some Simulation movement corresponds to non accountable movements,
      the parent applied rule decide wether this movement is accountable
      or not.
    """
    return self.getParentValue().isAccountable(self)


  #######################################################
  # Causality Workflow Methods

  security.declareProtected(Permissions.ModifyPortalContent, 'calculate')
  def calculate(self):
    """Move related delivery in 'calculating' state by activity

    Activity to update causality state is delayed until all related simulation
    movement are reindexed.
    This method should be only called by
    simulation_movement_causality_interaction_workflow.
    """
    delivery = self.getDeliveryValue()
    if delivery is not None:
      delivery = delivery.getRootDeliveryValue()
      tv = getTransactionalVariable()
      path = self.getPath()
      delivery_path = delivery.getPath()
      key = 'SimulationMovement.calculate', delivery_path
      try:
        tv[key].append(path)
      except KeyError:
        tv[key] = [path]
        def before_commit():
          method_id_list = ('immediateReindexObject',
                            'recursiveImmediateReindexObject')
          tag = delivery_path + '_calculate'
          delivery.activate(tag=tag).Delivery_calculate(activate_kw=
            {'after_path_and_method_id': (tv[key], method_id_list)})
          tv[key] = None # disallow further calls to 'calculate'
        transaction.get().addBeforeCommitHook(before_commit)

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, **kw):
    """
    Checks all existing applied rules and make sure they still apply.
    Checks for other possible rules and starts expansion process (instanciates
    applied rules and calls expand on them).

    First get all applicable rules,
    then, delete all applied rules that no longer match and are not linked to
    a delivery,
    finally, apply new rules if no rule with the same type is already applied.
    """
    portal_rules = getToolByName(self.getPortalObject(), 'portal_rules')

    tv = getTransactionalVariable()
    cache = tv.setdefault(TREE_DELIVERED_CACHE_KEY, {})
    cache_enabled = cache.get(TREE_DELIVERED_CACHE_ENABLED, 0)

    # enable cache
    if not cache_enabled:
      cache[TREE_DELIVERED_CACHE_ENABLED] = 1

    applied_rule_dict = {}
    applicable_rule_dict = {}
    for rule in portal_rules.searchRuleList(self, sort_on='version',
        sort_order='descending'):
      reference = rule.getReference()
      if reference:
        applicable_rule_dict.setdefault(reference, rule)

    for applied_rule in list(self.objectValues()):
      rule = applied_rule.getSpecialiseValue()
      if rule.test(self) or applied_rule._isTreeDelivered():
        applied_rule_dict[rule.getReference()] = applied_rule
      else:
        self._delObject(applied_rule.getId())

    for reference, rule in applicable_rule_dict.iteritems():
      if reference not in applied_rule_dict:
        applied_rule = rule.constructNewAppliedRule(self, **kw)
        applied_rule_dict[reference] = applied_rule

    self.setCausalityState('expanded')
    # expand
    for applied_rule in applied_rule_dict.itervalues():
      applied_rule.expand(**kw)

    # disable and clear cache
    if not cache_enabled:
      try:
        del tv[TREE_DELIVERED_CACHE_KEY]
      except KeyError:
        pass

  security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
  def diverge(self):
    """
       -> new status -> diverged

       Movements which diverge can not be expanded
    """
    self.setCausalityState('diverged')

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getExplanationValue')
  def getExplanationValue(self):
    """Returns the delivery if any or the order related to the root
    applied rule if any.
    """
    delivery_value = self.getDeliveryValue()
    if delivery_value is None:
      # If the parent is not an Applied Rule, self does not have the method.
      getRootAppliedRule = getattr(self, 'getRootAppliedRule', None)
      if getRootAppliedRule is None:
        return None
      ra = getRootAppliedRule()
      order = ra.getCausalityValue()
      if order is not None:
        return order
      else:
        # Ex. zero stock rule
        return ra
    else:
      explanation_value = delivery_value
      portal = self.getPortalObject()
      delivery_type_list = self.getPortalDeliveryTypeList() \
              + self.getPortalOrderTypeList()
      while explanation_value.getPortalType() not in delivery_type_list and \
          explanation_value != portal:
            explanation_value = explanation_value.getParentValue()
      if explanation_value != portal:
        return explanation_value

  # Deliverability / orderability
  security.declareProtected( Permissions.AccessContentsInformation,
                             'isOrderable')
  def isOrderable(self):
    # the value of this method is no longer used.
    return True

  getOrderable = isOrderable

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isDeliverable')
  def isDeliverable(self):
    # the value of this method is no longer used.
    return True

  getDeliverable = isDeliverable

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isDeletable')
  def isDeletable(self):
    return not self.isFrozen() and not self._isTreeDelivered()

  # Simulation Dates - acquire target dates
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderStartDate')
  def getOrderStartDate(self):
    # 'order' category is deprecated. it is kept for compatibility.
    order_value = self.getOrderValue()
    if order_value is not None:
      return order_value.getStartDate()
    delivery_value = self.getDeliveryValue()
    if delivery_value is not None:
      return delivery_value.getStartDate()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderStopDate')
  def getOrderStopDate(self):
    # 'order' category is deprecated. it is kept for compatibility.
    order_value = self.getOrderValue()
    if order_value is not None:
      return order_value.getStopDate()
    delivery_value = self.getDeliveryValue()
    if delivery_value is not None:
      return delivery_value.getStopDate()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryStartDateList')
  def getDeliveryStartDateList(self):
    """
      Returns the stop date of related delivery
    """
    start_date_list = []
    delivery_movement = self.getDeliveryValue()
    if delivery_movement is not None:
      start_date_list.append(delivery_movement.getStartDate())
    return start_date_list

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryStopDateList')
  def getDeliveryStopDateList(self):
    """
      Returns the stop date of related delivery
    """
    stop_date_list = []
    delivery_movement = self.getDeliveryValue()
    if delivery_movement is not None:
      stop_date_list.append(delivery_movement.getStopDate())
    return stop_date_list

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getDeliveryQuantity')
  def getDeliveryQuantity(self):
    """
      Returns the quantity of related delivery
    """
    quantity = 0.0
    delivery_movement = self.getDeliveryValue()
    if delivery_movement is not None:
      quantity = delivery_movement.getQuantity()
    return quantity

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isConvergent')
  def isConvergent(self):
    """
      Returns true if the Simulation Movement is convergent with the
      the delivery value
    """
    return not self.isDivergent()

  security.declareProtected( Permissions.AccessContentsInformation,
      'isDivergent')
  def isDivergent(self):
    """
      Returns true if the Simulation Movement is divergent from the
      the delivery value
    """
    return self.getParentValue().isDivergent(self)

  security.declareProtected( Permissions.AccessContentsInformation,
      'getDivergenceList')
  def getDivergenceList(self):
    """
    Returns detailed information about the divergence
    """
    return self.getParentValue().getDivergenceList(self)

  security.declareProtected( Permissions.ModifyPortalContent,
                             'setDefaultDeliveryProperties')
  def setDefaultDeliveryProperties(self):
    """
    Sets the delivery_ratio and delivery_error properties to the
    calculated value
    """
    delivery = self.getDeliveryValue()
    if delivery is not None:
      delivery.updateSimulationDeliveryProperties(movement_list = [self])

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCorrectedQuantity')
  def getCorrectedQuantity(self):
    """
    Returns the quantity property deducted by the possible profit_quantity and
    taking into account delivery error

    NOTE: XXX-JPS This method should not use profit_quantity. Profit and loss
          quantities are now only handled through explicit movements.
          Look are invocations of _isProfitAndLossMovement in
          ERP5.mixin.rule to understand how.
    """
    quantity = self.getQuantity()
    profit_quantity = self.getProfitQuantity() or 0
    delivery_error = self.getDeliveryError() or 0
    return quantity - profit_quantity + delivery_error

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRootSimulationMovement')
  def getRootSimulationMovement(self):
    """
      Return the root simulation movement in the simulation tree.
      FIXME : this method should be called getRootSimulationMovementValue
    """
    parent_applied_rule = self.getParentValue()
    if parent_applied_rule.getRootAppliedRule() == parent_applied_rule:
      return self
    else:
      return parent_applied_rule.getRootSimulationMovement()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRootSimulationMovementUid')
  def getRootSimulationMovementUid(self):
    """
      Return the uid of the root simulation movement in the simulation tree.
    """
    root_simulation_movement = self.getRootSimulationMovement()
    if root_simulation_movement is not None:
      return root_simulation_movement.getUid()
    return None

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getRootCausalityValueList')
  def getRootCausalityValueList(self):
    """
      Returns the initial causality value for this movement.
      This method will look at the causality and check if the
      causality has already a causality
    """
    root_rule = self.getRootAppliedRule()
    return root_rule.getCausalityValueList()

  # XXX FIXME Use a interaction workflow instead
  # XXX This behavior is now done by simulation_movement_interaction_workflow
  # The call to activate() must be done after actual call to
  # setDelivery() on the movement,
  # but activate() must be called on the previous delivery...
  #def _setDelivery(self, value):
  #  LOG('setDelivery before', 0, '')
  #  delivery_value = self.getDeliveryValue()
  #  Movement.setDelivery(value)
  #  LOG('setDelivery', 0, '')
  #  if delivery_value is not None:
  #    LOG('delivery_value = ', 0, repr(delivery_value))
  #    activity = delivery_value.activate(
  #                activity='SQLQueue',
  #                after_path_and_method_id=(
  #                                        self.getPath(),
  #                                        ['immediateReindexObject',
  #                                         'recursiveImmediateReindexObject']))
  #    activity.edit()

  def _isTreeDelivered(self, ignore_first=0):
    """
    checks if subapplied rules  of this movement (going down the complete
    simulation tree) have a child with a delivery relation.
    Returns True if at least one is delivered, False if none of them are.

    see AppliedRule._isTreeDelivered
    """
    tv = getTransactionalVariable()
    cache = tv.setdefault(TREE_DELIVERED_CACHE_KEY, {})
    cache_enabled = cache.get(TREE_DELIVERED_CACHE_ENABLED, 0)

    def getTreeDelivered(movement, ignore_first=0):
      if not ignore_first:
        if len(movement.getDeliveryList()) > 0:
          return True
      for applied_rule in movement.objectValues():
        if applied_rule._isTreeDelivered():
          return True
      return False

    if ignore_first:
      rule_key = (self.getRelativeUrl(), 1)
    else:
      rule_key = self.getRelativeUrl()
    if cache_enabled:
      try:
        return cache[rule_key]
      except KeyError:
        result = getTreeDelivered(self, ignore_first=ignore_first)
        cache[rule_key] = result
        return result
    else:
      return getTreeDelivered(self, ignore_first=ignore_first)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isBuildable')
  def isBuildable(self):
    """Simulation Movement buildable logic"""
    if self.getDelivery():
      # already delivered
      return False

    # might be buildable - business path dependent
    business_link = self.getCausalityValue(portal_type='Business Link')
    explanation_value = self.getExplanationValue()
    if business_link is None or explanation_value is None:
      return True

    ## XXX Code below following line has been moved to BusinessPath (cf r37116)
    #return len(business_path.filterBuildableMovementList([self])) == 1

    predecessor_state = business_link.getPredecessorValue()
    if predecessor_state is None:
      # first one, can be built
      return True # XXX-JPS wrong cause root is marked

    # movement is not built, and corresponding business path
    # has predecessors: check movements related to those predecessors!
    predecessor_path_list = predecessor_state.getSuccessorRelatedValueList()

    def isBuiltAndCompleted(simulation, path):
      return simulation.getCausalityValue() is not None and \
          simulation.getSimulationState() in path.getCompletedStateList()

    ### Step 1:
    ## Explore ancestors in ZODB (cheap)
    #

    # store a causality -> causality_related_movement_list mapping
    causality_dict = {}
    current = self.getParentValue().getParentValue()
    while current.getPortalType() == "Simulation Movement":
      causality_dict[current.getCausality(portal_type='Business Link')] = \
        current
      current = current.getParentValue().getParentValue()

    remaining_path_set = set()
    for path in predecessor_path_list:
      related_simulation = causality_dict.get(path.getRelativeUrl())
      if related_simulation is None:
        remaining_path_set.add(path)
        continue
      # XXX assumption is made here that if we find ONE completed ancestor
      # movement of self that is related to a predecessor path, then
      # that predecessor path is completed. Is it True? (aka when
      # Business Process goes downwards, is the maximum movements per
      # predecessor 1 or can we have more?)
      if not isBuiltAndCompleted(related_simulation, path):
        return False

    # in 90% of cases, Business Path goes downward and this is enough
    if not remaining_path_set:
      return True

    # But sometimes we have to dig deeper

    ### Step 2:
    ## Try catalog to find descendant movements, knowing
    # that it can be incomplete

    class treeNode(dict):
      """
      Used to cache accesses to ZODB objects.
      The idea is to put in visited_movement_dict the objects we've already
      loaded from ZODB in Step #2 to avoid loading them again in Step #3.

      - self represents a single ZODB container c
      - self.visited_movement_dict contains an id->(ZODB obj) cache for
        subobjects of c
      - self[id] contains the treeNode representing c[id]
      """
      def __init__(self):
        dict.__init__(self)
        self.visited_movement_dict = dict()

    path_tree = treeNode()
    def updateTree(simulation_movement, path):
      tree_node = path_tree
      movement_path = simulation_movement.getPhysicalPath()
      simulation_movement_id = movement_path[-1]
      # find container
      for path_id in movement_path[:-1]:
        tree_node = tree_node.setdefault(path_id, treeNode())
      # and mark the object as visited
      tree_node.visited_movement_dict[simulation_movement_id] = (simulation_movement, path)

    portal_catalog = self.getPortalObject().portal_catalog
    catalog_simulation_movement_list = portal_catalog(
      portal_type='Simulation Movement',
      causality_uid=[p.getUid() for p in remaining_path_set],
      path='%s/%%' % self.getPath())

    for movement in catalog_simulation_movement_list:
      path = movement.getCausalityValue()
      if not isBuiltAndCompleted(movement, path):
        return False
      updateTree(movement, path)

    ### Step 3:
    ## We had no luck, we have to explore descendant movements in ZODB
    #
    def descendantGenerator(document, tree_node, path_set_to_check):
      """
      generator yielding Simulation Movement descendants of document.
      It does _not_ explore the whole subtree if iteration is stopped.

      It uses the tree we built previously to avoid loading again ZODB
      objects that we already loaded during catalog querying

      path_set_to_check contains a set of Business Paths that we are
      interested in. A branch is only explored if this set is not
      empty; a movement is only yielded if its causality value is in this set
      """
      object_id_list = document.objectIds()
      for id in object_id_list:
        if id not in tree_node.visited_movement_dict:
          # we had not visited it in step #2
          subdocument = document._getOb(id)
          if subdocument.getPortalType() == "Simulation Movement":
            path = subdocument.getCausalityValue()
            t = (subdocument, path)
            tree_node.visited_movement_dict[id] = t
            if path in path_set_to_check:
              yield t
          else:
            # it must be an Applied Rule
            subtree = tree_node.get(id, treeNode())
            for d in descendantGenerator(subdocument,
                                         subtree,
                                         path_set_to_check):
              yield d

      for id, t in tree_node.visited_movement_dict.iteritems():
        subdocument, path = t
        to_check = path_set_to_check
        # do we need to change/copy the set?
        if path in to_check:
          if len(to_check) == 1:
            # no more paths to check in this branch
            continue
          to_check = to_check.copy()
          to_check.remove(path)
        subtree = tree_node.get(id, treeNode())
        for d in descendantGenerator(subdocument, subtree, to_check):
          yield d

    # descend in the tree to find self:
    tree_node = path_tree
    for path_id in self.getPhysicalPath():
      tree_node = tree_node.get(path_id, treeNode())

    # explore subobjects of self
    for descendant, path in descendantGenerator(self,
                                                tree_node,
                                                remaining_path_set):
      if not isBuiltAndCompleted(descendant, path):
        return False

    return True

  def getSolverProcessValueList(self, movement=None, validation_state=None):
    """
    Returns the list of solver processes which are
    are in a given state and which apply to delivery_or_movement.
    This method is useful to find applicable solver processes
    for a delivery.

    movement -- not applicable

    validation_state -- a state of a list of states
                        to filter the result
    """
    raise NotImplementedError

  def getSolverDecisionValueList(self, movement=None, validation_state=None):
    """
    Returns the list of solver decisions which apply
    to a given movement.

    movement -- not applicable

    validation_state -- a state of a list of states
                        to filter the result
    """
    raise NotImplementedError

  def getSolvedPropertyApplicationValueList(self, movement=None, divergence_tester=None):
    """
    Returns the list of documents at which a given divergence resolution
    can be resolved at. For example, in most cases, date divergences can
    only be resolved at delivery level whereas quantities are usually
    resolved at cell level.

    The result of this method is a list of ERP5 documents.

    movement -- not applicable
    """
    raise NotImplementedError

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMappedProperty')
  def getMappedProperty(self, property):
    mapping = self.getPropertyMappingValue()
    if mapping is not None:
      # Special case: corrected quantity is difficult to handle,
      # because, if quantity is inverse in the mapping, other
      # parameters, profit quantity (deprecated) and delivery error,
      # must be inverse as well.
      if property == 'corrected_quantity':
        mapped_quantity_id = mapping.getMappedPropertyId('quantity')
        quantity = mapping.getMappedProperty(self, 'quantity')
        profit_quantity = self.getProfitQuantity() or 0
        delivery_error = self.getDeliveryError() or 0
        if mapped_quantity_id[:1] == '-':
          # XXX what about if "quantity | -something_different" is
          # specified?
          return quantity + profit_quantity - delivery_error
        else:
          return quantity - profit_quantity + delivery_error
      return mapping.getMappedProperty(self, property)
    return self.getProperty(property)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setMappedProperty')
  def setMappedProperty(self, property, value):
    mapping = self.getPropertyMappingValue()
    if mapping is not None:
      return mapping.setMappedProperty(self, property, value)
    return self.setProperty(property, value)
