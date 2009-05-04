# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
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


from DeliverySolver import DeliverySolver

class Distribute(DeliverySolver):
  """
    Update new values equally on Simulation Movements.
  """

  def solveDelivery(self, delivery):
    for movement in delivery.getMovementList():
      self.solve(movement)

  def solveMovement(self, movement):
    """
      Solve a delivery by reducing / increasing each simulation movement
      it relates to
    """
    simulation_movement_list = movement.getDeliveryRelatedValueList()

    simulation_quantity = 0.
    for simulation_movement in simulation_movement_list:
      quantity = simulation_movement.getCorrectedQuantity()
      simulation_quantity += quantity

    if simulation_quantity != 0:
      for simulation_movement in simulation_movement_list:
        simulation_movement.edit(delivery_ratio=simulation_movement.getCorrectedQuantity() / simulation_quantity)
    else:
      if len(simulation_movement_list) > 0:
        delivery_ratio = 1./len(simulation_movement_list)
      for simulation_movement in simulation_movement_list:
        simulation_movement.edit(delivery_ratio=delivery_ratio)
