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
from Products.ERP5.Document.AcceptSolver import AcceptSolver

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

  # Declarative interfaces
  zope.interface.implements(interfaces.ISolver,)

  # ISolver Implementation
  def solve(self, activate_kw=None):
    """
    Adopt new property to simulation movements, with keeping the
    original one recorded.
    """
    configuration_dict = self.getConfigurationPropertyDict()
    portal_type = self.getPortalObject().portal_types.getTypeInfo(self)
    solved_property_list = configuration_dict.get('tested_property_list',
                                                  portal_type.getTestedPropertyList())
    # XXX it does not support multiple tested properties.
    solved_property = solved_property_list[0]
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)
    for movement, simulation_movement_list in delivery_dict.iteritems():
      if activate_kw is not None:
        movement.setDefaultActivateParameters(
          activate_kw=activate_kw, **activate_kw)
      new_value = configuration_dict.get('value')
      movement.setProperty(solved_property, new_value)
      for simulation_movement in simulation_movement_list:
        if activate_kw is not None:
          simulation_movement.setDefaultActivateParameters(
            activate_kw=activate_kw, **activate_kw)
        value_dict = {solved_property:new_value}
        for property_id, value in value_dict.iteritems():
          if not simulation_movement.isPropertyRecorded(property_id):
            simulation_movement.recordProperty(property_id)
          simulation_movement.setMappedProperty(property_id, value)
        simulation_movement.expand(activate_kw=activate_kw)
    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
