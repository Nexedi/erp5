##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent, aq_self

from Products.ERP5.ERP5Globals import current_inventory_state_list

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.DeliveryLine import DeliveryLine
from Products.ERP5.Document.Path import Path
from Products.ERP5.Document.Movement import Movement

from zLOG import LOG

class InventoryLine(DeliveryLine):
    """
      A DeliveryLine object allows to implement lines in
      Deliveries (packing list, order, invoice, etc.)

      It may include a price (for insurance, for customs, for invoices,
      for orders)
    """

    meta_type = 'ERP5 Inventory Line'
    portal_type = 'Inventory Line'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

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

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une ligne tarifaire."""
         , 'icon'           : 'inventory_line_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addInventoryLine'
         , 'immediate_view' : 'inventory_line_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'inventory_line_view'
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
          , 'action'        : 'inventory_line_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_view'
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
        return aggregate.total_inventory


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
        return self.getInventory()
        # Find total of movements in the past - XXX
        resource_value = self.getResourceValue()
        if resource_value is not None:
          # Inventories can only be done in "real" locations / sectinos, not categories thereof
          #  -> therefore we use node and section
          current_inventory = resource_value.getInventory(
                        at_date = self.getStartDate(),
                        variation_text = self.getVariationText(),
                        node = self.getDestination(),
                        section = self.getDestinationSection(),
                        simulation_state = current_inventory_state_list)
          inventory = self.getInventory()
          if inventory in (None, ''):
            return None # Do not change inventory if no inventory value provided
          return self.getInventory() - current_inventory
        return self.getInventory()
      else:
        return None

    # Cell Related
    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Inventory Cell",id=id)
      return self.get(id)

    # For generation of matrix lines
    security.declareProtected( Permissions.ModifyPortalContent, '_setVariationCategoryList' )
    def _setVariationCategoryList(self, value):
      """
          Define the indices provided
          one list per index (kw)

          Any number of list can be provided
      """
      LOG('setCellRange',0,'')
      Movement._setVariationCategoryList(self, value)
      # Update the cell range automatically
      # This is far from easy and requires some specific wizzardry
      base_id = 'movement'
      kwd = {'base_id': base_id}
      new_range = self.DeliveryLine_asCellRange() # This is a site dependent script
      self._setCellRange(*new_range, **kwd )
      cell_range_key_list = self.getCellRangeKeyList(base_id = base_id)
      if cell_range_key_list <> [[None, None]] :
        for k in cell_range_key_list:
          LOG('new cell',0,str(k))
          c = self.newCell(*k, **kwd)
          c.edit( domain_base_category_list = self.getVariationBaseCategoryList(),
                  mapped_value_property_list = ('inventory', 'price',),
                  predicate_operator = 'SUPERSET_OF',
                  predicate_value = filter(lambda k_item: k_item is not None, k),
                  variation_category_list = filter(lambda k_item: k_item is not None, k),
                  force_update = 1
                )
          c.flushActivity(invoke=1)
      else:
        # If only one cell, delete it
        cell_range_id_list = self.getCellRangeIdList(base_id = base_id)
        for k in cell_range_id_list:
          if self.get(k) is not None:
            self[k].flushActivity(invoke=0)
            self[k].immediateReindexObject() # We are forced to do this is url is changed (not uid)
            self._delObject(k)

      # TO BE DONE XXX
      # reindex cells when price, quantity or source/dest changes

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
