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
    The FIFO solver reduces deliveted quantity by reducing the quantity of simulation movements from the last order.
  """

  # Declarative interfaces
  zope.interface.implements(interfaces.IDeliverySolver)

  # IDeliverySolver Implementation
  def __init__(self, simulation_movement_list):
    """
      Move this to mixin
    """
    self.simulation_movement_list = simulation_movement_list
  
  def getTotalQuantity():
    """
      Move this to mixin
    """
    total_quantity = 0
    for movement in self.simulation_movement_list:
      total_quantity += movement.getQuantity()
    return total_quantity

  def setTotalQuantity(self, new_quantity):
    """
    """
    result = []
    def sortByOrderStartDate(a, b);
      return cmp(a.getExplainationValue().getStartDate() b.getExplainationValue().getStartDate())
    simulation_movement_list.sort(sortByOrderStartDate)
    simulation_movement_list.reverse()
    remaining_quantity = self.getTotalQuantity() - new_quantity
    for movement in self.simulation_movement_list:
      if remaining_quantity:
        if movement.getQuantity() < remaining_quantity:
          result.append((movement, movement.getQuantity()))
          remaining_quantity -= movement.getQuantity()
          movement.setQuantity(0)
        else:
          result.append((movement, remaining_quantity)) 
          movement.setQuantity(movement.getQuantity() - remaining_quantity)
          remaining_quantity = 0
    # Return movement, split_quantity tuples
    for movement in simulation_movement_list:
      movement.setDeliveryRatio(movement.getQuantity() / new_quantity)
    return result