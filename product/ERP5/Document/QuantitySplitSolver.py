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
from Acquisition import aq_base
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.mixin.solver import SolverMixin
from Products.ERP5.mixin.configurable import ConfigurableMixin
from Products.ERP5.MovementCollectionDiff import _getPropertyAndCategoryList

class QuantitySplitSolver(SolverMixin, ConfigurableMixin, XMLObject):
  """Target solver that split the prevision based on quantity.

  It creates another prevision movement with the delta quantity between decision
  and prevision.
  """
  meta_type = 'ERP5 Quantity Split Solver'
  portal_type = 'Quantity Split Solver'
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
                    , PropertySheet.Arrow
                    , PropertySheet.TargetSolver
                    )
  # Declarative interfaces
  zope.interface.implements(interfaces.ISolver,
                            interfaces.IConfigurable,
                           )

  # ISolver Implementation
  def solve(self, activate_kw=None):
    """
    """
    configuration_dict = self.getConfigurationPropertyDict()
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)
    for movement, simulation_movement_list in delivery_dict.iteritems():
      decision_quantity = movement.getQuantity()
      delivery_solver = self.getParentValue().newContent(
        portal_type=configuration_dict['delivery_solver'],
        temp_object=True)
      delivery_solver.setDeliveryValueList(simulation_movement_list)
      # Update the quantity using delivery solver algorithm
      split_list = delivery_solver.setTotalQuantity(decision_quantity,
                                                    activate_kw=activate_kw)
      # Create split movements
      for (simulation_movement, split_quantity) in split_list:
        split_index = 0
        new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
        applied_rule = simulation_movement.getParentValue()
        while getattr(aq_base(applied_rule), new_id, None) is not None:
          split_index += 1
          new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
        # Copy at same level
        kw = _getPropertyAndCategoryList(simulation_movement)
        kw.update({'portal_type':simulation_movement.getPortalType(),
                   'id':new_id,
                   'delivery':None,
                   'quantity':split_quantity})
        new_movement = applied_rule.newContent(activate_kw=activate_kw, **kw)
        if activate_kw is not None:
          new_movement.setDefaultActivateParameters(
            activate_kw=activate_kw, **activate_kw)
        start_date = configuration_dict.get('start_date', None)
        if start_date is not None:
          new_movement.recordProperty('start_date')
          new_movement.setStartDate(start_date)
        stop_date = configuration_dict.get('stop_date', None)
        if stop_date is not None:
          new_movement.recordProperty('stop_date')
          new_movement.setStopDate(stop_date)
        # XXX we need to call expand on both simulation_movement and new_movement here?
        # simulation_movement.expand(activate_kw=activate_kw)
        # new_movement.expand(activate_kw=activate_kw)
    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
