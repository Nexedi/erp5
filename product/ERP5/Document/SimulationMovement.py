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
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from Products.ERP5.Document.Movement import Movement

from zLOG import LOG, WARNING

from Acquisition import aq_base

from Products.ERP5.Document.AppliedRule import TREE_DELIVERED_CACHE_KEY, TREE_DELIVERED_CACHE_ENABLED
from Products.ERP5.mixin.property_recordable import PropertyRecordableMixin

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

class SimulationMovement(Movement, PropertyRecordableMixin):
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
    """
      Returns the current state in simulation

      Inherit from order or delivery or parent (but use a conversion
      table to make orders planned when parent is confirmed)

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
    delivery_value = self.getDeliveryValue()
    if delivery_value is None:
      ra = self.getRootAppliedRule()
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

  def asComposedDocument(self, *args, **kw):
    # XXX: What delivery should be used to find amount generator lines ?
    #      With the currently enabled code, entire branches in the simulation
    #      tree get (temporary) deleted when new delivery lines are being built
    #      (and don't have yet a specialise value).
    #      With the commented code, changing the STC on a SIT generated from a
    #      SPL/SO would have no impact (and would never make the SIT divergent).
    #return self.getRootSimulationMovement() \
    #           .getDeliveryValue() \
    #           .asComposedDocument(*args, **kw)
    while 1:
      delivery_value = self.getDeliveryValue()
      if delivery_value is not None:
        return delivery_value.asComposedDocument(*args, **kw)
      # below code is for compatibility with old rules
      grand_parent = self.getParentValue().getParentValue()
      if grand_parent.getPortalType() == 'Simulation Tool':
        return self.getOrderValue().asComposedDocument(*args, **kw)
      self = grand_parent

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
    if self.getDeliveryValue() is not None:
      # already delivered
      return False

    # might be buildable - business path dependent
    business_path = self.getCausalityValue(portal_type='Business Path')
    explanation_value = self.getExplanationValue()
    if business_path is None or explanation_value is None:
      return True

    return len(business_path.filterBuildableMovementList([self])) == 1

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
    else:
      return self.getProperty(property)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setMappedProperty')
  def setMappedProperty(self, property, value):
    mapping = self.getPropertyMappingValue()
    if mapping is not None:
      return mapping.setMappedProperty(self, property, value)
    else:
      return self.setProperty(property, value)
