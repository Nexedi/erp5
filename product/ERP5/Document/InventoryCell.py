##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, interfaces

from Products.ERP5.Document.DeliveryCell import DeliveryCell


class InventoryCell(DeliveryCell):
    """
      An InventoryCell allows to define specific inventory
      for each variation of a resource in an inventory line.
    """

    meta_type = 'ERP5 Inventory Cell'
    portal_type = 'Inventory Cell'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isMovement = 1
    isInventoryMovement = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    __implements__ = ( interfaces.IVariated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.InventoryMovement
                      , PropertySheet.Task
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                      , PropertySheet.ItemAggregation
                      )
    
    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalInventory')
    def getTotalInventory(self):
      """
        Returns the inventory if no cell or the total inventory if cells
      """
      if not self.hasCellContent():
        return self.getInventory()
      else:
        # Use MySQL
        aggregate = self.InventoryLine_zGetTotal()[0]
        return aggregate.total_inventory or 0.0

    security.declareProtected(Permissions.AccessContentsInformation, 'getQuantity')
    def getQuantity(self):
      """
        Computes a quantity which allows to reach inventory
      """
      if not self.hasCellContent():
        # First check if quantity already exists
        quantity = self._baseGetQuantity()
        if quantity not in (0.0, 0, None):
          return quantity
        # Make sure inventory is defined somewhere (here or parent)
        if getattr(aq_base(self), 'inventory', None) is None:
          return 0.0 # No inventory defined, so no quantity
        return self.getInventory()
      else:
        return None
      
    # Inventory cataloging
    security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedInventory')
    def getConvertedInventory(self):
      """
        provides a default inventory value - None since
        no inventory was defined.
      """
      return self.getInventory() # XXX quantity unit is missing

    def reindexObject(self, *args, **kw):
      """
      Make sure to reindex the inventory
      """
      self.getParentValue().reindexObject(*args, **kw)
