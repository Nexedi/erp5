# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2025 Nexedi SA and Contributors. All Rights Reserved.
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
from erp5.component.mixin.RuleMixin import RuleMixin
from erp5.component.mixin.MovementGeneratorMixin import MovementGeneratorMixin
from erp5.component.mixin.MovementCollectionUpdaterMixin import \
     MovementCollectionUpdaterMixin
from erp5.component.interface.IRule import IRule
from erp5.component.interface.IDivergenceController import IDivergenceController
from erp5.component.interface.IMovementCollectionUpdater import IMovementCollectionUpdater

@zope.interface.implementer(IRule,
                            IDivergenceController,
                            IMovementCollectionUpdater)
class BankReconciliationRootSimulationRule(RuleMixin, MovementCollectionUpdaterMixin):
  """
  Bank Reconciliation Rule creates Simulation Movements for Bank Reconciliation
  movements, and ensures consistency of these movements with Payment Transaction
  movements.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Bank Reconciliation Root Simulation Rule'
  portal_type = 'Bank Reconciliation Root Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
    PropertySheet.Task,
    PropertySheet.Predicate,
    PropertySheet.Reference,
    PropertySheet.Version,
    PropertySheet.Rule
  )

  security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
  def isAccountable(self, movement):
    """
    Bank Reconciliation movements are like Order movements, not accountable.
    """
    return False

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process.
    """
    return BankReconciliationRuleMovementGenerator(applied_rule=context, rule=self)

  def _isProfitAndLossMovement(self, movement):
    return False

class BankReconciliationRuleMovementGenerator(MovementGeneratorMixin):
  def _getUpdatePropertyDict(self, input_movement):
    """
    Set properties not already available on Bank Reconciliation Line.
    """
    price_currency = input_movement.getSourcePayment() and \
      input_movement.getSourcePaymentValue().getPriceCurrency()

    return {
      'causality': input_movement.getRelativeUrl(),
      'delivery': None,
      'price_currency': price_currency,
      'quantity_unit': price_currency,
      'resource': price_currency,
      'price': 1.0,
    }

  def _updateGeneratedMovementList(self, input_movement, generated_movement_list):
    """
    Tries to set aggregate on bank lines when possible. If any issue is
    encountered, nothing is set, and reconciliation of the line must be done
    manually.
    """
    # input_movement = Bank Reconciliation Line
    # generated_movement_list = Accounting Transaction Line
    for simulation_movement_value in generated_movement_list:
      trade_model_path_list = simulation_movement_value.getCausalityValueList(portal_type="Trade Model Path")
      if len(trade_model_path_list) == 1:
        if trade_model_path_list[0].getEfficiency() < 0.0:
          simulation_movement_value.setAggregateValue(input_movement)

    return generated_movement_list

  def _getInputMovementList(self, movement_list=None, rounding=None):
    """
    Input movements are lines from the Bank Reconciliation object.
    """
    bank_reconciliation = self._applied_rule.getDefaultCausalityValue()
    if bank_reconciliation is None:
      return []
    else:
      return bank_reconciliation.getSimulableMovementList()