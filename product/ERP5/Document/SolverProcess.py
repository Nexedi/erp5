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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.CMFActivity.ActiveProcess import ActiveProcess

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

  # Declarative interfaces
  zope.interface.implements(interfaces.ISolver,
                            interfaces.IConfigurable,
                           )

  # Implementation
  def buildTargetSolverList(self):
    """
      Builds target solvers from solver decisions
    """
    movement_dict = {}
    types_tool = self.portal_types

    # First create a mapping between delivery movements and solvers
    #   in order to know for each movements which solvers are needed
    #   and which parameters with
    for decision in self.contentValues(portal_type="Solver Decision"):
      solver = decision.getSolverValue()
      # do nothing if solver is not yet set.
      if solver is None:
        continue
      solver_type = solver.getId() # ex. Postpone Production Solver
      solver_conviguration_dict = decision.getConfigurationPropertyDict()
      solver_conviguration_key = tuple(solver_conviguration_dict.items())
      for movement in decision.getDeliveryValueList():
        # Detect incompatibilities
        movement_solver_dict = movement_dict.setdefault(movement.getRelativeUrl(), {})
        movement_solver_configuration_dict = movement_solver_dict.setdefault(solver_type, {})
        movement_solver_configuration_dict[solver_conviguration_key] = None

    # Second, make sure solvers do not conflict and configuration is valid
    # Build a movement and configuration structure per solver type
    solver_dict = {}
    for movement_url, movement_solver_dict in movement_dict.items():
      for solver_type, movement_solver_configuration_dict in movement_solver_dict.items():
        solver_movement_dict = solver_dict.setdefault(solver_type, {})
        configuration_list = solver_movement_dict.setdefault(movement_url, [])
        configuration_list.extend(movement_solver_configuration_dict) # XXX-JPS WRONG
    # Then start the grouping procedure
    for movement_url, movement_solver_dict in movement_dict.items():
      for solver_type, movement_solver_configuration_dict in movement_solver_dict.items():
        solver = types_tool[solver_type]
        for other_solver_type in movement_solver_dict.keys():
          if other_solver_type == solver_type:
            continue
          if solver.conflictsWithSolver(types_tool[other_solver_type]):
            # XXX6PJS REDO HERE
            raise ValueError, "Solver %s conflicts with solver %s on movement %s" % (solver_type, other_solver_type, movement_url)
        # Make sure multiple configuration are possible
        try:
          # Solver key contains only those properties which differentiate
          # solvers (ex. there should be only Production Reduction Solver)
          solver_key = solver.getSolverProcessGroupingKey(movement_url, movement_solver_configuration_dict, movement_solver_dict, solver_dict[solver_type])
        except: # Raise the exception generated by the solver in case of failure of grouping
          raise
        solver_key_dict = solver_dict.setdefault(solver_type, {})
        solver_movement_dict = solver_key_dict.setdefault(solver_key, {})
        solver_movement_dict[movement_url] = movement_solver_configuration_dict.keys()

    # Third, build target solvers
    solver_dict = {}
    for solver_type, solver_key_dict in solver_dict.items():
      for solver_key, solver_movement_dict in solver_key_dict.items():
         solver_instance = self.newContent(portal_type=solver_type)
         solver_instance._setDeliveryList(solver_movement_dict.keys())
         for movement_url, configuration_list in solver_movement_dict.iteritems():
           for configuration_kw in configuration_list:
             if len(configuration_kw):
               solver_instance.updateConfiguration(**dict(configuration_kw))

  # ISolver implementation
  # Solver Process Workflow Interface 
  #  NOTE: how can we consider that a workflow defines or provides an interface ?
  def solve(self):
    """
      Start solving
    """
    isTransitionPossible = self.getPortalObject().portal_workflow.isTransitionPossible
    for solver in self.contentValues(portal_type=self.getPortalObject().getPortalTargetSolverTypeList()):
      if isTransitionPossible(solver, 'start_solving'):
        solver.startSolving()
        solver.activate(active_process=self).solve()

  # API
  def isSolverDecisionListConsistent(self):
    """
    Returns True is the Solver Process decisions do not 
    need to be rebuilt, False else. This method can be
    invoked before invoking buildSolverDecisionList if
    this helps reducing CPU time.
    """

  def buildSolverDecisionList(self, delivery_or_movement=None,
                              temp_object=False):
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
    for x in delivery_or_movement:
      if x.isDelivery():
        movement_list.extend(x.getMovementList())

    # We suppose here that movement_list is a list of
    # delivery lines. Let us group decisions in such way
    # that a single decision is created per divergence tester instance
    # and per application level list
    solver_tool = self.getParentValue()
    solver_decision_dict = {}
    for movement in movement_list:
      for simulation_movement in movement.getDeliveryRelatedValueList():
        for divergence_tester in simulation_movement.getParentValue().getSpecialiseValue()._getDivergenceTesterList(exclude_quantity=False):
          if divergence_tester.compare(simulation_movement, movement):
            continue
          application_list = map(lambda x:x.getRelativeUrl(), 
                 solver_tool.getSolverDecisionApplicationValueList(movement, divergence_tester))
          application_list.sort()
          solver_decision_key = (divergence_tester.getRelativeUrl(), tuple(application_list))
          movement_dict = solver_decision_dict.setdefault(solver_decision_key, {})
          movement_dict[movement] = None

    # Now build the solver decision instances based on the previous
    # grouping
    solver_decision_list = self.objectValues(portal_type='Solver Decision')
    index = 1
    for solver_decision_key, movement_dict in solver_decision_dict.items():
      causality, delivery_list = solver_decision_key
      matched_solver_decision_list = [
        x for x in solver_decision_list \
        if x.getDeliveryList() == list(delivery_list) and \
        x.getCausality() == causality]
      if len(matched_solver_decision_list) > 0:
        solver_decision_list.remove(matched_solver_decision_list[0])
      else:
        if temp_object:
          new_decision = self.newContent(portal_type='Solver Decision',
                                         temp_object=True,
                                         #id=index,
                                         uid='new_%s' % index)
          index += 1
        else:
          new_decision = self.newContent(portal_type='Solver Decision')
        new_decision._setDeliveryValueList(movement_dict.keys())
        new_decision._setCausality(solver_decision_key[0])
        # XXX We need a relation between Simulation Movement and Solver
        # Process, but ideally, the relation should be created when a
        # Target Solver processes, not when a Solver Decision is
        # created.
        # for movement in movement_dict.keys():
        #   for simulation_movement in movement.getDeliveryRelatedValueList():
        #     solver_list = simulation_movement.getSolverValueList()
        #     if self not in solver_list:
        #       simulation_movement.setSolverValueList(
        #         solver_list + [self])
    # XXX what should we do for non-matched existing solver decisions?
    # do we need to cancel them by using an appropriate workflow?

  def _generateRandomId(self):
    # call ActiveProcess._generateRandomId() explicitly otherwise
    # Folder._generateRandomId() will be called and it returns 'str' not
    # 'int' id.
    return ActiveProcess._generateRandomId(self)
