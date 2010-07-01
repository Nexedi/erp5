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

import zope.interface
from Products.ERP5Type import interfaces
from DeliverySolver import DeliverySolver

class FIFO(DeliverySolver):
  """
  The FIFO solver reduces delivered quantity by reducing the quantity of
  simulation movements from the last order.
  """

  # Declarative interfaces
  zope.interface.implements(interfaces.IDeliverySolver)

  title = 'FIFO Solver'

  # IDeliverySolver Implementation
  def __init__(self, simulation_movement_list):
    """
      Move this to mixin
    """
    self.simulation_movement_list = simulation_movement_list

  def getTotalQuantity(self):
    """
      Move this to mixin
    """
    total_quantity = 0
    for movement in self.simulation_movement_list:
      total_quantity += movement.getQuantity()
    return total_quantity

  def setTotalQuantity(self, new_quantity, activate_kw=None):
    """
    """
    result = []
    remaining_quantity = self.getTotalQuantity() - new_quantity
    if remaining_quantity < 0:
      return result
    simulation_movement_list = self._getSimulationMovementList()
    for movement in simulation_movement_list:
      if remaining_quantity:
        quantity = movement.getQuantity()
        if quantity < remaining_quantity:
          result.append((movement, quantity))
          remaining_quantity -= quantity
          movement.edit(quantity=0, delivery_ratio=0, activate_kw=activate_kw)
        else:
          result.append((movement, remaining_quantity))
          movement_quantity = quantity - remaining_quantity
          movement.edit(quantity=movement_quantity,
                        delivery_ratio=movement_quantity / new_quantity,
                        activate_kw=activate_kw)
          remaining_quantity = 0
    # Return movement, split_quantity tuples
    return result

  def _getSimulationMovementList(self):
    """
    Returns a list of simulation movement sorted from the last order.
    """
    simulation_movement_list = self.simulation_movement_list
    if len(simulation_movement_list) > 1:
      return sorted(simulation_movement_list,
        key=lambda x:x.getExplainationValue().getStartDate(), reverse=True)
    else:
      return simulation_movement_list
