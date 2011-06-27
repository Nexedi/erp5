# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.AcceptSolver import AcceptSolver

class TradeModelSolver(AcceptSolver):
  """Solve Divergences on Invoice Lines, and dependant trade model lines.

  It consist in accepting decision from invoice lines, and adopting prevision
  on trade model lines.
  """
  meta_type = 'ERP5 Trade Model Solver'
  portal_type = 'Trade Model Solver'
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
    Adopt new values to simulation movements, with keeping the original
    one recorded, and then update Trade Model related lines accordingly.
    """
    configuration_dict = self.getConfigurationPropertyDict()
    portal_type = self.getPortalObject().portal_types.getTypeInfo(self)
    solved_property_list = configuration_dict.get('tested_property_list',
                                                  portal_type.getTestedPropertyList())
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)

    # Here, items of delivery_list should be movements, not deliveries.
    delivery_set = set()
    solved_movement_list = delivery_dict.iterkeys()
    for movement in solved_movement_list:
      delivery = movement.getRootDeliveryValue()
      delivery_set.add(delivery)
    all_movement_list = sum([x.getMovementList() for x in delivery_set], [])

    # First, separate movements into invoice lines and trade model
    # related lines.
    # XXX is there any better way than using rule's reference?
    trade_model_related_movement_list = []
    for movement in all_movement_list:
      if movement in solved_movement_list:
        continue
      applied_rule = movement.getDeliveryRelatedValue().getParentValue()
      # hard coded reference name
      if applied_rule.getSpecialiseReference() == 'default_trade_model_rule':
        trade_model_related_movement_list.append(movement)

    # Second, apply changes on invoice lines to simulation movements,
    # then expand.
    for movement, simulation_movement_list in delivery_dict.iteritems():
      if movement in trade_model_related_movement_list:
        continue
      for simulation_movement in simulation_movement_list:
        if activate_kw is not None:
          simulation_movement.setDefaultActivateParameters(
            activate_kw=activate_kw, **activate_kw)
        value_dict = {}
        for solved_property in solved_property_list:
          new_value = movement.getProperty(solved_property)
          if solved_property == 'quantity':
            new_quantity = new_value * simulation_movement.getDeliveryRatio()
            value_dict.update({'quantity':new_quantity})
          else:
            value_dict.update({solved_property:new_value})
        for property_id, value in value_dict.iteritems():
          if not simulation_movement.isPropertyRecorded(property_id):
            simulation_movement.recordProperty(property_id)
          simulation_movement.setMappedProperty(property_id, value)
        simulation_movement.expand(activate_kw=activate_kw)

    # Third, adopt changes on trade model related lines.
    # XXX non-linear case is not yet supported.
    for movement in trade_model_related_movement_list:
      if activate_kw is not None:
        movement.setDefaultActivateParameters(
          activate_kw=activate_kw, **activate_kw)
      for solved_property in solved_property_list:
        if solved_property == 'quantity':
          simulation_movement_list = movement.getDeliveryRelatedValueList()
          total_quantity = sum(
            [x.getQuantity() for x in simulation_movement_list])
          movement.setQuantity(total_quantity)
          for simulation_movement in simulation_movement_list:
            quantity = simulation_movement.getQuantity()
            delivery_ratio = quantity / total_quantity
            delivery_error = total_quantity * delivery_ratio - quantity
            simulation_movement.edit(delivery_ratio=delivery_ratio,
                                     delivery_error=delivery_error,
                                     activate_kw=activate_kw)
        else:
          # XXX TODO we need to support multiple values for categories or
          # list type property.
          simulation_movement = movement.getDeliveryRelatedValue()
          movement.setProperty(solved_property,
                               simulation_movement.getProperty(solved_property))

    # Finish solving
    if self.getPortalObject().portal_workflow.isTransitionPossible(
      self, 'succeed'):
      self.succeed()
