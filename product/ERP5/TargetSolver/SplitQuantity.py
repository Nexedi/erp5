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

from CopyToTarget import CopyToTarget
from zLOG import LOG

class SplitQuantity(CopyToTarget):
  """
    Split a simulation movement based on a resource quantity.
  """

  def solve(self, simulation_movement):
    """
      From simulation_movement, generate new_movement containing self.quantity
      resources, of start_date self.start_date and stop_date self.stop_date.
      
      movement.quantity is updated
      
      XXX incomplete docstring
    """
    split_index = 0
    new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
    while getattr(simulation_movement.getParentValue(), new_id, None) is not None:
      split_index += 1
      new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
    # Adopt different dates for defferred movements
    new_movement = simulation_movement.getParentValue().newContent(
      portal_type = "Simulation Movement",
      id = new_id,
      efficiency = simulation_movement.getEfficiency(),
      start_date = self.start_date,
      stop_date = self.stop_date,
      # XXX resource
      order = simulation_movement.getOrder(),
      deliverable = simulation_movement.isDeliverable(),
      quantity = self.quantity,
      source = simulation_movement.getSource(),
      destination = simulation_movement.getDestination(),
      source_section = simulation_movement.getSourceSection(),
      destination_section = simulation_movement.getDestinationSection(),
      activate_kw = self.activate_kw,
      **self.additional_parameters
    )
    simulation_movement._v_activate_kw = self.activate_kw
    simulation_movement.edit (
      quantity = (simulation_movement.getQuantity() - self.quantity)
                 * simulation_movement.getDeliveryRatio()
    )
    #XXX: vincent: I don't understand why it's multiplicated.
    return new_movement
