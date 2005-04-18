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
from zLOG import LOG

class Distribute(DeliverySolver):
  """
    Update new values equaly on Simulation Movements.
  """

  def solve(self, movement):
    """
      Solve a delivery by reducing / increasing each simulation movement
      it relates to
    """
    # Determine the amount to distribute
    d_source = movement.getSource()
    d_destination = movement.getDestination()
    d_source_section = movement.getSourceSection()
    d_destination_section = movement.getDestinationSection()
    d_start_date = movement.getStartDate()
    d_stop_date = movement.getStopDate()
    d_resource = movement.getResource()
    
    simulation_movement_list = movement.getDeliveryRelatedValueList()
    new_simulation_movement_list = []
    to_aggregate_list = []
    delivery_line_simulation_quantity = 0
    for simulation_movement in simulation_movement_list:
      m_source = simulation_movement.getSource()
      m_destination = simulation_movement.getDestination()
      m_source_section = simulation_movement.getSourceSection()
      m_destination_section = simulation_movement.getDestinationSection()
      m_start_date = simulation_movement.getStartDate()
      m_stop_date = simulation_movement.getStopDate()
      m_resource = simulation_movement.getResource()
      if m_source != d_source or \
         m_destination != d_destination or \
         m_source_section != d_source_section or \
         m_destination_section != d_destination_section or \
         m_start_date != d_start_date or \
         m_stop_date != d_stop_date or \
         m_resource != d_resource:
          # Disconnect the movement if anything else the quantity is changed
          to_aggregate_list.append(simulation_movement)
          simulation_movement.setDelivery('')
          simulation_movement.setProfitQuantity(simulation_movement.getQuantity())
          simulation_movement.setDeliveryError(0.)
          simulation_movement.immediateReindexObject()
      else:
        delivery_line_simulation_quantity += float(simulation_movement.getCorrectedQuantity())
        new_simulation_movement_list.append(simulation_movement)
        
    delivery_line_quantity = float(movement.getQuantity())
    to_distribute = delivery_line_quantity - delivery_line_simulation_quantity
    if to_distribute != 0:
      if delivery_line_simulation_quantity != 0:
        for m in new_simulation_movement_list:
          m_corrected_quantity = m.getCorrectedQuantity()
          m_quantity = m.getQuantity()
          m._v_previous_quantity = m_quantity
          distribute_ratio = m_corrected_quantity / delivery_line_simulation_quantity
          m.setQuantity(m_quantity + to_distribute * distribute_ratio)
          m.setDeliveryError(0.)
          m.immediateReindexObject()
      else:
        if len(new_simulation_movement_list) > 0:
          to_add_quantity = to_distribute / len(new_simulation_movement_list)
          for m in new_simulation_movement_list:
            m._v_previous_quantity = m.getQuantity()
            m.setQuantity(m.getQuantity() + to_add_quantity)
            m.setDeliveryError(0.)
            m.immediateReindexObject()

registerDeliverySolver(Distribute)
