# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5Type.UnrestrictedMethod import super_user

class SolverMixin(object):
  """
  Provides generic methods and helper methods to implement ISolver.
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements(interfaces.ISolver,)

  def _solve(self, activate_kw=None):
    raise NotImplementedError

  # Implementation of ISolver
  security.declarePrivate('solve')
  def solve(self, activate_kw=None):
    with super_user():
      self._solve(activate_kw=activate_kw)

  def getPortalTypeValue(self):
    return self.getPortalObject().portal_solvers._getOb(self.getPortalType())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'searchDeliverySolverList')
  def searchDeliverySolverList(self, **kw):
    """
    this method returns a list of delivery solvers

    XXX here we cannot test delivery solver as a predicate, because
    predicate's context should be Solver Decision, not a target
    solver.
    """
    target_solver_type = self.getPortalTypeValue()
    solver_list = target_solver_type.getDeliverySolverValueList()
    return solver_list

InitializeClass(SolverMixin)
