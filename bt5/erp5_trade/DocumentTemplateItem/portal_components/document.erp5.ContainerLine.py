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

from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.document.DeliveryLine import DeliveryLine

class ContainerLine(DeliveryLine):
  """
  A DeliveryLine object allows to implement lines in
  Deliveries (packing list, order, invoice, etc.)

  It may include a price (for insurance, for customs, for invoices,
  for orders)
  """
  meta_type = 'ERP5 Container Line'
  portal_type = 'Container Line'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Price
                    , PropertySheet.VariationRange
                    , PropertySheet.ItemAggregation
                    )

  # Cell Related
  security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
  def newCellContent(self, id, portal_type='Container Cell', **kw): # pylint: disable=redefined-builtin
    """Overriden to specify default portal type
    """
    return self.newContent(id=id, portal_type=portal_type, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
  def isAccountable(self):
    """
    Returns 1 if this needs to be accounted
    Only account movements which are not associated to a delivery
    Whenever delivery is there, delivery has priority
    """
    # Never accountable
    return 0

  security.declareProtected(Permissions.AccessContentsInformation, 'isDivergent')
  def isDivergent(self):
    """Return True if this movement diverges from the its simulation.
    Container Lines are never divergent.
    """
    return False

  security.declareProtected(Permissions.AccessContentsInformation, 'getTotalQuantity')
  def getTotalQuantity(self, *args, **kw):
    """
    Returns the quantity if no cell or the total quantity if cells
    """
    base_id = 'movement'
    if not self.hasCellContent(base_id=base_id):
      return self.getQuantity()
    return sum(cell.getQuantity() for cell in
      self.getCellValueList(base_id=base_id))