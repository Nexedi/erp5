##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
##############################################################################

from TargetSolver import TargetSolver

class CopyAndPropagate(TargetSolver):
  """
  This solver will copy properties and calculate quantities for
  specified divergence list.
  """
  def solveMovement(self, movement):
    """
      Solves a movement.
    """
    movement_relative_url = movement.getRelativeUrl()
    for divergence in self.divergence_list:
      if movement_relative_url == divergence.getProperty('object_relative_url'):
        self._acceptDecision(divergence)

  def _acceptDecision(self, divergence):
    """
    Accept decision according to movement group
    """
    scope = divergence.getProperty('divergence_scope')
    simulation_movement = divergence.getProperty('simulation_movement')
    delivery = simulation_movement.getDeliveryValue()
    value_dict = {}
    quantity_ratio = None
    if scope == 'quantity':
      new_quantity = simulation_movement.getDeliveryQuantity() * \
                     simulation_movement.getDeliveryRatio()
      old_quantity = simulation_movement.getQuantity()
      quantity_ratio = 0
      if old_quantity not in (None, 0.0):
        quantity_ratio = new_quantity / old_quantity
    elif scope == 'category':
      property_id = divergence.getProperty('tested_property')
      new_value_list = delivery.getPropertyList(property_id)
      # variation_category should be edited as variation_category_list
      if property_id == 'variation_category':
        property_id = 'variation_category_list'
      value_dict[property_id] = new_value_list
    else: # otherwise we assume that scope is 'property'
      property_id = divergence.getProperty('tested_property')
      new_value = delivery.getProperty(property_id)
      value_dict[property_id] = new_value
    self._solveRecursively(simulation_movement,
                           quantity_ratio=quantity_ratio,
                           value_dict=value_dict)

  def _solveRecursively(self, simulation_movement, is_last_movement=1,
                        quantity_ratio=None, value_dict=None):
    """
      Update value of the current simulation movement, and update
      his parent movement.
    """
    delivery = simulation_movement.getDeliveryValue()

    if is_last_movement and quantity_ratio is not None:
      delivery_quantity = delivery.getQuantity()
      delivery_ratio = simulation_movement.getDeliveryRatio()
      quantity = simulation_movement.getQuantity() * quantity_ratio
      quantity_error = delivery_quantity * delivery_ratio - quantity
      value_dict['delivery_error'] = quantity_error
      value_dict['quantity'] = quantity

    simulation_movement.edit(**value_dict)

    applied_rule = simulation_movement.getParentValue()
    parent_movement = applied_rule.getParentValue()
    if parent_movement.getPortalType() == 'Simulation Movement' and \
           not parent_movement.isFrozen():
      # backtrack to the parent movement while it is not frozen
      self._solveRecursively(parent_movement, is_last_movement=0,
                             quantity_ratio=quantity_ratio,
                             value_dict=value_dict)
