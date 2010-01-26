##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
XXX This file is experimental for new simulation implementation, and
will replace DeliveryRule.
"""

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.mixin.rule import RuleMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin
from Products.ERP5.MovementCollectionDiff import _getPropertyAndCategoryList

# XXX this class should be moved to Rule.py once new simulation is fully
# integrated.
class Rule(RuleMixin, MovementCollectionUpdaterMixin, Predicate):
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.IRule,
                            interfaces.IDivergenceController,
                            interfaces.IMovementCollectionUpdater,)

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

  security.declareProtected(Permissions.View, 'getDivergenceList')
  def getDivergenceList(self, movement):
    """
    Returns a list of divergences of the movements provided
    in delivery_or_movement.

    movement -- a movement, a delivery, a simulation movement,
                or a list thereof
    """
    if movement.getDelivery() is None:
      return []
    result_list = []
    for divergence_tester in self._getDivergenceTesterList(
      exclude_quantity=False):
      result = divergence_tester.explain(movement)
      if isinstance(result, (list, tuple)): # for compatibility
        result_list.extend(result)
      elif result is not None:
        result_list.append(result)
    return result_list

class TradeModelRule(Rule):
  """
    Rule for Trade Model
  """
  # CMF Type Definition
  meta_type = 'ERP5 Trade Model Rule'
  portal_type = 'Trade Model Rule'

  def _getMovementGenerator(self):
    """
    Return the movement generator to use in the expand process
    """
    return TradeModelRuleMovementGenerator()

  def _getMovementGeneratorContext(self, context):
    """
    Return the movement generator context to use for expand
    """
    return context

  def _getMovementGeneratorMovementList(self):
    """
    Return the movement lists to provide to the movement generator
    """
    return []

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

class TradeModelRuleMovementGenerator(MovementGeneratorMixin):
  def getGeneratedMovementList(self, context, movement_list=None,
                                rounding=False):
    """
    Generates list of movements
    """
    movement_list = []
    trade_condition = context.getTradeConditionValue()
    business_process = context.getBusinessProcessValue()

    if trade_condition is None or business_process is None:
      return movement_list

    context_movement = context.getParentValue()
    for amount in trade_condition.getAggregatedAmountList(context_movement):
      # business path specific
      business_path_list = business_process.getPathValueList(
          trade_phase=amount.getTradePhaseList())
      if len(business_path_list) == 0:
        raise ValueError('Cannot find Business Path')

      if len(business_path_list) != 1:
        raise NotImplementedError('Only one Business Path is supported')

      business_path = business_path_list[0]

      kw = self._getPropertyAndCategoryList(context_movement, business_path)

      # rule specific
      kw['price'] = amount.getProperty('price')
      kw['resource'] = amount.getProperty('resource_list')
      kw['reference'] = amount.getProperty('reference')
      kw['quantity'] = amount.getProperty('quantity')
      kw['base_application'] = amount.getProperty(
          'base_application_list')
      kw['base_contribution'] = amount.getProperty(
          'base_contribution_list')

      simulation_movement = context.newContent(
        portal_type=RuleMixin.movement_type,
        temp_object=True,
        order=None,
        delivery=None,
        **kw)
      movement_list.append(simulation_movement)

    return movement_list
