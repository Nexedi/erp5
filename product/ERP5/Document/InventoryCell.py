##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from Acquisition import aq_base, aq_inner, aq_parent, aq_self
from AccessControl import ClassSecurityInfo

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface

from Products.ERP5.Document.DeliveryCell import DeliveryCell
from Products.ERP5.Document.Movement import Movement

class InventoryCell(DeliveryCell):
    """
      A DeliveryCell allows to define specific quantities
      for each variation of a resource in a delivery line.
    """

    meta_type = 'ERP5 Inventory Cell'
    portal_type = 'Inventory Cell'
    add_permission = Permissions.AddERP5Content
    isPortalContent = 1
    isRADContent = 1
    isMovement = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Inventory
                      , PropertySheet.Task
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.Predicate
                      , PropertySheet.Domain
                      , PropertySheet.MappedValue
                      , PropertySheet.ItemAggregation
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une ligne tarifaire."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addInventoryCell'
         , 'immediate_view' : 'inventory_cell_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'inventory_cell_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'inventory_cell_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }


    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='movement'):
      """
          This method can be overriden
      """
      return 0

    security.declareProtected(Permissions.AccessContentsInformation, 'getQuantity')
    def getQuantity(self):
      """
        Computes a quantity which allows to reach inventory

        Bug fix method for Coramy purpose - Coramy used production_quantity as property
        list of mapped value which generated errors of stock. It can be safely removed in
        the near future.
      """
      aself = aq_base(self)
      if hasattr(aself, 'production_quantity') or  hasattr(aself, 'consumption_quantity'):
        # Error - we must fix this
        if getattr(aself, 'production_quantity', 0.0) > 0.0:
          self.setProductionQuantity(aself.production_quantity)
        elif getattr(aself, 'consumption_quantity', 0.0) > 0.0:
          self.setConsumptionQuantity(aself.consumption_quantity)
        if hasattr(aself, 'production_quantity'):
          delattr(self, 'production_quantity')
        if hasattr(aself, 'consumption_quantity'):
          delattr(self, 'consumption_quantity')
        if hasattr(self, 'mapped_value_property_list'):
          if 'consumption_quantity' in self.mapped_value_property_list:
            self.mapped_value_property_list = filter(lambda s: s!='consumption_quantity',self.mapped_value_property_list)
          if 'production_quantity' in self.mapped_value_property_list:
            self.mapped_value_property_list = filter(lambda s: s!='production_quantity',self.mapped_value_property_list)
          if 'quantity' not in self.mapped_value_property_list:
            self.mapped_value_property_list = list(self.mapped_value_property_list) + ['quantity']
      # First check if quantity already exists
      quantity = self._baseGetQuantity()
      if quantity not in (0.0, 0, None):
        return quantity
      return self.getInventory()
      # Find total of movements in the past - XXX
      current_inventory = self.InventoryLine_zGetInventoryList(
        section_uid = self.getDestinationSectionUid(), node_uid = getDestinationUid())[0].inventory
      return self.getInventory() - current_inventory

    def _setItemIdList(self, value):
      """
        Computes total_quantity of all given items and stores this total_quantity
        in the inventory attribute of the cell
      """
      given_item_id_list = value
      item_object_list = []
      for item in given_item_id_list :
        item_result_list = self.portal_catalog(id = item, portal_type="Piece Tissu")
        if len(item_result_list) == 1 :
          try :
            object = item_result_list[0].getObject()
          except :
            object = None
        else :
          object = None

        if object is not None :
          item_object_list.append(object)

      # update item_id_list and build relation
      self.setAggregateValueList(item_object_list)

      # update inventory if needed
      if len(item_object_list)>0 :

        quantity = 0

        for object_item in item_object_list :
          quantity += object_item.getQuantity()

        self.setInventory(quantity)

    # Required for indexing
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventoriatedQuantity')
    def getInventoriatedQuantity(self):
      """
        Take into account efficiency in converted target quantity
      """
      return Movement.getInventoriatedQuantity(self)

    def _setProducedItemIdList(self, value):
      """
        Computes total_quantity of all given items and stores this total_quantity
        in the quantity attribute of the cell
      """
      given_item_id_list = value
      item_object_list = []
      for item in given_item_id_list :
        item_result_list = self.portal_catalog(id = item, portal_type="Piece Tissu")
        if len(item_result_list) == 1 :
          try :
            object = item_result_list[0].getObject()
          except :
            object = None
        else :
          object = None

        if object is not None :
          item_object_list.append(object)

      # update item_id_list and build relation
      self.setAggregateValueList(item_object_list)

      # update inventory if needed
      if len(item_object_list)>0 :

        quantity = 0

        for object_item in item_object_list :
          quantity += object_item.getQuantity()

        self.setProductionQuantity(quantity)

    def _setConsumedItemIdList(self, value):
      """
        Computes total_quantity of all given items and stores this total_quantity
        in the quantity attribute of the cell
      """
      given_item_id_list = value
      item_object_list = []
      for item in given_item_id_list :
        item_result_list = self.portal_catalog(id = item, portal_type="Piece Tissu")
        if len(item_result_list) == 1 :
          try :
            object = item_result_list[0].getObject()
          except :
            object = None
        else :
          object = None

        if object is not None :
          item_object_list.append(object)

      # update item_id_list and build relation
      self.setAggregateValueList(item_object_list)

      # update inventory if needed
      if len(item_object_list)>0 :

        quantity = 0

        for object_item in item_object_list :
          quantity += object_item.getRemainingQuantity()

        self.setConsumptionQuantity(quantity)

    def getProducedItemIdList(self):
      """
        Returns list of items if production_quantity != 0.0
      """
      if self.getProductionQuantity() != 0.0 :
        return self.getItemIdList()
      else :
        return []

    def getConsumedItemIdList(self):
      """
        Returns list of items if consumption_quantity != 0.0
      """
      if self.getConsumptionQuantity() != 0.0 :
        return self.getItemIdList()
      else :
        return []
