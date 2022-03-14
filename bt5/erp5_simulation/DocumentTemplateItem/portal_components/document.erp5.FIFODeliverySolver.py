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
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.interface.IDeliverySolver import IDeliverySolver

@zope.interface.implementer(IDeliverySolver,)
class FIFODeliverySolver(XMLObject):
  """
  The FIFO solver reduces delivered quantity by reducing the quantity of
  simulation movements from the last order.
  """
  meta_type = 'ERP5 FIFO Delivery Solver'
  portal_type = 'FIFO Delivery Solver'
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
                    , PropertySheet.DeliverySolver
                    )

  # IDeliverySolver Implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
  def getTotalQuantity(self):
    """
      Move this to mixin
    """
    total_quantity = 0
    for movement in self.getDeliveryValueList():
      total_quantity += movement.getQuantity()
    return total_quantity

  security.declareProtected(Permissions.ModifyPortalContent, 'setTotalQuantity')
  def setTotalQuantity(self, new_quantity, activate_kw=None):
    """
    Affect the difference of quantity to different simulation movements

    We assume that quantities are either all positives, or all negatives.
    """
    result = []
    remaining_quantity = self.getTotalQuantity() - new_quantity
    if new_quantity < 0:
      if remaining_quantity > 0:
        return result
    else:
      if remaining_quantity < 0:
        return result
    simulation_movement_list = self._getSimulationMovementList()
    for movement in simulation_movement_list:
      quantity = movement.getQuantity()
      # make sure we have same sign, or this code solver would not work
      assert (quantity * remaining_quantity) >= 0, "Could not solve if we do not have same sign"
      if abs(quantity) < abs(remaining_quantity):
        result.append((movement, quantity))
        remaining_quantity -= quantity
        movement.edit(quantity=0, delivery_ratio=0, activate_kw=activate_kw)
      else:
        # only append movement if we decrease the quantity, which means we
        # would surely split it. If remaining quantity is 0, the code is
        # just used to update delivery ratio
        if remaining_quantity:
          result.append((movement, remaining_quantity))
        movement_quantity = quantity - remaining_quantity
        delivery_ratio = 1.
        if new_quantity:
          delivery_ratio = movement_quantity / new_quantity
        movement.edit(quantity=movement_quantity,
                      delivery_ratio=delivery_ratio,
                      activate_kw=activate_kw)
        remaining_quantity = 0
    # Return movement, split_quantity tuples
    return result

  def _getSimulationMovementList(self):
    """
    Returns a list of simulation movement sorted from the last order.
    """
    simulation_movement_list = self.getDeliveryValueList()
    if len(simulation_movement_list) > 1:
      return sorted(simulation_movement_list,
        key=lambda x:x.getExplanationValue().getStartDate(), reverse=True)
    else:
      return simulation_movement_list
