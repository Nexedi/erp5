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
  isInventory = 1

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
                    , PropertySheet.Inventory
                    )

  security.declarePublic('alternateReindexObject')
  def alternateReindexObject(self, **kw):
    """
    This method is called when an inventory object is included in a
    group of catalogged objects.
    """
    return self.immediateReindexObject(**kw)

  def immediateReindexObject(self, temp_constructor=None, **kw):
    """
    Rewrite reindexObject so that we can insert lines in stock table
    which will be equal to the difference between stock values for
    resource in the inventory and the one before the date of this inventory

    temp_constructor is used in some particular cases where we want
    to have our own temp object constructor, this is usefull if we
    want to use some classes with some particular methods
    """
    sql_catalog_id = kw.pop("sql_catalog_id", None)
    disable_archive = kw.pop("disable_archive", 0)
    connection_id = None
    if sql_catalog_id is not None:
      # try to get connection used in the catalog 
      catalog = self.portal_catalog[sql_catalog_id]
      for method in catalog.objectValues():
        if method.meta_type == "Z SQL Method":
          if 'deferred' not in method.connection_id \
               and 'transactionless' not in method.connection_id:
            connection_id = method.connection_id
            break
                
    resource_and_variation_dict = {}
    stock_object_list = []
    stock_append = stock_object_list.append
    if temp_constructor is None:
      from Products.ERP5Type.Document import newTempDeliveryLine
      temp_constructor = newTempDeliveryLine
    start_date = self.getStartDate()
    node = self.getDestination()
    # build a dict containing all inventory for this node 
    # group by resource/variation and then subvariation
    current_inventory_list = \
        self.getPortalObject().portal_simulation.getInventoryList(
                to_date=start_date,
                node=node,
                simulation_state=self.getPortalCurrentInventoryStateList(),
                group_by_sub_variation=1,
                group_by_variation=1,
                group_by_resource=1,
                connection_id=connection_id,
        )
    current_inventory_dict = {}
    current_inventory_key_id_list = ('resource_relative_url', 'variation_text')
    for line in current_inventory_list:
      current_inventory_key = tuple(
          [line[x] for x in current_inventory_key_id_list])
      if current_inventory_key[1] is None:
        # To be consistent
        current_inventory_key = (current_inventory_key[0], "")
      try:
        current_inventory_by_sub_variation = \
            current_inventory_dict[current_inventory_key]
      except KeyError:
        current_inventory_by_sub_variation = \
            current_inventory_dict[current_inventory_key] = {}
      current_inventory_by_sub_variation[line['sub_variation_text']] = \
            line['total_quantity']

    def getCurrentInventoryBySubVariation(**criterion_dict):
      current_inventory_key = tuple(
          [criterion_dict[x] for x in current_inventory_key_id_list])
      return current_inventory_dict.get(current_inventory_key, {})

    # Browse all movements on inventory and create diff line when necessary
    not_used_inventory_dict = {}
    inventory_uid = self.getUid()
    inventory_id = self.getId()
    for movement in self.getMovementList():
      if movement.getResourceValue() is not None and \
          movement.getQuantity() not in (None, ''):
        resource_path =  movement.getResource()
        variation_text = movement.getVariationText()
        movement_quantity = movement.getQuantity()
        destination_payment_path = movement.getDestinationPayment()          
        resource_and_variation_key = (resource_path, variation_text)
        inventory_by_subvariation_dict = getCurrentInventoryBySubVariation(
                          resource_relative_url=resource_path,
                          variation_text=variation_text)
        movement_sub_variation_text = movement.getSubVariationText()
        # Check wath is the quantity difference
        if movement_sub_variation_text in \
                              inventory_by_subvariation_dict.keys():
          total_quantity = inventory_by_subvariation_dict.pop(
                          movement_sub_variation_text)
          # Put remaining subvariation in a dict to know which one 
          # to removed at end
          not_used_inventory_dict[resource_and_variation_key] = \
                            inventory_by_subvariation_dict
          diff_quantity = movement_quantity - total_quantity
        else:
          # Inventory for new resource/variation/sub_variation
          diff_quantity = movement_quantity
          # Put remaining subvariation in a dict to know which one 
          # to removed at end
          not_used_inventory_dict[resource_and_variation_key] = \
                                        inventory_by_subvariation_dict

        # Create tmp movement with only diff between inventory
        # and previous stock values
        if diff_quantity != 0:
          kwd = {'uid': inventory_uid,
                 'start_date': start_date}
          if variation_text is not None:
            variation_list = variation_text.split('\n')
          else:
            variation_list = []
          category_list = self.getCategoryList()
          sub_variation_list = []
          if movement_sub_variation_text is not None:
            sub_variation_list = movement_sub_variation_text.split('\n')
          temp_delivery_line = temp_constructor(self,
                                                inventory_id)
          kwd['quantity'] = diff_quantity
          category_list.append('resource/%s' % resource_path)
          category_list.append(
              'destination_payment/%s' % destination_payment_path)
          category_list.extend(variation_list)
          category_list.extend(sub_variation_list)
          kwd['category_list'] = category_list
          temp_delivery_line.edit(**kwd)
          stock_append(temp_delivery_line)

    # Now create line to remove some subvariation text not present 
    # in new inventory
    for resource_and_variation_key in not_used_inventory_dict.keys():
      inventory_by_subvariation_dict = \
          not_used_inventory_dict[resource_and_variation_key]
      for sub_variation_text in inventory_by_subvariation_dict.keys():
        category_list = self.getCategoryList()
        quantity = inventory_by_subvariation_dict[sub_variation_text]
        resource_path, variation_text = resource_and_variation_key
        kwd = {'uid': inventory_uid,
               'start_date': start_date}
        if variation_text is not None:
          variation_list = variation_text.split('\n')
        else:
          variation_list = []                
        sub_variation_list = sub_variation_text.split('\n')
        diff_quantity = - quantity                    
        temp_delivery_line = temp_constructor(self, inventory_id)
        kwd['quantity'] = diff_quantity
        category_list.append('resource/%s' % resource_path)
        category_list.extend(variation_list)
        category_list.extend(sub_variation_list)
        kwd['category_list'] = category_list
        temp_delivery_line.edit(**kwd)
        stock_append(temp_delivery_line)

    # Reindex objects
    object_list = [self]
    self.portal_catalog.catalogObjectList(object_list, 
                                          disable_archive=disable_archive)
    if len(stock_object_list)==0:
      # Make sure to remove all lines
      from Products.ERP5Type.Document import newTempBase
      stock_append(temp_constructor(self, inventory_id, uid=inventory_uid))
    self.portal_catalog.catalogObjectList(
           stock_object_list, method_id_list=('z_catalog_stock_list', ),
           disable_cache=1, check_uid=0, disable_archive=disable_archive)

