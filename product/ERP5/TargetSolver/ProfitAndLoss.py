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

class ProfitAndLoss(CopyToTarget):
  """
    Profit and Loss target rule.

    Many 'deliverable movements' are created in the Simulation and
    either source or destination is set to a ProfitAndLoss, depending
    on the parent applied rule.
  """

  def solve(self, movement, new_target):
    """
      Movement difference as a profit (ie. a quantity coming from nowhere)
      Accumulate into delivered movement
    """
    target_quantity = movement.getTargetQuantity()
    new_target_quantity = new_target.target_quantity
    if target_quantity != new_target_quantity:
      previous_profit_quantity = movement.getProfitQuantity()
      movement.setProfitQuantity(new_target_quantity - target_quantity)
      new_profit_quantity = movement.getProfitQuantity()
      delivery_value = movement.getDeliveryValue()
      if delivery_value is not None:
        delivery_value.setProfitQuantity(delivery_value.getProfitQuantity() + new_profit_quantity -  previous_profit_quantity)
    CopyToTarget.solve(self, movement, new_target)

registerTargetSolver(ProfitAndLoss)
