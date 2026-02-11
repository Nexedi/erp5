# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

from erp5.component.document.AccountingTransaction import AccountingTransaction
from erp5.component.mixin.SimulableMixin import SimulableMixin

class BankReconciliation(AccountingTransaction):
  """
  Bank Reconciliations are a representation of periodic reports from banks.
  They come in two flavor: with and without lines. Reports with lines are a
  full vision of all lines from the bank statement, while reports without line
  simply aggregate the final statement amount.

  From an ERP5-model perspective, Bank Reconciliations are items, but with
  properties close to Accounting Transactions (especially for lines), and
  giving birth to Simulation Movements, being in fact Accounting Transaction
  Lines.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Bank Reconciliation'
  portal_type = 'Bank Reconciliation'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
  def isAccountable(self):
    """
    Bank Reconciliation are not actually deliveries, so override method from parent.
    """
    return 0

  def getSimulableMovementList(self):
    """
    Returns all lines which are either not linked to a transaction,
    or linked to a transaction which was built from the lines
    themselves.
    """
    simulable_movement_list = []
    for movement in self.getMovementList():
      aggregate_related_value = movement.getAggregateRelatedValue(portal_type=self.getPortalAccountingMovementTypeList())
      if aggregate_related_value is not None:
        delivery_related_value = aggregate_related_value.getDeliveryRelatedValue()
        if delivery_related_value is None or \
            delivery_related_value.getAggregateUid() != movement.getUid():
          continue
      simulable_movement_list.append(movement)
    return simulable_movement_list

  def _createRootAppliedRule(self):
    if self.getValidationState() not in ["open", "closed"]:
      return

    # Call directly super from Delivery, as Delivery redefines the method
    return SimulableMixin._createRootAppliedRule(self)

  def hasLineContent(self):
    return len(self.objectValues()) > 0

  def getQuantityRangeMax(self, **kw):
    if not self.hasLineContent():
      return self._baseGetQuantityRangeMax(**kw)

    # Strict test: do not match 0.0
    quantity_range_min = self.getQuantityRangeMin()
    if quantity_range_min is None:
      return None

    line_total = sum(line.getQuantity() for line in self.objectValues())

    return quantity_range_min + line_total