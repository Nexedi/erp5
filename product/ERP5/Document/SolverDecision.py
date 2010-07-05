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
from Products.ERP5.mixin.configurable import ConfigurableMixin

class SolverDecision(ConfigurableMixin, XMLObject):
  """
    The goal of Solver Decision is to record the fact that
    "the user decided to solve a list of divergent delivery lines
    - which are divergent because of given divergence tester -
    by applying specific heuristic (target solver) and storing
    properties at a given level (ex. delivery vs. delivery line)."

    Every Solver Decision has a relation (delivery category) to a list of
    accountable Delivery Line or Cell (ie. not to an enclosing
    Delivery Line). Solver Decision specifies the heuristic to use
    through a relation to a single target solver portal type 
    (target_solver pgroup) using the "solver" base category.

    Every Solver Decision acquires the configuration properties
    of its related Target Solver. Configuration properties may include
    the choice of a Delivery Solver each time divergence is related
    to suantity.

    The level of application of the resolution is specified by specifying
    a relation to a list of "non accountable" movements (ex. delivery lines,
    deliveries) which enclose divergent accountable movements, using 
    base category XXX. (to be defined)

    TODO:
    - which base category is used to specify resolution application level ?
      (delivery ?)
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
                    , PropertySheet.SolverSelection
                    , PropertySheet.Configurable
                    )
  # XXX-JPS missing property sheet or categories to specify 
  #   (default)delivery or solver_application or order -> the object of application of resolution
  #         ie. a specified delivery, a specified delivery line, etc.
  #         (delivery should be enough)
  #   all property sheets of target solvers (with their configuration properties)

  # Declarative interfaces
  zope.interface.implements(interfaces.IConfigurable,
                           )

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

  def getExplanationMessage(self, all=False):
    """
    Returns the HTML message that describes the detail of divergences to
    be solved with this Solver Decision.
    """
    movement_list = self.getDeliveryValueList()
    message_list = []
    for tester in self.getCausalityValueList():
      for movement in movement_list:
        for simulation_movement in movement.getDeliveryRelatedValueList():
          message = tester.getExplanationMessage(simulation_movement)
          if message is None:
            continue
          if all or len(message_list) == 0:
            message_list.append(message)
          elif len(message_list) == 1:
            # XXX it should be a link to the detailed view.
            message_list.append('...')
    return ''.join(message_list)
