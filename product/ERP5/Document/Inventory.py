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

  # method used to build category list that willbe set on tmp line
  def appendToCategoryListFromUid(self, category_list, uid, base_category):
    object_list = [x.getObject() for x in self.portal_catalog(uid=uid)]
    if len(object_list):
      category_list.append("%s/%s" %(base_category, object_list[0].getRelativeUrl()))

  def appendToCategoryList(self, category_list, value, base_category):
    category_list.append("%s/%s" %(base_category, value))
  
  def splitAndExtendToCategoryList(self, category_list, value, *args, **kw):
    if value is not None:
      value_list = value.split('\n')
    else:
      value_list = []
    category_list.extend(value_list)


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

    if self.getSimulationState() in self.getPortalDraftOrderStateList():
      # this prevent from trying to calculate stock
      # with not all properties defined and thus making
      # request with no condition in mysql
      object_list = [self]
      immediate_reindex_archive = sql_catalog_id is not None    
      self.portal_catalog.catalogObjectList(object_list,
                                            sql_catalog_id = sql_catalog_id,
                                            disable_archive=disable_archive,
                                            immediate_reindex_archive=immediate_reindex_archive)      
      return
    
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

    default_inventory_calculation_list = ({ "inventory_params" : {"node" : self.getDestination(),
                                                                          "group_by_sub_variation" : 1,
                                                                          "group_by_variation" : 1,
                                                                          "group_by_resource" : 1,
                                                                          },
                                            "list_method" : "getMovementList",
                                            "first_level" : ({'key' : 'resource_relative_url',
                                                             'getter' : 'getResource',
                                                              'setter' : ("appendToCategoryList", "resource")},
                                                             {'key' : 'variation_text',
                                                              'getter' : 'getVariationText',
                                                              'setter' : "splitAndExtendToCategoryList"},
                                                             ),
                                            "second_level" : ({'key' : 'sub_variation_text',
                                                               'getter' : 'getSubVariationText',
                                                               'setter' : "splitAndExtendToCategoryList"},
                                                              ),
                                            },
                                          )

    method = self._getTypeBasedMethod('getDefaultInventoryCalculationList')    
    if method is not None:
      default_inventory_calculation_list = method()
      

    if temp_constructor is None:
      from Products.ERP5Type.Document import newTempDeliveryLine
      temp_constructor = newTempDeliveryLine
    stop_date = self.getStopDate()

    stock_object_list = []
    stock_append = stock_object_list.append

    for inventory_calculation_dict in default_inventory_calculation_list:

      # build a dict containing all inventory for this node 
      # group by resource/variation and then subvariation
      current_inventory_list = \
          self.getPortalObject().portal_simulation.getInventoryList(        
                  to_date=stop_date,
                  simulation_state=self.getPortalCurrentInventoryStateList(),
                  connection_id=connection_id,
                  **inventory_calculation_dict['inventory_params']
          )
      current_inventory_dict = {}
      current_inventory_key_id_list = [x["key"] for x in inventory_calculation_dict['first_level']]
      for line in current_inventory_list:


        current_inventory_key = [line[x] for x in current_inventory_key_id_list]
        for x in xrange(len(current_inventory_key)):
          if current_inventory_key[x] is None:
            current_inventory_key[x] = ""
        current_inventory_key = tuple(current_inventory_key)        

        if inventory_calculation_dict.has_key("second_level"):
          # two level of variation
          try:
            current_inventory_by_sub_variation = \
                current_inventory_dict[current_inventory_key]
          except KeyError:
            current_inventory_by_sub_variation = \
                current_inventory_dict[current_inventory_key] = {}
          second_level_key_id_list = [x['key'] for x in inventory_calculation_dict['second_level']]
          second_level_key = tuple([line[x] for x in second_level_key_id_list])
          current_inventory_by_sub_variation[second_level_key] = line['total_quantity']
        else:
          # only one level of variation
          current_inventory_dict[current_inventory_key] = line['total_quantity']

      # Browse all movements on inventory and create diff line when necessary
      not_used_inventory_dict = {}
      inventory_id = self.getId()
      list_method = inventory_calculation_dict['list_method']      
      method = getattr(self, list_method)      
      for movement in method():
        if movement.getResourceValue() is not None and \
            movement.getQuantity() not in (None, ''):

          movement_quantity = movement.getQuantity()
          # construct key to retrieve inventory into dict
          getter_list = [x['getter'] for x in inventory_calculation_dict['first_level']]
          key_list = []
          for getter in getter_list:
            method = getattr(movement, getter, None)
            if method is not None:
              key_list.append(method())
          inventory_value = current_inventory_dict.get(tuple(key_list), 0)
          second_key_list = []
          if inventory_calculation_dict.has_key('second_level'):
            if inventory_value == 0:
              inventory_value = {}
            # two level
            second_getter_list = [x['getter'] for x in inventory_calculation_dict['second_level']]
            for getter in second_getter_list:
              method = getattr(movement, getter, None)
              if method is not None:
                second_key_list.append(method())
              second_key_list = tuple(second_key_list)
              if inventory_value.has_key(second_key_list):
                total_quantity = inventory_value.pop(second_key_list)
                # Put remaining subvariation in a dict to know which one 
                # to removed at end
                not_used_inventory_dict[tuple(key_list)] = inventory_value
                diff_quantity = movement_quantity - total_quantity
              else:
                # Inventory for new resource/variation/sub_variation
                diff_quantity = movement_quantity
                # Put remaining subvariation in a dict to know which one 
                # to removed at end
                not_used_inventory_dict[tuple(key_list)] = inventory_value
          else:
            # we got the quantity from first level key
            diff_quantity = movement_quantity - inventory_value
              
          # Create tmp movement
          kwd = {'uid': movement.getUid(),
                 'start_date': stop_date}
          temp_delivery_line = temp_constructor(self,
                                                inventory_id)
          # set category on it only if quantity not null
          # thus line with same uid will be deleted but we
          # don't insert line with null quantity as we test
          # some categories like resource/destination/source
          # before insert but not before delete
          if diff_quantity != 0:
            kwd['quantity'] = diff_quantity
            category_list = self.getCategoryList()            

            setter_list = [x['setter'] for x in inventory_calculation_dict['first_level']]
            if inventory_calculation_dict.has_key("second_level"):
              setter_list.extend([x['setter'] for x in inventory_calculation_dict['second_level']])
            value_list = list(key_list) + list(second_key_list)
            for x in xrange(len(setter_list)):
              value = value_list[x]
              setter = setter_list[x]
              base_category = ""
              if isinstance(setter, (tuple, list)):
                base_category = setter[1]
                setter = setter[0]
              method = getattr(self, setter, None)
              if method is not None:
                method(category_list, value, base_category)

            kwd['category_list'] = category_list
          temp_delivery_line.edit(**kwd)
          stock_append(temp_delivery_line)

      # Now create line to remove some subvariation text not present 
      # in new inventory
      if len(not_used_inventory_dict):
        inventory_uid = self.getUid()
        for first_level_key in not_used_inventory_dict.keys():
          inventory_value = \
              not_used_inventory_dict[tuple(first_level_key)]
          for second_level_key in inventory_value.keys():
            diff_quantity = - inventory_value[tuple(second_level_key)]

            kwd = {'uid': inventory_uid,
                   'start_date': stop_date}

            # create the tmp line and set category on it
            temp_delivery_line = temp_constructor(self,
                                                  inventory_id)
            kwd['quantity'] = diff_quantity
            category_list = self.getCategoryList()            

            setter_list = [x['setter'] for x in inventory_calculation_dict['first_level']]
            if inventory_calculation_dict.has_key("second_level"):
              setter_list.extend([x['setter'] for x in inventory_calculation_dict['second_level']])
            value_list = list(first_level_key) + list(second_level_key)
            for x in xrange(len(setter_list)):
              value = value_list[x]
              setter = setter_list[x]
              base_category = ""
              if isinstance(setter, (tuple, list)):
                base_category = setter[1]
                setter = setter[0]
              method = getattr(self, setter, None)
              if method is not None:
                method(category_list, value, base_category)

            kwd['category_list'] = category_list
            temp_delivery_line.edit(**kwd)
            stock_append(temp_delivery_line)

    # Reindex objects
    object_list = [self]
    immediate_reindex_archive = sql_catalog_id is not None    
    self.portal_catalog.catalogObjectList(object_list,
                                          sql_catalog_id = sql_catalog_id,
                                          disable_archive=disable_archive,
                                          immediate_reindex_archive=immediate_reindex_archive)
    
    self.portal_catalog.catalogObjectList(
           stock_object_list, method_id_list=('z_catalog_stock_list', ),
           sql_catalog_id = sql_catalog_id,
           disable_cache=1, check_uid=0, disable_archive=disable_archive,
           immediate_reindex_archive=immediate_reindex_archive)
