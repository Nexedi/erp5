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
from Products.ERP5Type.XMLMatrix import XMLMatrix
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
                      , PropertySheet.Inventory
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

# XXX Following method should be useless now
#     def _setItemIdList(self, value):
#       """
#         Computes total_quantity of all given items and stores this total_quantity
#         in the inventory attribute of the cell
#       """
#       if value is None:
#         return
#       previous_item_list = self.getAggregateValueList()
#       given_item_id_list = value
#       item_object_list = []
#       for item in given_item_id_list:
#         item_result_list = self.portal_catalog(id=item, portal_type="Piece Tissu")
#         if len(item_result_list) == 1:
#           try:
#             object = item_result_list[0].getObject()
#           except :
#             object = None
#         else:
#           object = None
#         if object is not None:
#           # if item was in previous_item_list keep it
#           if object in previous_item_list:
#             # we can add this item to the list of aggregated items
#             item_object_list.append(object)
#           # if new item verify if variated_resource of item == variated_resource of movement
#           elif (self.getResource() == object.getResource()) \
#            and (self.getVariationCategoryList() == object.getVariationCategoryList()):
#             # we can add this item to the list of aggregated items
#             item_object_list.append(object)
#       # update item_id_list and build relation
#       self.setAggregateValueList(item_object_list)
#       # update inventory if needed
#       if len(item_object_list) > 0:
#         quantity = 0
#         for object_item in item_object_list:
#           quantity += object_item.getQuantity()
#         self.setInventory(quantity)
# 
#     def _setProducedItemIdList(self, value):
#       """
#         Computes total_quantity of all given items and stores this total_quantity
#         in the quantity attribute of the cell
#       """
#       if value is None:
#         return
#       previous_item_list = self.getAggregateValueList()
#       given_item_id_list = value
#       item_object_list = []
#       for item in given_item_id_list:
#         item_result_list = self.portal_catalog(id=item, portal_type="Piece Tissu")
#         if len(item_result_list) == 1:
#           try:
#             object = item_result_list[0].getObject()
#           except:
#             object = None
#         else:
#           object = None
#         if object is not None:
#           # if item was in previous_item_list keep it
#           if object in previous_item_list:
#             # we can add this item to the list of aggregated items
#             item_object_list.append(object)
#           # if new item verify if variated_resource of item == variated_resource of movement
#           elif (self.getResource() == object.getResource()) \
#            and (self.getVariationCategoryList() == object.getVariationCategoryList()):
#             # now verify if item can be moved (not already done)
#             last_location_title = object.getLastLocationTitle()
#             if self.getDestinationTitle() != last_location_title or last_location_title == '':
#               # we can add this item to the list of aggregated items
#               item_object_list.append(object)
#       # update item_id_list and build relation
#       self.setAggregateValueList(item_object_list)
#       # update inventory if needed
#       if len(item_object_list) > 0:
#         quantity = 0
#         for object_item in item_object_list:
#           quantity += object_item.getQuantity()
#         self.setProductionQuantity(quantity)
# 
#     def _setConsumedItemIdList(self, value):
#       """
#         Computes total_quantity of all given items and stores this total_quantity
#         in the quantity attribute of the cell
#       """
#       if value is None:
#         return
#       previous_item_list = self.getAggregateValueList()
#       given_item_id_list = value
#       item_object_list = []
#       for item in given_item_id_list:
#         item_result_list = self.portal_catalog(id=item, portal_type="Piece Tissu")
#         if len(item_result_list) == 1:
#           try:
#             object = item_result_list[0].getObject()
#           except:
#             object = None
#         else:
#           object = None
#         if object is not None:
#           # if item was in previous_item_list keep it
#           if object in previous_item_list:
#             # we can add this item to the list of aggregated items
#             item_object_list.append(object)
#           # if new item verify if variated_resource of item == variated_resource of movement
#           elif (self.getResource() == object.getResource()) \
#            and (self.getVariationCategoryList() == object.getVariationCategoryList()):
#             # now verify if item can be moved (not already done)
#             last_location_title = object.getLastLocationTitle()
#             if self.getDestinationTitle() == last_location_title or last_location_title == '':
#               # we can add this item to the list of aggregated items
#               item_object_list.append(object)
#       # update item_id_list and build relation
#       self.setAggregateValueList(item_object_list)
#       # update inventory if needed
#       if len(item_object_list) > 0:
#         quantity = 0
#         for object_item in item_object_list:
#           quantity += object_item.getRemainingQuantity()
#           # we reset the location of the item
#           object_item.setLocation('')
#         self.setConsumptionQuantity(quantity)
# 
#     def getProducedItemIdList(self):
#       """
#         Returns list of items if production_quantity != 0.0
#       """
#       if self.getProductionQuantity() != 0.0:
#         return self.getItemIdList()
#       else:
#         return []
# 
#     def getConsumedItemIdList(self):
#       """
#         Returns list of items if consumption_quantity != 0.0
#       """
#       if self.getConsumptionQuantity() != 0.0:
#         return self.getItemIdList()
#       else:
#         return []

    # Inventory cataloging
    security.declareProtected(Permissions.AccessContentsInformation, 'getConvertedInventory')
    def getConvertedInventory(self):
      """
        provides a default inventory value - None since
        no inventory was defined.
      """
      return self.getInventory() # XXX quantity unit is missing

    # Required for indexing
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
    def getInventoriatedQuantity(self):
      """
        Take into account efficiency in converted target quantity
      """
      return Movement.getInventoriatedQuantity(self)

    def reindexObject(self, *args, **kw):
      """
      Make sure to reindex the inventory
      """
      self.getParentValue().recursiveReindexObject()

