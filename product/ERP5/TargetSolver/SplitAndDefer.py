##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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


from Products.ERP5.Tool.SimulationTool import registerTargetSolver
from CopyToTarget import CopyToTarget
from zLOG import LOG

class SplitAndDefer(CopyToTarget):
  """
    Split and defer simulation movement.

    Many 'deliverable movements' are created in the Simulation and
    may need to be delivered later. Solver accumulates such movements
    in the solving process and creates a new delivery

    This only works when some movements can not be delivered (excessive qty is not covered)
  """

  def __init__(self, simulation_tool, **kw):
    """
      Creates an instance of TargetSolver with parameters
    """
    CopyToTarget.__init__(self, simulation_tool, **kw)
    self.split_movement_list = []

  def solve(self, movement, new_target):
    """
      Split a movement and accumulate
    """
    target_quantity = movement.getTargetQuantity()
    new_target_quantity = new_target.target_quantity
    if target_quantity > new_target_quantity:
      split_index = 0
      new_id = "%s_split_%s" % (movement.getId(), split_index)
      while getattr(movement.aq_parent, new_id, None) is not None:
        split_index += 1
        new_id = "%s_split_%s" % (movement.getId(), split_index)
      # Adopt different dates for defferred movements
      # XXX What about quantity_unit ? resource ?
      new_movement = movement.aq_parent.newContent(portal_type = "Simulation Movement",
                                            id = new_id,
                                            efficiency = movement.getEfficiency(),
                                            target_efficiency = movement.getTargetEfficiency(),
                                            target_start_date = self.target_start_date,
                                            target_stop_date = self.target_stop_date,
                                            start_date = self.target_start_date,
                                            stop_date = self.target_stop_date,
                                            source = movement.getSource(),
                                            destination = movement.getDestination(),
                                            source_section = movement.getSourceSection(),
                                            destination_section =  movement.getDestinationSection(),
                                            order = movement.getOrder(),
                                            deliverable = movement.isDeliverable()
                                          )
      new_movement._setTargetQuantity(target_quantity - new_target_quantity)
      new_movement._setQuantity(target_quantity - new_target_quantity)
      self.split_movement_list.append(new_movement)
    CopyToTarget.solve(self, movement, new_target)

  def close(self):
    """
      After resolution has taken place,  create a new delivery
      with deliverable split movements.
    """
    movement_group = self.simulation_tool.collectMovement(self.split_movement_list)
    return self.simulation_tool.buildDeliveryList(movement_group)

registerTargetSolver(SplitAndDefer)
