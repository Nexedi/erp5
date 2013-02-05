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
"""
"""

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5.Document.DeliveryRootSimulationRule \
     import DeliveryRootSimulationRule, DeliveryRuleMovementGenerator

class InvoiceRootSimulationRule(DeliveryRootSimulationRule):
  """
  """
  # CMF Type Definition
  meta_type = 'ERP5 Invoice Root Simulation Rule'
  portal_type = 'Invoice Root Simulation Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self, movement):
    """
    Tells whether generated movement needs to be accounted or not.

    Invoice movement are never accountable, so simulation movement for
    invoice movements should not be accountable either.
    """
    return False

  def _getMovementGenerator(self, context):
    """
    Return the movement generator to use in the expand process
    """
    return InvoiceRuleMovementGenerator(applied_rule=context, rule=self)

class InvoiceRuleMovementGenerator(DeliveryRuleMovementGenerator):

  def _getPortalDeliveryMovementTypeList(self): # This is bad XXX-JPS - use use
    portal = self._rule.getPortalObject()
    return portal.getPortalInvoiceMovementTypeList() + \
           portal.getPortalTaxMovementTypeList()
