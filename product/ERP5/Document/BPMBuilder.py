# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5.Document.Alarm import Alarm
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.MovementGroup import MovementGroupNode
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.ERP5Type.CopySupport import CopyError, tryMethodCallWithTemporaryPermission
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Acquisition import aq_parent, aq_inner

class CollectError(Exception): pass
class MatrixError(Exception): pass
class DuplicatedPropertyDictKeysError(Exception): pass
class SelectMethodError(Exception): pass

class BPMBuilder(Alarm):
  """Top class for builders.

  WARNING: This is BPM evaluation of building approach.
  WARNING: Do NOT use it in production environment.

  There are two types of builders - global safe and global unsafe.

  Global safe builders can be configured like alarms.

  Global unsafe builders have to be invoked by passing restrictive parameters
  to them, so they cannot behave like alarms, they have to be invoked from
  scripts.

  Global safe builders characteristics are described in erp5-Updated.Builder.Ideas

  Scripts assumptions:

   * simulation_select_method_id have to return non delivered movements - it
     shall parse returned list to manually remove delivered movements
  """

  meta_type = 'ERP5 Builder'
  portal_type = 'Builder'
  security = ClassSecurityInfo()

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Arrow
                    , PropertySheet.Amount
                    , PropertySheet.Comment
                    , PropertySheet.DeliveryBuilder
                    , PropertySheet.Alarm
                    , PropertySheet.Periodicity
                    )

  security.declareProtected(Permissions.View, 'build')
  def build(self, tag=None, input_movement_list=None,
        existing_delivery_list=None, select_method_dict=None, **kwargs):
    """Builds document according to self configuration mixed with passed parameters

    Selecting parameters (like input movement list) might be passed directly
    to builder, but if not passed builder is able to find those values by
    itself.

    select_method_dict - dictionary which will be passed to input movement
      select method
    """
    # XXX: TODO backward compatibility with old parameters
    if select_method_dict is None:
      select_method_dict = {}
    # Call a script before building
    self.callBeforeBuildingScript()
    # Select movements
    if input_movement_list is None:
      business_path_value_list = self.getRelatedBusinessPathValueList()
      if len(business_path_value_list) > 0:
        # use only Business Path related movements
        select_method_dict['causality_uid'] = [q.getUid() for q in business_path_value_list]
      # do search
      input_movement_value_list = self.searchMovementList(
        delivery_relative_url_list=existing_delivery_list,
        **select_method_dict)
    else:
      # movements were passed directly
      input_movement_value_list = [self.unrestrictedTraverse(relative_url) for
          relative_url in input_movement_list]
    # Collect
    root_group_node = self.collectMovement(input_movement_value_list)
    # Build
    delivery_value_list = self.buildDeliveryList(
                       root_group_node,
                       delivery_relative_url_list=existing_delivery_list,
                       movement_list=input_movement_value_list)
    # Call a script after building
    self.callAfterBuildingScript(delivery_value_list,
        input_movement_value_list)
    return delivery_value_list

  security.declareProtected(Permissions.View, 'activeSense')
  def activeSense(self):
    """Activate building, only one builder at time"""
    self.setNextAlarmDate()
    # A tag is provided as a parameter in order to be
    # able to notify the user after all processes are ended
    # Tag is generated from portal_ids so that it can be retrieved
    # later when creating an active process for example
    tag = str(self.portal_ids.generateNewLengthId(id_group=self.getId()))
    self.activate(tag=tag).build(tag=tag)

    if self.isAlarmNotificationMode():
      self.activate(after_tag=tag).notify(include_active=True)

  def searchMovementList(self, *args, **kw):
    """
      defines how to query all input movements which meet certain criteria
      First, select movement matching to criteria define on Builder
    """
    searchMovementList = UnrestrictedMethod(self._searchMovementList)
    return searchMovementList(*args, **kw)

  def _searchMovementList(self, **kw):
    """This method is wrapped by UnrestrictedMethod."""
    input_movement_value_list = []
    # We only search Simulation Movement - Luke do not know why...
    kw['portal_type'] = 'Simulation Movement' # blah!

    select_method = getattr(self.getPortalObject(),
        self.simulation_select_method_id or
        self._getTypeBasedMethod('_selectDefaultMovement'))
    input_movement_value_list = select_method(**kw)

    movement_dict = {}
    for movement in input_movement_value_list:
      if not movement.isBuildable():
        raise ValueError('Movement %s is not buildable' % movement.getRelativeUrl())
      if movement_dict.has_key(movement):
        # if duplicated - fail
        raise SelectMethodError("%s repeated %s in list" %
                    (str(self.simulation_select_method_id),
                    str(movement.getRelativeUrl())))
      else:
        movement_dict[movement] = 1

    return input_movement_value_list

  def _setDeliveryMovementProperties(self, delivery_movement,
                                     input_movement, property_dict,
                                     update_existing_movement=0,
                                     force_update=0, activate_kw=None):
    """
      Initialize or update delivery movement properties.
      Set delivery ratio on simulation movement.
    """

    """force_update is calculated in cryptic way
       in new implementation we will be know if delivery is still modifiable by
       builder or not
    """
    if update_existing_movement == 1 and not force_update:
