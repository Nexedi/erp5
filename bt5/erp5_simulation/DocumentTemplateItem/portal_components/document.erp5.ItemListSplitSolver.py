# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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
from erp5.component.mixin.SolverMixin import SolverMixin
from erp5.component.mixin.ConfigurableMixin import ConfigurableMixin
from erp5.component.module.MovementCollectionDiff import _getPropertyAndCategoryList
from erp5.component.interface.ISolver import ISolver
from erp5.component.interface.IConfigurable import IConfigurable
import six

@zope.interface.implementer(ISolver,
                            IConfigurable,)
class ItemListSplitSolver(SolverMixin, ConfigurableMixin, XMLObject):
  """Target solver that split the prevision based on aggregated items.

  It creates another prevision movement with the items that were in prevision
  and have been removed in decision.
  """
  meta_type = 'ERP5 Item List Split Solver'
  portal_type = 'Item List Split Solver'
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

  def _solve(self, activate_kw=None):
    """This method create new movement based on difference of aggregate sets.
    It supports only removed items.
    Quantity divergence is also solved with sum of aggregated quantities stored
    on each updated movements.
    """
    configuration_dict = self.getConfigurationPropertyDict()
    delivery_dict = {}
    portal = self.getPortalObject()
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)

    for movement, simulation_movement_list in six.iteritems(delivery_dict):
      decision_aggregate_set = set(movement.getAggregateList())
      split_list = []
      for simulation_movement in simulation_movement_list:
        simulated_aggregate_set = set(simulation_movement.getAggregateList())
        difference_set = simulated_aggregate_set.difference(decision_aggregate_set)
        mirror_difference_set = decision_aggregate_set.difference(simulated_aggregate_set)
        if difference_set:
          # There is less aggregates in prevision compare to decision
          split_list.append((simulation_movement, difference_set))
        elif mirror_difference_set:
          # There is additional aggregates in decision compare to prevision
          raise NotImplementedError('Additional items detected. This solver'\
                ' does not support such divergence resolution.')
        else:
          # Same set, no divergence
          continue
      # Create split movements
      for (simulation_movement, splitted_aggregate_set) in split_list:
        split_index = 0
        new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
        applied_rule = simulation_movement.getParentValue()
        while getattr(aq_base(applied_rule), new_id, None) is not None:
          split_index += 1
          new_id = "%s_split_%s" % (simulation_movement.getId(), split_index)
        # Copy at same level
        kw = _getPropertyAndCategoryList(simulation_movement)
        previous_aggregate_list = simulation_movement.getAggregateList()
        new_aggregate_list = list(set(previous_aggregate_list)\
                                .symmetric_difference(splitted_aggregate_set))
        # freeze those properties only if not yet recorded
        # to avoid freezing already recorded value
        if not simulation_movement.isPropertyRecorded('aggregate'):
          simulation_movement.recordProperty('aggregate')

        # edit prevision movement
        simulation_movement.setAggregateList(new_aggregate_list)
        total_quantity = sum(item.getQuantity() for item in\
                                   simulation_movement.getAggregateValueList())
        simulation_movement.setQuantity(total_quantity)

        # create compensation decision movement
        total_quantity = sum([portal.restrictedTraverse(aggregate).getQuantity()\
                              for aggregate in splitted_aggregate_set])
        kw.update({'portal_type': simulation_movement.getPortalType(),
                   'id': new_id,
                   'delivery': None})
        # propagate same recorded properties from original movement
        # to store them in recorded_property
        for frozen_property in ('aggregate', 'start_date', 'stop_date',):
          if simulation_movement.isPropertyRecorded(frozen_property):
            kw[frozen_property] = simulation_movement.getRecordedProperty(frozen_property)

        new_movement = applied_rule.newContent(activate_kw=activate_kw, **kw)
        # freeze aggregate property
        new_movement.recordProperty('aggregate')
        # edit compensation decision movement
        new_movement.setAggregateList(list(splitted_aggregate_set))
        new_movement.setQuantity(total_quantity)

        if activate_kw is not None:
          new_movement.setDefaultActivateParameterDict(activate_kw)
        start_date = configuration_dict.get('start_date', None)
        if start_date is not None:
          new_movement.recordProperty('start_date')
          new_movement.setStartDate(start_date)
        stop_date = configuration_dict.get('stop_date', None)
        if stop_date is not None:
          new_movement.recordProperty('stop_date')
          new_movement.setStopDate(stop_date)

    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
