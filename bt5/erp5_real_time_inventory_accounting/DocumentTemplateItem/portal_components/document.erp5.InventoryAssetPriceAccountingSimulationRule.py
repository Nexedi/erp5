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

from erp5.component.document.InvoiceTransactionSimulationRule import (InvoiceTransactionSimulationRule,
                                                                     InvoiceTransactionRuleMovementGenerator)

class InventoryAssetPriceAccountingRuleMovementGenerator(InvoiceTransactionRuleMovementGenerator):
  """
  """

  def _updateGeneratedMovementList(self, input_movement, generated_movement_list):
    """Support Transit use case
    """
    generated_movement_list = super(
      InventoryAssetPriceAccountingRuleMovementGenerator,
      self,
    )._updateGeneratedMovementList(
      input_movement,
      generated_movement_list,
    )
    for movement in generated_movement_list:
      update_dict = {}
      if movement.getLedger() in ('stock/stock/entree',
                                  'stock/preparation/entree',
                                  'stock/transit/sortie',
                                  'stock/customs/entree'):
        update_dict['start_date'] = update_dict['stop_date'] = input_movement.getStopDate()
      elif movement.getLedger() in ('stock/stock/sortie',
                                    'stock/preparation/sortie',
                                    'stock/transit/entree'):
        update_dict['start_date'] = update_dict['stop_date'] = input_movement.getStartDate()
      movement._edit(**update_dict)

      input_movement.log("%r (input_movement=%r): ledger=%r, start_date=%r, stop_date=%r" %
                          (movement,
                          input_movement,
                          movement.getLedger(),
                          movement.getStartDate(),
                          movement.getStopDate()))
    return generated_movement_list

  def _getInputMovementList(self, movement_list=None, rounding=False):
    simulation_movement = self._applied_rule.getParentValue()

    # No expand if price is not set (already checked in 'Test Method ID' on the Rule).
    # Price is automatically acquired from Supply if not set directly on PL Movement.
    quantity = simulation_movement.getPrice()
    if quantity is None:
      return []

    return [simulation_movement.asContext(quantity=quantity)]

  def _getUpdatePropertyDict(self, input_movement):
    update_property_dict = InvoiceTransactionRuleMovementGenerator._getUpdatePropertyDict(
      self,
      input_movement)

    if input_movement.getRootAppliedRule().getCausalityValue().getPortalType().startswith('Purchase'):
      update_property_dict['source_section'] = input_movement.getDestinationSection()

    return update_property_dict


class InventoryAssetPriceAccountingSimulationRule(InvoiceTransactionSimulationRule):
  # CMF Type Definition
  meta_type = 'ERP5 Inventory Asset Price Accounting Simulation Rule'
  portal_type = 'Inventory Asset Price Accounting Simulation Rule'

  def _getMovementGenerator(self, context):
    return InventoryAssetPriceAccountingRuleMovementGenerator(
      applied_rule=context, rule=self)
