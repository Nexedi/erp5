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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.ERP5Type import Permissions, PropertySheet, Interface
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Movement import Movement

from zLOG import LOG

class InventoryLine(DeliveryLine):
    """
      An Inventory Line describe the inventory of a resource, by variations.
    """

    meta_type = 'ERP5 Inventory Line'
    portal_type = 'Inventory Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isInventoryLine = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.InventoryMovement
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.VariationRange
                      , PropertySheet.ItemAggregation
                      )

    def _edit(self, REQUEST=None, force_update = 0, **kw):
      DeliveryLine._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
      # Calculate inventory
      item_list = self.getAggregateValueList()
      if item_list not in [None,[]]:
        inventory = 0
        for item in item_list:
          if item.getQuantity() not in [None, '']:
            inventory += item.getQuantity()
        self.setInventory(inventory)


    security.declareProtected(Permissions.AccessContentsInformation, 'getTotalInventory')
    def getTotalInventory(self):
      """
        Returns the inventory if no cell or the total inventory if cells
      """
      if not self.hasCellContent():
        return self.getInventory()
      else:
        # Use MySQL
        # There is no inventory column in mysql any more,
        # is it required to add it again. It is only
        # usefull for the user interface
        # aggregate = self.InventoryLine_zGetTotal()[0]
        # return aggregate.total_inventory or 0.0

        total_quantity = 0.0
        for cell in self.getCellValueList(base_id='movement'):
          if cell.getInventory() is not None:
            total_quantity += cell.getInventory()
        return total_quantity

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantity')
    def getQuantity(self):
      """
        Computes a quantity which allows to reach inventory
      """
      if not self.hasCellContent():
        # First check if quantity already exists
        quantity = self._baseGetQuantity()
        if quantity not in (0.0,0,None):
          return quantity
        # Make sure inventory is defined somewhere (here or parent)
        _marker = []
        inventory = getattr(aq_base(self), 'inventory', _marker)
        if inventory is not _marker and inventory is not None:
          return inventory
        return quantity
      else:
        return None

    # Inventory cataloging
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getConvertedInventory')
    def getConvertedInventory(self):
      """
        provides a default inventory value - None since
        no inventory was defined.
      """
      return self.getInventory() # XXX quantity unit is missing

    # Required for indexing
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInventoriatedQuantity')
    def getInventoriatedQuantity(self):
      """
        Take into account efficiency in converted target quantity
      """
      return Movement.getInventoriatedQuantity(self)

    def reindexObject(self, *args, **kw):
      """
      Make sure to reindex the inventory
      """
      self.getParentValue().recursiveReindexObject(*args, **kw)

