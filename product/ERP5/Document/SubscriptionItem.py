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
from Products.ERP5.mixin.rule import MovementGeneratorMixin
from Products.ERP5.mixin.periodicity import PeriodicityMixin

from zLOG import LOG

class SubscriptionItem(Item, MovementGeneratorMixin, PeriodicityMixin):
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
  zope.interface.implements(interfaces.IExpandable,
                            interfaces.IMovementGenerator,
                           )

  # IExpandable interface implementation
  def expand(self, applied_rule_id=None, activate_kw=None, **kw):
    """
      Lookup start / stop properties in related Open Order
      or Path and expand.
    """
    # only try to expand if we are not in draft state
    if self.getValidationState() in ('draft', ): # XXX-JPS harcoded
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

  def isSimulated(self):
    """
      We are never simulated (unlike deliveries)
    """
    return False

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
        rule_value_list = portal_rules.searchRuleList(self, 
                 tested_base_category_list=tested_base_category_list)
        if len(rule_value_list) > 1:
          raise SimulationError('Expandable Document %s has more than one'
                                ' matching rule.' % self.getRelativeUrl())
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

    # Try to find the source open order
    open_order_movement_list = self.getAggregateRelatedValueList(
                portal_type="Open Sale Order Line") # XXX-JPS Hard Coded    
    if not open_order_movement_list:
      return result

    # Find out which parent open orders
    explanation_uid_list = map(lambda x:x.getParentUid(), open_order_movement_list) # Instead, should call getDeliveryValue or equivalent
    open_order_list = catalog_tool.searchResults(uid = explanation_uid_list,
                                                 validation_state = 'validated') # XXX-JPS hard coding

    # Now generate movements for each valid open order
    for movement in open_order_movement_list:
      if movement.getParentValue().getValidationState() in ('open', 'validated'): # XXX-JPS hard coding
        resource = movement.getResource()
        start_date = movement.getStartDateRangeMin() # Is this appropriate ?
        stop_date = movement.getStartDateRangeMax() # Is this appropriate ?
        source = movement.getSource()
        source_section = movement.getSourceSection()
        destination = movement.getDestination()
        destination_section = movement.getDestinationSection() # XXX More arrows ? use context instead ?
        quantity = self.getQuantity() # Is it so ? XXX-JPS
        quantity_unit = movement.getQuantityUnit()
        price = movement.getPrice()
        specialise = movement.getSpecialise()
        current_date = self.getNextPeriodicalDate(start_date)
        id_index = 0
        while current_date < stop_date:
          next_date = self.getNextPeriodicalDate(current_date)
          generated_movement = newTempMovement(self, 'subscription_%s' % id_index)
          generated_movement._edit(  aggregate_value=self,
                                     resource=resource,
                                     quantity=quantity,
                                     quantity_unit=quantity_unit,
                                     price=price,
                                     start_date=current_date,
                                     stop_date=next_date,
                                     source=source,
                                     source_section=source_section,
                                     destination=destination,
                                     destination_section=destination_section,
                                     specialise=specialise,
                                #     delivery_value=movement # ??? to be confirmed - if we want order step or not
                                    )
          result.append(generated_movement)
          current_date = next_date
          id_index += 1

    # And now return result
    return result
