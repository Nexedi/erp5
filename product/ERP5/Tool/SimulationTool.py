##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

from Products.CMFCore.utils import UniqueObject

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5.ERP5Globals import default_section_category, order_type_list, current_inventory_state_list

from Products.ERP5 import _dtmldir

from zLOG import LOG

from Products.ERP5.Capacity.GLPK import solve
from Numeric import zeros, resize

# Solver Registration
is_initialized = 0
delivery_solver_dict = {}
delivery_solver_list = []

def registerDeliverySolver(solver):
    global delivery_solver_list, delivery_solver_dict
    LOG('Register Solver', 0, str(solver.__name__))
    delivery_solver_list.append(solver)
    delivery_solver_dict[solver.__name__] = solver

target_solver_dict = {}
target_solver_list = []

def registerTargetSolver(solver):
    global target_solver_list, target_solver_dict
    LOG('Register Solver', 0, str(solver.__name__))
    target_solver_list.append(solver)
    target_solver_dict[solver.__name__] = solver

class Target:

  def __init__(self, **kw):
    """
      Defines a target (target_quantity, start_date, stop_date)
    """
    self.__dict__.update(kw)

class SimulationTool (Folder, UniqueObject):
    """
    The SimulationTool implements the ERP5
    simulation algorithmics.


    Examples of applications:

    -

    -
    ERP5 main purpose:

    -

    -

    """
    id = 'portal_simulation'
    meta_type = 'ERP5 Simulation Tool'
    allowed_types = ( 'ERP5 Applied Rule', )

    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainSimulationTool', _dtmldir )

    # Filter content (ZMI))
    def __init__(self):
        return Folder.__init__(self, SimulationTool.id)

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = SimulationTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    def initialize(self):
      """
        Update values of simulation movements based on delivery
        target values and solver
      """
      from Products.ERP5.TargetSolver import Reduce, Defer, SplitAndDefer, CopyToTarget
      from Products.ERP5.DeliverySolver import Distribute, Copy

    def isInitialized(self):
      global is_initialized
      return is_initialized

    def newDeliverySolver(self, solver_id, *args, **kw):
      """
        Returns a solver instance
      """
      if not self.isInitialized(): self.initialize()
      solver = delivery_solver_dict[solver_id](self, *args, **kw)
      return solver

    def applyDeliverySolver(self, movement, solver):
      """
        Update values of simulation movements based on delivery
        target values and solver.

        movement  --  a delivery line or cell

        solver    --  a delivery solver
      """
      if not self.isInitialized(): self.initialize()
      solver.solve(movement)

    def newTargetSolver(self, solver_id, *args, **kw):
      """
        Returns a solver instance
      """
      if not self.isInitialized(): self.initialize()
      solver = target_solver_dict[solver_id](self, *args, **kw)
      return solver

    def applyTargetSolver(self, movement, solver, new_target=None):
      """
        Update upper targets based on new targets

        movement  --  a simulation movement

        solver    --  a target solver

        new_target--  new target values for that movement
      """
      if new_target is None:
        # Default behaviour is to solve target based on
        # target defined by Delivery
        # it must be overriden in recursive upward update
        # to make sure
        new_target = Target(target_quantity = movement.getQuantity(),
                            target_start_date = movement.getStartDate(),
                            target_stop_date = movement.getStopDate())
      if not self.isInitialized(): self.initialize()
      solver.solve(movement, new_target)

    def closeTargetSolver(self, solver):
      return solver.close()

    def showTargetSolver(self, solver):
      LOG("SimulationTool",0,"in showTargetSolver")
      return str(solver.__dict__)


    #######################################################
    # Stock Management
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventory')
    def getInventory(self, resource_uid=None, at_date = None, section = None, node = None,
            node_category=None, section_category=default_section_category, simulation_state=None,
            ignore_variation=0, **kw):
      result = self.Resource_zGetInventory(resource_uid = resource_uid,
                                           to_date=at_date,
                                           section=section, node=node,
                                           node_category=node_category,
                                           section_category=section_category)
      if len(result) > 0:
        return result[0].inventory
      return 0.0

    #######################################################
    # Movement Group Collection / Delivery Creation
    def collectMovement(self, movement_list):

      class RootGroup:

        def __init__(self,movement=None):
          self.movement_list = []
          self.group_list = []
          if movement is not None :
            self.append(movement)

        def appendGroup(self, movement):
          self.group_list.append(OrderGroup(movement))

        def append(self,movement):
          self.movement_list.append(movement)
          movement_in_group = 0
          for group in self.group_list :
            if group.test(movement) :
              group.append(movement)
              movement_in_group = 1
              break
          if movement_in_group == 0 :
            self.appendGroup(movement)

      class OrderGroup(RootGroup):

        def __init__(self,movement):
          RootGroup.__init__(self,movement)
          order_value = movement.getRootAppliedRule().getCausalityValue(
                                                      portal_type=order_type_list)
          if order_value is None:
            order_relative_url = None
          else:
            # get the id of the enclosing delivery
            # for this cell or line
            order_relative_url = order_value.getRelativeUrl()
          self.order = order_relative_url

        def appendGroup(self, movement):
          self.group_list.append(PathGroup(movement))

        def test(self,movement):
          order_value = movement.getRootAppliedRule().getCausalityValue(
                                                      portal_type=order_type_list)
          if order_value is None:
            order_relative_url = None
          else:
            # get the id of the enclosing delivery
            # for this cell or line
            order_relative_url = order_value.getRelativeUrl()
          if order_relative_url == self.order:
            return 1
          else :
            return 0

      class PathGroup(RootGroup):

        def __init__(self,movement):
          RootGroup.__init__(self,movement)
          self.source = movement.getSource()
          self.destination = movement.getDestination()
          self.source_section = movement.getSourceSection()
          self.destination_section = movement.getDestinationSection()

        def appendGroup(self, movement):
          self.group_list.append(DateGroup(movement))

        def test(self,movement):
          if movement.getSource() == self.source and \
            movement.getDestination() == self.destination and \
            movement.getSourceSection() == self.source_section and \
            movement.getDestinationSection() == self.destination_section :
            return 1
          else :
            return 0

      class DateGroup(RootGroup):

        def __init__(self,movement):
          RootGroup.__init__(self,movement)
          self.target_start_date = movement.getTargetStartDate()
          self.target_stop_date = movement.getTargetStopDate()
          self.start_date = movement.getStartDate()
          self.stop_date = movement.getStopDate()

        def appendGroup(self, movement):
          self.group_list.append(ResourceGroup(movement))

        def test(self,movement):
          if movement.getStartDate() == self.start_date and \
            movement.getStopDate() == self.stop_date :
            return 1
          else :
            return 0

      class ResourceGroup(RootGroup):

        def __init__(self,movement):
          RootGroup.__init__(self,movement)
          self.resource = movement.getResource()

        def appendGroup(self, movement):
          self.group_list.append(VariantGroup(movement))

        def test(self,movement):
          if movement.getResource() == self.resource :
            return 1
          else :
            return 0

      class VariantGroup(RootGroup):

        def __init__(self,movement):
          RootGroup.__init__(self,movement)
          self.category_list = movement.getVariationCategoryList()

        def appendGroup(self, movement):
          pass

        def test(self,movement):
          # we must have the same number of categories
          categories_identity = 0
          if len(self.category_list) == len(movement.getVariationCategoryList()) :
            for category in movement.getVariationCategoryList() :
              if not category in self.category_list :
                break
            else :
              categories_identity = 1
          return categories_identity

      my_root_group = RootGroup()
      for movement in movement_list :
        if not movement in my_root_group.movement_list :
          my_root_group.append(movement)

      return my_root_group

    def buildOrderList(self, movement_group):
      # Build orders from a list of movements (attached to orders)
      order_list = []

      if movement_group is not None:
        for order_group in movement_group.group_list:
          if order_group.order is None:
            # Only build if there is not order yet
            for path_group in order_group.group_list :
              if path_group.destination.find('site/Stock_PF') >=0 :
                # Build a Production Order
                delivery_module = self.ordre_fabrication
                delivery_type = 'Production Order'
                delivery_line_type = delivery_type + ' Line'
                delivery_cell_type = 'Delivery Cell'
              else:
                # Build a Purchase Order
                delivery_module = self.commande_achat
                delivery_type = 'Purchase Order'
                delivery_line_type = delivery_type + ' Line'
                delivery_cell_type = 'Delivery Cell'
              # we create a new delivery for each DateGroup
              for date_group in path_group.group_list :

                for resource_group in date_group.group_list :

                  # Create a new production Order for each resource (Modele)
                  modele_url_items = resource_group.resource.split('/')
                  modele_id = modele_url_items[len(modele_url_items)-1]
                  try :
                    modele_object = self.getPortalObject().modele[modele_id]
                  except :
                    modele_object = None
                  if modele_object is not None :
                    of_description = modele_id + ' ' + modele_object.getDefaultDestinationTitle('')
                  else :
                    of_description = modele_id

                  new_delivery_id = str(delivery_module.generateNewId())
                  self.portal_types.constructContent(type_name = delivery_type,
                                                      container = delivery_module,
                                                      id = new_delivery_id,
                                                      target_start_date = date_group.start_date,
                                                      target_stop_date = date_group.stop_date,
                                                      start_date = date_group.start_date,
                                                      stop_date = date_group.stop_date,
                                                      source = path_group.source,
                                                      destination = path_group.destination,
                                                      source_section = path_group.source_section,
                                                      destination_section = path_group.destination_section,
                                                      description = of_description,
                                                      title = "Auto Planned"
                                                    )
                  delivery = delivery_module[new_delivery_id]
                  # the new delivery is added to the order_list
                  order_list.append(delivery)

                  # Create each delivery_line in the new delivery

                  new_delivery_line_id = str(delivery.generateNewId())
                  self.portal_types.constructContent(type_name = delivery_line_type,
                  container = delivery,
                  id = new_delivery_line_id,
                  resource = resource_group.resource,
                  )
                  delivery_line = delivery[new_delivery_line_id]

                  line_variation_category_list = []
                  line_variation_base_category_dict = {}

                  # compute line_variation_base_category_list and
                  # line_variation_category_list for new delivery_line
                  for variant_group in resource_group.group_list :
                    for variation_item in variant_group.category_list :
                      if not variation_item in line_variation_category_list :
                        line_variation_category_list.append(variation_item)
                        variation_base_category_items = variation_item.split('/')
                        if len(variation_base_category_items) > 0 :
                          line_variation_base_category_dict[variation_base_category_items[0]] = 1

                  # update variation_base_category_list and line_variation_category_list for delivery_line
                  line_variation_base_category_list = line_variation_base_category_dict.keys()
                  delivery_line.setVariationBaseCategoryList(line_variation_base_category_list)
                  delivery_line.setVariationCategoryList(line_variation_category_list)

                  # IMPORTANT : delivery cells are automatically created during setVariationCategoryList

                  # update target_quantity for each delivery_cell
                  for variant_group in resource_group.group_list :
                    object_to_update = None
                    # if there is no variation of the resource, update delivery_line with quantities and price
                    if len(variant_group.category_list) == 0 :
                      object_to_update = delivery_line
                    # else find which delivery_cell is represented by variant_group
                    else :
                      categories_identity = 0
                      for delivery_cell in delivery_line.contentValues(filter={'portal_type':'Delivery Cell'}) :
                        if len(variant_group.category_list) == len(delivery_cell.getVariationCategoryList()) :
                          for category in delivery_cell.getVariationCategoryList() :
                            if not category in variant_group.category_list :
                              break
                          else :
                            categories_identity = 1

                        if categories_identity :
                          object_to_update = delivery_cell
                          break

                    # compute target_quantity, quantity and price for delivery_cell or delivery_line and
                    # build relation between simulation_movement and delivery_cell or delivery_line
                    if object_to_update is not None :
                      cell_target_quantity = 0
                      for movement in variant_group.movement_list :
                        cell_target_quantity += movement.getConvertedTargetQuantity()
                      # We do not create a relation or modifu anything
                      # since planification of this movement will create new applied rule
                      object_to_update.edit(target_quantity = cell_target_quantity,
                                            quantity = cell_target_quantity,)

      return order_list

    def buildDeliveryList(self, movement_group):
      # Build deliveries from a list of movements

      delivery_list = []
      reindexable_movement_list = []

      if movement_group is not None:
        for order_group in movement_group.group_list:
          # Order should never be None
          if order_group.order is not None:
            order = self.portal_categories.resolveCategory(order_group.order)
            if order is not None:
              # define some variables
              if order.getPortalType() == 'Purchase Order' :
                delivery_module = order.getPortalObject().livraison_achat
                delivery_type = 'Purchase Packing List'
                delivery_line_type = delivery_type + ' Line'
                delivery_cell_type = 'Delivery Cell'
              else :
                delivery_module = order.getPortalObject().livraison_vente
                delivery_type = 'Sales Packing List'
                delivery_line_type = delivery_type + ' Line'
                delivery_cell_type = 'Delivery Cell'
            else:
              LOG("ERP5 Simulation", 100, "None order makes no sense")
              return delivery_list

            for path_group in order_group.group_list :
              # we create a new delivery for each DateGroup

              # if path is internal ???
              # JPS NEW
              if path_group.source is None or path_group.destination is None:
                # Production Path
                LOG("Builder",0, "Strange Path %s " % path_group.source)
                LOG("Builder",0, "Strange Path %s " % path_group.destination)

              if path_group.source is None or path_group.destination is None:
                delivery_module = self.rapport_fabrication
                delivery_type = 'Production Report'
                delivery_line_type = 'Production Report Line'
                delivery_cell_type = 'Production Report Cell'
              elif path_group.destination.find('site/Stock_PF') >= 0 and \
                  path_group.source.find('site/Piquage') >= 0:
                delivery_module = self.livraison_fabrication
                delivery_type = 'Production Packing List'
                delivery_line_type = delivery_type + ' Line'
                delivery_cell_type = 'Delivery Cell'
              elif path_group.source.find('site/Stock_MP') >= 0 and \
                  path_group.destination.find('site/Piquage') >= 0:
                delivery_module = self.livraison_fabrication
                delivery_type = 'Production Packing List'
                delivery_line_type = delivery_type + ' Line'
                delivery_cell_type = 'Delivery Cell'

              for date_group in path_group.group_list :

                # Create a new packing list
                new_delivery_id = str(delivery_module.generateNewId())
                self.portal_types.constructContent(type_name = delivery_type,
                                          container = delivery_module,
                                          id = new_delivery_id,
                                          title = order.getTitle(),
                                          causality_value = order,
                                          incoterm = order.getIncoterm(),
                                          delivery_mode = order.getDeliveryMode(),
                                          target_start_date = date_group.start_date,
                                          target_stop_date = date_group.stop_date,
                                          start_date = date_group.start_date,
                                          stop_date = date_group.stop_date,
                                          source = path_group.source,
                                          destination = path_group.destination,
                                          source_section = path_group.source_section,
                                          destination_section = path_group.destination_section
                                          )
                delivery = delivery_module[new_delivery_id]
                # the new delivery is added to the delivery_list
                delivery_list.append(delivery)
        #        LOG('Livraison créée',0,str(delivery.getId()))

                # Create each delivery_line in the new delivery

                for resource_group in date_group.group_list :
                  if delivery_type == 'Production Report':
                    if resource_group.resource.find('operation') == 0:
                      delivery_line_type = 'Production Report Operation'
                    else:
                      delivery_line_type = 'Production Report Component'

                  new_delivery_line_id = str(delivery.generateNewId())
                  self.portal_types.constructContent(type_name = delivery_line_type,
                  container = delivery,
                  id = new_delivery_line_id,
                  resource = resource_group.resource,
                  )
                  delivery_line = delivery[new_delivery_line_id]
                  #LOG('Ligne créée',0,str(delivery_line.getId())+' '+str(delivery_line.getResource()))

                  line_variation_category_list = []
                  line_variation_base_category_dict = {}

                  # compute line_variation_base_category_list and
                  # line_variation_category_list for new delivery_line
                  for variant_group in resource_group.group_list :
                    for variation_item in variant_group.category_list :
                      if not variation_item in line_variation_category_list :
                        line_variation_category_list.append(variation_item)
                        variation_base_category_items = variation_item.split('/')
                        if len(variation_base_category_items) > 0 :
                          line_variation_base_category_dict[variation_base_category_items[0]] = 1

                  # update variation_base_category_list and line_variation_category_list for delivery_line
                  line_variation_base_category_list = line_variation_base_category_dict.keys()
                  delivery_line._setVariationBaseCategoryList(line_variation_base_category_list)
                  delivery_line.setVariationCategoryList(line_variation_category_list)

                  # IMPORTANT : delivery cells are automatically created during setVariationCategoryList

                  # update target_quantity for each delivery_cell
                  for variant_group in resource_group.group_list :
                    #LOG('Variant_group examin?,0,str(variant_group.category_list))
                    object_to_update = None
                    # if there is no variation of the resource, update delivery_line with quantities and price
                    if len(variant_group.category_list) == 0 :
                      object_to_update = delivery_line
                    # else find which delivery_cell is represented by variant_group
                    else :
                      categories_identity = 0
                      #LOG('Before Check cell',0,str(delivery_cell_type))
                      #LOG('Before Check cell',0,str(delivery_line.contentValues()))
                      for delivery_cell in delivery_line.contentValues(
                                                            filter={'portal_type':delivery_cell_type}) :
                        #LOG('Check cell',0,str(delivery_cell))
                        if len(variant_group.category_list) == len(delivery_cell.getVariationCategoryList()) :
                          #LOG('Parse category',0,str(delivery_cell.getVariationCategoryList()))
                          for category in delivery_cell.getVariationCategoryList() :
                            if not category in variant_group.category_list :
                              #LOG('Not found category',0,str(category))
                              break
                          else :
                            categories_identity = 1

                        if categories_identity :
                          object_to_update = delivery_cell
                          break

                    # compute target_quantity, quantity and price for delivery_cell or delivery_line and
                    # build relation between simulation_movement and delivery_cell or delivery_line
                    if object_to_update is not None :
                      cell_target_quantity = 0
                      cell_total_price = 0
                      for movement in variant_group.movement_list :
                        cell_target_quantity += movement.getNetConvertedTargetQuantity()
                        try:
                          cell_total_price += movement.getNetConvertedTargetQuantity()*movement.getPrice() # XXX WARNING - ADD PRICED QUANTITY
                        except:
                          cell_total_price = None

                        # update every simulation_movement
                        # we set delivery_value and target dates and quantity
                        movement._setDeliveryValue(object_to_update)
                        movement._setTargetQuantity(movement.getTargetQuantity())
                        movement._setQuantity(movement.getTargetQuantity())
                        movement._setEfficiency(movement.getTargetEfficiency())
                        movement._setTargetStartDate(movement.getTargetStartDate())
                        movement._setTargetStopDate(movement.getTargetStopDate())
                        movement._setStartDate(movement.getTargetStartDate())
                        movement._setStopDate(movement.getTargetStopDate())
                        # We will reindex later
                        reindexable_movement_list.append(movement)

                      if cell_target_quantity <> 0 and cell_total_price is not None:
                        average_price = cell_total_price/cell_target_quantity
                      else :
                        average_price = 0
                      #LOG('object mis ?jour',0,str(object_to_update.getRelativeUrl()))
                      object_to_update.edit(target_quantity = cell_target_quantity,
                                            quantity = cell_target_quantity,
                                            price = average_price,
                                            )

      # If we reach this point, it means we could
      # create deliveries
      # get_transaction().commit()
      # DO NOT USE COMMIT BECAUSE OF WORKFLOW

      # Now, let us index what must be indexed
      # Since we comitted changes, there should be no risk of conflict
      for movement in reindexable_movement_list:
        movement.reindexObject() # we do it now because we need to
                                 # update category relation

      # Now return deliveries which were created
      return delivery_list

    #######################################################
    # Capacity Management
    security.declareProtected( Permissions.ModifyPortalContent, 'updateCapacity' )
    def updateCapacity(self, node):
      capacity_item_list = []
      for o in node.contentValues():
        if o.isCapacity():
          # Do whatever is needed
          capacity_item_list += o.asCapacityItemList()
          pass
      # Do whatever with capacity_item_list
      # and store the resulting new capacity in node
      node._capacity_item_list = capacity_item_list

    security.declareProtected( Permissions.ModifyPortalContent, 'isMovementInsideCapacity' )
    def isMovementInsideCapacity(self, movement):
      """
        Purpose: provide answer to customer for the question "can you do it ?"

        movement:
          date
          source destination (2 nodes)
          source_section ...
      """
      # Get nodes and dat
      source_node = movement.getSourceValue()
      destination_node = movement.getDestinationValue()
      start_date = movement.getTargetStartDate()
      stop_date = movement.getTargetStopDate()
      # Return result
      return self.isNodeInsideCapacity(source_node, start_date, additional_movement=movement, sign=1) and self.isNodeInsideCapacity(destination_node, stop_date, additional_movement=movement, sign=-1)

    security.declareProtected( Permissions.ModifyPortalContent, 'isNodeInsideCapacity' )
    def isNodeInsideCapacity(self, node, date, simulation_state=None, additional_movement=None, sign=1):
      """
        Purpose: decide if a node is consistent with its capacity definitions
        at a certain date (ie. considreing the stock / production history
      """
      # First get the current inventory situation for this node
      inventory_list = node.getInventoryList(XXXXX)
      # Add additional movement
      if additional_movement:
          inventory_list = inventory_list + sign * additional_movement # needs to be implemented
      # Return answer
      return self.isAmountListInsideCapacity(node, inventory_list)

    security.declareProtected( Permissions.ModifyPortalContent, 'isAmountListInsideCapacity' )
    def isAmountListInsideCapacity(self, node, amount_list,
         resource_aggregation_base_category=None, resource_aggregation_depth=None):
      """
        Purpose: decide if a list of amounts is consistent with the capacity of a node

        If any resource in amount_list is missing in the capacity of the node, resource
        aggregation is performed, based on resource_aggregation_base_category. If the
        base category is not specified, it is an error (should guess instead?). The resource
        aggregation is done at the level of resource_aggregation_depth in the tree
        of categories. If resource_aggregation_depth is not specified, it's an error.

        Assumptions: amount_list is an association list, like ((R1 V1) (R2 V2)).
                     node has an attribute '_capacity_item_list' which is a list of association lists.
                     resource_aggregation_base_category is a Base Category object or a list of Base
                     Category objects or None.
                     resource_aggregation_depth is a strictly positive integer or None.
      """
      # Make a copy of the attribute _capacity_item_list, because it may be necessary
      # to modify it for resource aggregation.
      capacity_item_list = node._capacity_item_list[:]

      # Make a mapping between resources and its indices.
      resource_map = {}
      index = 0
      for alist in capacity_item_list:
        for pair in alist:
          resource = pair[0]
