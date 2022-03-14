# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from Products.ERP5Type import Permissions
from erp5.component.document.QuantitySplitSolver import QuantitySplitSolver
from erp5.component.interface.ISolver import ISolver
from erp5.component.interface.IConfigurable import IConfigurable

@zope.interface.implementer(ISolver,
                            IConfigurable,)
class QuantitySplitMoveSolver(QuantitySplitSolver):
  """Target solver that split the prevision based on quantity.

  Similar to QuantitySplitSolver, it creates another prevision movement with the
  delta quantity between decision and prevision.

  But this time we will move quantities to an existing delivery that would be
  passed as parameter to this solver (usually selected directly by user).
  """
  meta_type = 'ERP5 Quantity Split And Move Solver'
  portal_type = 'Quantity Split And Move Solver'
  add_permission = Permissions.AddPortalContent
  isIndexable = 0 # We do not want to fill the catalog with objects on which we need no reporting

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # ISolver Implementation
  def _solve(self, activate_kw=None):
    """
    Split simulation movements, and build them into existing delivery
    """
    portal = self.getPortalObject()
    diverged_simulation_movement = self.getDeliveryValue()
    solver_dict = self._solveBySplitting(activate_kw=activate_kw)
    configuration_dict = self.getConfigurationPropertyDict()
    new_movement_list = solver_dict['new_movement_list']
    delivery = diverged_simulation_movement.getDeliveryValue().getParentValue()
    assert delivery.isDelivery()
    trade_phase = self.getDeliveryValue().getTradePhase()
    assert trade_phase is not None, "Unable to solve, no trade phase is defined for %s" % \
      diverged_simulation_movement.getRelativeUrl()
    business_link_list = diverged_simulation_movement.asComposedDocument(
      ).getBusinessLinkValueList(trade_phase=trade_phase)
    assert len(business_link_list) == 1, \
      "Expected to find only one business link for trade_phase %s, but found %r" % (trade_phase,
      [x.getRelativeUrl() for x in business_link_list])
    business_link, = business_link_list
    delivery_builder_list = [x for x in business_link.getDeliveryBuilderValueList() \
                             if x.getDeliveryPortalType() == delivery.getPortalType()]
    assert len(delivery_builder_list) == 1, \
      "Expected to find only one builder on business link %s, but found %r" % (
      business_link.getRelativeUrl(), [x.getRelativeUrl() for x in delivery_builder_list])
    delivery_builder, = delivery_builder_list
    # Update simulation movements to make sure they match the new delivery
    delivery_level_movement_group = [x for x in delivery_builder.objectValues() \
                      if x.getCollectOrderGroup() == "delivery"]
    delivery_to_move = portal.unrestrictedTraverse(configuration_dict['delivery_url'])
    assert delivery_to_move.getDivergenceList() == []
    for movement_group in delivery_level_movement_group:
      tested_property_list = movement_group.getTestedPropertyList()
      for tested_property in tested_property_list:
        for new_movement in new_movement_list:
          new_movement.setPropertyList(tested_property, delivery_to_move.getPropertyList(tested_property))
          new_movement.recordProperty(tested_property)
    delivery_builder.build(delivery_relative_url_list=[configuration_dict['delivery_url']],
                           movement_list=new_movement_list)
    # Now the delivery_builder has chance to be divergent. In such case, make sure to accept value
    # from simulation
    divergence_list = delivery_to_move.getDivergenceList()
    if divergence_list:
      solver_process_tool = portal.portal_solver_processes
      solver_process = solver_process_tool.newSolverProcess(delivery_to_move)
      solver_decision, = [x for x in solver_process.contentValues()
        if x.getCausalityValue().getTestedProperty() == "quantity"]
      # use Quantity Accept Solver.
      solver_decision.setSolverValue(portal.portal_solvers['Adopt Solver'])
      # configure for Accept Solver.
      solver_decision.updateConfiguration(tested_property_list=['quantity'])
      solver_process.buildTargetSolverList()
      solver_process.solve()

    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
    solver_dict["new_movement_list"] = new_movement_list
    return solver_dict
