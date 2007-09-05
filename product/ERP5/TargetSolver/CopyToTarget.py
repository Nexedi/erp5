##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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

from TargetSolver import TargetSolver
from Products.ERP5Type.DateUtils import createDateTimeFromMillis

class CopyToTarget(TargetSolver):
  """
    This solver calculates the ratio between the new (delivery) and old
    (simulation) quantity and applies this ratio to the simulation movement
    and to its parent, until a stable one is found

    XXX: This solver's name is not good, and it tries too many things.
    Once the new isDivergent engine is implemented, this solver can be
    splitted in smaller ones (one for profit and loss, one for backtracking)
    
    Backtracking alone is not enough to solve completely, it must be used with
    another solver (profit and loss, or creating a compensation branch ...)
  """
  def _generateValueDeltaDict(self, simulation_movement):
    """
      Get interesting values
      XXX: better description is possible. But is it needed ?
    """
    # Get interesting value
    old_quantity = simulation_movement.getQuantity()
    old_start_date = simulation_movement.getStartDate()
    old_stop_date = simulation_movement.getStopDate()
    new_quantity = simulation_movement.getDeliveryQuantity() * \
                   simulation_movement.getDeliveryRatio()
    new_start_date = simulation_movement.getDeliveryStartDateList()[0]
    new_stop_date = simulation_movement.getDeliveryStopDateList()[0]
    # Calculate delta
    quantity_ratio = 0
    if old_quantity not in (None,0.0): # XXX: What if quantity happens to be an integer ?
      quantity_ratio = new_quantity / old_quantity
    start_date_delta = 0
    stop_date_delta = 0
    # get the date delta in milliseconds, to prevent rounding issues
    if new_start_date is not None and old_start_date is not None:
      start_date_delta = new_start_date.millis() - old_start_date.millis()
    if new_stop_date is not None and old_stop_date is not None:
      stop_date_delta = new_stop_date.millis() - old_stop_date.millis()
    return {
      'quantity_ratio': quantity_ratio,
      'start_date_delta': start_date_delta,
      'stop_date_delta': stop_date_delta,
    }

  def solve(self, simulation_movement):
    """
      Adopt values as new target
    """
    value_dict = self._generateValueDeltaDict(simulation_movement)
    # Modify recursively simulation movement
    self._recursivelySolve(simulation_movement, **value_dict)

  def _generateValueDict(self, simulation_movement, quantity_ratio=1, 
                         start_date_delta=0, stop_date_delta=0,
                         **value_delta_dict):
    """
      Generate values to save on simulation movement.
    """
    value_dict = {}
    # Modify quantity, start_date, stop_date
    start_date = simulation_movement.getStartDate()
    if start_date is not None:
      value_dict['start_date'] = createDateTimeFromMillis(start_date.millis() + start_date_delta)
    stop_date = simulation_movement.getStopDate()
    if stop_date is not None:
      value_dict['stop_date'] = createDateTimeFromMillis(stop_date.millis() + stop_date_delta)
    value_dict['quantity'] = simulation_movement.getQuantity() * quantity_ratio
    return value_dict

  def _getParentParameters(self, simulation_movement, 
                           **value_delta_dict):
    """
      Get parent movement, and its value delta dict.
    """
    #XXX max_allowed_delta is the maximum number of days we want not to
    # account as a divergence. It should be configurable through a Rule
    max_allowed_delta = 15

    applied_rule = simulation_movement.getParentValue()
    parent_movement = applied_rule.getParentValue()
    if parent_movement.getPortalType() != "Simulation Movement":
      parent_movement = None

    for date_delta in ('start_date_delta', 'stop_date_delta'):
      if date_delta in value_delta_dict.keys():
        if abs(value_delta_dict[date_delta]) <= \
            applied_rule.getProperty('max_allowed_delta', max_allowed_delta):
          value_delta_dict.pop(date_delta)
        
    return parent_movement, value_delta_dict

  def _recursivelySolve(self, simulation_movement, is_last_movement=1, **value_delta_dict):
    """
      Update value of the current simulation movement, and update
      his parent movement.
    """
    value_dict = self._generateValueDict(simulation_movement, **value_delta_dict)

    parent_movement, parent_value_delta_dict = \
                self._getParentParameters(simulation_movement, **value_delta_dict)
    
    #if parent is not None and parent_movement.isFrozen():
      # If backtraxcking is not possible, we have to make sure that the
      # divergence is solved locally by using profit and loss
      # sm_quantity = simulation_movement.getQuantity()
      # delivery_quantity = \
      #      simulation_movement.getDeliveryValue().getQuantity()
      #  simulation_movement.edit(
      #    profit_quantity=sm_quantity - delivery_quantity)
    #else:
    if is_last_movement:
        delivery_quantity = \
            simulation_movement.getDeliveryValue().getQuantity()
        simulation_movement.setDeliveryError(delivery_quantity -
            value_dict['quantity'])
    
    delivery = simulation_movement.getDeliveryValue()
    
    # XXX Hardcoded Set 
    simulation_movement.setDestination(delivery.getDestination())
    simulation_movement.setSource(delivery.getSource())
    simulation_movement.setDestinationSection(delivery.getDestinationSection())
    simulation_movement.setSourceSection(delivery.getSourceSection())
		
    simulation_movement.edit(**value_dict)
      
    if parent_movement is not None and not parent_movement.isFrozen():
        # backtrack to the parent movement only if it is not frozen
        self._recursivelySolve(parent_movement, is_last_movement=0,
            **parent_value_delta_dict)
