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


from Products.ERP5.Tool.SimulationTool import registerDeliverySolver
from DeliverySolver import DeliverySolver

class Distribute(DeliverySolver):
  """
    Update new values equaly on Simulation Movements.
  """

  def solve(self, movement):
    """
      Solve a delivery by reducing / increasing each simulation movement
      it relates to
    """
    delivery_line_quantity = float(movement.getQuantity())
    delivery_line_target_quantity = float(movement.getTargetQuantity())
    if delivery_line_quantity != delivery_line_target_quantity:
      if delivery_line_quantity != 0 :
      # XXXXXXXXXXXXXXXXXXXXXXXXX something special should be done if delivery_line_quantity == 0 !
        distribute_ratio = delivery_line_target_quantity  / delivery_line_quantity
        for s in movement.getDeliveryRelatedValueList():
          # Reduce quantity
          s.setQuantity(s.getQuantity() * distribute_ratio)
          # Change dates
          s.setStartDate(movement.getStartDate())
          s.setStopDate(movement.getStopDate())
          s.diverge() # Make sure everyone knows this simulation movement is inconsistent
      else:
        delivery_related_value_list = movement.getDeliveryRelatedValueList()
        distribute_ratio = float(len(delivery_related_value_list))
        target_quantity = movement.getTargetQuantity()
        for s in delivery_related_value_list:
          # Define new quantity
          s.setQuantity(target_quantity / distribute_ratio)
          # Change dates
          s.setStartDate(movement.getStartDate())
          s.setStopDate(movement.getStopDate())
          s.diverge() # Make sure everyone knows this simulation movement is inconsistent
    movement.setQuantity(movement.getTargetQuantity())
    # No need to touch date since it should be defined at the upper level.

registerDeliverySolver(Distribute)