#          LOG('isAmountListInsideCapacity', 0,
#              "resource is %s" % repr(resource))
          if resource not in resource_map:
            resource_map[resource] = index
            index += 1

      # Build a point from the amount list.
      point = zeros(index, 'd') # Fill up zeros for safety.
      mask_map = {}     # This is used to skip items in amount_list.
      for amount in amount_list:
        if amount[0] in mask_map:
          continue
        # This will fail, if amount_list has any different resource from the capacity.
        # If it has any different point, then we should ......
        #
        # There would be two possible different solutions:
        # 1) If a missing resource is a meta-resource of resources supported by the capacity,
        #    it is possible to add the resource into the capacity by aggregation.
        # 2) If a missing resource has a meta-resource as a parent and the capacity supports
        #    the meta-resource directly or indirectly (`indirectly' means `by aggregation'),
        #    it is possible to convert the missing resource into the meta-resource.
        #
        # However, another way has been implemented here. This does the following, if the resource
        # is not present in the capacity:
        # 1) If the value is zero, just ignore the resource, because zero is always acceptable.
        # 2) Attempt to aggregate resources both of the capacity and of the amount list. This aggregation
        #    is performed at the depth of 'resource_aggregation_depth' under the base category
        #    'resource_aggregation_base_category'.
        #
        resource = amount[0]
        if resource in resource_map:
          point[resource_map[amount[0]]] = amount[1]
        else:
          if amount[1] == 0:
            # If the value is zero, no need to consider.
            pass
          elif resource_aggregation_base_category is None or resource_aggregation_depth is None:
            # XXX use an appropriate error class
            # XXX should guess a base category instead of emitting an exception
            raise RuntimeError, "The resource '%s' is not found in the capacity, and the argument 'resource_aggregation_base_category' or the argument 'resource_aggregation_depth' is not specified" % resource
          else:
            # It is necessary to aggregate resources, to guess the capacity of this resource.

            def getAggregationResourceUrl(url, depth):
              # Return a partial url of the argument 'url'.
              # If 'url' is '/foo/bar/baz' and 'depth' is 2, return '/foo/bar'.
              pos = 0
              for i in range(resource_aggregation_depth):
                pos = url.find('/', pos+1)
                if pos < 0:
                  break
              if pos < 0:
                return None
              pos = url.find('/', pos+1)
              if pos < 0:
                pos = len(url)
              return url[:pos]

            def getAggregatedResourceList(aggregation_url, category, resource_list):
              # Return a list of resources which should be aggregated. 'aggregation_url' is used
              # for a top url of those resources. 'category' is a base category for the aggregation.
              aggregated_resource_list = []
              for resource in resource_list:
                for url in resource.getCategoryMembershipList(category, base=1):
                  if url.startswith(aggregation_url):
                    aggregated_resource_list.append(resource)
              return aggregated_resource_list

            def getAggregatedItemList(item_list, resource_list, aggregation_resource):
              # Return a list of association lists, which is a result of an aggregation.
              # 'resource_list' is a list of resources which should be aggregated.
              # 'aggregation_resource' is a category object which is a new resource created by
              # this aggregation.
              # 'item_list' is a list of association lists.
              new_item_list = []
              for alist in item_list:
                new_val = 0
                new_alist = []
                # If a resource is not a aggregated, then add it to the new alist as it is.
                # Otherwise, aggregate it to a single value.
                for pair in alist:
                  if pair[0] in resource_list:
                    new_val += pair[1]
                  else:
                    new_alist.append(pair)
                # If it is zero, ignore this alist, as it is nonsense.
                if new_val != 0:
                  new_alist.append([aggregation_resource, new_val])
                  new_item_list.append(new_alist)
              return new_item_list

            # Convert this to a string if necessary, for convenience.
            if type(resource_aggregation_base_category) not in (type([]), type(())):
              resource_aggregation_base_category = (resource_aggregation_base_category,)

            done = 0
