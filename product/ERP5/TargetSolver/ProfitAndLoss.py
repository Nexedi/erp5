from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from .CopyToTarget import CopyToTarget

class ProfitAndLoss(CopyToTarget):
  """
    Profit and Loss target rule.

    Many 'deliverable movements' are created in the Simulation and
    either source or destination is set to a ProfitAndLoss, depending
    on the parent applied rule.
  """

  def solve(self, simulation_movement):
    """
      Movement difference as a profit (ie. a quantity coming from nowhere)
      Accumulate into delivered movement
    """
    delivery_line = simulation_movement.getDeliveryValue()
    delivery_line_quantity = delivery_line.getQuantity()
    if delivery_line_quantity is not None:
      target_quantity = delivery_line_quantity * simulation_movement.getDeliveryRatio()
      added_quantity = simulation_movement.getQuantity() - target_quantity
      simulation_movement.edit(profit_quantity=added_quantity)
    tag = 'ProfitAndLoss_solve_' + simulation_movement.getPath()
    simulation_movement.reindexObject(activate_kw={'tag': tag})
    delivery_line.activate(after_tag=tag).edit()
