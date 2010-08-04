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
     import DeliveryRootSimulationRule

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

  def _getInputMovementList(self, applied_rule):
    """Return list of movements from delivery"""
    delivery = applied_rule.getDefaultCausalityValue()
    movement_list = []
    delivery_movement_type_list = self.getPortalAccountingMovementTypeList()
    if delivery is not None:
      existing_movement_list = applied_rule.objectValues()
      for movement in delivery.getMovementList(
        portal_type=delivery_movement_type_list):
        simulation_movement = self._getDeliveryRelatedSimulationMovement(
          movement)
        if simulation_movement is None or \
               simulation_movement in existing_movement_list:
          movement_list.append(movement)
    return movement_list
