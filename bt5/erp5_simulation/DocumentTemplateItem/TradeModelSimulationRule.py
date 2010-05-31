# -*- coding: utf-8 -*-
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
from Products.ERP5.mixin.rule import RuleMixin, MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin

class TradeModelSimulationRule(RuleMixin, MovementCollectionUpdaterMixin, Predicate):
  """
    Rule for Trade Model
  """
  # CMF Type Definition
  meta_type = 'ERP5 Trade Model Simulation Rule'
  portal_type = 'Trade Model Simulation Rule'

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

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return TradeModelRuleMovementGenerator(applied_rule=context, rule=self)

  def _getMovementGeneratorContext(self, context):
    """
    Return the movement generator context to use for expand
    """
    return context

  def _getMovementGeneratorMovementList(self, context):
    """
    Return the movement lists to provide to the movement generator
    """
    return []

  def _isProfitAndLossMovement(self, movement):
    # For a kind of trade rule, a profit and loss movement lacks source
    # or destination.
    return (movement.getSource() is None or movement.getDestination() is None)

class TradeModelRuleMovementGenerator(MovementGeneratorMixin):

  def getGeneratedMovementList(self, movement_list=None, rounding=False):
    """
    Generates list of movements
    XXX-JPS This could become a good default implementation 
            but I do not understand why input system not used here
          (I will rewrite this)
    """
    result = []
    simulation_movement = self._applied_rule.getParentValue()
    trade_model = simulation_movement.asComposedDocument()

    if trade_model is None:
      return result

    context_movement = context.getParentValue()
    rule = context.getSpecialiseValue()
    for amount in context_movement.getAggregatedAmountList(
        # XXX add a 'trade_amount_generator' group type
        amount_generator_type_list=('Purchase Trade Condition',
                                    'Sale Trade Condition',
                                    'Trade Model Line')):
      # business path specific
      business_path_list = trade_model.getPathValueList(
          trade_phase=amount.getTradePhaseList()) # Why a list of trade phases ? XXX-JPS
      if len(business_path_list) == 0:
        raise ValueError('Cannot find Business Path')

      if len(business_path_list) != 1:
        raise NotImplementedError('Only one Business Path is supported')

      business_path = business_path_list[0]

      kw = self._getPropertyAndCategoryList(context_movement, business_path,
                                            rule)

      # rule specific
      kw['price'] = amount.getPrice() or amount.getEfficiency()
      kw['resource'] = amount.getProperty('resource_list') # Inconsistent... list and not list XXX-JPS
      kw['reference'] = amount.getProperty('reference')
      kw['quantity'] = amount.getProperty('quantity')
      kw['base_application'] = amount.getProperty(
          'base_application_list')
      kw['base_contribution'] = amount.getProperty(
          'base_contribution_list')

      kw['order'] = None
      kw['delivery'] = None # Where does this come from ??? XXX-JPS - Why not None ?
                            # XXX-JPS Way too many properties are copied

      simulation_movement = context.newContent(
        portal_type=RuleMixin.movement_type,
        temp_object=True,
        **kw)
      result.append(simulation_movement)

    return movement_list
