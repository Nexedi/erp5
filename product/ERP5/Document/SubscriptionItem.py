# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Errors import SimulationError
from Products.ERP5.Document.Item import Item
from Products.ERP5.mixin.composition import CompositionMixin
from Products.ERP5.mixin.rule import MovementGeneratorMixin
from Products.ERP5.mixin.periodicity import PeriodicityMixin
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5Type.Base import Base

from zLOG import LOG

class SubscriptionItem(Item, CompositionMixin, MovementGeneratorMixin, PeriodicityMixin):
  """
    A SubscriptionItem is an Item which expands itself
    into simulation movements which represent the item future.
    Examples of subscription items (or subclasses) include:
    employee paysheet contracts, telecommunication subscriptions,
    banking service subscriptions, etc
  """
  meta_type = 'ERP5 Subscription Item'
  portal_type = 'Subscription Item'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Price
                    , PropertySheet.Item
                    , PropertySheet.Amount
                    , PropertySheet.Reference
                    , PropertySheet.Periodicity
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.IExpandableItem,
                            interfaces.IMovementGenerator,
                           )

  # IExpandable interface implementation
  @UnrestrictedMethod # YXU - Is it a good permission setting?
  def expand(self, applied_rule_id=None, activate_kw=None, **kw):
    """
      Lookup start / stop properties in related Open Order
      or Path and expand.
    """
    # only try to expand if we are not in draft state
    if self.getValidationState() in ('draft', ): # XXX-JPS harcoded
      return

    # do not expand if no bp/stc is applied
    if self.getSpecialiseValue() is None:
      return

    # use hint if provided (but what for ?) XXX-JPS
    if applied_rule_id is not None:
      portal_simulation = getToolByName(self, 'portal_simulation')
      my_applied_rule = portal_simulation[applied_rule_id]
    else:
      my_applied_rule = self._getRootAppliedRule(activate_kw=activate_kw)

    # Pass expand
    if my_applied_rule is not None:
      my_applied_rule.expand(activate_kw=activate_kw, **kw) # XXX-JPS why **kw ?

  # IExpandableItem interface implementation
  def getSimulationMovementSimulationState(self, simulation_movement):
    """Returns the simulation state for this simulation movement.

    This generic implementation assumes that if there is one open order line
    which is validated or archived, the movements will be planned. This
    behaviour might have to be adapted in subclasses.
    """
    for path in self.getAggregateRelatedValueList(
        portal_type=self.getPortalObject().getPortalSupplyPathTypeList(),):
      if path.getValidationState() in ('validated', 'archived'):
        return 'planned'
    return 'draft'

  def isSimulated(self):
    """
      We are never simulated (unlike deliveries)
    """
    return False

  def getRuleReference(self):
    """Returns an appropriate rule reference.
    XXX Copy/Paste from delivery
    """
    method = self._getTypeBasedMethod('getRuleReference')
    if method is not None:
      return method()
    else:
      raise SimulationError('%s_getRuleReference script is missing.'
                            % self.getPortalType().replace(' ', ''))

  @UnrestrictedMethod # XXX-JPS What is this ?
  def updateAppliedRule(self, rule_reference=None, rule_id=None, **kw):
    """
    Create a new Applied Rule if none is related, or call expand
    on the existing one.

    The chosen applied rule will be the validated rule with reference ==
    rule_reference, and the higher version number.
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
      raise ValueError, 'No such rule as %r is found' % rule_reference

    self._createAppliedRule(rule_id, **kw)

  def _createAppliedRule(self, rule_id, activate_kw=None, **kw):
    """
      Create a new Applied Rule is none is related, or call expand
      on the existing one.
    """
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
            constructNewAppliedRule(portal_simulation,
                                    activate_kw=activate_kw)
        # Set causality
        my_applied_rule.setCausalityValue(self)
        # We must make sure this rule is indexed
        # now in order not to create another one later
        my_applied_rule.reindexObject(activate_kw=activate_kw, **kw)
    elif len(my_applied_rule_list) == 1:
      # Re expand the rule if possible
      my_applied_rule = my_applied_rule_list[0]
    else:
      raise SimulationError('Delivery %s has more than one applied'
                            ' rule.' % self.getRelativeUrl())

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
        applied_rule_id=my_applied_rule_id,
        activate_kw=activate_kw, **kw)

  def _getRootAppliedRule(self, tested_base_category_list=None,
                                activate_kw=None):
    """
      Returns existing root applied rule or, if none,
      create a new one a return it
    """
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
        search_rule_kw = { 'sort_on': 'version', 'sort_order': 'descending' }
        if self.getRuleReference() is None:
          rule_value_list = portal_rules.searchRuleList(self, **search_rule_kw)
          if len(rule_value_list) > 1:
            raise SimulationError('Expandable Document %s has more than one'
                                  ' matching rule.' % self.getRelativeUrl())
        else:
          rule_value_list = portal_rules.searchRuleList(self,
            reference=self.getRuleReference(), **search_rule_kw)
        if len(rule_value_list):
          rule_value = rule_value_list[0]
          my_applied_rule = rule_value.constructNewAppliedRule(portal_simulation,
                                    activate_kw=activate_kw)
          # Set causality
          my_applied_rule.setCausalityValue(self)
          # We must make sure this rule is indexed
          # now in order not to create another one later
          my_applied_rule.reindexObject(activate_kw=activate_kw) # XXX-JPS removed **kw
    elif len(my_applied_rule_list) == 1:
      # Re expand the rule if possible
      my_applied_rule = my_applied_rule_list[0]
    else:
      raise SimulationError('Expandable Document %s has more than one root'
                            ' applied rule.' % self.getRelativeUrl())

    return my_applied_rule

  # IMovementGenerator interface implementation
  def _getUpdatePropertyDict(self, input_movement):
    # Default implementation bellow can be overriden by subclasses
    return {}

  def _getInputMovementList(self, movement_list=None, rounding=None):
    """
      Generate the list of input movements by looking at all
      open order lines relating to this subscription item.

      TODO: clever handling of quantity (based on the nature
      of resource, ie. float or unit)
    """
    from Products.ERP5Type.Document import newTempMovement
    result = []
    catalog_tool = getToolByName(self, 'portal_catalog')

    # Now generate movements for each valid open order
    for movement in catalog_tool(portal_type="Open Sale Order Line",
        default_aggregate_uid=self.getUid(),
        validation_state=('open', 'validated', 'archived'), # XXX-JPS hard coding
        sort_on=(('effective_date', 'descending'),),
        limit=1 # Note Luke: Support the newest Open Order which defines
                # something for current subscription item
        ): # YXU-Why we have a list here?
        resource = movement.getResource()
        start_date = movement.getStartDate()
        stop_date = movement.getStopDate()
        if start_date is None or stop_date is None or start_date>=stop_date:
          # infinity nor time back machine does not exist
          continue
        source = movement.getSource()
        source_section = movement.getSourceSection()
        source_decision = movement.getSourceDecision()
        destination = movement.getDestination()
        destination_section = movement.getDestinationSection()
        destination_decision = movement.getDestinationDecision()
        quantity = movement.getQuantity()
        quantity_unit = movement.getQuantityUnit()
        price = movement.getPrice()
        price_currency = movement.getPriceCurrency()
        base_application_list = movement.getBaseApplicationList()
        base_contribution_list = movement.getBaseContributionList()
        use_list = movement.getUseList()

        specialise = movement.getSpecialise()
        current_date = start_date
        id_index = 0
        while current_date < stop_date:
          next_date = self.getNextPeriodicalDate(current_date)
          generated_movement = newTempMovement(self, 'subscription_%s' % id_index)
          generated_movement._edit(  aggregate_value=self,
                                     resource=resource,
                                     quantity=quantity,
                                     quantity_unit=quantity_unit,
                                     price=price,
                                     price_currency=price_currency,
                                     start_date=current_date,
                                     stop_date=next_date,
                                     source=source,
                                     source_section=source_section,
                                     source_decision=source_decision,
                                     destination=destination,
                                     destination_section=destination_section,
                                     destination_decision=destination_decision,
                                     specialise=specialise,
                                     base_application_list=base_application_list,
                                     base_contribution_list=base_contribution_list,
                                     use_list=use_list
                                    )
          result.append(generated_movement)
          current_date = next_date
          id_index += 1

    return result

  # XXX BELOW HACKS
  def getResource(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getResource()

  def getStartDate(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getStartDate()

  def getStopDate(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getStopDate()

  def getSource(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSource()

  def getSourceSection(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSourceSection()

  def getDestination(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getDestination()

  def getDestinationSection(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getDestinationSection()

  def getQuantity(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getQuantity()

  def getQuantityUnit(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getQuantityUnit()

  def getPrice(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getPrice()

  def getPriceCurrency(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getPriceCurrency()

  def getSpecialise(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSpecialise()

  def getSpecialiseList(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return []
    return open_order_line.getSpecialiseList()

  def getSpecialiseValue(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return None
    return open_order_line.getSpecialiseValue()

  def getSpecialiseValueList(self):
    open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
    if open_order_line is None:
      return []
    return open_order_line.getSpecialiseValueList()

  def _getCategoryMembershipList(self, category, spec=(), filter=None,
      portal_type=(), base=0, keep_default=1, checked_permission=None, **kw):
    if category == 'specialise':
      open_order_line = self.getAggregateRelatedValue(portal_type='Open Sale Order Line')
      return open_order_line._getCategoryMembershipList(category, spec=spec, filter=filter,
                             portal_type=portal_type, base=base, keep_default=keep_default,
                             checked_permission=checked_permission, **kw)
    return Base._getCategoryMembershipList(self, category, spec=spec, filter=filter,
                portal_type=portal_type, base=base, keep_default=keep_default,
                checked_permission=checked_permission, **kw)
