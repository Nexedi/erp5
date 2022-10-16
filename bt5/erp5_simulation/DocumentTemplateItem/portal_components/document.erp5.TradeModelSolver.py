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
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.AcceptSolver import AcceptSolver
from erp5.component.interface.ISolver import ISolver
import six

@zope.interface.implementer(ISolver,)
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

  def _solve(self, activate_kw=None):
    """
    Adopt new values to simulation movements, with keeping the original
    one recorded, and then update Trade Model related lines accordingly.
    """
    portal = self.getPortalObject()
    solved_property_list = self.getConfigurationPropertyDict() \
                               .get('tested_property_list')
    if solved_property_list is None:
      solved_property_list = \
        portal.portal_types.getTypeInfo(self).getTestedPropertyList()
    delivery_dict = {} # {movement: simulation_movement_list}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)

    # First, separate movements into invoice lines and trade model
    # related lines.
    # XXX is there any better way than using rule's reference?
    trade_model_related_movement_dict = {}
    for delivery in {movement.getRootDeliveryValue()
                     for movement in delivery_dict}:
      for movement in delivery.getMovementList():
        movement_list = delivery_dict.get(movement)
        # hard coded reference name
        if movement_list:
          rule = movement_list[0].getParentValue().getSpecialiseReference()
          if rule != 'default_trade_model_rule':
            continue
          movement_list = movement.getDeliveryRelatedValueList()
        else:
          movement_list = movement.getDeliveryRelatedValueList()
          rule = movement_list[0].getParentValue().getSpecialiseReference()
          if rule != 'default_trade_model_rule':
            continue
        trade_model_related_movement_dict[movement] = movement_list

    with self.defaultActivateParameterDict(activate_kw, True):
      # Second, apply changes on invoice lines to simulation movements,
      # then expand.
      for movement, simulation_movement_list in six.iteritems(delivery_dict):
        if movement in trade_model_related_movement_dict:
          continue
        for simulation_movement in simulation_movement_list:
          value_dict = {}
          for solved_property in solved_property_list:
            new_value = movement.getProperty(solved_property)
            if solved_property == 'quantity':
              new_value *= simulation_movement.getDeliveryRatio()
            value_dict[solved_property] = new_value
          for property_id, value in six.iteritems(value_dict):
            if not simulation_movement.isPropertyRecorded(property_id):
              simulation_movement.recordProperty(property_id)
            simulation_movement.setProperty(property_id, value)
          simulation_movement.expand('immediate')

      # Third, adopt changes on trade model related lines.
      # XXX non-linear case is not yet supported.
      for movement, simulation_movement_list in \
          six.iteritems(trade_model_related_movement_dict):
        for solved_property in solved_property_list:
          if solved_property == 'quantity':
            total_quantity = sum(x.getQuantity()
              for x in simulation_movement_list)
            movement.setQuantity(total_quantity)
            for simulation_movement in simulation_movement_list:
              quantity = simulation_movement.getQuantity()
              if total_quantity:
                delivery_ratio = quantity / total_quantity
              else:
                delivery_ratio = 1.0 / len(simulation_movement_list)
              delivery_error = total_quantity * delivery_ratio - quantity
              simulation_movement.edit(delivery_ratio=delivery_ratio,
                                       delivery_error=delivery_error)
          else:
            # XXX TODO we need to support multiple values for categories or
            # list type property.
            movement.setProperty(solved_property,
              simulation_movement_list[0].getProperty(solved_property))

    # Finish solving
    if portal.portal_workflow.isTransitionPossible(self, 'succeed'):
      self.succeed()
