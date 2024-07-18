##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Guillaume Michon        <guillaume@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.document.Amount import Amount


class Item(XMLObject, Amount):
  """
  Items in ERP5 are intended to provide a way to track objects
  """

  meta_type = 'ERP5 Item'
  portal_type = 'Item'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Price
                    , PropertySheet.Item
                    , PropertySheet.Amount
                    , PropertySheet.Reference
                    )

  security.declareProtected(Permissions.AccessContentsInformation, 'getPrice')
  def getPrice(self,context=None,**kw):
    """
    Get the Price in the context.

    If price is not stored locally, lookup a price
    """
    local_price = self._baseGetPrice()
    if local_price is None:
      # We must find a price for this movement
      # XXX we should not set a resource on item
      resource = self.getResourceValue()
      if resource is not None:
        local_price = resource.getPrice(self.asContext( context=context, **kw))
    return local_price

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getRemainingQuantity')
  def getRemainingQuantity(self):
    """
    Computes the quantity of an item minus quantity of all sub_items
    """
    sub_quantity = 0
    for sub_item in self.objectValues():
      if sub_item.isItem():
        sub_quantity += sub_item.getQuantity()
    return self.getQuantity() - sub_quantity
