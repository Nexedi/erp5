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
from Products.ERP5Type.Utils import ensure_list
from Products.ERP5Type.XMLObject import XMLObject
from Products.CMFActivity.ActiveProcess import ActiveProcess
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from erp5.component.interface.IMovement import IMovement
from erp5.component.interface.ISolver import ISolver
from erp5.component.interface.IConfigurable import IConfigurable

@zope.interface.implementer(ISolver,
                            IConfigurable,)
class SolverProcess(XMLObject, ActiveProcess):
  """
    Solver Process class represents the decision of the user
    to solve a divergence. The data structure is the following:

    Solver Process can contain:

    - Solver Decision documents which represent the decision
      of the user to solve a divergence on a given Delivery Line
      by using a certain heuristic

    - Target Solver documents which encapsulate the resolution
      heuristic in relation with DivergenceTester (ie. each
      DivergenceTester must provide a list of Target Solver portal
      types whch are suitable to solve a given divergence) and
      which may eventually use a Delivery Solver each time divergence
      is related to quantities.

    Every Simulation Movement affected by a Solver Process has a relation
    to the solver process through the "solver" base category.
  """
  meta_type = 'ERP5 Solver Process'
  portal_type = 'Solver Process'
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
                    )

  # Implementation
  security.declareProtected(Permissions.ModifyPortalContent, 'buildTargetSolverList')
  @UnrestrictedMethod
  def buildTargetSolverList(self):
    """
      Builds target solvers from solver decisions
    """
    movement_dict = {}
    message_list = []

    # First create a mapping between simulation movements and solvers
    #   in order to know for each movements which solvers are needed
    #   and which parameters with
    #
    #   movement_dict[movement] = {
    #              solver : [((c1, v1), (c2, v2 )),
    #                        ((c1, v1), (c2, v2 )),
    #                       ],
    for decision in self.contentValues(portal_type="Solver Decision"):
      solver = decision.getSolverValue()
      # do nothing if solver is not yet set.
      if solver is None:
        continue
      solver_conviguration_dict = decision.getConfigurationPropertyDict()
      configuration_mapping = sorted(solver_conviguration_dict.items()) # Make sure the list is sorted in canonical way
      configuration_mapping = tuple(configuration_mapping)
      for movement in decision.getDeliveryValueList():
        # Detect incompatibilities
        movement_solver_dict = movement_dict.setdefault(movement, {})
        movement_solver_configuration_list = movement_solver_dict.setdefault(solver, [])
        if configuration_mapping not in movement_solver_configuration_list:
          movement_solver_configuration_list.append(configuration_mapping)

    # Second, create a mapping between solvers and movements
    # and their configuration
    #
    #   solver_dict[solver] = {
    #     movement : [((c1, v1), (c2, v2 )),
    #                 ((c1, v1), (c2, v2 )),
    #                ],
    #   }
    #
    solver_dict = {}
    for movement, movement_solver_dict in movement_dict.items():
      for solver, movement_solver_configuration_list in movement_solver_dict.items():
        solver_movement_dict = solver_dict.setdefault(solver, {})
        solver_movement_dict[movement] = movement_solver_configuration_list

    # Third, group solver configurations and make sure solvers do not conflict
    # by creating a mapping between solvers and movement configuration grouped
    # by a key which is used to aggregate multiple configurations
    #
    #   grouped_solver_dict[solver] = {
    #     solver_key: {
    #        movement : [((c1, v1), (c2, v2 )),
    #                    ((c1, v1), (c2, v2 )),
    #                   ],
    #          }
    #   }
    grouped_solver_dict = {}
    for movement, movement_solver_dict in movement_dict.items():
      for solver, movement_solver_configuration_list in movement_solver_dict.items():
        for configuration_mapping in movement_solver_configuration_list:
          # Detect conflicts. This includes finding out that a solver which
          # is exclusive per movement, conflicts with another solver on the same
          # movement
          solver_message_list = solver.getSolverConflictMessageList(movement, configuration_mapping, solver_dict, movement_dict)
          if solver_message_list:
            message_list.extend(solver_message_list)
            continue # No need to keep on
          # Solver key contains only those properties which differentiate
          # solvers (ex. there should be only Production Reduction Solver)
          solver_key = solver.getSolverProcessGroupingKey(movement, configuration_mapping, solver_dict, movement_dict)
          solver_key_dict = grouped_solver_dict.setdefault(solver, {})
          solver_movement_dict = solver_key_dict.setdefault(solver_key, {})
          movement_solver_configuration_list = solver_movement_dict.setdefault(movement, [])
          if configuration_mapping not in movement_solver_configuration_list:
            movement_solver_configuration_list.append(configuration_mapping)

    # If conflicts where detected, return them and do nothing
    if message_list:
      return message_list

    # Fourth, build target solvers
    for solver, solver_key_dict in grouped_solver_dict.items():
      for solver_key, solver_movement_dict in solver_key_dict.items():
        solver_instance = self.newContent(portal_type=solver.getId())
        solver_instance._setDeliveryValueList(ensure_list(solver_movement_dict.keys()))
        for movement, configuration_list in six.iteritems(solver_movement_dict):
          for configuration_mapping in configuration_list:
            if len(configuration_mapping):
              solver_instance.updateConfiguration(**dict(configuration_mapping))

    # Return empty list of conflicts
    return []

  # ISolver implementation
  # Solver Process Workflow Interface
  #  NOTE: how can we consider that a workflow defines or provides an interface ?
  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self, activate_kw=None):
    """
      Start solving
    """
    portal = self.getPortalObject()
    isTransitionPossible = portal.portal_workflow.isTransitionPossible
    for solver in self.objectValues(portal_type=portal.getPortalTargetSolverTypeList()):
      if solver.isTempObject():
        solver_type = solver.getPortalTypeValue()
        # Since multiple documents may need the same solver, activity must be
        # executed individually. Thus SQLQueue is needed.
        solver_type.activate(activity='SQLQueue', activate_kw=activate_kw).solve(
          activate_kw=activate_kw,
          delivery_list=solver.getDeliveryList(),
          configuration_dict=solver.getConfigurationPropertyDict()
          )
      else:
        if isTransitionPossible(solver, 'start_solving'):
          solver.startSolving()
        # SQLQueue is needed for the same reason.
        solver.activate(activity='SQLQueue', active_process=self, activate_kw=activate_kw).solve(
          activate_kw=activate_kw)

  # API
  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSolverDecisionListConsistent')
  def isSolverDecisionListConsistent(self):
    """
    Returns True is the Solver Process decisions do not
    need to be rebuilt, False else. This method can be
    invoked before invoking buildSolverDecisionList if
    this helps reducing CPU time.
    """

  security.declareProtected(Permissions.ModifyPortalContent,
                            'buildSolverDecisionList')
  def buildSolverDecisionList(self, delivery_or_movement=None):
    """
    Build (or rebuild) the solver decisions in the solver process

    delivery_or_movement -- a movement, a delivery,
                            or a list thereof
    """
    if delivery_or_movement is None:
      raise NotImplementedError
      # Gather all delivery lines already found
      # in already built solvers

    if not isinstance(delivery_or_movement, (tuple, list)):
      delivery_or_movement = [delivery_or_movement]
    movement_list = []
    isMovement = IMovement.providedBy
    for x in delivery_or_movement:
      if isMovement(x):
        movement_list.append(x)
      else:
        movement_list.extend(x.getMovementList())

    # We suppose here that movement_list is a list of
    # delivery movements. Let us group decisions in such way
    # that a single decision is created per divergence tester instance
    # and per application level list and per available target solver
    # list
    solver_tool = self.getPortalObject().portal_solvers
    solver_decision_dict = {}
    for movement in movement_list:
      for simulation_movement in movement.getDeliveryRelatedValueList():
        for divergence_tester in simulation_movement.getParentValue().getSpecialiseValue()._getDivergenceTesterList(exclude_quantity=False):
          if divergence_tester.test(simulation_movement):
            if divergence_tester.explain(simulation_movement) in (None, []):
              continue
            application_list = [
              x.getRelativeUrl()
              for x in solver_tool.getSolverDecisionApplicationValueList(movement, divergence_tester)]
            application_list.sort()
            solver_list = solver_tool.searchTargetSolverList(
              divergence_tester, simulation_movement)
            solver_list.sort(key=lambda x:x.getId())
            solver_decision_key = (divergence_tester.getRelativeUrl(), tuple(application_list), tuple(solver_list))
            movement_dict = solver_decision_dict.setdefault(solver_decision_key, {})
            movement_dict[simulation_movement] = None

    # Now build the solver decision instances based on the previous
    # grouping
    solver_decision_list = self.objectValues(portal_type='Solver Decision')
    unmatched_solver_decision_list = set(solver_decision_list)
    for solver_decision_key, movement_dict in solver_decision_dict.items():
      causality, _, solver_list = solver_decision_key
      movement_url_list = [x.getRelativeUrl() for x in movement_dict.keys()]
      movement_url_list.sort()
      matched_solver_decision_list = [
        x for x in solver_decision_list \
        if sorted(x.getDeliveryList()) == movement_url_list and \
        x.getCausality() == causality]
      unmatched_solver_decision_list.difference_update(matched_solver_decision_list)
      if len(matched_solver_decision_list) > 0:
        solver_decision_list.remove(matched_solver_decision_list[0])
      else:
        new_decision = self.newContent(portal_type='Solver Decision')
        new_decision._setDeliveryList(movement_url_list)
        new_decision._setCausality(solver_decision_key[0])
        # If we have only one available automatic solver, we just use it
        # automatically.
        automatic_solver_list = [x for x in solver_list if x.isAutomaticSolver()]
        if len(automatic_solver_list) == 1:
          automatic_solver = automatic_solver_list[0]
          new_decision.setSolverValue(automatic_solver)
          new_decision.updateConfiguration(
            **automatic_solver.getDefaultConfigurationPropertyDict(
            new_decision))
        # XXX We need a relation between Simulation Movement and Solver
        # Process, but ideally, the relation should be created when a
        # Target Solver processes, not when a Solver Decision is
        # created.
        # for simulation_movement in movement_dict.keys():
        #   solver_list = simulation_movement.getSolverValueList()
        #   if self not in solver_list:
        #     simulation_movement.setSolverValueList(
        #       solver_list + [self])


    # delete non-matched existing solver decisions, unless they have been
    # solved already (we detect this by the fact that the solver decision is
    # associated to a target solver)
    self.manage_delObjects(ids=[x.getId() for x in
          unmatched_solver_decision_list if not x.getCausality()])

  def _generateRandomId(self):
    # call ActiveProcess._generateRandomId() explicitly otherwise
    # Folder._generateRandomId() will be called and it returns 'str' not
    # 'int' id.
    return ActiveProcess._generateRandomId(self)
