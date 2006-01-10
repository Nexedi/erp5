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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Delivery import Delivery
from Acquisition import aq_base
from zLOG import LOG

class Inventory(Delivery):
    """
      Inventory
    """
    # CMF Type Definition
    meta_type = 'ERP5 Inventory'
    portal_type = 'Inventory'
    isPortalContent = 1
    isRADContent = 1
    isDelivery = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Delivery
                      , PropertySheet.Path
                      , PropertySheet.FlowCapacity
                      )

    security.declareProtected(Permissions.AccessContentsInformation, 'getSimulationState')
    def getSimulationState(self, id_only=1):
      """
        Returns the current state in simulation
      """
      return 'delivered' # For now, consider that Inventory has no workflow XXX


    def immediateReindexObject(self,**kw):
      """
      Rewrite reindexObject so that we can insert lines in stock table
      to make sure all stock values for resources in this inventory
      is equal to null before the date of this inventory
      """
      resource_and_variation_list = []
      stock_object_list = []
      from Products.ERP5Type.Document import newTempDeliveryLine
      start_date = self.getStartDate()
      node = self.getDestination()
      for movement in self.getMovementList():
        resource =  movement.getResourceValue()
        if resource is not None and movement.getInventory() not in (None,''):
          variation_text = movement.getVariationText()
          if (resource,variation_text) not in resource_and_variation_list:
            resource_and_variation_list.append((resource,variation_text))
            current_inventory_list = resource.getInventoryList( \
                                    to_date          = start_date
                                  , variation_text   = variation_text
                                  , node             = node
                                  , simulation_state = self.getPortalCurrentInventoryStateList()
                                  , group_by_sub_variation = 1
                                  , group_by_variation = 1
                                  )
            kwd = {'uid':self.getUid()}
            kwd['start_date'] = start_date
            variation_list = variation_text.split('/n')
            for inventory in current_inventory_list:
              sub_variation_list = []
              if inventory.sub_variation_text is not None:
                sub_variation_list = inventory.sub_variation_text.split('\n')
              category_list = self.getCategoryList()
              if inventory.total_quantity != 0:
                temp_delivery_line = newTempDeliveryLine(self, 
                                                         self.getId())
                kwd['quantity'] = - inventory.total_quantity
                category_list.append('resource/%s' % inventory.resource_relative_url)
                category_list.extend(variation_list)
                category_list.extend(sub_variation_list)
                kwd['category_list'] = category_list
                temp_delivery_line.edit(**kwd)
                stock_object_list.append(temp_delivery_line)
      object_list = [self]
      self.portal_catalog.catalogObjectList(object_list)
      if len(stock_object_list)==0:
        # Make sure to remove all lines 
        from Products.ERP5Type.Document import newTempBase
        stock_object_list.append(newTempDeliveryLine(self,self.getId(),
                                 uid=self.getUid()))
      LOG('stock_object_list',0,[x.__dict__ for x in stock_object_list])
      self.portal_catalog.catalogObjectList(stock_object_list,
           method_id_list=('z_catalog_stock_list',),
           disable_cache=1,check_uid=0)

    security.declarePublic( 'recursiveReindexObject' )
    def recursiveReindexObject(self, *args, **kw):
      """
      Do not use group_method_id for the inventory, but it can
      be used for inventory lines and cells
      """
      root_indexable = int(getattr(self.getPortalObject(),'isIndexable',1))
      self._reindexObject()
      if self.isIndexable and root_indexable:
        self.activate(group_method_id='portal_catalog/catalogObjectList', 
            expand_method_id='getIndexableChildValueList', 
            **kw).recursiveImmediateReindexObject(*args, **kw)

    security.declareProtected( Permissions.AccessContentsInformation, 'getIndexableChildValueList' )
    def getIndexableChildValueList(self):
      """
        Get indexable childen recursively.
      """
      value_list = []
      if self.isIndexable:
        #value_list.append(self) # do not include self
        for c in self.objectValues():
          if hasattr(aq_base(c), 'getIndexableChildValueList'):
            value_list.extend(c.getIndexableChildValueList())
      return value_list

    def _reindexObject(self, *args, **kw):
      """
      Defined here because we want to 
      Make sure to call without the group_method_id for inventories
      """
      root_indexable = int(getattr(self.getPortalObject(),'isIndexable',1))
      if self.isIndexable and root_indexable:
        self.activate(**kw).immediateReindexObject(*args, **kw)
