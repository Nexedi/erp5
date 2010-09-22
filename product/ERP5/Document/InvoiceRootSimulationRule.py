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
"""

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.mixin.rule import RuleMixin, MovementGeneratorMixin
from Products.ERP5.mixin.movement_collection_updater import \
     MovementCollectionUpdaterMixin

class InvoiceRootSimulationRule(RuleMixin, MovementCollectionUpdaterMixin, Predicate):
  """
  """
  # CMF Type Definition
  meta_type = 'ERP5 Invoice Root Simulation Rule'
  portal_type = 'Invoice Root Simulation Rule'

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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """
    Tells whether generated movement needs to be accounted or not.

    Invoice movement are never accountable, so simulation movement for
    invoice movements should not be accountable either.
    """
    return False

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return InvoiceRuleMovementGenerator(applied_rule=context, rule=self)

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

class InvoiceRuleMovementGenerator(MovementGeneratorMixin):

  def _getInputMovementList(self, movement_list=None, rounding=None):
    """Input movement list comes from delivery"""
    delivery = self._applied_rule.getDefaultCausalityValue()
    if delivery is None:
      return []
    else:
      ret = []
      existing_movement_list = self._applied_rule.objectValues()
      for movement in delivery.getMovementList(
        portal_type=(delivery.getPortalInvoiceMovementTypeList() + \
                     delivery.getPortalTaxMovementTypeList())): # This is bad XXX-JPS - use use
        simulation_movement = self._getDeliveryRelatedSimulationMovement(movement)
        if simulation_movement is None or \
               simulation_movement in existing_movement_list:
          ret.append(movement)
      return ret

  def _getDeliveryRelatedSimulationMovement(self, delivery_movement):
    """Helper method to get the delivery related simulation movement.
    This method is more robust than simply calling getDeliveryRelatedValue
    which will not work if simulation movements are not indexed.
    """
    simulation_movement = delivery_movement.getDeliveryRelatedValue()
    if simulation_movement is not None:
      return simulation_movement
    # simulation movement was not found, maybe simply because it's not indexed
    # yet. We'll look in the simulation tree and try to find it anyway before
    # creating another simulation movement.
    # Try to find the one from trade model rule, which is the most common case
    # where we may expand again before indexation of simulation movements is
    # finished.
    delivery = delivery_movement.getExplanationValue()
    for movement in delivery.getMovementList():
      related_simulation_movement = movement.getDeliveryRelatedValue()
      if related_simulation_movement is not None:
        for applied_rule in related_simulation_movement.contentValues():
          for simulation_movement in applied_rule.contentValues():
            if simulation_movement.getDeliveryValue() == delivery_movement:
              return simulation_movement
    return None
