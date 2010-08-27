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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Legacy.Document.DeliveryRule import DeliveryRule

class DeliveryRootSimulationRule(DeliveryRule):
  """
  Delivery Root Simulation Rule is a root level rule for Deliveries.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Delivery Root Simulation Rule'
  portal_type = 'Delivery Root Simulation Rule'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
                                       business_link, current_property_dict):
    """Order rule specific update dictionary"""
    return {
      'delivery': movement.getRelativeUrl(),
    }

# Fix subclasses (ex: AccountingTransactionRootSimulationRule)
from Products.ERP5.Document import DeliveryRootSimulationRule as original_module
original_class = original_module.DeliveryRootSimulationRule
try:
  original_module.DeliveryRootSimulationRule = DeliveryRootSimulationRule
  import gc, os, sys
  from Products.ERP5Type.Utils import importLocalDocument
  for bases in gc.get_referrers(original_class):
    if type(bases) is tuple:
      for subclass in gc.get_referrers(bases):
        if getattr(subclass, '__bases__', None) is bases:
          importLocalDocument(subclass.__name__,
            os.path.dirname(sys.modules[subclass.__module__].__file__))
finally:
  original_module.DeliveryRootSimulationRule = original_class
