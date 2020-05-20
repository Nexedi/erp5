##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.ERP5Type import ERP5TypeInformation

class DeliveryTypeInformation(ERP5TypeInformation):
  """
  Base type for Delivery Type.
  A Delivery Type is a Base Type on which a list of ledgers is set,
  which is the list of ledger allowed on the delivery documents.

  When creating new deliveries, the delivery's ledger will be initialized to
  the default ledger (the first one) set on the delivery type.
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  portal_type = "Delivery Type"
  meta_type = "ERP5 Delivery Type"

  security.declarePublic('constructInstance')
  def constructInstance(self, *args, **kw):
    "Creates a new delivery with a default ledger found on the portal type"
    delivery = super(DeliveryTypeInformation, self).constructInstance(*args, **kw)
    if not delivery.hasLedger():
      delivery.setLedger(self.getDefaultLedger())
    return delivery

InitializeClass( DeliveryTypeInformation )
