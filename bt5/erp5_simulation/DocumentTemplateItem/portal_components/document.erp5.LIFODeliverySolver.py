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
class LIFODeliverySolver(FIFODeliverySolver):
  """
  The LIFO solver reduces delivered quantity by reducing the quantity of
  simulation movements from the first order.
  """
  meta_type = 'ERP5 LIFO Delivery Solver'
  portal_type = 'LIFO Delivery Solver'
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

  def _getSimulationMovementList(self):
    """
    Returns a list of simulation movement sorted from the first order.
    """
    simulation_movement_list = self.getDeliveryValueList()
    if len(simulation_movement_list) > 1:
      return sorted(simulation_movement_list,
        key=lambda x:x.getExplanationValue().getStartDate())
    else:
      return simulation_movement_list
