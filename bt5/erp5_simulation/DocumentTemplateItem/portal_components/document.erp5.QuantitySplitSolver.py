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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Globals import PersistentMapping
from erp5.component.mixin.SolverMixin import SolverMixin
from erp5.component.mixin.ConfigurableMixin import ConfigurableMixin
from erp5.component.module.MovementCollectionDiff import _getPropertyAndCategoryList
from erp5.component.interface.ISolver import ISolver
from erp5.component.interface.IConfigurable import IConfigurable
import six

@zope.interface.implementer(ISolver,
                            IConfigurable,)
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

  # ISolver Implementation
  def _solve(self, activate_kw=None):
    """
    """
    self._solveBySplitting(activate_kw=activate_kw)

  def _solveBySplitting(self, activate_kw=None):
    """
    contains all the logic to split. This method is convenient in case
    another solver needs it.
    """
    solver_dict = {}
    new_movement_list = []
    configuration_dict = self.getConfigurationPropertyDict()
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)
    for movement, simulation_movement_list in six.iteritems(delivery_dict):
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
        simulation_id = simulation_movement.getId().split("_split_")[0]
        new_id = "%s_split_%s" % (simulation_id, split_index)
        applied_rule = simulation_movement.getParentValue()
        while getattr(aq_base(applied_rule), new_id, None) is not None:
          split_index += 1
          new_id = "%s_split_%s" % (simulation_id, split_index)
        # Copy at same level
        kw = _getPropertyAndCategoryList(simulation_movement)
        kw.update(delivery=None, quantity=split_quantity)
        new_movement = applied_rule.newContent(
          new_id, simulation_movement.getPortalType(),
          activate_kw=activate_kw, **kw)
        new_movement_list.append(new_movement)
        # Dirty code until IPropertyRecordable is revised.
        # Merge original simulation movement recorded property to new one.
        recorded_property_dict = simulation_movement._getRecordedPropertyDict(None)
        if recorded_property_dict:
          new_movement_recorded_property_dict = new_movement._getRecordedPropertyDict(None)
          if new_movement_recorded_property_dict is None:
            new_movement_recorded_property_dict = new_movement._recorded_property_dict = PersistentMapping()
          new_movement_recorded_property_dict.update(recorded_property_dict)
        # record zero quantity property, because this was originally zero.
        # without this, splitanddefer after accept decision does not work
        # properly.
        current_quantity = new_movement.getQuantity()
        new_movement.setQuantity(0)
        new_movement.recordProperty('quantity')
        new_movement.setQuantity(current_quantity)
        start_date = configuration_dict.get('start_date', None)
        if start_date is not None:
          new_movement.recordProperty('start_date')
          new_movement.setStartDate(start_date)
        stop_date = configuration_dict.get('stop_date', None)
        if stop_date is not None:
          new_movement.recordProperty('stop_date')
          new_movement.setStopDate(stop_date)
        if activate_kw:
          new_movement.setDefaultActivateParameterDict({})
        simulation_movement.expand(activate_kw=activate_kw)
        new_movement.expand(activate_kw=activate_kw)
    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
    solver_dict["new_movement_list"] = new_movement_list
    return solver_dict