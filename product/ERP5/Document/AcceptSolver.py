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

class AcceptSolver(ConfigurablePropertySolverMixin):
  """Target solver that accepts the values from the decision on the prevision.
  """
  meta_type = 'ERP5 Accept Solver'
  portal_type = 'Accept Solver'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _solve(self, activate_kw=None):
    """
    Adopt new property to simulation movements, with keeping the
    original one recorded.
    """
    portal = self.getPortalObject()
    solved_property_list = self.getConfigurationPropertyDict() \
                               .get('tested_property_list')
    if solved_property_list is None:
      solved_property_list = \
        portal.portal_types.getTypeInfo(self).getTestedPropertyList()
    with self.defaultActivateParameterDict(activate_kw, True):
      for simulation_movement in self.getDeliveryValueList():
        movement = simulation_movement.getDeliveryValue()
        value_dict = {}
        base_category_set = set(movement.getBaseCategoryList())
        for solved_property in solved_property_list:
          if solved_property in base_category_set:
            # XXX-Leo: Hack, the accept solver was 'accepting' only the first
            # value of a category and discarding all others by using only
            # movement.getProperty().
            # A proper fix would perhaps be to use .getPropertyList() always
            # (and use .setPropertyList()), but we need to do property
            # mapping on simulation and there is no
            # simulation_movement.setMappedPropertyList().
            new_value = movement.getPropertyList(solved_property)
          else:
            new_value = movement.getProperty(solved_property)
          # XXX hard coded
          if solved_property == 'quantity':
            new_value *= simulation_movement.getDeliveryRatio()
          value_dict[solved_property] = new_value
        self._updateSimulationMovement(simulation_movement, value_dict,
                                       activate_kw)
    # Finish solving
    if portal.portal_workflow.isTransitionPossible(self, 'succeed'):
      self.succeed()

  # allow subclasses to override this method and do interesting things
  # like recording the same values in other simulation movements
  def _updateSimulationMovement(self, simulation_movement, value_dict,
                                activate_kw):
    for property_id, value in value_dict.iteritems():
      if not simulation_movement.isPropertyRecorded(property_id):
        simulation_movement.recordProperty(property_id)
      simulation_movement.setProperty(property_id, value)
    simulation_movement.expand(activate_kw=activate_kw)
