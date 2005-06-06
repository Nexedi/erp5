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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.Document.Amount import Amount
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.ERP5 import MovementGroup
from Products.ERP5Type.Utils import convertToUpperCase

from zLOG import LOG

class DeliveryBuilder(XMLObject, Amount, Predicate):
  """
    Delivery Builder objects allow to gather multiple Simulation Movements
    into a single Delivery. 

    The initial quantity property of the Delivery Line is calculated by
    summing quantities of related Simulation Movements.

    Delivery Builders are called for example whenever an order is confirmed.
    They are also called globaly in order to gather any confirmed or above 
    Simulation Movement which was not associated to any Delivery Line. 
    Such movements are called orphaned Simulation Movements.

    Delivery Builder objects are provided with a set a parameters to achieve 
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

    Delivery Builders can also be provided with optional parameters to 
    restrict selection to a given root Applied Rule caused by a single Order
    or to Simulation Movements related to a limited set of existing 
    Deliveries.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Delivery Builder'
  portal_type = 'Delivery Builder'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

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

  security.declareProtected(Permissions.ModifyPortalContent, 'build')
  def build(self, applied_rule_uid=None, movement_relative_url_list=[]):
    """
      Build deliveries from a list of movements

      Delivery Builders can also be provided with optional parameters to
      restrict selection to a given root Applied Rule caused by a single Order
      or to Simulation Movements related to a limited set of existing
    """
    # Select
    if movement_relative_url_list == []:
      movement_list = self.searchMovementList(
                                      applied_rule_uid=applied_rule_uid)
    else:
      movement_list = [self.restrictedTraverse(relative_url) for relative_url\
                       in movement_relative_url_list]
    # Collect
    root_group = self.collectMovement(movement_list)

    # Build
    delivery_list = self.buildDeliveryList(root_group)

    delivery_after_generation_script_id =\
                              self.getDeliveryAfterGenerationScriptId()

    # Call script on each delivery built
    if delivery_after_generation_script_id not in ["", None]:
      for delivery in delivery_list:
        getattr(delivery, delivery_after_generation_script_id)()
      
    return delivery_list

  def searchMovementList(self, applied_rule_uid=None):
    """
      defines how to query all Simulation Movements which meet certain criteria
      (including the above path path definition).

      First, select movement matching to criteria define on DeliveryBuilder
      Then, call script simulation_select_method to restrict movement_list
    """
    movement_list = []
    kw = {}
    # We only search Simulation Movement
    kw['portal_type'] = 'Simulation Movement'
    # Search only child movement from this applied rule
    if applied_rule_uid is not None:
      kw['parent_uid'] = applied_rule_uid
    # XXX Add profile query
    # Add resource query
    if self.resource_portal_type not in ('', None):
      kw['resourceType'] = self.resource_portal_type

    if self.simulation_select_method_id in ['', None]:
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      movement_list = [x.getObject() for x in self.portal_catalog(**kw)]
    else:
      select_method = getattr(self, self.simulation_select_method_id)
      movement_list = select_method(kw)

    # XXX Use buildSQLQuery will be better
    movement_list = filter(lambda x: x.getDeliveryRelatedValueList()==[],
                           movement_list)

    # XXX  Add predicate test
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
    class_list = []
    for class_name in self.getCollectOrderList():
      class_list.append(getattr(MovementGroup, class_name))

    last_line_class_name = self.getDeliveryLineCollectOrderList()[-1]
    separate_method_name_list = self.getDeliveryCellSeparateOrderList()

    my_root_group = MovementGroup.RootMovementGroup(
                           class_list,
                           last_line_class_name=last_line_class_name,
                           separate_method_name_list=separate_method_name_list)
    for movement in movement_list:
      my_root_group.append(movement)

    return my_root_group

  def testObjectProperties(self, object, property_dict):
    """
      Test object properties.
    """
    result = 1
    for key in property_dict:
      # XXX FIXME (or not)
      # Relation is not coherent
      # You set it with set...Value
      # And get it with get...
      new_key = key
      if key.endswith("_value"):
        new_key = key[:-len("_value")]
      getter_name = 'get%s' % convertToUpperCase(new_key)
      if hasattr(object, getter_name):
        value = getattr(object, getter_name)()
        if value != property_dict[key]:
          result = 0
          break
      else:
        result = 0
        break
    return result

  def buildDeliveryList(self, movement_group):
    """
      Build deliveries from a list of movements
    """
    # Module where we can create new deliveries
    delivery_module = getattr(self, self.getDeliveryModule())
    
    # Deliveries we are trying to update
    to_update_delivery_list = []
    delivery_select_method_id = self.getDeliverySelectMethodId()
    if delivery_select_method_id not in ["", None]:
      to_update_delivery_sql_list = getattr(self, delivery_select_method_id)()
      to_update_delivery_list = [x.getObject() for x\
                                 in to_update_delivery_sql_list]

    delivery_list = self._deliveryGroupProcessing(
                          delivery_module,
                          movement_group,
                          self.getDeliveryCollectOrderList(),
                          {},
                          delivery_to_update_list=to_update_delivery_list)

    return delivery_list

  def _deliveryGroupProcessing(self, delivery_module, movement_group, 
                               collect_order_list, property_dict,
                               delivery_to_update_list=[]):
    """
      Build empty delivery from a list of movement
    """
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
                                            property_dict.copy())

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

      if delivery == None:
        # Create delivery
        new_delivery_id = str(delivery_module.generateNewId())
        delivery = delivery_module.newContent(
                                  portal_type=self.getDeliveryPortalType(),
                                  id=new_delivery_id)
        # Put properties on delivery
        delivery.edit(**property_dict)

      # Then, create delivery line
      for group in movement_group.getGroupList():
        self._deliveryLineGroupProcessing(
                                delivery,
                                group,
                                self.getDeliveryLineCollectOrderList()[1:],
                                {})

      delivery_list.append(delivery)

    return delivery_list
      
  def _deliveryLineGroupProcessing(self, delivery, movement_group,
                                   collect_order_list, property_dict):
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
          delivery, group, collect_order_list[1:], property_dict.copy())
    else:
      # Test if we can update an existing line, or if we need to create a new
      # one
      delivery_line = None
      update_existing_line=0
      for delivery_line_to_update in delivery.contentValues(
               filter={'portal_type':self.getDeliveryLinePortalType()}):
        if self.testObjectProperties(delivery_line_to_update, property_dict):
          delivery_line = delivery_line_to_update
          update_existing_line=1
          break

      if delivery_line == None:
        # Create delivery line
        new_delivery_line_id = str(delivery.generateNewId())
        delivery_line = delivery.newContent(
                                  portal_type=self.getDeliveryLinePortalType(),
                                  id=new_delivery_line_id,
                                  variation_category_list=[])
        # Put properties on delivery line
        delivery_line.edit(**property_dict)

      # Update variation category list on line
      line_variation_category_list = delivery_line.getVariationCategoryList()
      for movement in movement_group.getMovementList():
        line_variation_category_list.extend(
                                      movement.getVariationCategoryList())
      # erase double
      line_variation_category_list = dict([(x, 1) for x in\
                                          line_variation_category_list]).keys()
      delivery_line.setVariationCategoryList(line_variation_category_list)

      # Then, create delivery movement (delivery cell or complete delivery
      # line)
      for group in movement_group.getGroupList():
        self._deliveryCellGroupProcessing(
                                    delivery_line,
                                    group,
                                    self.getDeliveryCellCollectOrderList()[1:],
                                    {},
                                    update_existing_line=update_existing_line)

  def _deliveryCellGroupProcessing(self, delivery_line, movement_group,
                                   collect_order_list, property_dict,
                                   update_existing_line=0):
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
        self._deliveryLineGroupProcessing(
          delivery_line, group, collect_order_list[1:], property_dict.copy())
    else:
      movement_list = movement_group.getMovementList()
      if len(movement_list) != 1:
        raise "CollectError", "DeliveryBuilder: %s unable to distinct those\
              movements: %s" % (self.getId(), str(movement_list))
      else:
        # XXX Hardcoded value
        base_id = 'movement'
        object_to_update = None
        # We need to initialize the cell
        update_existing_movement=0
        movement = movement_list[0]
        # decide if we create a cell or if we update the line
        # Decision can only be made with line matrix range:
        # because matrix range can be empty even if line variation category
        # list is not empty
        if list(delivery_line.getCellKeyList(base_id=base_id)) == []:
          # update line
          object_to_update = delivery_line
          if self.testObjectProperties(delivery_line, property_dict):
            if update_existing_movement == 1:
              # We update a initialized line
              update_existing_movement=1

        else:
          for cell in delivery_line.contentValues(
                   filter={'portal_type':self.getDeliveryCellPortalType()}):
            if self.testObjectProperties(cell, property_dict):
              # We update a existing cell
              # delivery_ratio of new related movement to this cell 
              # must be updated to 0.
              update_existing_movement=1
              object_to_update = cell
              break

        if object_to_update is None:
          # create a new cell
          cell_key = movement.getVariationCategoryList()
          if not delivery_line.hasCell(base_id=base_id, *cell_key):
            cell = delivery_line.newCell(base_id=base_id,\
                       portal_type=self.getDeliveryCellPortalType(), *cell_key)
            cell._edit(category_list=cell_key,
                      # XXX hardcoded value
                      mapped_value_property_list=['quantity', 'price'],
                      membership_criterion_category_list=cell_key,
                      membership_criterion_base_category_list=movement.\
                                             getVariationBaseCategoryList())
            object_to_update = cell

          else:
            raise 'MatrixError', 'Cell: %s already exists on %s' %\
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
      Create the relation between simulation movement
      and delivery movement.
    """
    if update_existing_movement == 1:
      # Important.
      # Attributes of object_to_update must not be modified here.
      # Because we can not change values that user modified.
      # Delivery will probably diverge now, but this is not the job of
      # DeliveryBuilder to resolve such problem.
      # Use Solver instead.
      simulation_movement.setDeliveryRatio(0)
    else:
      # Now, only 1 movement is possible, so copy from this movement
      # XXX hardcoded value
      property_dict['quantity'] = simulation_movement.getQuantity()
      property_dict['price'] = simulation_movement.getPrice()
                
      # Update properties on object (quantity, price...)
      delivery_movement.edit(**property_dict)
      simulation_movement.setDeliveryRatio(1)

    # Update simulation movement
    simulation_movement.setDeliveryValue(delivery_movement)



  # Simulation consistency propagation
  security.declareProtected(Permissions.ModifyPortalContent, 
                            'updateFromSimulation')
  def updateFromSimulation(self, delivery_relative_url, create_new_delivery=1):
    """
      Update all lines of this transaction based on movements in the 
      simulation related to this transaction.
    """
    # We have to get a delivery, else, raise a Error
    delivery = self.restrictedTraverse(delivery_relative_url)

    delivery_uid = delivery.getUid()

    # Select
    simulation_movement_list = []
    for movement in delivery.getMovementList():
      movement.edit(quantity=0)
      for simulation_movement in movement.getDeliveryRelatedValueList(
                                            portal_type="Simulation Movement"):
        simulation_movement.setDelivery(None)
        simulation_movement_list.append(simulation_movement) 

    # Collect
    root_group = self.collectMovement(simulation_movement_list)

    # Update delivery
    rejected_movement_list = self._deliveryUpdateGroupProcessing(
                                          delivery,
                                          root_group)

    for sim_mvt in root_group.getMovementList():
      sim_mvt.immediateReindexObject()

    # Store the good quantity value on delivery line
    for movement in delivery.getMovementList():
      total_quantity = 0
      for simulation_movement in movement.getDeliveryRelatedValueList(
                                            portal_type="Simulation Movement"):
        total_quantity += simulation_movement.getQuantity()

      for simulation_movement in movement.getDeliveryRelatedValueList(
                                            portal_type="Simulation Movement"):
        simulation_movement.setDeliveryRatio(
             simulation_movement.getQuantity()/total_quantity)

      movement.edit(quantity=total_quantity)

    # Launch delivery creation
    if (create_new_delivery == 1) and\
       (rejected_movement_list != []):
      movement_relative_url_list = [x.getRelativeUrl() for x in\
                                    rejected_movement_list]
      self.activate().build(
                        movement_relative_url_list=movement_relative_url_list)


  def _deliveryUpdateGroupProcessing(self, delivery, movement_group):
    """
      Update delivery movement
    """
    rejected_movement_list = []
    property_dict = {}

    for collect_order in self.getDeliveryCollectOrderList():
      for group in movement_group.getGroupList()[1:]:
        rejected_movement_list.extend(movement_group.getMovementList())
      movement_group = movement_group.getGroupList()[0]
      property_dict.update(movement_group.getGroupEditDict())
    
    # Put properties on delivery
    delivery.edit(**property_dict)

    # Then, reconnect simulation to delivery line
    for group in movement_group.getGroupList():
      self._deliveryLineGroupProcessing(
                                  delivery,
                                  group,
                                  self.getDeliveryLineCollectOrderList()[1:],
                                  {})
    return rejected_movement_list
