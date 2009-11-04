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

from Products.CMFCore.utils import getToolByName

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool

from Products.ERP5 import _dtmldir

from zLOG import LOG

class SolverTool(BaseTool):
    """
      The SolverTool provides API to find out which solver can
      be applied in which case and contains SolverProcess instances
      which are used to keep track of solver decisions, solver
      history and global optimisation.

      NOTE: this class is experimental and is subject to be removed
    """
    id = 'portal_solvers'
    meta_type = 'ERP5 Solver Tool'
    portal_type = 'Solver Tool'
    allowed_types = ( 'ERP5 Solver Process', )

    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainSolverTool', _dtmldir )

    def filtered_meta_types(self, user=None):
      # Filters the list of available meta types.
      all = SolverTool.inheritedAttribute('filtered_meta_types')(self)
      meta_types = []
      for meta_type in self.all_meta_types():
        if meta_type['name'] in self.allowed_types:
          meta_types.append(meta_type)
      return meta_types

    def tpValues(self) :
      """ show the content in the left pane of the ZMI """
      return self.objectValues()

    def buildSolvedSimulationMovement(self, movement):
      """
      Builds a Temp Simulation Movement 

      Update a given simulation movement which has been
      affected by the SolverProcess 
      """