#      # Important.
#      # Attributes of object_to_update must not be modified here.
#      # Because we can not change values that user modified.
#      # Delivery will probably diverge now, but this is not the job of
#      # DeliveryBuilder to resolve such problem.
#      # Use Solver instead.
      if getattr(input_movement, 'setDeliveryRatio', None) is not None:
        input_movement.edit(delivery_ratio=0)
    else:
      # Update quantity on movement
      # XXX hardcoded value
      property_dict['quantity'] = delivery_movement.getQuantity() + \
          input_movement.getQuantity() # float point
      property_dict['price'] = input_movement.getPrice() or 0.0
      delivery_movement_price = delivery_movement.getPrice()
      if delivery_movement_price is not None:
        # doSomethingWithPrice - this is only example
        property_dict['price'] = (property_dict['price'] \
            + delivery_movement_price) / 2

      # Update properties on object (quantity, price...)
      delivery_movement._edit(force_update=1, **property_dict)
      if getattr(input_movement, 'setDeliveryRatio', None) is not None:
        if delivery_movement.getQuantity() in [0, 0.0, None]:
          delivery_ratio = 1
        else:
          delivery_ratio = input_movement.getQuantity() / delivery_movement \
              .getQuantity() # float point
        input_movement.edit(delivery_ratio=delivery_ratio)
    if getattr(input_movement,'setDeliveryValue', None) is not None:
      input_movement.edit(delivery_value=delivery_movement,
                               activate_kw=activate_kw)

  def getRelatedBusinessPathValueList(self):
    return self.getDeliveryBuilderRelatedValueList(
        portal_type='Business Path') + self.getOrderBuilderRelatedValueList(
        portal_type='Business Path')

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

  def collectMovement(self, movement_list):
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
      last_line_movement_group=last_line_movement_group)
    root_group_node.append(movement_list)
    return root_group_node

  def _test(self, instance, movement_group_node_list,
                    divergence_list):
    """XXX TODO docstring"""
    result = True
    new_property_dict = {}
    for movement_group_node in movement_group_node_list:
      tmp_result, tmp_property_dict = movement_group_node.test(
        instance, divergence_list)
      if not tmp_result:
        result = tmp_result
      new_property_dict.update(tmp_property_dict)
    return result, new_property_dict

  def _findUpdatableObject(self, instance_list, movement_group_node_list,
                           divergence_list):
    """XXX TODO docstring"""
    instance = None
    property_dict = {}
    if not len(instance_list):
      for movement_group_node in movement_group_node_list:
        for k,v in movement_group_node.getGroupEditDict().iteritems():
          if k in property_dict:
            raise DuplicatedPropertyDictKeysError(k)
          else:
            property_dict[k] = v
    else:
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
        result, property_dict = self._test(
          instance_to_update, movement_group_node_list, divergence_list)
        if result == True:
          instance = instance_to_update
          break
    return instance, property_dict

  def buildDeliveryList(self, *args, **kw):
    """
      Build deliveries from a list of movements
    """
    buildDeliveryList = UnrestrictedMethod(self._buildDeliveryList)
    return buildDeliveryList(*args, **kw)

  def _buildDeliveryList(self, movement_group_node, delivery_relative_url_list=None,
                         movement_list=None,**kw):
    """This method is wrapped by UnrestrictedMethod. XXX do docstring which have a sense"""
    # Parameter initialization
    if delivery_relative_url_list is None:
      delivery_relative_url_list = []
    if movement_list is None:
      movement_list = []
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

  def _processDeliveryGroup(self, delivery_module, movement_group_node,
                            collect_order_list, movement_group_node_list=None,
                            delivery_to_update_list=None,
                            divergence_list=None,
                            activate_kw=None, force_update=0, **kw):
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
                              force_update=force_update)
        delivery_list.extend(new_delivery_list)
        force_update = 0
    else:
      # Test if we can update a existing delivery, or if we need to create
      # a new one
      delivery_to_update_list = [
        x for x in delivery_to_update_list \
        if x.getPortalType() == self.getDeliveryPortalType() and \
        not self._isUpdated(x, 'delivery')]
      delivery, property_dict = self._findUpdatableObject(
        delivery_to_update_list, movement_group_node_list,
        divergence_list)

      # if all deliveries are rejected in case of update, we update the
      # first one.
      if force_update and delivery is None and len(delivery_to_update_list):
        delivery = delivery_to_update_list[0]

      if delivery is None:
        # Create delivery
        try:
          old_delivery = self._searchUpByPortalType(
            movement_group_node.getMovementList()[0].getDeliveryValue(),
            self.getDeliveryPortalType())
        except AttributeError:
          old_delivery = None
        if old_delivery is None:
          # from scratch
          new_delivery_id = str(delivery_module.generateNewId())
          delivery = delivery_module.newContent(
            portal_type=self.getDeliveryPortalType(),
            id=new_delivery_id,
            created_by_builder=1,
            activate_kw=activate_kw)
        else:
          # from duplicated original delivery
          cp = tryMethodCallWithTemporaryPermission(
            delivery_module, 'Copy or Move',
            lambda parent, *ids:
            parent._duplicate(parent.manage_copyObjects(ids=ids))[0],
            (delivery_module, old_delivery.getId()), {}, CopyError)
          delivery = delivery_module[cp['new_id']]
          # delete non-split movements
          keep_id_list = [y.getDeliveryValue().getId() for y in \
                          movement_group_node.getMovementList()]
          delete_id_list = [x.getId() for x in delivery.contentValues() \
                           if x.getId() not in keep_id_list]
          delivery.deleteContent(delete_id_list)
      # Put properties on delivery
      self._setUpdated(delivery, 'delivery')
      if property_dict:
        delivery.edit(**property_dict)

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
        try:
          old_delivery_line = self._searchUpByPortalType(
            movement_group_node.getMovementList()[0].getDeliveryValue(),
            self.getDeliveryLinePortalType())
        except AttributeError:
          old_delivery_line = None
        if old_delivery_line is None:
          # from scratch
          new_delivery_line_id = str(delivery.generateNewId())
          delivery_line = delivery.newContent(
            portal_type=self.getDeliveryLinePortalType(),
            id=new_delivery_line_id,
            variation_category_list=[],
            activate_kw=activate_kw)
        else:
          # from duplicated original line
          cp = tryMethodCallWithTemporaryPermission(
            delivery, 'Copy or Move',
            lambda parent, *ids:
            parent._duplicate(parent.manage_copyObjects(ids=ids))[0],
            (delivery, old_delivery_line.getId()), {}, CopyError)
          delivery_line = delivery[cp['new_id']]
          # reset variation category list
          delivery_line.setVariationCategoryList([])
          # delete non-split movements
          keep_id_list = [y.getDeliveryValue().getId() for y in \
                          movement_group_node.getMovementList()]
          delete_id_list = [x.getId() for x in delivery_line.contentValues() \
                           if x.getId() not in keep_id_list]
          delivery_line.deleteContent(delete_id_list)
      # Put properties on delivery line
      self._setUpdated(delivery_line, 'line')
      if property_dict:
        delivery_line.edit(**property_dict)

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
      variation_category_dict = dict([(variation_category, True) for
                                      variation_category in
                                      delivery_line.getVariationCategoryList()])
      for movement in movement_group_node.getMovementList():
        for category in movement.getVariationCategoryList():
          variation_category_dict[category] = True
      variation_category_list = sorted(variation_category_dict.keys())
      delivery_line.setVariationCategoryList(variation_category_list)
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
            try:
              old_cell = movement_group_node.getMovementList()[0].getDeliveryValue()
            except AttributeError:
              old_cell = None
            if old_cell is None:
              # from scratch
              cell = delivery_line.newCell(base_id=base_id, \
                       portal_type=self.getDeliveryCellPortalType(),
                       activate_kw=activate_kw,*cell_key)
            else:
              # from duplicated original line
              cp = tryMethodCallWithTemporaryPermission(
                delivery_line, 'Copy or Move',
                lambda parent, *ids:
                parent._duplicate(parent.manage_copyObjects(ids=ids))[0],
                (delivery_line, old_cell.getId()), {}, CopyError)
              cell = delivery_line[cp['new_id']]

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
        self._setUpdated(object_to_update, 'cell')
        self._setDeliveryMovementProperties(
                            object_to_update, movement, property_dict,
                            update_existing_movement=update_existing_movement,
                            force_update=force_update, activate_kw=activate_kw)

  def callAfterBuildingScript(self, *args, **kw):
    """
      Call script on each delivery built.
    """
    callAfterBuildingScript = UnrestrictedMethod(self._callAfterBuildingScript)
    return callAfterBuildingScript(*args, **kw)

  def _callAfterBuildingScript(self, delivery_list, movement_list=None, **kw):
    """
      Call script on each delivery built.
      This method is wrapped by UnrestrictedMethod.
    """
    if not len(delivery_list):
      return
    # Parameter initialization
    if movement_list is None:
      movement_list = []
    delivery_after_generation_script_id = \
                              self.getDeliveryAfterGenerationScriptId()
    related_simulation_movement_path_list = \
                              [x.getPath() for x in movement_list]
    if delivery_after_generation_script_id not in ["", None]:
      for delivery in delivery_list:
        script = getattr(delivery, delivery_after_generation_script_id)
        # BBB: Only Python Scripts were used in the past, and they might not
        # accept an arbitrary argument. So to keep compatibility,
        # check if it can take the new parameter safely, only when
        # the callable object is a Python Script.
        safe_to_pass_parameter = True
        meta_type = getattr(script, 'meta_type', None)
        if meta_type == 'Script (Python)':
          # check if the script accepts related_simulation_movement_path_list
          safe_to_pass_parameter = False
          for param in script.params().split(','):
            param = param.split('=', 1)[0].strip()
            if param == 'related_simulation_movement_path_list' \
                    or param.startswith('**'):
              safe_to_pass_parameter = True
              break

        if safe_to_pass_parameter:
          script(related_simulation_movement_path_list=related_simulation_movement_path_list)
        else:
          script()

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
    tv = getTransactionalVariable(self)
    return level in tv['builder_processed_list'].get(obj, [])

  def _setUpdated(self, obj, level):
    tv = getTransactionalVariable(self)
    if tv.get('builder_processed_list', None) is None:
      self._resetUpdated()
    tv['builder_processed_list'][obj] = \
       tv['builder_processed_list'].get(obj, []) + [level]

  def _resetUpdated(self):
    tv = getTransactionalVariable(self)
    tv['builder_processed_list'] = {}
