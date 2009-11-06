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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet
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
  isPortalContent = 1
  isRADContent = 1
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

  def buildTargetSolverList(self):
    """
      Builds target solvers from solver decisions
    """
    solver_dict = {}
    movement_dict = {}
    types_tool = self.portal_types

    # First create a mapping between delivery movements and solvers
    #   in order to know for each movements which solvers are needed
    #   and which parameters with
    for decision in self.contentValues(portal_type="Solver Decision"):
      solver = decision.getSolverValue()
      solver_type = solver.getId() # ex. Postpone Production Solver
      solver_conviguration_dict = decision.getConfigurationPropertyDict()
      solver_conviguration_key = solver_conviguration_dict.items()
      for movement in decision.getDeliveryValueList():
        # Detect incompatibilities
        movement_solver_dict = movement_dict.setdefault(movement.getRelativeUrl(), {})
        movement_solver_configuration_dict = movement_solver_dict.setdefault(solver_type, {})
        movement_solver_configuration_dict[solver_key] = None

    # Second, make sure solvers do not conflict and configuration is valid
    for movement_url, movement_solver_dict in movement_dict.items():
      for solver_type, movement_solver_configuration_dict in movement_solver_dict.items():
        solver = types_tool[solver_type]
        for other_solver in movement_solver_dict.keys():
          if solver.conflictsWithSolver(other_solver):
            raise "Solver %s conflicts with solver %s on movement %s" % (solver_type, other_solver, movement_url)
        # Make sure multiple configuration are possible
        try:
          # Solver key contains only those properties which differentiate
          # solvers (ex. there should be only Production Reduction Solver)
          solver_key = solver.reduceConfigurationList(movement_solver_configuration_dict.keys())
        except:
          raise
        solver_key_dict = solver_dict.setdefault(solver_type, {})
        solver_movement_dict = solver_key_dict.setdefault(solver_key, {})
        solver_movement_dict[movement_url] = movement_solver_configuration_dict.keys()

    # Third, build target solvers
    for portal_type, solver_key_dict in solver_dict.items():
      for solver_key, solver_movement_dict in solver_key_dict.items():
         solver_instance = self.newContent(portal_type=solver_type)
         solver_instance._setDeliveryList(solver_movement_dict.keys())
         for movement_url, configuration_list in solver_movement_dict.iteritems():
           for configuration_kw in configuration_list:
            solver_instance.updateConfiguration(**configuration_kw)

  # Solver Process Workflow Interface 
  #  NOTE: how can we consider that a workflow defines or provides an interface ?
  def solve(self):
    """
      Start solving
    """
    for solver in self.contentValues(portal_type=self.getPortalObject().getPortalTargetSolverTypeList()):
      solver.activate(active_process=self).solve()
