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
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool

from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from erp5.component.interface.IDivergenceController import IDivergenceController

@zope.interface.implementer(IDivergenceController,)
class SolverProcessTool(BaseTool):
  """ Container for solver processes.
  """
  id = 'portal_solver_processes'
  meta_type = 'ERP5 Solver Process Tool'
  portal_type = 'Solver Process Tool'
  title = 'Solver Processes'
  allowed_types = ( 'ERP5 Solver Process', )

  # Declarative Security
  security = ClassSecurityInfo()

  # IDivergenceController implementation
  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDivergent')
  def isDivergent(self, delivery_or_movement=None):
    """
    Returns True if any of the movements provided
    in delivery_or_movement is divergent

    delivery_or_movement -- a movement, a delivery,
                            or a list thereof
    """
    if not isinstance(delivery_or_movement, (tuple, list)):
      delivery_or_movement = [delivery_or_movement]
    for movement in delivery_or_movement:
      if movement.isDivergent():
        return True
    return False

  security.declareProtected(Permissions.AddPortalContent,
                            'newSolverProcess')
  @UnrestrictedMethod
  def newSolverProcess(self, delivery_or_movement=None, temp_object=False):
    """
    Builds a new solver process from the divergence
    analaysis of delivery_or_movement. All movements
    which are not divergence are placed in a Solver
    Decision with no Divergence Tester specified.

    delivery_or_movement -- a movement, a delivery,
                            or a list thereof
    """
    # Do not create a new solver process if no divergence
    # XXX (possible performance issue) Here it calls all divergence
    # testers, but they should be called later.
    if not self.isDivergent(delivery_or_movement=delivery_or_movement):
      return None

    # Create an empty solver process
    new_solver = self.newContent(portal_type='Solver Process',
                                 temp_object=temp_object)
    # And build decisions
    new_solver.buildSolverDecisionList(delivery_or_movement)

    if not temp_object:
      # Append the solver process into the delivery's solver category
      # XXX using delivery's solver category is not so good idea,
      # because we might want to solve several deliveries with one
      # solver process, several users want to solve one document etc.
      delivery = delivery_or_movement.getRootDeliveryValue()
      solver_list = delivery.getSolverValueList()
      solver_list.append(new_solver)
      delivery.setSolverValueList(solver_list)

    return new_solver

InitializeClass(SolverProcessTool)
