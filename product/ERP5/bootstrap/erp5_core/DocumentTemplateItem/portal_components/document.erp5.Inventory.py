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

from six.moves import xrange
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from erp5.component.document.Delivery import Delivery

class Inventory(Delivery):
  """
  Inventory
  """
  # CMF Type Definition
  meta_type = 'ERP5 Inventory'
  portal_type = 'Inventory'
  isInventory = ConstantGetter('isInventory', value=True)

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
    return self._immediateReindexObject(**kw)

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


  def _immediateReindexObject(self, temp_constructor=None, **kw):
    """
    Rewrite indexation method so that we can insert lines in stock table
    which will be equal to the difference between stock values for
    resource in the inventory and the one before the date of this inventory

    temp_constructor is used in some particular cases where we want
    to have our own temp object constructor, this is usefull if we
    want to use some classes with some particular methods
    """
    portal = self.getPortalObject()
    sql_catalog_id = kw.pop("sql_catalog_id", None)
    disable_archive = kw.pop("disable_archive", 0)

    state = self.getSimulationState()
    # we need reindex when cancelling inventories
    if (state in portal.getPortalDraftOrderStateList() and
        state != 'cancelled'):
      # this prevent from trying to calculate stock
      # with not all properties defined and thus making
      # request with no condition in mysql
      immediate_reindex_archive = sql_catalog_id is not None
      portal.portal_catalog.catalogObjectList([self],
        sql_catalog_id = sql_catalog_id,
        disable_archive=disable_archive,
        immediate_reindex_archive=immediate_reindex_archive)
      return

    connection_id = None
    if sql_catalog_id is not None:
      # try to get connection used in the catalog
      catalog = portal.portal_catalog[sql_catalog_id]
      connection_id = catalog.getConnectionId()

    default_inventory_calculation_list = ({ "inventory_params" : {"section": self.getDestinationSection(),
                                                                  "node" : self.getDestination(),
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
      temp_constructor = lambda self, id, *args, **kw: self.newContent(
        temp_object=True, portal_type='Movement',
        id=id, *args, **kw)
    stop_date = self.getStopDate()

    stock_object_list = []
    stock_append = stock_object_list.append
    to_delete_stock_uid_set = set()
    to_delete_stock_uid_add = to_delete_stock_uid_set.add
    to_delete_list = []
    to_delete_list_append = to_delete_list.append

    for inventory_calculation_dict in default_inventory_calculation_list:

      # build a dict containing all inventory for this node
      # group by resource/variation and then subvariation
      current_inventory_list = \
          portal.portal_simulation.getCurrentInventoryList(
                  to_date=stop_date,
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

        if "second_level" in inventory_calculation_dict:
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
      if self.isFullInventory():
        not_used_inventory_dict = current_inventory_dict
      else:
        not_used_inventory_dict = {}
      inventory_id = self.getId()
      list_method = inventory_calculation_dict['list_method']
      method = getattr(self, list_method)

      __order_id_counter_list = [0]
      def getOrderIdCounter():
        value = __order_id_counter_list[0] # pylint: disable=cell-var-from-loop
        __order_id_counter_list[0] = value + 1 # pylint: disable=cell-var-from-loop
        return value

      for movement in method():
        if movement.getResourceValue() is not None and \
            movement.getInventoriatedQuantity() not in (None, ''):

          movement_quantity = movement.getInventoriatedQuantity()
          # construct key to retrieve inventory into dict
          getter_list = [x['getter'] for x in inventory_calculation_dict['first_level']]
          key_list = []
          for getter in getter_list:
            method = getattr(movement, getter, None)
            if method is not None:
              key_list.append(method())
          inventory_value = current_inventory_dict.get(tuple(key_list), 0)
          second_key_list = []
          if 'second_level' in inventory_calculation_dict:
            if inventory_value == 0:
              inventory_value = {}
            # two level
            second_getter_list = [x['getter'] for x in inventory_calculation_dict['second_level']]
            for getter in second_getter_list:
              method = getattr(movement, getter, None)
              if method is not None:
                second_key_list.append(method())
              second_key_list = tuple(second_key_list)
              if second_key_list in inventory_value:
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
                 'start_date': stop_date,
                 'order_id': getOrderIdCounter(),
                 'mirror_order_id':getOrderIdCounter()
                 }
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
            if "second_level" in inventory_calculation_dict:
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
          to_delete_list_append(temp_delivery_line)
        else:
          # Make sure we remove any any value
          to_delete_stock_uid_add(movement.getUid())

      # Now create line to remove some subvariation text not present
      # in new inventory
      if len(not_used_inventory_dict):
        inventory_uid = self.getUid()
        for first_level_key in not_used_inventory_dict.keys():
          inventory_value = \
              not_used_inventory_dict[tuple(first_level_key)]
          # XXX-Aurel : this code does not work with only one level of variation
          for second_level_key in inventory_value.keys():
            diff_quantity = - inventory_value[tuple(second_level_key)]

            kwd = {'uid': inventory_uid,
                   'start_date': stop_date,
                   'order_id': getOrderIdCounter(),
                   'mirror_order_id':getOrderIdCounter()
                   }

            # create the tmp line and set category on it
            temp_delivery_line = temp_constructor(self,
                                                  inventory_id)
            kwd['quantity'] = diff_quantity
            category_list = self.getCategoryList()

            setter_list = [x['setter'] for x in inventory_calculation_dict['first_level']]
            if "second_level" in inventory_calculation_dict:
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
    immediate_reindex_archive = sql_catalog_id is not None
    portal.portal_catalog.catalogObjectList([self],
      sql_catalog_id = sql_catalog_id,
      disable_archive=disable_archive,
      immediate_reindex_archive=immediate_reindex_archive)

    # Do deletion for everything first, even if there is no need to apply correction,
    # in case we need to remove previous corrections
    to_delete_stock_uid_add(self.getUid())
    for uid in to_delete_stock_uid_set:
      temp_line = temp_constructor(self, inventory_id)
      temp_line.setUid(uid)
      to_delete_list_append(temp_line)
    catalog_kw = dict(sql_catalog_id=sql_catalog_id,
         disable_cache=1, check_uid=0, disable_archive=disable_archive,
         immediate_reindex_archive=immediate_reindex_archive)
    method_id_list = ['z0_uncatalog_stock']
    if portal.portal_catalog.getSQLCatalog(sql_catalog_id) \
       .hasObject('SQLCatalog_trimInventoryCacheOnCatalog'):
      method_id_list.append('SQLCatalog_trimInventoryCacheOnCatalog')
    # Delete existing stock records and old inventory_cache first.
    portal.portal_catalog.catalogObjectList(
         to_delete_list[:], method_id_list=method_id_list, **catalog_kw)
    if stock_object_list:
      # Then insert new records without delete.
      portal.portal_catalog.catalogObjectList(
           stock_object_list[:], method_id_list=('z_catalog_stock_list_without_delete_for_inventory_virtual_movement', ),
           **catalog_kw)