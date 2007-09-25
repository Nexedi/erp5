##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.Document.Amount import Amount
from Products.ERP5 import MovementGroup
from Products.ERP5Type.Utils import convertToUpperCase
from DateTime import DateTime
from zLOG import LOG

class CollectError(Exception): pass
class MatrixError(Exception): pass

class OrderBuilder(XMLObject, Amount, Predicate):
  """
    Order Builder objects allow to gather multiple Simulation Movements
    into a single Delivery. 

    The initial quantity property of the Delivery Line is calculated by
    summing quantities of related Simulation Movements.

    Order Builder objects are provided with a set a parameters to achieve 
    their goal:

    A path definition: source, destination, etc. which defines the general 
    kind of movements it applies.

    simulation_select_method which defines how to query all Simulation 
    Movements which meet certain criteria (including the above path path 
    definition).

    collect_order_list which defines how to group selected movements 
    according to gathering rules.

    delivery_select_method which defines how to select existing Delivery 
    which may eventually be updated with selected simulation movements.

    delivery_module, delivery_type and delivery_line_type which define the 
    module and portal types for newly built Deliveries and Delivery Lines.

    Order Builders can also be provided with optional parameters to 
    restrict selection to a given root Applied Rule caused by a single Order
    or to Simulation Movements related to a limited set of existing 
    Deliveries.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Order Builder'
  portal_type = 'Order Builder'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Arrow
                    , PropertySheet.Amount
                    , PropertySheet.Comment
                    , PropertySheet.DeliveryBuilder
                    )
 
  security.declarePublic('build')
  def build(self, applied_rule_uid=None, movement_relative_url_list=None,
            delivery_relative_url_list=None,**kw):
    """
      Build deliveries from a list of movements

      Delivery Builders can also be provided with optional parameters to
      restrict selection to a given root Applied Rule caused by a single Order
      or to Simulation Movements related to a limited set of existing
    """
    # Parameter initialization
    if movement_relative_url_list is None:
      movement_relative_url_list = []
    if delivery_relative_url_list is None:
      delivery_relative_url_list = []
    # Call a script before building
    self.callBeforeBuildingScript()
    # Select
    if movement_relative_url_list == []:
      movement_list = self.searchMovementList(
                                      applied_rule_uid=applied_rule_uid,**kw)
    else:
      movement_list = [self.restrictedTraverse(relative_url) for relative_url \
                       in movement_relative_url_list]
    # Collect
    root_group = self.collectMovement(movement_list)
    # Build
    delivery_list = self.buildDeliveryList(
                       root_group,
                       delivery_relative_url_list=delivery_relative_url_list,
                       movement_list=movement_list,**kw)
    # Call a script after building
    self.callAfterBuildingScript(delivery_list,**kw)
    # XXX Returning the delivery list is probably not necessary
    return delivery_list

  def callBeforeBuildingScript(self):
    """
      Call a script on the module, for example, to remove some 
      auto_planned Order.
      This part can only be done with a script, because user may want 
      to keep existing auto_planned Order, and only update lines in 
      them.
      No activities are used when deleting a object, so, current
      implementation should be OK.
    """
    delivery_module_before_building_script_id = \
        self.getDeliveryModuleBeforeBuildingScriptId()
    if delivery_module_before_building_script_id not in ["", None]:
      delivery_module = getattr(self.getPortalObject(), self.getDeliveryModule())
      getattr(delivery_module, delivery_module_before_building_script_id)()

  def searchMovementList(self, applied_rule_uid=None,**kw):
    """
      Defines how to query all Simulation Movements which meet certain
      criteria (including the above path path definition).
      First, select movement matching to criteria define on 
      DeliveryBuilder.
      Then, call script simulation_select_method to restrict 
      movement_list.
    """
    from Products.ERP5Type.Document import newTempMovement
    movement_list = []
    for attribute, method in [('node_uid', 'getDestinationUid'),
                              ('section_uid', 'getDestinationSectionUid')]:
      if getattr(self, method)() not in ("", None):
        kw[attribute] = getattr(self, method)()
    # We have to check the inventory for each stock movement date.
    # Inventory can be negative in some date, and positive in futur !!
    # This must be done by subclassing OrderBuilder with a new inventory
    # algorithm.
    sql_list = self.portal_simulation.getFutureInventoryList(
                                                   group_by_variation=1,
                                                   group_by_resource=1,
                                                   group_by_node=1,
                                                   group_by_section=0,
                                                   **kw)
    id_count = 0
    for inventory_item in sql_list:
      # XXX FIXME SQL return None inventory...
      # It may be better to return always good values
      if (inventory_item.inventory is not None):
        dumb_movement = inventory_item.getObject()
        # Create temporary movement
        movement = newTempMovement(self.getPortalObject(), 
                                   str(id_count))
        id_count += 1
        movement.edit(
            resource=inventory_item.resource_relative_url,
            variation_category_list=dumb_movement.getVariationCategoryList(),
            destination_value=self.getDestinationValue(),
            destination_section_value=self.getDestinationSectionValue())
        # We can do other test on inventory here
        # XXX It is better if it can be sql parameters
        resource_portal_type = self.getResourcePortalType()
        resource = movement.getResourceValue()
        # FIXME: XXX Those properties are defined on a supply line !!
        # min_flow, max_delay
        min_flow = resource.getMinFlow(0)
        if (resource.getPortalType() == resource_portal_type) and\
           (round(inventory_item.inventory, 5) < min_flow):
          # FIXME XXX getNextNegativeInventoryDate must work
          stop_date = DateTime()+10
#         stop_date = resource.getNextNegativeInventoryDate(
#                               variation_text=movement.getVariationText(),
#                               from_date=DateTime(),
# #                             node_category=node_category,
# #                             section_category=section_category)
#                               node_uid=self.getDestinationUid(),
#                               section_uid=self.getDestinationSectionUid())
          max_delay = resource.getMaxDelay(0)
          movement.edit(
            start_date=DateTime(((stop_date-max_delay).Date())),
            stop_date=DateTime(stop_date.Date()),
            quantity=min_flow-inventory_item.inventory,
            quantity_unit=resource.getQuantityUnit()
            # XXX FIXME define on a supply line
            # quantity_unit
          )
          movement_list.append(movement)
    return movement_list

  def getCollectOrderList(self):
    """
      Simply method to get the 3 collect order lists define on a
      DeliveryBuilder
    """
    return self.getDeliveryCollectOrderList()+\
           self.getDeliveryLineCollectOrderList()+\
           self.getDeliveryCellCollectOrderList()

  def collectMovement(self, movement_list):
    """
      group movements in the way we want. Thanks to this method, we are able 
      to retrieve movement classed by order, resource, criterion,....
      movement_list : the list of movement wich we want to group
      check_list : the list of classes used to group movements. The order
                   of the list is important and determines by what we will
                   group movement first
                   Typically, check_list is :
                   [DateMovementGroup,PathMovementGroup,...]
    """
    class_list = [getattr(MovementGroup, x) \
                  for x in self.getCollectOrderList()]
    last_line_class_name = self.getDeliveryCollectOrderList()[-1]
    separate_method_name_list = self.getDeliveryCellSeparateOrderList([])
    my_root_group = MovementGroup.RootMovementGroup(
                           class_list,
                           last_line_class_name=last_line_class_name,
                           separate_method_name_list=separate_method_name_list)
    for movement in movement_list:
      my_root_group.append(movement)
    return my_root_group

  def testObjectProperties(self, instance, property_dict):
    """
      Test instance properties.
    """
    result = 1
    for key in property_dict:
      getter_name = 'get%s' % convertToUpperCase(key)
      if hasattr(instance, getter_name):
        value = getattr(instance, getter_name)()
        if value != property_dict[key]:
          result = 0
          break
      else:
        result = 0
        break
    return result

  def buildDeliveryList(self, movement_group, delivery_relative_url_list=None,
                        movement_list=None,**kw):
    """
      Build deliveries from a list of movements
    """
    # Parameter initialization
    if delivery_relative_url_list is None:
      delivery_relative_url_list = []
    # Module where we can create new deliveries
    portal = self.getPortalObject()
    delivery_module = getattr(portal, self.getDeliveryModule())
    delivery_to_update_list = [portal.restrictedTraverse(relative_url) for \
                               relative_url in delivery_relative_url_list]
    # Deliveries we are trying to update
    delivery_select_method_id = self.getDeliverySelectMethodId()
    if delivery_select_method_id not in ["", None]:
      to_update_delivery_sql_list = getattr(self, delivery_select_method_id) \
                                      (movement_list=movement_list)
      delivery_to_update_list.extend([sql_delivery.getObject() \
                                     for sql_delivery \
                                     in to_update_delivery_sql_list])
    delivery_list = self._deliveryGroupProcessing(
                          delivery_module,
                          movement_group,
                          self.getDeliveryCollectOrderList(),
                          {},
                          delivery_to_update_list=delivery_to_update_list,
                          **kw)
    return delivery_list

  def _deliveryGroupProcessing(self, delivery_module, movement_group, 
                               collect_order_list, property_dict,
                               delivery_to_update_list=None,
                               activate_kw=None,**kw):
    """
      Build empty delivery from a list of movement
    """
    # Parameter initialization
    if delivery_to_update_list is None:
      delivery_to_update_list = []
    delivery_list = []
    # Get current properties from current movement group
    # And fill property_dict
    property_dict.update(movement_group.getGroupEditDict())
    if collect_order_list != []:
      # Get sorted movement for each delivery
      for group in movement_group.getGroupList():
        new_delivery_list = self._deliveryGroupProcessing(
                              delivery_module,
                              group,
                              collect_order_list[1:],
                              property_dict.copy(),
                              delivery_to_update_list=delivery_to_update_list,
                              activate_kw=activate_kw)
        delivery_list.extend(new_delivery_list)
    else:
      # Test if we can update a existing delivery, or if we need to create 
      # a new one
      delivery = None
      for delivery_to_update in delivery_to_update_list:
        if self.testObjectProperties(delivery_to_update, property_dict):
          # Check if delivery has the correct portal_type
          if delivery_to_update.getPortalType() ==\
                                        self.getDeliveryPortalType():
            delivery = delivery_to_update
            break
      if delivery is None:
        # Create delivery
        new_delivery_id = str(delivery_module.generateNewId())
        delivery = delivery_module.newContent(
                                  portal_type=self.getDeliveryPortalType(),
                                  id=new_delivery_id,
                                  created_by_builder=1,
                                  activate_kw=activate_kw,**kw)
        # Put properties on delivery
        delivery.edit(**property_dict)

      # Then, create delivery line
      for group in movement_group.getGroupList():
        self._deliveryLineGroupProcessing(
                                delivery,
                                group,
                                self.getDeliveryLineCollectOrderList()[1:],
                                {},
                                activate_kw=activate_kw,**kw)
      delivery_list.append(delivery)
    return delivery_list
      
  def _deliveryLineGroupProcessing(self, delivery, movement_group,
                                   collect_order_list, property_dict,
                                   activate_kw=None,**kw):
    """
      Build delivery line from a list of movement on a delivery
    """
    # Get current properties from current movement group
    # And fill property_dict
    property_dict.update(movement_group.getGroupEditDict())
    if collect_order_list != []:
      # Get sorted movement for each delivery line
      for group in movement_group.getGroupList():
        self._deliveryLineGroupProcessing(
          delivery, group, collect_order_list[1:], property_dict.copy(),
          activate_kw=activate_kw)
    else:
      # Test if we can update an existing line, or if we need to create a new
      # one
      delivery_line = None
      update_existing_line = 0
      for delivery_line_to_update in delivery.contentValues(
               filter={'portal_type':self.getDeliveryLinePortalType()}):
        if self.testObjectProperties(delivery_line_to_update, property_dict):
          delivery_line = delivery_line_to_update
          update_existing_line = 1
          break
      if delivery_line is None:
        # Create delivery line
        new_delivery_line_id = str(delivery.generateNewId())
        delivery_line = delivery.newContent(
                                  portal_type=self.getDeliveryLinePortalType(),
                                  id=new_delivery_line_id,
                                  variation_category_list=[],
                                  activate_kw=activate_kw)
        # Put properties on delivery line
        delivery_line.edit(**property_dict)
      # Update variation category list on line
      line_variation_category_list = delivery_line.getVariationCategoryList()
      for movement in movement_group.getMovementList():
        line_variation_category_list.extend(
                                      movement.getVariationCategoryList())
      # erase double
      line_variation_category_list = dict([(variation_category, 1) \
                                          for variation_category in \
                                          line_variation_category_list]).keys()
      delivery_line.setVariationCategoryList(line_variation_category_list)
      # Then, create delivery movement (delivery cell or complete delivery
      # line)
      group_list = movement_group.getGroupList()
      # If no group is defined for cell, we need to continue, in order to 
      # save the quantity value
      if list(group_list) != []:
        for group in group_list:
          self._deliveryCellGroupProcessing(
                                    delivery_line,
                                    group,
                                    self.getDeliveryCellCollectOrderList()[1:],
                                    {},
                                    update_existing_line=update_existing_line,
                                    activate_kw=activate_kw)
      else:
        self._deliveryCellGroupProcessing(
                                  delivery_line,
                                  movement_group,
                                  [],
                                  {},
                                  update_existing_line=update_existing_line,
                                  activate_kw=activate_kw)


  def _deliveryCellGroupProcessing(self, delivery_line, movement_group,
                                   collect_order_list, property_dict,
                                   update_existing_line=0,activate_kw=None):
    """
      Build delivery cell from a list of movement on a delivery line
      or complete delivery line
    """
    # Get current properties from current movement group
    # And fill property_dict
    property_dict.update(movement_group.getGroupEditDict())
    if collect_order_list != []:
      # Get sorted movement for each delivery line
      for group in movement_group.getGroupList():
        self._deliveryCellGroupProcessing(
                                    delivery_line, 
                                    group, 
                                    collect_order_list[1:], 
                                    property_dict.copy(),
                                    update_existing_line=update_existing_line,
                                    activate_kw=activate_kw)
    else:
      movement_list = movement_group.getMovementList()
      if len(movement_list) != 1:
        raise CollectError, "DeliveryBuilder: %s unable to distinct those\
              movements: %s" % (self.getId(), str(movement_list))
      else:
        # XXX Hardcoded value
        base_id = 'movement'
        object_to_update = None
        # We need to initialize the cell
        update_existing_movement = 0
        movement = movement_list[0]
        # decide if we create a cell or if we update the line
        # Decision can only be made with line matrix range:
        # because matrix range can be empty even if line variation category
        # list is not empty
        if list(delivery_line.getCellKeyList(base_id=base_id)) == []:
          # update line
          object_to_update = delivery_line
          if self.testObjectProperties(delivery_line, property_dict):
            if update_existing_line == 1:
              # We update a initialized line
              update_existing_movement = 1
        else:
          for cell_key in delivery_line.getCellKeyList(base_id=base_id):
            if delivery_line.hasCell(base_id=base_id, *cell_key):
              cell = delivery_line.getCell(base_id=base_id, *cell_key)
              if self.testObjectProperties(cell, property_dict):
                # We update a existing cell
                # delivery_ratio of new related movement to this cell 
                # must be updated to 0.
                update_existing_movement = 1
                object_to_update = cell
                break
        if object_to_update is None:
          # create a new cell
          cell_key = movement.getVariationCategoryList(
                                                   omit_option_base_category=1)
          if not delivery_line.hasCell(base_id=base_id, *cell_key):
            cell = delivery_line.newCell(base_id=base_id, \
                       portal_type=self.getDeliveryCellPortalType(), 
                       activate_kw=activate_kw,*cell_key)
            vcl = movement.getVariationCategoryList()
            cell._edit(category_list=vcl,
                      # XXX hardcoded value
                      mapped_value_property_list=['quantity', 'price'],
                      membership_criterion_category_list=vcl,
                      membership_criterion_base_category_list=movement.\
                                             getVariationBaseCategoryList())
            object_to_update = cell
          else:
            raise MatrixError, 'Cell: %s already exists on %s' % \
                  (str(cell_key), str(delivery_line))
        self._setDeliveryMovementProperties(
                            object_to_update, movement, property_dict,
                            update_existing_movement=update_existing_movement)

  def _setDeliveryMovementProperties(self, delivery_movement,
                                     simulation_movement, property_dict,
                                     update_existing_movement=0):
    """
      Initialize or update delivery movement properties.
      Set delivery ratio on simulation movement.
    """
    if update_existing_movement == 1:
      # Important.
      # Attributes of object_to_update must not be modified here.
      # Because we can not change values that user modified.
      # Delivery will probably diverge now, but this is not the job of
      # DeliveryBuilder to resolve such problem.
      # Use Solver instead.
      #simulation_movement.setDeliveryRatio(0)
      simulation_movement.edit(delivery_ratio=0)
    else:
      # Now, only 1 movement is possible, so copy from this movement
      # XXX hardcoded value
      property_dict['quantity'] = simulation_movement.getQuantity()
      property_dict['price'] = simulation_movement.getPrice()
      # Update properties on object (quantity, price...)
      delivery_movement._edit(force_update=1, **property_dict)
      #simulation_movement.setDeliveryRatio(1)
      simulation_movement.edit(delivery_ratio=1)

  def callAfterBuildingScript(self, delivery_list,**kw):
    """
      Call script on each delivery built
    """
    delivery_after_generation_script_id = \
                              self.getDeliveryAfterGenerationScriptId()
    if delivery_after_generation_script_id not in ["", None]:
      for delivery in delivery_list:
        getattr(delivery, delivery_after_generation_script_id)()
