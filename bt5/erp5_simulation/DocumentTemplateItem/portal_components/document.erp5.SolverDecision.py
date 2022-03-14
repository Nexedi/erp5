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
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.ConfigurableMixin import ConfigurableMixin
from erp5.component.interface.IConfigurable import IConfigurable

@zope.interface.implementer(IConfigurable,)
class SolverDecision(ConfigurableMixin, XMLObject):
  """Solver Decision

    The goal of Solver Decision is to record the fact that "the user decided to
    solve a list of divergent simulation movement - which are divergent because
    of given divergence tester - by applying specific heuristic (target
    solver)."

    Every Solver Decision has a relation (delivery category) to a list of
    simulation movements.
    Solver Decision specifies the heuristic to use through a relation to a
    single target solver portal type (target_solver pgroup) using the "solver"
    base category.

    Every Solver Decision acquires the configuration properties of its related
    Target Solver. Configuration properties may include the choice of a
    Delivery Solver each time divergence is related to quantity.

  """
  meta_type = 'ERP5 Solver Decision'
  portal_type = 'Solver Decision'
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
                    , PropertySheet.Comment
                    , PropertySheet.SolverSelection
                    , PropertySheet.Configurable
                    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDefaultConfigurationPropertyDict')
  def getDefaultConfigurationPropertyDict(self):
    """
    Returns a dictionary of default properties for specified
    configurable object
    (implementation)
    """
    solver_type = self.getSolverValue()
    if solver_type is None:
      return {}
    else:
      return solver_type.getDefaultConfigurationPropertyDict(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConfigurationPropertyListDict')
  def getConfigurationPropertyListDict(self):
    """
    Returns a dictionary of possible values for specified
    configurable object
    (implementation)
    """
    solver_type = self.getSolverValue()
    if solver_type is None:
      return {}
    else:
      return solver_type.getConfigurationPropertyListDict(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'searchDeliverySolverList')
  def searchDeliverySolverList(self, **kw):
    """
    this method returns a list of delivery solvers, as predicates against
    solver decision.
    """
    target_solver_type = self.getSolverValue()
    if target_solver_type is None:
      return []
    solver_list = target_solver_type.getDeliverySolverValueList()
    return [x for x in solver_list if x.test(self)]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExplanationMessage')
  def getExplanationMessage(self, all=False): # pylint: disable=redefined-builtin
    """
    Returns the HTML message that describes the detail of divergences to
    be solved with this Solver Decision.
    """
    message_list = []
    for tester in self.getCausalityValueList():
      for simulation_movement in self.getDeliveryValueList():
        message = tester.getExplanationMessage(simulation_movement)
        if message is None:
          continue
        if all or len(message_list) == 0:
          message_list.append(message)
        elif len(message_list) == 1:
          # XXX it should be a link to the detailed view.
          message_list.append('...')
    return ''.join(message_list)
