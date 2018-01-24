# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5.Document.InvoiceTransactionSimulationRule import (InvoiceTransactionSimulationRule,
                                                                     InvoiceTransactionRuleMovementGenerator)

class InventoryAssetPriceAccountingRuleMovementGenerator(InvoiceTransactionRuleMovementGenerator):
  """
  """
  # CMF Type Definition
  meta_type = 'ERP5 Inventory Asset Price Accounting Simulation Rule'
  portal_type = 'Inventory Asset Price Accounting Simulation Rule'

  ## XXX: "the applicable sale/internal supply (if defined)" => even if the
  ## price is set to None on the PPLL/SPLL, it will be set anyway by
  ## Movement_getPriceCalculationOperandDict (lookup for Sale Supply)

  def _getInputMovementList(self, movement_list=None, rounding=False):
    simulation_movement = self._applied_rule.getParentValue()

    # ERP5 generic implementation of getPrice():
    # 1. PL 'price' => 
    # 2. Movement_getPriceCalculationOperandDict()
    #    => Supply Line...
    quantity = simulation_movement.getPrice()
    if quantity is None:
      # XXX: "or fails to generate, and creates a "stock decrease" (expense)"???
      raise NotImplementedError

      # use = simulation_movement.getUse()
      # if use == 'trade/sale':
      #   portal_type = 'Sale Supply Line'
      # elif use == 'trade/purchase':
      #   portal_type = 'Purchase Supply Line'
      # else:
      #   raise NotImplementatedError("%s: use='%s' not handled by this Rule" %
      #                               (simulation_movement.getPath(), use))

      # domain_tool = simulation_movement.getPortalObject().portal_domains
      # sale_supply_line_list = domain_tool.searchPredicateList(
      #   simulation_movement,
      #   portal_type=portal_type)

      # if len(sale_supply_line_list) == 0:
      #   return ()

      # quantity = sale_supply_line_list[0].getBasePrice()

    return [simulation_movement.asContext(quantity=quantity)]

  def _getUpdatePropertyDict(self, input_movement):
    update_property_dict = InvoiceTransactionRuleMovementGenerator._getUpdatePropertyDict(
      self,
      input_movement)

    # XXX: Root Applied Rule?
    use = input_movement.getUse()
    if use == 'trade/sale':
      start_date = stop_date = input_movement.getStartDate()
    elif use == 'trade/purchase':
      start_date = stop_date = input_movement.getStopDate()
      update_property_dict['source_section'] = input_movement.getDestinationSection()
    else:
      raise NotImplementedError("%s: use='%s' not handled by this Rule" %
                                  (input_movement.getPath(), use))

    update_property_dict['start_date'] = start_date
    update_property_dict['stop_date'] = stop_date

    return update_property_dict

class InventoryAssetPriceAccountingSimulationRule(InvoiceTransactionSimulationRule):
  def _getMovementGenerator(self, context):
    return InventoryAssetPriceAccountingRuleMovementGenerator(
      applied_rule=context, rule=self)
