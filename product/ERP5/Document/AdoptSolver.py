# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5.mixin.configurable_property_solver import ConfigurablePropertySolverMixin

class AdoptSolver(ConfigurablePropertySolverMixin):
  """Target solver that adopts the values from the prevision on the decision.
  """
  meta_type = 'ERP5 Adopt Solver'
  portal_type = 'Adopt Solver'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _solve(self, activate_kw=None):
    """
    Adopt new property to movements or deliveries.
    """
    solved_property_list = self.getTestedPropertyList()
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)
    for movement, simulation_movement_list in delivery_dict.iteritems():
      if activate_kw is not None:
        movement.setDefaultActivateParameterDict(activate_kw)
      for solved_property in solved_property_list:
        # XXX hardcoded
        if solved_property == 'quantity':
          # For 'quantity' case, we need to recalculate delivery_ratio
          # for all related simulation movements.
          simulation_movement_list = movement.getDeliveryRelatedValueList()
          total_quantity = sum(
            [x.getQuantity() for x in simulation_movement_list])
          movement.setQuantity(total_quantity)
          for simulation_movement in simulation_movement_list:
            quantity = simulation_movement.getQuantity()
            if total_quantity == 0:
              delivery_ratio = 1.
              delivery_error = 0
            else:
              delivery_ratio = quantity / total_quantity
              delivery_error = total_quantity * delivery_ratio - quantity
            simulation_movement.edit(delivery_ratio=delivery_ratio,
                                     delivery_error=delivery_error,
                                     activate_kw=activate_kw)
        else:
          # XXX TODO we need to support multiple values for categories or
          # list type property.

          # XXX-Leo: If there is more than one simulation_movement in
          # the simulation_movement_list, this indicates a wrong
          # configuration or bad selection by the user. Should we do
          # anything about it, like log or fail?
          # Also, the behaviour below is naive, and could cause another
          # non-divergent Simulation Movement to become divergent.
          for simulation_movement in simulation_movement_list:
            obj = movement
            while movement.getRootDeliveryValue() is not obj:
              if obj.hasProperty(solved_property):
                break

              obj = obj.getParentValue()

            obj.setProperty(
              solved_property,
              simulation_movement.getProperty(solved_property)
            )
    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