#            LOG('isAmountListInsideCapacity', 0,
#                "resource_aggregation_base_category is %s" % repr(resource_aggregation_base_category))
            for category in resource_aggregation_base_category:
              for resource_url in resource.getCategoryMembershipList(category, base=1):
                aggregation_url = getAggregationResourceUrl(resource_url,
                                                            resource_aggregation_depth)
                if aggregation_url is None:
                  continue
                aggregated_resource_list = getAggregatedResourceList (aggregation_url,
                                                                      category,
                                                                      resource_map.keys())
                # If any, do the aggregation.
                if len(aggregated_resource_list) > 0:
                  aggregation_resource = self.portal_categories.resolveCategory(aggregation_url)
                  # Add the resource to the mapping.
 #                 LOG('aggregation_resource', 0, str(aggregation_resource))
                  resource_map[aggregation_resource] = index
                  index += 1
                  # Add the resource to the point.
                  point = resize(point, (index,))
                  val = 0
                  for aggregated_amount in amount_list:
                    for url in aggregated_amount[0].getCategoryMembershipList(category, base=1):
                      if url.startswith(aggregation_url):
                        val += aggregated_amount[1]
                        mask_map[aggregated_amount[0]] = None
                        break
                  point[index-1] = val
                  # Add capacity definitions of the resource into the capacity.
                  capacity_item_list += getAggregatedItemList(capacity_item_list,
                                                              aggregated_resource_list,
                                                              aggregation_resource)
                  done = 1
                  break
              if done:
                break
            if not done:
              raise RuntimeError, "Aggregation failed"

      # Build a matrix from the capacity item list.
