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

from Products.ERP5.MovementCollectionDiff import _getPropertyAndCategoryList
from Products.ERP5Type.Globals import PersistentMapping
from CopyToTarget import CopyToTarget
from Acquisition import aq_base

class SplitAndDefer(CopyToTarget):
  """
    Split and defer simulation movement.

    Many 'deliverable movements' are created in the Simulation and
    may need to be delivered later. Solver accumulates such movements
    in the solving process and creates a new delivery

    This only works when some movements can not be delivered
    (excessive qty is not covered)
  """

  def solve(self, simulation_movement):
    """
      Split a simulation movement and accumulate
    """
    movement_quantity = simulation_movement.getQuantity()
    delivery_quantity = simulation_movement.getDeliveryQuantity()
    new_movement_quantity = delivery_quantity * simulation_movement.getDeliveryRatio()
    applied_rule = simulation_movement.getParentValue()
    rule = applied_rule.getSpecialiseValue()

    # When accounting, the debit price is expressed by a minus quantity.
    # Thus, we must take into account the both minus and plus quantity.
    if ((movement_quantity < new_movement_quantity <= 0) or
        (movement_quantity > new_movement_quantity >= 0)):
      split_index = 0
      new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
      while getattr(aq_base(applied_rule), new_id, None) is not None:
        split_index += 1
        new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
      # Adopt different dates for deferred movements
      movement_dict = _getPropertyAndCategoryList(simulation_movement)
      # new properties
      delivery = simulation_movement.getDeliveryValue()
      aggregate_set = set(simulation_movement.getAggregateList())
      aggregate_diff_set = aggregate_set.difference(delivery.getAggregateList())
      movement_dict.update(
        portal_type="Simulation Movement",
        id=new_id,
        quantity=movement_quantity - new_movement_quantity,
        activate_kw=self.activate_kw,
        delivery=None,
        **self.additional_parameters
      )
      new_movement = applied_rule.newContent(**movement_dict)
      # Dirty code until IPropertyRecordable is revised.
      # Merge original simulation movement recorded property to new one.
      recorded_property_dict = simulation_movement._getRecordedPropertyDict(None)
      if recorded_property_dict:
        new_movement_recorded_property_dict = new_movement._getRecordedPropertyDict(None)
        if new_movement_recorded_property_dict is None:
          new_movement_recorded_property_dict = new_movement._recorded_property_dict = PersistentMapping()
        new_movement_recorded_property_dict.update(recorded_property_dict)
      # record zero quantity property, because this was originally zero.
      # without this, splitanddefer after accept decision does not work
      # properly.
      current_quantity = new_movement.getQuantity()
      new_movement.setQuantity(0)
      new_movement.recordProperty('quantity')
      new_movement.setQuantity(current_quantity)
      start_date = getattr(self, 'start_date', None)
      if start_date is not None:
        new_movement.recordProperty('start_date')
        new_movement.edit(start_date=start_date)
      stop_date = getattr(self, 'stop_date', None)
      if stop_date is not None:
        new_movement.recordProperty('stop_date')
        new_movement.edit(stop_date=stop_date)

      new_movement.recordProperty('aggregate')
      new_movement.edit(aggregate_list = list(aggregate_diff_set))
      new_movement.expand(activate_kw=self.additional_parameters)

      # Only update simulation movement if quantity was changed.
      simulation_movement.recordProperty('aggregate')
      simulation_movement.edit(aggregate_list=delivery.getAggregateList())

    # adopt new quantity on original simulation movement
    simulation_movement.edit(quantity=new_movement_quantity)
    simulation_movement.setDefaultActivateParameterDict(self.activate_kw)
    simulation_movement.expand(activate_kw=self.additional_parameters)

    # SplitAndDefer solves the divergence at the current level, no need to
    # backtrack.
