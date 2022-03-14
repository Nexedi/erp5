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
from erp5.component.document.FIFODeliverySolver import FIFODeliverySolver
from erp5.component.interface.IDeliverySolver import IDeliverySolver

@zope.interface.implementer(IDeliverySolver,)
class MinimisePriceDeliverySolver(FIFODeliverySolver):
  """
  The Minimise Price deliver solver distributes quantity in order to minimise
  price.
  """
  meta_type = 'ERP5 Minimise Price Delivery Solver'
  portal_type = 'Minimise Price Delivery Solver'
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
  security.declareProtected(Permissions.ModifyPortalContent, 'setTotalQuantity')
  def setTotalQuantity(self, new_quantity, activate_kw=None):
    """
    """
    result = []
    simulation_movement_list = self._getSimulationMovementList()
    remaining_quantity = self.getTotalQuantity() - new_quantity
    if remaining_quantity > 0:
      # In case of reducing the quantity, we should start from the more
      # expensive price.
      simulation_movement_list.reverse()
    for movement in simulation_movement_list:
      if remaining_quantity:
        quantity = movement.getQuantity()
        if quantity < remaining_quantity:
          result.append((movement, quantity))
          remaining_quantity -= quantity
          movement.edit(quantity=0, delivery_ratio=0, activate_kw=activate_kw)
        else:
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
    Returns a list of simulation movement sorted from the lower price.
    """
    simulation_movement_list = self.getDeliveryValueList()
    if len(simulation_movement_list) > 1:
      return sorted(simulation_movement_list, key=lambda x:x.getPrice())
    else:
      return simulation_movement_list
