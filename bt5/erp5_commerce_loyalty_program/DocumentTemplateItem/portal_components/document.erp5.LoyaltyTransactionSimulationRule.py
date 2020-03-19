# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.rule import RuleMixin
from Products.ERP5.mixin.movement_generator import MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin
from Acquisition import aq_base

class LoyaltyTransactionSimulationRule(RuleMixin,MovementCollectionUpdaterMixin):
  """  """
  # CMF Type Definition
  meta_type = 'ERP5 Loyalty Transaction Simulation Rule'
  portal_type = 'Loyalty Transaction Simulation Rule'

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
    return LoyaltyTransactionRuleMovementGenerator(applied_rule=context, rule=self)

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

class LoyaltyTransactionRuleMovementGenerator(MovementGeneratorMixin):
  def _getUpdatePropertyDict(self, input_movement):
    # Adjust loyalty point quantity according to trade model line setting
    tml = input_movement.getCausalityValue(portal_type='Trade Model Line')
    loyalty_point_quantity = tml.getLoyaltyPointQuantity()
    if not loyalty_point_quantity:
      loyalty_point_quantity =self._applied_rule.getParentValue().getTotalPrice() * tml.getLoyaltyPointPrice()
    input_movement.setQuantity(loyalty_point_quantity)
    return {'causality': input_movement.getCausalityList(),
            'delivery': None,
            'price': 1}

  def _getInputMovementList(self, movement_list=None, rounding=False):
    simulation_movement = self._applied_rule.getParentValue()
    portal = self._applied_rule.getPortalObject()
    amount_list = simulation_movement.getAggregatedAmountList(
      amount_generator_type_list=portal.getPortalAmountGeneratorAllTypeList(0))
    input_movement = aq_base(simulation_movement).__of__(self._applied_rule)
    for amount in amount_list:
      # Only take loyalty trade model line
      if amount.getResource() and [x for x in amount.getBaseApplicationList() if x.startswith('base_amount/loyalty_program')]:
        movement = input_movement.asContext(**{k: v
            for k, v in amount.__dict__.iteritems()
            if k[0] != '_' and k != 'categories'})
        base_category_set = set([x for x in amount.getBaseCategoryList() if x not in ('price_currency')])
        movement._setCategoryMembership(base_category_set,
                                        amount.getCategoryList(),
                                        base=True)
        yield movement
