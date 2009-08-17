# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
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

class DeliverySolver:
  """
    Delivery solver is used to have control of how quantity property is
    accepted into simulation.

    Delivery solver is only used for quantity property.

    Delivery solver is working on movement's quantity and related simulation
    movements' quantities.

    Can be used to:

     * distribute
     * queue (FIFO, FILO, ...)
     * etc
  """

  def __init__(self, simulation_tool=None, **kw):
    """
      Initialisation
    """
    self.simulation_tool = simulation_tool
    self.__dict__.update(kw)

  def solveMovement(self, movement):
    """
      Solves a delivery movement
    """
    raise NotImplementedError

  def solveDelivery(self, delivery):
    """
      Solves the delivery itself
    """
    result_list = []
    for movement in delivery.getMovementList():
      result_list.append(self.solveMovement(movement))
    return result_list
