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

  def build(self, applied_rule=None):
    """
      Build deliveries from a list of movements

      Delivery Builders can also be provided with optional parameters to
      restrict selection to a given root Applied Rule caused by a single Order
      or to Simulation Movements related to a limited set of existing
    """
    # Select
    movement_list = self.selectMovement(applied_rule=applied_rule)
    # Collect
    root_group = self.collectMovement(movement_list)
    # And finally build
    delivery_list = self.buildDeliveryList(root_group)
    return delivery_list

  def selectMovement(self, applied_rule=None):
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
    if applied_rule is not None:
      kw['parent_uid'] = applied_rule.getUid()
    # XXX Add profile query
    # Add resource query
    if self.resource_portal_type != '':
      kw['resourceType'] = self.resource_portal_type

    if self.simulation_select_method_id in ['', None]:
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      movement_list = [x.getObject() for x in self.portal_catalog(**kw)]
    else:
      select_method = getattr(self, self.simulation_select_method_id) 
      movement_list = select_method(kw)
      sql_query = select_method(kw, src__=1)

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

    my_root_group = MovementGroup.RootMovementGroup(class_list=class_list)
    for movement in movement_list:
      my_root_group.append(movement,class_list=class_list)

    return my_root_group

  def buildDeliveryList(self, movement_group):
    """
      Build deliveries from a list of movements
    """
    delivery_module = getattr(self, self.getDeliveryModule())

    delivery_list,\
    reindexable_movement_list = self._deliveryGroupProcessing(
                                            delivery_module,
                                            movement_group,
                                            self.getDeliveryCollectOrderList(),
                                            {})

    for movement in reindexable_movement_list:
      # We have to use 'immediate' to bypass the activity tool,
      # because we will depend on these objects when we try to call 
      # buildInvoiceList
      movement.immediateReindexObject() 

    return delivery_list

  def _deliveryGroupProcessing(self, delivery_module, movement_group, 
                               collect_order_list, property_dict):
    """
      Build empty delivery from a list of movement
    """
    delivery_list = []
    reindexable_movement_list = []

    # Get current properties from current movement group
    # And fill property_dict
    property_dict.update(movement_group.getGroupEditDict())


    if collect_order_list != []:
      # Get sorted movement for each delivery
      for group in movement_group.getGroupList():
        new_delivery_list, \
        new_reindexable_movement_list = self._deliveryGroupProcessing(
            delivery_module,
            group,
            collect_order_list[1:],
            property_dict.copy())

        delivery_list.extend(new_delivery_list)
        reindexable_movement_list.extend(new_reindexable_movement_list)

    else:
      # Create delivery
      new_delivery_id = str(delivery_module.generateNewId())
      delivery = delivery_module.newContent(
                                type_name=self.getDeliveryPortalType(),
                                id=new_delivery_id)
      # Put properties on delivery
      delivery.edit(**property_dict)

      # Then, create delivery line
      for group in movement_group.getGroupList():
        reindexable_movement_list = self._deliveryLineGroupProcessing(
                                    delivery,
                                    group,
                                    self.getDeliveryLineCollectOrderList()[1:],
                                    {})

      delivery_list.append(delivery)

    # XXX temporary
    reindexable_movement_list = []
    return delivery_list, reindexable_movement_list
      
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
      # Create delivery line
      new_delivery_line_id = str(delivery.generateNewId())
      delivery_line = delivery.newContent(
                                type_name=self.getDeliveryLinePortalType(),
                                id=new_delivery_line_id)
      # Put properties on delivery line
      delivery_line.edit(**property_dict)

      # Set variation category list on line
      line_variation_category_list = []
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
        reindexable_movement_list = self._deliveryCellGroupProcessing(
                                    delivery_line,
                                    group,
                                    self.getDeliveryCellCollectOrderList()[1:],
                                    {})

  def _deliveryCellGroupProcessing(self, delivery_line, movement_group,
                                   collect_order_list, property_dict):
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
        # decide if we create a cell or if we update the line
        # Decision can only be made with variation_category_list
        movement = movement_list[0]
        movement_variation_category_list = movement.getVariationCategoryList()
        if movement_variation_category_list == []:
          # update line
          object_to_update = delivery_line
        else:
          # create a new cell
          base_id = 'movement'
          cell_key = movement_variation_category_list
          if not delivery_line.hasCell(base_id=base_id, *cell_key ):
            cell = delivery_line.newCell(base_id=base_id,\
                       portal_type=self.getDeliveryCellPortalType(), *cell_key)
            cell.setCategoryList(cell_key)
            # XXX hardcoded value
            cell.setMappedValuePropertyList(['quantity', 'price'])
            cell.setMembershipCriterionCategoryList(cell_key)
            cell.setMembershipCriterionBaseCategoryList(movement.\
                                          getVariationBaseCategoryList())
            object_to_update = cell
          else:
            raise 'MatrixError', 'Cell: %s already exists on %s' %\
                  (str(cell_key), str(delivery_line))

        # XXX hardcoded value
        # Now, only 1 movement is possible, so copy from this movement
        property_dict['quantity'] = movement.getQuantity()
        property_dict['price'] = movement.getPrice()
                  
        # Update properties on object (quantity, price...)
        object_to_update.edit(**property_dict)

        # Update simulation movement
        movement._setDeliveryValue(object_to_update)
