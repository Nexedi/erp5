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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.AcceptSolver import AcceptSolver
from erp5.component.interface.ISolver import ISolver
import six

@zope.interface.implementer(ISolver,)
class UnifySolver(AcceptSolver):
  """
  """
  meta_type = 'ERP5 Unify Solver'
  portal_type = 'Unify Solver'
  add_permission = Permissions.AddPortalContent
  isIndexable = 0 # We do not want to fill the catalog with objects on which we need no reporting

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.TargetSolver
                    )

  def _getActualTargetMovement(self, movement, solved_property):
    # The movement might not be the right place to correct the
    # divergence, if the property is obtained by direct Acquisition.
    root_delivery = movement.getRootDeliveryValue()
    while (movement != root_delivery and
           not movement.hasProperty(solved_property)):
      movement = movement.getParentValue()
    # NOTE: the code above was copied and adapted from the top of
    # "SolverTool.getSolverDecisionApplicationValueList()", because
    # we don't have enough info (a divergence tester) to invoke it
    # from here, and also because a Solver instance needs to be
    # independent from the divergence testers that caused it, as it
    # could be the consolidated result of many divergence testers.
    return movement

  def _getAffectedSimulationMovementList(self, movement, solved_property):
    # All Simulations movements pointing to this movement, or to
    # submovements that also don't have the property, need to be
    # updated, otherwise we could be solving one divergence just to
    # create another divergence in a simulation movement that wasn't
    # divergent before.
    simulation_movement_list = []
    for sub_movement in movement.getMovementList():
      if sub_movement.hasProperty(solved_property):
        # XXX-Leo, what if there is a sub_movement that doesn't have the
        # property, but has a "parent" that DOES have the property and
        # that parent is not 'movement'? Perhaps we should check instead if
        # self._getActualTargetMovement(sub_movement,solved_property)==movement
        # before considering its related simulation movements for inclusion...
        continue
      for simulation_movement in sub_movement.getDeliveryRelatedValueList():
        simulation_movement_list.append(simulation_movement)
    return simulation_movement_list

  def _solve(self, activate_kw=None):
    """
    Adopt new property value to simulation movements and their deliveries,
    while keeping the original one recorded.
    """
    portal = self.getPortalObject()
    configuration_dict = self.getConfigurationPropertyDict()
    solved_property_list = configuration_dict.get('tested_property_list')
    if solved_property_list is None:
      solved_property_list = \
        portal.portal_types.getTypeInfo(self).getTestedPropertyList()
    # XXX it does not support multiple tested properties.
    solved_property = solved_property_list[0]
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               set()).add(simulation_movement)
    for movement, simulation_movement_set in six.iteritems(delivery_dict):
      # get the movement that actually has the property to update
      movement = self._getActualTargetMovement(movement, solved_property)
      # and all other simulation movements we should also update
      simulation_movement_set.update(self._getAffectedSimulationMovementList(
          movement,
          solved_property,
      ))
      if activate_kw is not None:
        movement.setDefaultActivateParameterDict(activate_kw)
      value = configuration_dict.get('value')
      movement.setProperty(solved_property, value)
      for simulation_movement in simulation_movement_set:
        if activate_kw is not None:
          simulation_movement.setDefaultActivateParameterDict(activate_kw)
        if not simulation_movement.isPropertyRecorded(solved_property):
          simulation_movement.recordProperty(solved_property)
        simulation_movement.setProperty(solved_property, value)
        # XXX: would it be safe to expand by activity ?
        simulation_movement.expand('immediate')
    # Finish solving
    if portal.portal_workflow.isTransitionPossible(self, 'succeed'):
      self.succeed()
