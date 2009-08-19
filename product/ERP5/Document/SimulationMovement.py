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
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Globals import PersistentMapping

from Products.ERP5.Document.Movement import Movement

from zLOG import LOG, WARNING

from Acquisition import aq_base

from Products.ERP5.Document.AppliedRule import TREE_DELIVERED_CACHE_KEY, TREE_DELIVERED_CACHE_ENABLED
from Products.ERP5Type.patches.WorkflowTool import WorkflowHistoryList

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

class SimulationMovement(Movement):
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
  isMovement = 1

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
    """
      Returns the current state in simulation

      Inherit from order or delivery or parent (but use a conversion
      table to make orders planned when parent is confirmed)

      XXX: movements in zero stock rule can not acquire simulation state
    """
    delivery = self.getDeliveryValue()
    if delivery is not None:
      return delivery.getSimulationState()
    order = self.getOrderValue()
    if order is not None:
      return order.getSimulationState()
    try:
      parent_state = self.getParentValue().getSimulationState()
      return parent_to_movement_simulation_state[parent_state]
    except (KeyError, AttributeError):
      LOG('SimulationMovement.getSimulationState', WARNING,
          'Could not acquire simulation state from %s'
          % self.getRelativeUrl())
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
    """Zope publisher docstring. Documentation in ISimulationMovement"""
    # only available in BPM, so fail totally in case of working without BPM
    return self.getSimulationState() in self.getCausalityValue(
        portal_type='Business Path').getCompletedStateList()

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

  # Ordering / Delivering
  security.declareProtected( Permissions.AccessContentsInformation,
                             'requiresOrder')
  def requiresOrder(self):
    """
      Returns 1 if this needs to be ordered
    """
    if isOrderable():
      return len(self.getCategoryMembership('order')) is 0
    else:
      return 0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'requiresDelivery')
  def requiresDelivery(self):
    """
      Returns 1 if this needs to be accounted
    """
    if isDeliverable():
      return len(self.getCategoryMembership('delivery')) is 0
    else:
      return 0


  #######################################################
  # Causality Workflow Methods

  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, force=0, **kw):
    """
    Checks all existing applied rules and make sure they still apply.
    Checks for other possible rules and starts expansion process (instanciates
    applied rules and calls expand on them).

    First get all applicable rules,
    then, delete all applied rules that no longer match and are not linked to
    a delivery,
    finally, apply new rules if no rule with the same type is already applied.
    """
    portal_rules = getToolByName(self, 'portal_rules')

    tv = getTransactionalVariable(self)
    cache = tv.setdefault(TREE_DELIVERED_CACHE_KEY, {})
    cache_enabled = cache.get(TREE_DELIVERED_CACHE_ENABLED, 0)

    # enable cache
    if not cache_enabled:
      cache[TREE_DELIVERED_CACHE_ENABLED] = 1

    applied_rule_dict = {}
    applicable_rule_dict = {}
    for rule in portal_rules.searchRuleList(self, sort_on='version',
        sort_order='descending'):
      ref = rule.getReference()
      if ref and ref not in applicable_rule_dict.iterkeys():
        applicable_rule_dict[ref] = rule

    for applied_rule in self.objectValues():
      rule = applied_rule.getSpecialiseValue()
      if not applied_rule._isTreeDelivered() and not rule.test(self):
        self._delObject(applied_rule.getId())
      else:
        applied_rule_dict[rule.getPortalType()] = applied_rule

    for rule in applicable_rule_dict.itervalues():
      rule_type = rule.getPortalType()
      if rule_type not in applied_rule_dict.iterkeys():
        applied_rule = rule.constructNewAppliedRule(self, **kw)
        applied_rule_dict[rule_type] = applied_rule

    self.setCausalityState('expanded')
    # expand
    for applied_rule in applied_rule_dict.itervalues():
      applied_rule.expand(force=force, **kw)

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
    if self.getDeliveryValue() is None:
      ra = self.getRootAppliedRule()
      order = ra.getCausalityValue()
      if order is not None:
        return order
      else:
        # Ex. zero stock rule
        return ra
    else:
      explanation_value = self.getDeliveryValue()
      while explanation_value.getPortalType() not in \
              self.getPortalDeliveryTypeList() and \
          explanation_value != self.getPortalObject():
            explanation_value = explanation_value.getParentValue()
      if explanation_value != self.getPortalObject():
        return explanation_value

  # Deliverability / orderability
  security.declareProtected( Permissions.AccessContentsInformation,
                             'isOrderable')
  def isOrderable(self):
    applied_rule = self.getParentValue()
    rule = applied_rule.getSpecialiseValue()
    if rule is not None:
      return rule.isOrderable(self)
    return 0

  getOrderable = isOrderable

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isDeliverable')
  def isDeliverable(self):
    applied_rule = self.getParentValue()
    rule = applied_rule.getSpecialiseValue()
    if rule is not None:
      return rule.isDeliverable(self)
    return 0

  getDeliverable = isDeliverable

  # Simulation Dates - acquire target dates
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderStartDate')
  def getOrderStartDate(self):
    order_value = self.getOrderValue()
    if order_value is not None:
      return order_value.getStartDate()

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getOrderStopDate')
  def getOrderStopDate(self):
    order_value = self.getOrderValue()
    if order_value is not None:
      return order_value.getStopDate()

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

  security.declareProtected( Permissions.AccessContentsInformation,
      'getSolverList')
  def getSolverList(self):
    """
    Returns solvers that can fix the current divergence
    """
    return self.getParentValue().getSolverList(self)

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
    tv = getTransactionalVariable(self)
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
      except:
        result = getTreeDelivered(self, ignore_first=ignore_first)
        cache[rule_key] = result
        return result
    else:
      return getTreeDelivered(self, ignore_first=ignore_first)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isBuildable')
  def isBuildable(self):
    """Simulation Movement buildable logic"""
    if self.getDeliveryValue() is not None:
      # already delivered
      return False
    # might be buildable - business path depended
    business_path = self.getCausalityValue(portal_type='Business Path')
    explanation_value = self.getExplanationValue()
    if business_path is not None and explanation_value is not None:
      predecessor = business_path.getPredecessorValue()
      if predecessor is None:
        # first one, can be built
        return True
      else:
        for successor_related in predecessor.getSuccessorRelatedValueList():
          for business_path_movement in successor_related \
              .getRelatedSimulationMovementValueList(explanation_value):
            if successor_related.isMovementRelatedWithMovement(self,
                business_path_movement):
              business_path_movement_delivery = business_path_movement \
                  .getDeliveryValue()
              if business_path_movement_delivery is None:
                return False # related movement is not delivered yet
              business_path_movement_delivery_document = \
                  business_path_movement_delivery.getParentValue()
              # here we can optimise somehow, as
              # business_path_movement_delivery_document would repeat
              if not successor_related.isCompleted(
                  business_path_movement_delivery_document):
                # related movements delivery is not completed
                return False
    return True

  security.declareProtected( Permissions.ModifyPortalContent,
                             'appendDecision')
  def appendDecision(self, decision):
    """Appends decision, optionally initialises"""
    property = decision.divergence.tested_property
    if getattr(aq_base(self), 'divergence_history', None) is None:
      # initialise divergence history mapping
      self.divergence_history = PersistentMapping()
    if self.divergence_history.get(property, None) is None:
      self.divergence_history[property] = WorkflowHistoryList()
    self.divergence_history[property].append(decision)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'isPropertyForced')
  def isPropertyForced(self, property):
    """Check if property was forced by user"""
    divergence_history = getattr(aq_base(self), 'divergence_history', None)
    if divergence_history is None:
      return False

    for decision in divergence_history.get(property, [])[::-1]:
      # fuzzy logic:
      #  * if there was accept decision with force - force
      #  * but if there was accept without force after - do not force
      # To be discussed.
      if decision.decision == 'accept':
        if decision.force_property:
          return True
        return False
    return False
