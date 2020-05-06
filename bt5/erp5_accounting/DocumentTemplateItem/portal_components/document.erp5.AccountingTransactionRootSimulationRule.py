##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5.Document.DeliveryRootSimulationRule \
     import DeliveryRootSimulationRule, DeliveryRuleMovementGenerator

class AccountingTransactionRootSimulationRule(DeliveryRootSimulationRule):
  """
  Accounting Transaction Root Simulation Rule is a root level rule for
  Accounting Transaction.
  """
  # CMF Type Definition
  meta_type = 'ERP5 Accounting Transaction Root Simulation Rule'
  portal_type = 'Accounting Transaction Root Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return AccountingTransactionRuleMovementGenerator(applied_rule=context,
                                                      rule=self)

class AccountingTransactionRuleMovementGenerator(DeliveryRuleMovementGenerator):

  def _getPortalDeliveryMovementTypeList(self):
    return self._rule.getPortalObject().getPortalAccountingMovementTypeList()
