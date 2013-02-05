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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.rule import RuleMixin, MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin

class DeliveryRootSimulationRule(RuleMixin, MovementCollectionUpdaterMixin):
  """
  Delivery Rule object make sure an Delivery in the simulation
  is consistent with the real delivery

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Delivery Root Simulation Rule'
  portal_type = 'Delivery Root Simulation Rule'

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
    return DeliveryRuleMovementGenerator(applied_rule=context, rule=self)

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

class DeliveryRuleMovementGenerator(MovementGeneratorMixin):

  def _getPortalDeliveryMovementTypeList(self):
    return self._rule.getPortalObject().getPortalDeliveryMovementTypeList()

  def _getInputMovementList(self, movement_list=None, rounding=None):
    """Input movement list comes from delivery"""
    delivery = self._applied_rule.getDefaultCausalityValue()
    if delivery is None:
      return []
    else:
      result = []
      for movement in delivery.getMovementList(
        portal_type=self._getPortalDeliveryMovementTypeList()):
        simulation_movement_list = movement.getDeliveryRelatedValueList()
        if not simulation_movement_list or self._applied_rule in (
            simulation_movement.getParentValue()
            for simulation_movement in simulation_movement_list):
          result.append(movement)
      return result
