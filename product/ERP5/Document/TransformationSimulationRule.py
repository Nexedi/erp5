# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5.mixin.rule import RuleMixin
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin

class TransformationSimulationRule(RuleMixin, MovementCollectionUpdaterMixin):
  """
  """
  # CMF Type Definition
  meta_type = 'ERP5 Transformation Simulation Rule'
  portal_type = 'Transformation Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Task,
    PropertySheet.Predicate,
    PropertySheet.Reference,
    PropertySheet.Version,
    PropertySheet.Rule
    )

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return TransformationRuleMovementGenerator(applied_rule=context, rule=self,
            produce_at_source=True)

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

  def testTransformationSourcing(self, context):
    # make sure to ignore produced resources to keep consumed resources
    if context.getReference().split('/', 1)[0] == 'pr':
      return False
    # context consumes a resource: maybe sourcing is required.
    # Let's see if the business process defines any trade phase that:
    # - is not yet expanded (well, we only checks parents and siblings)
    # - and precedes a phase of the current transformation
    phase = context.getTradePhase()
    parent = context.getParentValue()
    tv = getTransactionalVariable()
    key = 'isSourcingNeeded', parent.getUid()
    try:
      needed_set = tv[key]
    except KeyError:
      phase_set = set(x.getTradePhase() for x in parent.objectValues())
      phase_list = phase_set.copy()
      movement = parent.getParentValue()
      while movement.getPortalType() == 'Simulation Movement':
        phase_set.add(movement.getTradePhase())
        movement = movement.getParentValue().getParentValue()
      previous_dict = context.asComposedDocument().getPreviousTradePhaseDict()
      needed_set = tv[key] = frozenset(x for x in phase_list
        if previous_dict[x] - phase_set)
    return phase in needed_set

class TransformationRuleMovementGenerator(MovementGeneratorMixin):

  def __init__(self, *args, **kw):
    produce_at_source = kw.pop("produce_at_source", False)
    super(TransformationRuleMovementGenerator, self).__init__(*args, **kw)
    self.produce_at_source = produce_at_source

  def _getUpdatePropertyDict(self, input_movement):
    return {}

  def _getInputMovementList(self, movement_list=None, rounding=None):
    parent_movement = self._applied_rule.getParentValue()
    portal = self._applied_rule.getPortalObject()
    amount_list = parent_movement.getAggregatedAmountList(
      amount_generator_type_list=portal.getPortalAmountGeneratorAllTypeList(1))
    if self.produce_at_source:
      arrow_list = ['destination' + x[6:]
        for x in parent_movement.getCategoryMembershipList(
          ('source', 'source_section'), base=True)]
    else:
      arrow_list = parent_movement.getCategoryMembershipList(
          ('destination', 'destination_section'), base=True)
    def newMovement(reference, kw={}):
      movement = aq_base(parent_movement.asContext(**kw)).__of__(
        self._applied_rule)
      movement._setReference(reference)
      movement._setCategoryMembership(('destination', 'source_section',
                                       'destination_section', 'source'),
                                      arrow_list, base=True)
      return movement
    phase_set = set()
    for amount in amount_list:
      # Do not ignore amount with price = 0 (such behaviour can be obtained by
      # specifying a predicate on the amount generator line/cell).
      if amount.getResource():
        phase_set.add(amount.getTradePhase())
        # FIXME: Is it the right way to have source/destination and other
        #        non-Amount properties set on the generated movement ?
        movement = newMovement(amount.getCausality(), dict((k, v)
            for k, v in amount.__dict__.iteritems()
            if k[0] != '_' and k != 'categories'))
        base_category_set = set(amount.getBaseCategoryList())
        base_category_set.remove('price_currency') # XXX
        movement._setCategoryMembership(base_category_set,
                                        amount.getCategoryList(),
                                        base=True)
        movement.quantity = - movement.quantity
        # aggregation of items should not be propagated to what comes from transformation
        movement.setAggregateList([])
        yield movement
    phase_dict = parent_movement.asComposedDocument() \
                                .getPreviousTradePhaseDict(phase_set)
    final_set = phase_set.copy()
    previous_set = final_set.copy()
    while previous_set:
      phase_list = phase_dict[previous_set.pop()]
      final_set.difference_update(phase_list)
      previous_set.update(phase_list)
    # We should not need an option not to generate movements for intermediate
    # resources. This can be configured on Trade Model Paths by filtering out
    # movement with an industrial_phase (other properties like reference
    # starting with "pr/" is possible). The drawback with such filter is that
    # Same Total Quantity check must be disabled.
    if 1:
      cr_quantity = - parent_movement.getQuantity()
      def newIntermediateMovement(reference_prefix, industrial_phase, **kw):
        movement = newMovement(reference_prefix + phase, kw)
        movement._setTradePhase(phase)
        movement._setIndustrialPhase('trade_phase/' + industrial_phase)
        return movement
      for phase in phase_set:
        for previous in phase_dict[phase]:
          # for consumed resource
          yield newIntermediateMovement('cr/', previous, quantity=cr_quantity)
        if phase not in final_set:
          # for produced resource
          yield newIntermediateMovement('pr/', phase)
    movement = newMovement('pr')
    movement._setTradePhaseList(final_set)
    yield movement
