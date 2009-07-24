# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5.Document.BPMDeliveryRule import BPMDeliveryRule

class BPMOrderRule(BPMDeliveryRule):
  """
    DISCLAIMER: Refer to BPMRule docstring disclaimer.

    This is BPM enabled Order Rule.
  """
  # CMF Type Definition
  meta_type = 'ERP5 BPM Order Rule'
  portal_type = 'BPM Order Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getInputMovementList(self, applied_rule):
    """Input movement list comes from order"""
    order = applied_rule.getDefaultCausalityValue()
    if order is not None:
      return order.getMovementList(
                     portal_type=order.getPortalOrderMovementTypeList())
    return []

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_path, current_property_dict):
    """Order rule specific update dictionary"""
    return {
      'order_value': movement,
      'order_ratio': 1,
      'delivery_ratio': 1,
      'deliverable': 1,
    }
