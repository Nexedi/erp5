# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Legacy.Document.OrderRule import OrderRule

class OrderRootSimulationRule(OrderRule):
  """
  Order Rule object make sure an Order in the simulation
  is consistent with the real order

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Order Root Simulation Rule'
  portal_type = 'Order Root Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_link, current_property_dict):
    """Order rule specific update dictionary"""
    return {
      'delivery': movement.getRelativeUrl(),
    }
