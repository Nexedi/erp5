# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.MovementGroup import MovementGroupNode
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5.ExplanationCache import _getExplanationCache
from DateTime import DateTime
from Acquisition import aq_parent, aq_inner

class CollectError(Exception): pass
class MatrixError(Exception): pass
class DuplicatedPropertyDictKeysError(Exception): pass

class SelectMethodError(Exception): pass

class BuilderMixin(XMLObject, Amount, Predicate):
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
                  delivery_relative_url_list=None, movement_list=None,
                  explanation=None, business_link=None, activate_kw=None,
                  merge_delivery=None, **kw):
    """
      Build deliveries from a list of movements

      Delivery Builders can also be provided with optional parameters to
      restrict selection to a given root Applied Rule caused by a single Order
      or to Simulation Movements related to a limited set of existing
    """
    # Parameter initialization
    if delivery_relative_url_list is None:
      delivery_relative_url_list = []
    # Call a script before building
    self.callBeforeBuildingScript() # XXX-JPS Used ?
    # Select
    if not movement_list:
      if movement_relative_url_list:
        movement_list = map(self.restrictedTraverse,
                            movement_relative_url_list)
      else:
        if explanation is not None:
          explanation_cache = _getExplanationCache(explanation)
          kw['path'] = explanation_cache.getSimulationPathPatternList()
        if business_link is not None:
          kw['causality_uid'] = business_link.getUid()
        elif kw.get('causality_uid') is None:
          business_link_value_list = self.getRelatedBusinessLinkValueList()
          if len(business_link_value_list) > 0:
            # use only Business Link related movements
            kw['causality_uid'] = [link_value.getUid() for link_value in business_link_value_list]
        if applied_rule_uid is not None:
          kw['applied_rule_uid'] = applied_rule_uid
        movement_list = self.searchMovementList(**kw)
        if not movement_list:
          return []
    # Collect
    root_group_node = self.collectMovement(movement_list, merge_delivery=merge_delivery)
    # Build
    delivery_list = self.buildDeliveryList(
                       root_group_node,
                       delivery_relative_url_list=delivery_relative_url_list,
                       movement_list=movement_list, activate_kw=activate_kw,
                       merge_delivery=merge_delivery, **kw)
    # Call a script after building
    self.callAfterBuildingScript(delivery_list, movement_list, **kw)
    return delivery_list

  def getRelatedBusinessLinkValueList(self):
    return self.getDeliveryBuilderRelatedValueList(portal_type='Business Link')

  security.declarePrivate('callBeforeBuildingScript')
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
    if delivery_module_before_building_script_id:
      delivery_module = getattr(self.getPortalObject(), self.getDeliveryModule())
      getattr(delivery_module, delivery_module_before_building_script_id)()

  def generateMovementListForStockOptimisation(self, group_by_node=1, **kw):
    from Products.ERP5Type.Document import newTempMovement
    now = DateTime()
    movement_list = []
    for attribute, method in [('node_uid', 'getDestinationUid'),
                              ('section_uid', 'getDestinationSectionUid')]:
      if getattr(self, method)() not in ("", None):
        kw[attribute] = getattr(self, method)()
    # We have to check the inventory for each stock movement date.
    # Inventory can be negative in some date, and positive in futur !!
    # This must be done by subclassing OrderBuilder with a new inventory
    # algorithm.
    inventory_kw = kw.copy()
    inventory_kw.setdefault('group_by_variation', 1)
    inventory_kw.setdefault('group_by_resource', 1)
    inventory_kw.setdefault('group_by_section', 0)
    sql_list = self.portal_simulation.getFutureInventoryList(
                                                   group_by_node=group_by_node,
                                                   **inventory_kw)
    # min_flow and max_delay are stored on a supply line. By default
    # we can get them through a method having the right supply type prefix
    # like getPurchaseSupplyLineMinFlow. So we need to guess the supply prefix
    supply_prefix = ''
    delivery_type = self.getDeliveryPortalType()
    portal = self.getPortalObject()
    if delivery_type in portal.getPortalPurchaseTypeList():
      supply_prefix = 'purchase'
    elif delivery_type in portal.getPortalSaleTypeList():
      supply_prefix = 'sale'
    else:
      supply_prefix = 'internal'

    resource_portal_type_list = self.getResourcePortalTypeList()
    def newMovement(inventory_item, resource):
      # Create temporary movement
      movement = newTempMovement(self.getPortalObject(), "temp")
      resource_portal_type = resource.getPortalType()
      assert resource_portal_type in resource_portal_type_list, \
        "Builder %r does not support resource of type : %r" % (
        self.getRelativeUrl(), resource_portal_type)
      movement.edit(
          resource=inventory_item.resource_relative_url,
          # XXX FIXME define on a supply line
          # quantity_unit
          quantity_unit=resource.getQuantityUnit(),
          destination_value=self.getDestinationValue(),
          resource_portal_type=resource_portal_type,
          destination_section_value=self.getDestinationSectionValue())
      # define variation after resource is set
      movement.edit(variation_text=inventory_item.variation_text)
      return movement

    for inventory_item in sql_list:
      if (inventory_item.inventory is not None):
        resource = portal.portal_catalog.getObject(inventory_item.resource_uid)
        # Get min_flow, max_delay on supply line
        min_flow = 0
        max_delay = 0
        min_stock = 0
        if supply_prefix:
          min_flow = resource.getProperty(supply_prefix + '_supply_line_min_flow', 0)
          max_delay = resource.getProperty(supply_prefix + '_supply_line_max_delay', 0)
          min_stock = resource.getProperty(supply_prefix + '_supply_line_min_stock', 0)
        if round(inventory_item.inventory, 5) < min_stock:
          stop_date = resource.getNextAlertInventoryDate(
                               reference_quantity=min_stock,
                               variation_text=inventory_item.variation_text,
                               from_date=now,
                               group_by_node=group_by_node,
                               **kw)
          if stop_date is None:
            stop_date = now
          movement = newMovement(inventory_item, resource)
          movement.edit(
            start_date=stop_date-max_delay,
            stop_date=stop_date,
            quantity=max(min_flow, -inventory_item.inventory),
          )
          movement_list.append(movement)
        # We could need to cancel automated stock optimization if for some reasons
        # previous optimisations are obsolete
        elif round(inventory_item.inventory, 5) > min_stock:
          delta = inventory_item.inventory - min_stock
          node_uid = inventory_item.node_uid
          # if node_uid is provided, we have to look at all provided nodes
          if kw.has_key('node_uid'):
            node_uid = kw['node_uid']
          optimized_kw = {}
          if kw.get('group_by_variation', 1):
            optimized_kw['variation_text'] = inventory_item.variation_text
          optimized_inventory_list = portal.portal_simulation.getInventoryList(
                               resource_uid=inventory_item.resource_uid,
                               node_uid=node_uid,
                               simulation_state="auto_planned",
                               sort_on=[("date", "descending")],
                               group_by_node=group_by_node,
                               **optimized_kw)
          for optimized_inventory in optimized_inventory_list:
            movement = newMovement(inventory_item, resource)
            quantity = min(delta, optimized_inventory.inventory)
            delta = delta - quantity
            movement.edit(start_date=optimized_inventory.date,
                          quantity=-quantity)
            movement_list.append(movement)
            if delta <= 0:
              break
    return movement_list

  def _searchMovementList(self, **kw):
    """
      Returns a list of simulation movements (or something similar to
      simulation movements) to construct a new delivery.
    """
    method_id = self.getSimulationSelectMethodId() or 'portal_catalog'
    select_method = getattr(self, method_id)

    movement_list = [] # use list to preserve order
    movement_set = set()
    for movement in select_method(**kw):
      movement = movement.getObject()
      if movement in movement_set:
        raise SelectMethodError('%s returned %s twice or more' % \
                (method_id, movement.getRelativeUrl()))
      movement_set.add(movement)
      movement_list.append(movement)

    return movement_list

  security.declarePrivate('searchMovementList')
  searchMovementList = UnrestrictedMethod(_searchMovementList)

  security.declarePrivate('collectMovement')
  def collectMovement(self, movement_list, merge_delivery=False):
    """
      group movements in the way we want. Thanks to this method, we are able
      to retrieve movement classed by order, resource, criterion,....
      movement_list : the list of movement wich we want to group
      class_list : the list of classes used to group movements. The order
                   of the list is important and determines by what we will
                   group movement first
                   Typically, check_list is :
                   [DateMovementGroup,PathMovementGroup,...]
    """
    movement_group_list = self.getMovementGroupList()
    last_line_movement_group = self.getDeliveryMovementGroupList()[-1]
    separate_method_name_list = self.getDeliveryCellSeparateOrderList([])
    root_group_node = MovementGroupNode(
      separate_method_name_list=separate_method_name_list,
      movement_group_list=movement_group_list,
      last_line_movement_group=last_line_movement_group,
      merge_delivery=merge_delivery)
    root_group_node.append(movement_list)
    return root_group_node

  def _test(self, instance, movement_group_node_list,
                    divergence_list):
    result = True
    new_property_dict_list = []
    for movement_group_node in movement_group_node_list:
      tmp_result, tmp_property_dict = movement_group_node.test(
        instance, divergence_list)
      if not tmp_result:
        result = tmp_result
      new_property_dict_list.append(tmp_property_dict)
    return result, new_property_dict_list

  @staticmethod
  def _getSortedPropertyDict(property_dict_list):
    # Sort the edit keywords according to the order of their movement
    # groups. This is important so that, for example, the 'resource'
    # is already set on a movement before trying to set the
    # 'variation_category' or 'variation_property' pseudo properties,
    # which rely on the resource being set to discover which
    # categories/properties to set
    # XXX-Leo: in the future: using an ordered_dict would be nice,
    # but this would have to be respected on Base._edit()
    edit_order = []
    property_dict = {'edit_order': edit_order}
    for d in property_dict_list:
      for k,v in d.iteritems():
        if k in property_dict:
          raise DuplicatedPropertyDictKeysError(k)
        property_dict[k] = v
        edit_order.append(k)
    return property_dict

  def _findUpdatableObject(self, instance_list, movement_group_node_list,
                           divergence_list):
    instance = None
    if instance_list:
      # we want to check the original delivery first.
      # so sort instance_list by that current is exists or not.
      try:
        current = movement_group_node_list[-1].getMovementList()[0].getDeliveryValue()
        portal = self.getPortalObject()
        while current != portal:
          if current in instance_list:
            instance_list.sort(key=lambda x: x != current and 1 or 0)
            break
          current = current.getParentValue()
      except AttributeError:
        pass
      for instance_to_update in instance_list:
        result, property_dict_list = self._test(
          instance_to_update, movement_group_node_list, divergence_list)
        if result:
          instance = instance_to_update
          break
    else:
      property_dict_list = [movement_group_node.getGroupEditDict()
                            for movement_group_node in movement_group_node_list]
    return instance, self._getSortedPropertyDict(property_dict_list)

  security.declarePrivate('buildDeliveryList')
  @UnrestrictedMethod
  def buildDeliveryList(self, movement_group_node,
                        delivery_relative_url_list=None,
                        movement_list=None, update=True, **kw):
    """
      Build deliveries from a list of movements
    """
    # Parameter initialization
    if delivery_relative_url_list is None:
      delivery_relative_url_list = []
    if movement_list is None:
      movement_list = []
    # Module where we can create new deliveries
    portal = self.getPortalObject()
    delivery_module = getattr(portal, self.getDeliveryModule())
    if update:
      delivery_to_update_list = [portal.restrictedTraverse(relative_url) for \
                                 relative_url in delivery_relative_url_list]
      # Only use select method when the list of delivery is not already provided
      if len(delivery_to_update_list) == 0:
        # Deliveries we are trying to update
        delivery_select_method_id = self.getDeliverySelectMethodId()
        if delivery_select_method_id not in ["", None]:
          to_update_delivery_sql_list = getattr(self, delivery_select_method_id) \
                                        (movement_list=movement_list)
          delivery_to_update_list.extend([sql_delivery.getObject() \
                                          for sql_delivery \
                                          in to_update_delivery_sql_list])
    else:
      delivery_to_update_list = []
    # We do not want to update the same object more than twice in one
    # _deliveryGroupProcessing().
    self._resetUpdated()
    delivery_list = self._processDeliveryGroup(
                          delivery_module,
                          movement_group_node,
                          self.getDeliveryMovementGroupList(),
                          delivery_to_update_list=delivery_to_update_list,
                          **kw)
    return delivery_list

  def _createDelivery(self, delivery_module, movement_list, activate_kw):
    """
      Create a new delivery in case where a builder may not update
      an existing one.
    """
    return delivery_module.newContent(
      portal_type=self.getDeliveryPortalType(),
      created_by_builder=1,
      activate_kw=activate_kw)

  def _processDeliveryGroup(self, delivery_module, movement_group_node,
                            collect_order_list, movement_group_node_list=None,
                            delivery_to_update_list=None,
                            divergence_list=None,
                            activate_kw=None, force_update=0,
                            merge_delivery=None, **kw):
    """
      Build delivery from a list of movement
    """
    if movement_group_node_list is None:
      movement_group_node_list = []
    if divergence_list is None:
      divergence_list = []
    # do not use 'append' or '+=' because they are destructive.
    movement_group_node_list = movement_group_node_list + [movement_group_node]
    # Parameter initialization
    if delivery_to_update_list is None:
      delivery_to_update_list = []
    delivery_list = []

    if len(collect_order_list):
      # Get sorted movement for each delivery
      for grouped_node in movement_group_node.getGroupList():
        new_delivery_list = self._processDeliveryGroup(
                              delivery_module,
                              grouped_node,
                              collect_order_list[1:],
                              movement_group_node_list=movement_group_node_list,
                              delivery_to_update_list=delivery_to_update_list,
                              divergence_list=divergence_list,
                              activate_kw=activate_kw,
                              force_update=force_update,
                              merge_delivery=merge_delivery)
        delivery_list.extend(new_delivery_list)
        force_update = 0
    else:
      # Test if we can update a existing delivery, or if we need to create
      # a new one
      delivery_to_update_list = [
        x for x in delivery_to_update_list \
        if x.getPortalType() == self.getDeliveryPortalType() and \
        not self._isUpdated(x, 'delivery')]
      if merge_delivery:
        # We must have only one delivery to update in the case of merge
        delivery, = delivery_to_update_list
        property_dict = {}
      else:
        delivery, property_dict = self._findUpdatableObject(
          delivery_to_update_list, movement_group_node_list,
          divergence_list)

      # if all deliveries are rejected in case of update, we update the
      # first one.
      if force_update and delivery is None and len(delivery_to_update_list):
        delivery = delivery_to_update_list[0]

      if delivery is None:
        if not self.isDeliveryCreatable():
          raise SelectMethodError('No updatable delivery found with %s for %s' \
                  % (self.getPath(), movement_group_node_list))

        delivery = self._createDelivery(delivery_module,
                                        movement_group_node.getMovementList(),
                                        activate_kw)
      # Put properties on delivery
      self._setUpdated(delivery, 'delivery')
      if property_dict:
        property_dict.setdefault('edit_order', ('stop_date', 'start_date'))
        delivery._edit(reindex_object=1, **property_dict)

      # Then, create delivery line
      for grouped_node in movement_group_node.getGroupList():
        self._processDeliveryLineGroup(
                                delivery,
                                grouped_node,
                                self.getDeliveryLineMovementGroupList()[1:],
                                divergence_list=divergence_list,
                                activate_kw=activate_kw,
                                force_update=force_update)
      delivery_list.append(delivery)
    return delivery_list

  def _createDeliveryLine(self, delivery, movement_list, activate_kw):
    """
      Create a new delivery line in case where a builder may not update
      an existing one.
    """
    return delivery.newContent(
      portal_type=self.getDeliveryLinePortalType(),
      created_by_builder=1,
      activate_kw=activate_kw)

  def _processDeliveryLineGroup(self, delivery, movement_group_node,
                                collect_order_list, movement_group_node_list=None,
                                divergence_list=None,
                                activate_kw=None, force_update=0, **kw):
    """
      Build delivery line from a list of movement on a delivery
    """
    if movement_group_node_list is None:
      movement_group_node_list = []
    if divergence_list is None:
      divergence_list = []
    # do not use 'append' or '+=' because they are destructive.
    movement_group_node_list = movement_group_node_list + [movement_group_node]

    if len(collect_order_list) and not movement_group_node.getCurrentMovementGroup().isBranch():
      # Get sorted movement for each delivery line
      for grouped_node in movement_group_node.getGroupList():
        self._processDeliveryLineGroup(
          delivery,
          grouped_node,
          collect_order_list[1:],
          movement_group_node_list=movement_group_node_list,
          divergence_list=divergence_list,
          activate_kw=activate_kw,
          force_update=force_update)
    else:
      # Test if we can update an existing line, or if we need to create a new
      # one
      delivery_line_to_update_list = [x for x in delivery.contentValues(
        portal_type=self.getDeliveryLinePortalType()) if \
                                      not self._isUpdated(x, 'line')]
      delivery_line, property_dict = self._findUpdatableObject(
        delivery_line_to_update_list, movement_group_node_list,
        divergence_list)
      if delivery_line is not None:
        update_existing_line = 1
      else:
        # Create delivery line
        update_existing_line = 0
        delivery_line = self._createDeliveryLine(
                delivery,
                movement_group_node.getMovementList(),
                activate_kw)
      # Put properties on delivery line
      self._setUpdated(delivery_line, 'line')
      if property_dict:
        property_dict.setdefault('edit_order', ('stop_date', 'start_date'))
        delivery_line.edit(force_update=1, **property_dict)

      if movement_group_node.getCurrentMovementGroup().isBranch():
        for grouped_node in movement_group_node.getGroupList():
          self._processDeliveryLineGroup(
            delivery_line,
            grouped_node,
            collect_order_list[1:],
            movement_group_node_list=movement_group_node_list,
            divergence_list=divergence_list,
            activate_kw=activate_kw,
            force_update=force_update)
        return

      # Update variation category list on line
      variation_category_set = set(delivery_line.getVariationCategoryList())
      for movement in movement_group_node.getMovementList():
        variation_category_set.update(movement.getVariationCategoryList())
      delivery_line.setVariationCategoryList(sorted(variation_category_set))
      # Then, create delivery movement (delivery cell or complete delivery
      # line)
      grouped_node_list = movement_group_node.getGroupList()
      # If no group is defined for cell, we need to continue, in order to
      # save the quantity value
      if len(grouped_node_list):
        for grouped_node in grouped_node_list:
          self._processDeliveryCellGroup(
                                    delivery_line,
                                    grouped_node,
                                    self.getDeliveryCellMovementGroupList()[1:],
                                    update_existing_line=update_existing_line,
                                    divergence_list=divergence_list,
                                    activate_kw=activate_kw,
                                    force_update=force_update)
      else:
        self._processDeliveryCellGroup(
                                  delivery_line,
                                  movement_group_node,
                                  [],
                                  update_existing_line=update_existing_line,
                                  divergence_list=divergence_list,
                                  activate_kw=activate_kw,
                                  force_update=force_update)

  def _createDeliveryCell(self, delivery_line, movement, activate_kw,
                          base_id, cell_key):
    """
      Create a new delivery cell in case where a builder may not update
      an existing one.
    """
    cell = delivery_line.newCell(base_id=base_id,
                                 portal_type=self.getDeliveryCellPortalType(),
                                 activate_kw=activate_kw,
                                 *cell_key)
    return cell

  def _processDeliveryCellGroup(self, delivery_line, movement_group_node,
                                collect_order_list, movement_group_node_list=None,
                                update_existing_line=0,
                                divergence_list=None,
                                activate_kw=None, force_update=0):
    """
      Build delivery cell from a list of movement on a delivery line
      or complete delivery line
    """
    if movement_group_node_list is None:
      movement_group_node_list = []
    if divergence_list is None:
      divergence_list = []
    # do not use 'append' or '+=' because they are destructive.
    movement_group_node_list = movement_group_node_list + [movement_group_node]

    if len(collect_order_list):
      # Get sorted movement for each delivery line
      for grouped_node in movement_group_node.getGroupList():
        self._processDeliveryCellGroup(
          delivery_line,
          grouped_node,
          collect_order_list[1:],
          movement_group_node_list=movement_group_node_list,
          update_existing_line=update_existing_line,
          divergence_list=divergence_list,
          activate_kw=activate_kw,
          force_update=force_update)
    else:
      movement_list = movement_group_node.getMovementList()
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
        property_dict = {}
        if len(delivery_line.getCellKeyList(base_id=base_id)) == 0:
          # update line
          if update_existing_line == 1:
            if self._isUpdated(delivery_line, 'cell'):
              object_to_update_list = []
            else:
              object_to_update_list = [delivery_line]
          else:
            object_to_update_list = []
          object_to_update, property_dict = self._findUpdatableObject(
            object_to_update_list, movement_group_node_list,
            divergence_list)
          if object_to_update is not None:
            update_existing_movement = 1
          else:
            object_to_update = delivery_line
        else:
          object_to_update_list = [
            delivery_line.getCell(base_id=base_id, *cell_key) for cell_key in \
            delivery_line.getCellKeyList(base_id=base_id) \
            if delivery_line.hasCell(base_id=base_id, *cell_key)]
          object_to_update, property_dict = self._findUpdatableObject(
            object_to_update_list, movement_group_node_list,
            divergence_list)
          if object_to_update is not None:
            # We update a existing cell
            # delivery_ratio of new related movement to this cell
            # must be updated to 0.
            update_existing_movement = 1

        if object_to_update is None:
          # create a new cell
          cell_key = movement.getVariationCategoryList(
              omit_optional_variation=1)
          if not delivery_line.hasCell(base_id=base_id, *cell_key):
            cell = self._createDeliveryCell(delivery_line, movement,
                                            activate_kw, base_id, cell_key)
            vcl = movement.getVariationCategoryList()
            cell._edit(category_list=vcl,
                       # XXX hardcoded value
                       mapped_value_property_list=('quantity', 'price'),
                       membership_criterion_category_list=vcl,
                       membership_criterion_base_category_list=movement.\
                                             getVariationBaseCategoryList())
          else:
            raise MatrixError, 'Cell: %s already exists on %s' % \
                  (str(cell_key), str(delivery_line))
          object_to_update = cell
        self._setUpdated(object_to_update, 'cell')
        self._setDeliveryMovementProperties(
                            object_to_update, movement, property_dict,
                            update_existing_movement=update_existing_movement,
                            force_update=force_update, activate_kw=activate_kw)

  def _setDeliveryMovementProperties(self, delivery_movement,
                                     simulation_movement, property_dict,
                                     update_existing_movement=0,
                                     force_update=0, activate_kw=None):
    """
      Initialize or update delivery movement properties.
    """
    if not update_existing_movement or force_update:
      # Now, only 1 movement is possible, so copy from this movement
      # XXX hardcoded value
      property_dict['quantity'] = simulation_movement.getQuantity()
      property_dict['price'] = simulation_movement.getPrice()
      # Update properties on object (quantity, price...)
      delivery_movement._edit(force_update=1, **property_dict)

  security.declarePrivate('callAfterBuildingScript')
  @UnrestrictedMethod
  def callAfterBuildingScript(self, delivery_list, movement_list=(), **kw):
    """
      Call script on each delivery built.
    """
    delivery_after_generation_script_id = \
                              self.getDeliveryAfterGenerationScriptId()
    if delivery_after_generation_script_id:
      related_simulation_movement_path_list = \
                                [x.getPath() for x in movement_list]
      for delivery in delivery_list:
        script = getattr(delivery, delivery_after_generation_script_id)
        # BBB: Only Python Scripts were used in the past, and they might not
        # accept an arbitrary argument. So to keep compatibility,
        # check if it can take the new parameter safely, only when
        # the callable object is a Python Script.
        meta_type = getattr(script, 'meta_type', None)
        if meta_type == 'Script (Python)':
          # check parameters accepted by the script
          for param in script.params().split(','):
            param = param.split('=', 1)[0].strip()
            if param == "movement_list": # XXX-Aurel: path does not work with temp objects
              script(movement_list=movement_list)
              break
            if param == 'related_simulation_movement_path_list' \
                    or param.startswith('**'):
              script(related_simulation_movement_path_list=related_simulation_movement_path_list)
              break
          else:
            script()
            continue
        else:
          script(related_simulation_movement_path_list=related_simulation_movement_path_list)


  security.declareProtected(Permissions.AccessContentsInformation,
                           'getMovementGroupList')
  def getMovementGroupList(self, portal_type=None, collect_order_group=None,
                            **kw):
    """
    Return a list of movement groups sorted by collect order group and index.
    """
    category_index_dict = {}
    for i in self.getPortalObject().portal_categories.collect_order_group.contentValues():
      category_index_dict[i.getId()] = i.getIntIndex()

    def sort_movement_group(a, b):
        return cmp(category_index_dict.get(a.getCollectOrderGroup()),
                   category_index_dict.get(b.getCollectOrderGroup())) or \
               cmp(a.getIntIndex(), b.getIntIndex())
    if portal_type is None:
      portal_type = self.getPortalMovementGroupTypeList()
    movement_group_list = [x for x in self.contentValues(filter={'portal_type': portal_type}) \
                           if collect_order_group is None or collect_order_group == x.getCollectOrderGroup()]
    return sorted(movement_group_list, sort_movement_group)

  # XXX category name is hardcoded.
  def getDeliveryMovementGroupList(self, **kw):
    return self.getMovementGroupList(collect_order_group='delivery')

  # XXX category name is hardcoded.
  def getDeliveryLineMovementGroupList(self, **kw):
    return self.getMovementGroupList(collect_order_group='line')

  # XXX category name is hardcoded.
  def getDeliveryCellMovementGroupList(self, **kw):
    return self.getMovementGroupList(collect_order_group='cell')

  def _searchUpByPortalType(self, obj, portal_type):
    limit_portal_type = self.getPortalObject().getPortalType()
    while obj is not None:
      obj_portal_type = obj.getPortalType()
      if obj_portal_type == portal_type:
        break
      elif obj_portal_type == limit_portal_type:
        obj = None
        break
      else:
        obj = aq_parent(aq_inner(obj))
    return obj

  def _isUpdated(self, obj, level):
    tv = getTransactionalVariable()
    return level in tv['builder_processed_list'].get(obj, ())

  def _setUpdated(self, obj, level):
    tv = getTransactionalVariable()
    if 'builder_processed_list' not in tv:
      self._resetUpdated()
    tv['builder_processed_list'].setdefault(obj, []).append(level)

  def _resetUpdated(self):
    tv = getTransactionalVariable()
    tv['builder_processed_list'] = {}

  # for backward compatibilities.
  _deliveryGroupProcessing = _processDeliveryGroup
  _deliveryLineGroupProcessing = _processDeliveryLineGroup
  _deliveryCellGroupProcessing = _processDeliveryCellGroup

InitializeClass(BuilderMixin)
