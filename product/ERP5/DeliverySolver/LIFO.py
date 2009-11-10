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

from FIFO import FIFO

class LIFO(FIFO):
  """
  The LIFO solver reduces delivered quantity by reducing the quantity of
  simulation movements from the first order.
  """

  # Declarative interfaces
  zope.interface.implements(interfaces.IDeliverySolver)

  title = 'LIFO Solver'

  def _getSimulationMovementList(self):
    """
    Returns a list of simulation movement sorted from the first order.
    """
    simulation_movement_list = self.simulation_movement_list
    if len(simulation_movement_list) > 1:
      return sorted(simulation_movement_list,
        key=lambda x:x.getExplainationValue().getStartDate())
    else:
      return simulation_movement_list