#      LOG('resource_map', 0, str(resource_map))
      matrix = zeros((len(capacity_item_list)+1, index), 'd')
      for index in range(len(capacity_item_list)):
        for pair in capacity_item_list[index]:
          matrix[index,resource_map[pair[0]]] = pair[1]

#      LOG('isAmountListInsideCapacity', 0,
#          "matrix = %s, point = %s, capacity_item_list = %s" % (str(matrix), str(point), str(capacity_item_list)))
      return solve(matrix, point)


    # Asset Price Calculation
    def updateAssetPrice(self, resource, variation_text, section_category, node_category,
                         strict_membership=0, simulation_state=current_inventory_state_list):
      section_value = self.portal_categories.resolveCategory(section_category)
      node_value = self.portal_categories.resolveCategory(node_category)
      # Initialize price
      current_asset_price = 0.0 # Missing: initial inventory price !!!
      current_inventory = 0.0
      # Parse each movement
      for b in self.Resource_zGetMovementHistoryList(resource=[resource],
                             variation_text=variation_text,
                             section_category=section_category,
                             node_category=node_category,
                             strict_membership=strict_membership,
                             simulation_state=simulation_state): # strict_membership not taken into account
        m = b.getObject()
        result = []
        update_source = 0
        update_destination = 0
        if m is not None:
            previous_inventory = current_inventory
            quantity = m.getQuantity()
            if quantity is None:
              quantity = 0.0
            if m.getSourceValue() is None:
              # This is a production movement
              # Use Industrial Price
              current_inventory += quantity # Update inventory
              asset_price = 0.0
              # asset_price = m.getIndustrialPrice()
              result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                             m.getQuantity(), 'Production or Inventory', 'Price: %s' % asset_price
                           ))
              update_source = 0
              update_destination = 1
            elif m.getDestinationValue() is None:
              # This is a consumption movement - do nothing
              current_inventory += quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                             m.getQuantity(), 'Consumption or Inventory', 'Price: %s' % asset_price
                           ))
              update_source = 1
              update_destination = 0
            elif m.getSourceValue().isMemberOf(node_category) and m.getDestinationValue().isMemberOf(node_category):
              # This is an internal movement - do nothing
              current_inventory += quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                             m.getQuantity(), 'Internal', 'Price: %s' % asset_price
                           ))
              update_source = 1
              update_destination = 1
            elif m.getSourceValue().isMemberOf(node_category) and quantity < 0:
              # This is a physically inbound movement - try to use commercial price
              if m.getSourceSectionValue() is None:
                # No meaning
                current_inventory += quantity # Update inventory
                asset_price = current_asset_price
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Error', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 1
              elif m.getDestinationSectionValue() is None:
                # No meaning
                current_inventory += quantity # Update inventory
                asset_price = current_asset_price
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Error', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 1
              elif m.getDestinationSectionValue().isMemberOf(section_category):
                # Inbound from same section
                current_inventory += quantity # Update inventory
                asset_price = current_asset_price
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Inbound same section', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 1
              else:
                current_inventory += quantity # Update inventory
                asset_price = m.getPrice()
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Inbound different section', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 0
            elif m.getDestinationValue().isMemberOf(node_category) and quantity > 0:
              # This is a physically inbound movement - try to use commercial price
              # This is a physically inbound movement - try to use commercial price
              if m.getSourceSectionValue() is None:
                # No meaning
                current_inventory += quantity # Update inventory
                asset_price = current_asset_price
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Error', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 1
              elif m.getDestinationSectionValue() is None:
                # No meaning
                current_inventory += quantity # Update inventory
                asset_price = current_asset_price
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Error', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 1
              elif m.getSourceSectionValue().isMemberOf(section_category):
                # Inbound from same section
                current_inventory += quantity # Update inventory
                asset_price = current_asset_price
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Inbound same section', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 1
              else:
                current_inventory += quantity # Update inventory
                asset_price = m.getPrice()
                result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Inbound different section', 'Price: %s' % asset_price
                             ))
                update_source = 1
                update_destination = 0
            else:
              # Outbound movement
              current_inventory += quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                               m.getQuantity(), 'Outbound', 'Price: %s' % asset_price
                             ))
              if quantity > 0:
                update_source = 0
                update_destination = 1
              else:
                update_source = 1
                update_destination = 0

            # Update asset_price
            if current_inventory > 0:
              # Update price with an average of incoming goods and current goods
              current_asset_price = ( current_asset_price * previous_inventory + asset_price * quantity ) / float(current_inventory)
            else:
              # New price is the price of incoming goods - negative stock has no meaning for asset calculation
              current_asset_price = asset_price

            # Update Asset Price on the right side
            if update_source:
              m.setSourceAssetPrice(current_asset_price)
            if update_destination:
              m.setDestinationAssetPrice(current_asset_price)

        return result

InitializeClass(SimulationTool)
