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

from Products.CMFCore.utils import UniqueObject

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type import Permissions
from Products.ERP5Type.Tool.BaseTool import BaseTool

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
    #LOG('Register Solver', 0, str(solver.__name__))
    delivery_solver_list.append(solver)
    delivery_solver_dict[solver.__name__] = solver

target_solver_dict = {}
target_solver_list = []

def registerTargetSolver(solver):
    global target_solver_list, target_solver_dict
    #LOG('Register Solver', 0, str(solver.__name__))
    target_solver_list.append(solver)
    target_solver_dict[solver.__name__] = solver

class Target:

  def __init__(self, **kw):
    """
      Defines a target (target_quantity, start_date, stop_date)
    """
    self.__dict__.update(kw)

class SimulationTool (BaseTool):
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
    portal_type = 'Simulation Tool'
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
    #def __init__(self):
    #    return Folder.__init__(self, SimulationTool.id)

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
      from Products.ERP5.TargetSolver import Reduce, Defer, SplitAndDefer, CopyToTarget, Redirect
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
                            target_stop_date = movement.getStopDate(),
                            target_destination = movement.getDestination(),
                            target_destination_section = movement.getDestinationSection(),
                            target_source = movement.getSource(),
                            target_source_section = movement.getSourceSection())

      if not self.isInitialized(): self.initialize()
      solver.solve(movement, new_target)

    def closeTargetSolver(self, solver):
      return solver.close()

    def showTargetSolver(self, solver):
      #LOG("SimulationTool",0,"in showTargetSolver")
      return str(solver.__dict__)


    #######################################################
    # Stock Management
    security.declareProtected(Permissions.AccessContentsInformation, 'getInventory')
    def getInventory(self, resource_uid=None, at_date = None, section = None, node = None,
            node_category=None, section_category=None, simulation_state=None,
            ignore_variation=0, **kw):
      if section_category is None:
        section_category = self.getPortalDefaultSectionCategory()
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
    def collectMovement(self, movement_list,class_list=None,**kw):
      """
      group movements in the way we want. Thanks to this method, we are able to retrieve
      movement classed by order, resource, criterion,....

      movement_list : the list of movement wich we want to group

      check_list : the list of classes used to group movements. The order
                   of the list is important and determines by what we will
                   group movement first
                   Typically, check_list is :
                   [DateMovementGroup,PathMovementGroup,...]
      """
      s_tool = self.portal_simulation
      from Products.ERP5.MovementGroup import OrderMovementGroup, PathMovementGroup
      from Products.ERP5.MovementGroup import DateMovementGroup, ResourceMovementGroup
      from Products.ERP5.MovementGroup import VariantMovementGroup, RootMovementGroup
      if class_list is None:
        # For compatibility reasons, by default we keep the previous order
        class_list = [OrderMovementGroup,PathMovementGroup,DateMovementGroup,
                      ResourceMovementGroup,VariantMovementGroup]
      my_root_group = RootMovementGroup(class_list=class_list)
      for movement in movement_list:
        if not movement in my_root_group.movement_list :
          my_root_group.append(movement,class_list=class_list)

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
                                                      target_source = path_group.source,
                                                      target_destination = path_group.destination,
                                                      target_source_section = path_group.source_section,
                                                      target_destination_section = path_group.destination_section,
                                                      description = of_description,
                                                      title = new_delivery_id
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
                    #LOG('Variant_group examin',0,str(variant_group.category_list))
                    object_to_update = None
                    # if there is no variation of the resource, update delivery_line with quantities and price
                    if len(variant_group.category_list) == 0 :
                      object_to_update = delivery_line
                    # else find which delivery_cell is represented by variant_group
                    else :
                      categories_identity = 0
                      #LOG('Before Check cell',0,str(delivery_cell_type))
                      #LOG('Before Check cell',0,str(delivery_line.contentValues()))
                      for delivery_cell in delivery_line.contentValues(filter={'portal_type':'Delivery Cell'}) :
                        #LOG('Check cell',0,str(delivery_cell))
                        #LOG('Check cell',0,str(variant_group.category_list))
                        #LOG('Check cell',0,str(delivery_cell.getVariationCategoryList()))
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
                      for movement in variant_group.movement_list :
                        cell_target_quantity += movement.getConvertedTargetQuantity()
                      # We do not create a relation or modifu anything
                      # since planification of this movement will create new applied rule
                      object_to_update.edit(target_quantity = cell_target_quantity,
                                            quantity = cell_target_quantity,
                                            force_update = 1)

      return order_list





    def buildDeliveryList(self, movement_group):
      # Build deliveries from a list of movements
      LOG('buildDeliveryList root_group',0,movement_group)
      LOG('buildDeliveryList root_group.__dict__',0,movement_group.__dict__)
      for group in movement_group.group_list:
        LOG('buildDeliveryList group.__dict__',0,group.__dict__)
      LOG('buildDeliveryList nested_class.__dict__',0,movement_group.nested_class.__dict__)


      def orderGroupProcessing(order_group, delivery_list, reindexable_movement_list, **kw):

        # Order should never be None
        LOG("buildDeliveryList", 0, str(order_group.__dict__))
        if order_group.order is not None:
          order = self.portal_categories.resolveCategory(order_group.order)
          if order is not None:
            # define some variables
            LOG("order", 0, str(order.__dict__))
            if order.getPortalType() == 'Purchase Order' :
              delivery_module = order.getPortalObject().livraison_achat
              delivery_type = 'Purchase Packing List'
              delivery_line_type = delivery_type + ' Line'
              delivery_cell_type = 'Delivery Cell'
            elif order.getPortalType() == 'Sale Order' :
              delivery_module = order.getPortalObject().sale_packing_list
              delivery_type = 'Sale Packing List'
              delivery_line_type = delivery_type + ' Line'
              delivery_cell_type = 'Delivery Cell'
            else :
              delivery_module = order.getPortalObject().livraison_vente
              delivery_type = 'Sales Packing List'
              delivery_line_type = delivery_type + ' Line'
              delivery_cell_type = 'Delivery Cell'
          else : # should never be none
            LOG("order is None", 0, str(order.__dict__))
            return -1
        else: # order is None
          order = None
          # possible when we build deliveries for tranfer of property
          delivery_module = self.getPortalObject().livraison_vente
          delivery_type = 'Sales Packing List'
          delivery_line_type = delivery_type + ' Line'
          delivery_cell_type = 'Delivery Cell'

        for path_group in order_group.group_list:
          pathGroupProcessing(path_group=path_group,
                              delivery_module=delivery_module,
                              delivery_type=delivery_type,
                              delivery_line_type=delivery_line_type,
                              delivery_cell_type=delivery_cell_type,
                              order=order,
                              delivery_list=delivery_list,
                              reindexable_movement_list=reindexable_movement_list, **kw)

        return 0


      def pathGroupProcessing(path_group, delivery_module, delivery_type, delivery_line_type, delivery_cell_type, order, delivery_list, reindexable_movement_list, default_rule_id=None, **kw):
        # we create a new delivery for each DateGroup


        if default_rule_id is 'default_amortisation_rule':
          pass
        else:
          # if path is internal ???
          # JPS NEW
          if path_group.target_source is None or path_group.target_destination is None:
            # Production Path
            LOG("Builder",0, "Strange Path %s " % path_group.target_source)
            LOG("Builder",0, "Strange Path %s " % path_group.target_destination)
          LOG("Builder path_group in pathGroupProcessing",0, path_group.__dict__)

          
          if path_group.target_source is None or path_group.target_destination is None:
            pass
            #delivery_module = self.rapport_fabrication
            #delivery_type = 'Production Report'
            #delivery_line_type = 'Production Report Line'
            #delivery_cell_type = 'Production Report Cell'
          elif path_group.target_destination.find('site/Stock_PF') >= 0 and \
              path_group.target_source.find('site/Piquage') >= 0:
            delivery_module = self.livraison_fabrication
            delivery_type = 'Production Packing List'
            delivery_line_type = delivery_type + ' Line'
            delivery_cell_type = 'Delivery Cell'
          elif path_group.target_source.find('site/Stock_MP') >= 0 and \
              path_group.target_destination.find('site/Piquage') >= 0:
            delivery_module = self.livraison_fabrication
            delivery_type = 'Production Packing List'
            delivery_line_type = delivery_type + ' Line'
            delivery_cell_type = 'Delivery Cell'

          for date_group in path_group.group_list :
            dateGroupProcessing(date_group=date_group,
                                path_group=path_group,
                                delivery_module=delivery_module,
                                delivery_type=delivery_type,
                                delivery_line_type=delivery_line_type,
                                delivery_cell_type=delivery_cell_type,
                                order=order,
                                delivery_list=delivery_list,
                                reindexable_movement_list=reindexable_movement_list,
                                default_rule_id=default_rule_id, **kw)


      def dateGroupProcessing(date_group, path_group, delivery_module, delivery_type, delivery_line_type, delivery_cell_type, order, delivery_list, reindexable_movement_list, default_rule_id=None, resource=None, **kw):

        if default_rule_id == 'default_amortisation_rule':
          accounting_transaction_data_list = {}

          for path_group in date_group.group_list:
            source_section = path_group.source_section
            destination_section = path_group.destination_section
            source = path_group.source
            destination = path_group.destination

            accounting_transaction_data = accounting_transaction_data_list.get( (source_section, destination_section), None)
            if accounting_transaction_data is None:
              accounting_transaction_data_list[ (source_section, destination_section) ] = {}
              accounting_transaction_data = accounting_transaction_data_list.get( (source_section, destination_section), None)
            quantity = 0
            source_movement_list = []

            for movement in path_group.movement_list:
              if movement.getDeliveryValue() is None:
                quantity += movement.getQuantity()
                source_movement_list.append(movement)
                LOG('buildDeliveryList :', 0, 'adding movement %s : quantity = %s' % (repr(movement), repr(movement.getQuantity())))
              else:
                LOG('buildDeliveryList :', 0, 'movement %s... delivery value = %s' % (repr(movement), repr(movement.getDeliveryValue())))

            accounting_transaction_data[ (source, destination) ] = (quantity, source_movement_list)
            if len(source_movement_list) == 0:
              LOG('buildDeliveryList :', 0, 'deleting transaction line because no source movement list... path_group.movement_list = %s' % repr(path_group.movement_list))
              del accounting_transaction_data[ (source, destination) ]

          for (source_section, destination_section), accounting_transaction_data in accounting_transaction_data_list.items():
            if len(accounting_transaction_data.items()) > 0:
              new_delivery_id = str(delivery_module.generateNewId())
              accounting_transaction = delivery_module.newContent(type_name = delivery_type,
                                                id = new_delivery_id,
                                                target_start_date = date_group.start_date,
                                                target_stop_date = date_group.stop_date,
                                                start_date = date_group.start_date,
                                                stop_date = date_group.stop_date,
                                                source_section = source_section,
                                                destination_section = destination_section
                                                )
              accounting_transaction.setResource(resource)
              for (source, destination), (quantity, source_movement_list) in accounting_transaction_data.items():
                new_transaction_line_id = str(accounting_transaction.generateNewId())
                accounting_transaction_line = accounting_transaction.newContent(type_name = delivery_line_type,
                                                  id = new_transaction_line_id,
                                                  source = source,
                                                  destination = destination)
                accounting_transaction_line = accounting_transaction[new_transaction_line_id]
                accounting_transaction_line.setQuantity(quantity)
                LOG('buildDeliveryList :', 0, 'setting resource for line %s... resource = %s' % (repr(accounting_transaction_line), repr(resource)))
                accounting_transaction_line.setResource(resource)
                for movement in source_movement_list:
                  LOG('buildDeliveryList :', 0, 'setting delivery value... movement = %s, accounting_transaction_line = %s' % (repr(movement), repr(accounting_transaction_line)))
                  movement.setDeliveryValue(accounting_transaction_line)
                  LOG('buildDeliveryList :', 0, 'after setting it, movement.delivery_value = %s' % repr(movement.getDeliveryValue()))
                  movement.recursiveImmediateReindexObject()

        else:
          # Create a new packing list
          new_delivery_id = str(delivery_module.generateNewId())
          delivery = delivery_module.newContent(type_name = delivery_type,
                                    id = new_delivery_id,
                                    target_start_date = date_group.start_date,
                                    target_stop_date = date_group.stop_date,
                                    start_date = date_group.start_date,
                                    stop_date = date_group.stop_date,
                                    source = path_group.source,
                                    destination = path_group.destination,
                                    source_section = path_group.source_section,
                                    destination_section = path_group.destination_section,
                                    target_source = path_group.source,
                                    target_destination = path_group.destination,
                                    target_source_section = path_group.source_section,
                                    target_destination_section = path_group.destination_section
                                    )
          if order is not None :
            delivery.edit(title = order.getTitle(),
                          causality_value = order,
                          incoterm = order.getIncoterm(),
                          delivery_mode = order.getDeliveryMode()
                          )
          # the new delivery is added to the delivery_list
          delivery_list.append(delivery)
  #        LOG('Livraison créée',0,str(delivery.getId()))

          # Create each delivery_line in the new delivery

          for resource_group in date_group.group_list :
            resourceGroupProcessing(resource_group=resource_group,
                                    delivery=delivery,
                                    delivery_type=delivery_type,
                                    delivery_line_type=delivery_line_type,
                                    delivery_cell_type=delivery_cell_type,
                                    delivery_list=delivery_list,
                                    reindexable_movement_list=reindexable_movement_list, **kw)


      def resourceGroupProcessing(resource_group, delivery, delivery_type, delivery_line_type, delivery_cell_type, delivery_list, reindexable_movement_list, delivery_module=None, default_rule_id=None, **kw):

        if default_rule_id == 'default_amortisation_rule':
          resource = resource_group.resource
          for date_group in resource_group.group_list:
            dateGroupProcessing(date_group=date_group,
                                path_group=None,
                                delivery_module=delivery_module,
                                delivery_type=delivery_type,
                                delivery_line_type=delivery_line_type,
                                delivery_cell_type=delivery_cell_type,
                                order=None,
                                delivery_list=delivery_list,
                                reindexable_movement_list=reindexable_movement_list,
                                default_rule_id=default_rule_id,
                                resource=resource)
        else:

          if delivery_type == 'Production Report':
            if resource_group.resource.find('operation') == 0:
              delivery_line_type = 'Production Report Operation'
            else:
              delivery_line_type = 'Production Report Component'

          #new_delivery_line_id = str(delivery.generateNewId())
          delivery_line = delivery.newContent(type_name = delivery_line_type,
                                              resource = resource_group.resource,
                                            )

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
          for variant_group in resource_group.group_list:
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
                LOG('SimulationTool, movement.getPhysicalPath',0,movement.getPhysicalPath())
                LOG('SimulationTool, movement.showDict',0,movement.showDict())
                cell_target_quantity += movement.getNetConvertedTargetQuantity()
                try:
                  cell_total_price += movement.getNetConvertedTargetQuantity()*movement.getPrice() # XXX WARNING - ADD PRICED QUANTITY
                except:
                  cell_total_price = None

                if movement.getPortalType() == 'Simulation Movement' :
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
                  movement._setSource(movement.getTargetSource())
                  movement._setDestination(movement.getTargetDestination())
                  movement._setTargetSource(movement.getTargetSource())
                  movement._setTargetDestination(movement.getTargetDestination())
                  movement._setSourceSection(movement.getTargetSourceSection())
                  movement._setDestinationSection(movement.getTargetDestinationSection())
                  movement._setTargetSourceSection(movement.getTargetSourceSection())
                  movement._setTargetDestinationSection(movement.getTargetDestinationSection())

                  # We will reindex later
                  reindexable_movement_list.append(movement)

              if cell_target_quantity <> 0 and cell_total_price is not None:
                average_price = cell_total_price/cell_target_quantity
              else :
                average_price = 0
              #LOG('object mis à jour',0,str(object_to_update.getRelativeUrl()))
              object_to_update._edit(target_quantity = cell_target_quantity,
                                    quantity = cell_target_quantity,
                                    price = average_price,
                                    force_update = 1,
                                    )



      delivery_list = []
      reindexable_movement_list = []


      if movement_group is not None:
        # Verify the rule used to build the movements
        default_rule_id = None
        if len(movement_group.movement_list) > 0:
          f = getattr(movement_group.movement_list[0], 'getRootAppliedRule', None)
          if f is not None:
            applied_rule = f()
            default_rule_id = applied_rule.getSpecialiseId()


        LOG('buildDeliveryList :', 0, 'default_rule = %s' % repr(default_rule_id))
        if default_rule_id == 'default_amortisation_rule':
          LOG('buildDeliveryList :', 0, 'default_rule is default_amortisation_rule')
          delivery_module = self.getPortalObject().accounting
          delivery_type = 'Amortisation Transaction'
          delivery_line_type = delivery_type + ' Line'
          delivery_cell_type = None

          for resource_group in movement_group.group_list:
            resourceGroupProcessing(resource_group=resource_group,
                                    delivery=None,
                                    delivery_module=delivery_module,
                                    delivery_type=delivery_type,
                                    delivery_line_type=delivery_line_type,
                                    delivery_cell_type=delivery_cell_type,
                                    delivery_list=delivery_list,
                                    reindexable_movement_list=reindexable_movement_list,
                                    default_rule_id=default_rule_id)
          for movement in movement_group.movement_list:
            movement.immediateReindexObject()


        else:
          for order_group in movement_group.group_list:
            if orderGroupProcessing(order_group=order_group,
                                    delivery_list=delivery_list,
                                    reindexable_movement_list=reindexable_movement_list) == -1:
              return delivery_list


      # If we reach this point, it means we could
      # create deliveries
      # get_transaction().commit()
      # DO NOT USE COMMIT BECAUSE OF WORKFLOW

      # Now, let us index what must be indexed
      # Since we comitted changes, there should be no risk of conflict
      LOG('reindexable_movement_list',0,reindexable_movement_list)
      for movement in reindexable_movement_list:
        LOG('will reindex this object: ',0,movement)
        # We have to use 'immediate' to bypass the activity tool,
        # because we will depend on these objects when we try to call buildInvoiceList
        
        # movement.reindexObject() # we do it now because we need to
        movement.immediateReindexObject() # we do it now because we need to
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
                         strict_membership=0, simulation_state=None):
      if simulation_state is None:
        simulation_state = self.getPortalCurrentInventoryStateList()
      section_value = self.portal_categories.resolveCategory(section_category)
      node_value = self.portal_categories.resolveCategory(node_category)
      # Initialize price
      current_asset_price = 0.0 # Missing: initial inventory price !!!
      current_inventory = 0.0
      # Parse each movement
      brain_list = self.Resource_zGetMovementHistoryList(resource=[resource],
                             variation_text=variation_text,
                             section_category=section_category,
                             node_category=node_category,
                             strict_membership=strict_membership,
                             simulation_state=simulation_state) # strict_membership not taken into account
                             # We select movements related to certain nodes (ex. Stock) and sections (ex.Coramy Group)
      result = []
      for b in brain_list:
        m = b.getObject()
        if m is not None:
          previous_inventory = current_inventory
          inventory_quantity = b.quantity # We should use the aggregated quantity provided by Resource_zGetMovementHistoryList
          quantity = m.getQuantity() # The movement quantity is important to determine the meaning of source and destination
          # Maybe we should take care of target qty in delired deliveries
          if quantity is None:
            quantity = 0.0
          if m.getSourceValue() is None:
            # This is a production movement or an inventory movement
            # Use Industrial Price
            current_inventory += inventory_quantity # Update inventory
            if m.getPortalType() in ('Inventory Line', 'Inventory Cell'): # XX should be replaced by isInventory ???
              asset_price = m.getPrice()
              if asset_price in (0.0, None):
                asset_price = current_asset_price # Use current price if no price defined
            else: # this is a production
              asset_price = m.getIndustrialPrice()
              if asset_price is None: asset_price = current_asset_price  # Use current price if no price defined
            result.append((m.getRelativeUrl(), m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                          m.getTargetQuantity(), 'Production or Inventory', 'Price: %s' % asset_price
                        ))
          elif m.getDestinationValue() is None:
            # This is a consumption movement or an inventory movement
            current_inventory += inventory_quantity # Update inventory
            asset_price = current_asset_price
            result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                          m.getTargetQuantity(), 'Consumption or Inventory', 'Price: %s' % asset_price
                        ))
          elif m.getSourceValue().isAcquiredMemberOf(node_category) and m.getDestinationValue().isAcquiredMemberOf(node_category):
            # This is an internal movement
            current_inventory += inventory_quantity # Update inventory
            asset_price = current_asset_price
            result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                          m.getTargetQuantity(), 'Internal', 'Price: %s' % asset_price
                        ))
          elif m.getSourceValue().isAcquiredMemberOf(node_category) and quantity < 0:
            # This is a physically inbound movement - try to use commercial price
            if m.getSourceSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getDestinationSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getDestinationSectionValue().isAcquiredMemberOf(section_category):
              current_inventory += inventory_quantity # Update inventory
              if m.getDestinationValue().isAcquiredMemberOf('site/Piquage'):
                # Production
                asset_price = m.getIndustrialPrice()
                if asset_price is None: asset_price = current_asset_price  # Use current price if no price defined
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                              m.getTargetQuantity(), 'Production', 'Price: %s' % asset_price
                            ))
              else:
                # Inbound from same section
                asset_price = current_asset_price
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                              m.getTargetQuantity(), 'Inbound same section', 'Price: %s' % asset_price
                            ))
            else:
              current_inventory += inventory_quantity # Update inventory
              asset_price = m.getPrice()
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Inbound different section', 'Price: %s' % asset_price
                          ))
          elif m.getDestinationValue().isAcquiredMemberOf(node_category) and quantity > 0:
            # This is a physically inbound movement - try to use commercial price
            if m.getSourceSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getDestinationSectionValue() is None:
              # No meaning
              current_inventory += inventory_quantity # Update inventory
              asset_price = current_asset_price
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Error', 'Price: %s' % asset_price
                          ))
            elif m.getSourceSectionValue().isAcquiredMemberOf(section_category):
              current_inventory += inventory_quantity # Update inventory
              if m.getSourceValue().isAcquiredMemberOf('site/Piquage'):
                # Production
                asset_price = m.getIndustrialPrice()
                if asset_price is None: asset_price = current_asset_price  # Use current price if no price defined
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                              m.getTargetQuantity(), 'Production', 'Price: %s' % asset_price
                            ))
              else:
                # Inbound from same section
                asset_price = current_asset_price
                result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Inbound same section', 'Price: %s' % asset_price
                          ))
            else:
              current_inventory += inventory_quantity # Update inventory
              asset_price = m.getPrice()
              result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Inbound different section', 'Price: %s' % asset_price
                          ))
          else:
            # Outbound movement
            current_inventory += inventory_quantity # Update inventory
            asset_price = current_asset_price
            result.append((m.getRelativeUrl(),m.getStartDate(), m.getSource(), m.getSourceSection(), m.getDestination(), m.getDestinationSection(),
                            m.getTargetQuantity(), 'Outbound', 'Price: %s' % asset_price
                          ))

          # Update asset_price
          if current_inventory > 0:
            if inventory_quantity is not None:
              # Update price with an average of incoming goods and current goods
              current_asset_price = ( current_asset_price * previous_inventory + asset_price * inventory_quantity ) / float(current_inventory)
          else:
            # New price is the price of incoming goods - negative stock has no meaning for asset calculation
            current_asset_price = asset_price

          result.append(('###New Asset Price', current_asset_price, 'New Inventory', current_inventory))

          # Update Asset Price on the right side
          if m.getSourceSectionValue() is not None and m.getSourceSectionValue().isAcquiredMemberOf(section_category):
            # for each movement, source section is member of one and one only accounting category
            # therefore there is only one and one only source asset price
            m._setSourceAssetPrice(current_asset_price)
            #quantity = m.getInventoriatedQuantity()
            #if quantity:
            #  #total_asset_price = - current_asset_price * quantity
            #  #m.Movement_zSetSourceTotalAssetPrice(uid=m.getUid(), total_asset_price = total_asset_price)
            #  m._setSourceAssetPrice(current_asset_price)
          if m.getDestinationSectionValue() is not None and m.getDestinationSectionValue().isMemberOf(section_category):
            # for each movement, destination section is member of one and one only accounting category
            # therefore there is only one and one only destination asset price
            m._setDestinationAssetPrice(current_asset_price)
            #quantity = m.getInventoriatedQuantity()
            #if quantity:
            #  total_asset_price = current_asset_price * quantity
            #  m.Movement_zSetDestinationTotalAssetPrice(uid=m.getUid(), total_asset_price = total_asset_price)
          # Global reindexing required afterwards in any case: so let us do it now
          # Until we get faster methods (->reindexObject())
          #m.immediateReindexObject()
          m.reindexObject()
          #m.activate(priority=7).immediateReindexObject() # Too slow

      return result

    # Used for mergeDeliveryList.
    class MergeDeliveryListError(Exception): pass

    security.declareProtected( Permissions.ModifyPortalContent, 'mergeDeliveryList' )
    def mergeDeliveryList(self, delivery_list):
      """
        Merge multiple deliveries into one delivery.
        All delivery lines are merged into the first one.
        The first one is therefore called main_delivery here.
        The others are cancelled.
        Return the main delivery.
      """
      # Sanity checks.
      if len(delivery_list) == 0:
        raise self.MergeDeliveryListError, "No delivery is passed"
      elif len(delivery_list) == 1:
        raise self.MergeDeliveryListError, "Only one delivery is passed"

      main_delivery = delivery_list[0]
      delivery_list = delivery_list[1:]

      # Another sanity check. It is necessary for them to be identical in some attributes.
      for delivery in delivery_list:
        for attr in ('portal_type', 'simulation_state',
                     'source', 'destination',
                     'source_section', 'destination_section',
                     'source_decision', 'destination_decision',
                     'source_administration', 'destination_administration',
                     'source_payment', 'destination_payment'):
          main_value = main_delivery.getProperty(attr)
          value = delivery.getProperty(attr)
          if  main_value != value:
            raise self.MergeDeliveryListError, \
              "%s is not the same between %s and %s (%s and %s)" % (attr, delivery.getId(), main_delivery.getId(), value, main_value)

      # One more sanity check. Check if discounts are the same, if any.
      main_discount_list = main_delivery.contentValues(filter = {'portal_type': self.getPortalDiscountTypeList()})
      for delivery in delivery_list:
        discount_list = delivery.contentValues(filter = {'portal_type': self.getPortalDiscountTypeList()})
        if len(main_discount_list) != len(discount_list):
          raise self.MergeDeliveryListError, "Discount is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())
        for discount in discount_list:
          for main_discount in main_discount_list:
            if discount.getDiscount() == main_discount.getDiscount() \
               and discount.getDiscountRatio() == main_discount.getDiscountRatio() \
               and discount.getDiscountType() == main_discount.getDiscountType() \
               and discount.getImmediateDiscount() == main_discount.getImmediateDiscount():
              break
          else:
            raise self.MergeDeliveryListError, "Discount is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())

      # One more sanity check. Check if payment conditions are the same, if any.
      main_payment_condition_list = main_delivery.contentValues(filter = {'portal_type': self.getPortalPaymentConditionTypeList()})
      for delivery in delivery_list:
        payment_condition_list = delivery.contentValues(filter = {'portal_type': self.getPortalPaymentConditionTypeList()})
        if len(main_payment_condition_list) != len(payment_condition_list):
          raise self.MergeDeliveryListError, "Payment Condition is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())
        for condition in payment_condition_list:
          for main_condition in main_payment_condition_list:
            if condition.getPaymentMode() == main_condition.getPaymentMode() \
               and condition.getPaymentAdditionalTerm() == main_condition.getPaymentAdditionalTerm() \
               and condition.getPaymentAmount() == main_condition.getPaymentAmount() \
               and condition.getPaymentEndOfMonth() == main_condition.getPaymentEndOfMonth() \
               and condition.getPaymentRatio() == main_condition.getPaymentRatio() \
               and condition.getPaymentTerm() == main_condition.getPaymentTerm():
              break
          else:
            raise self.MergeDeliveryListError, "Payment Condition is not the same between %s and %s" % (delivery.getId(), main_delivery.getId())

      # Make sure that all activities are flushed, to get simulation movements from delivery cells.
      for delivery in delivery_list:
        for order in delivery.getCausalityValueList(portal_type = self.getPortalOrderTypeList()):
          for applied_rule in order.getCausalityRelatedValueList(portal_type = 'Applied Rule'):
            applied_rule.flushActivity(invoke = 1)
        for causality_related_delivery in delivery.getCausalityValueList(portal_type = self.getPortalDeliveryTypeList()):
          for applied_rule in causality_related_delivery.getCausalityRelatedValueList(portal_type = 'Applied Rule'):
            applied_rule.flushActivity(invoke = 1)

      # Get a list of simulated movements and invoice movements.
      main_simulated_movement_list = main_delivery.getSimulatedMovementList()
      main_invoice_movement_list = main_delivery.getInvoiceMovementList()
      simulated_movement_list = main_simulated_movement_list[:]
      invoice_movement_list = main_invoice_movement_list[:]
      for delivery in delivery_list:
        simulated_movement_list.extend(delivery.getSimulatedMovementList())
        invoice_movement_list.extend(delivery.getInvoiceMovementList())

      #for movement in simulated_movement_list + invoice_movement_list:
      #  parent = movement.aq_parent
      #  LOG('mergeDeliveryList', 0, 'movement = %s, parent = %s, movement.getPortalType() = %s, parent.getPortalType() = %s' % (repr(movement), repr(parent), repr(movement.getPortalType()), repr(parent.getPortalType())))

      LOG('mergeDeliveryList', 0, 'simulated_movement_list = %s, invoice_movement_list = %s' % (str(simulated_movement_list), str(invoice_movement_list)))
      for main_movement_list, movement_list in \
        ((main_simulated_movement_list, simulated_movement_list),
         (main_invoice_movement_list, invoice_movement_list)):
        root_group = self.collectMovement(movement_list,
                                          check_order = 0,
                                          check_path = 0,
                                          check_date = 0,
                                          check_criterion = 1,
                                          check_resource = 1,
                                          check_base_variant = 1,
                                          check_variant = 1)
        for criterion_group in root_group.group_list:
          LOG('mergeDeliveryList dump tree', 0, 'criterion = %s, movement_list = %s, group_list = %s' % (repr(criterion_group.criterion), repr(criterion_group.movement_list), repr(criterion_group.group_list)))
          for resource_group in criterion_group.group_list:
            LOG('mergeDeliveryList dump tree', 0, 'resource = %s, movement_list = %s, group_list = %s' % (repr(resource_group.resource), repr(resource_group.movement_list), repr(resource_group.group_list)))
            for base_variant_group in resource_group.group_list:
              LOG('mergeDeliveryList dump tree', 0, 'base_category_list = %s, movement_list = %s, group_list = %s' % (repr(base_variant_group.base_category_list), repr(base_variant_group.movement_list), repr(base_variant_group.group_list)))
              for variant_group in base_variant_group.group_list:
                LOG('mergeDeliveryList dump tree', 0, 'category_list = %s, movement_list = %s, group_list = %s' % (repr(variant_group.category_list), repr(variant_group.movement_list), repr(variant_group.group_list)))

        for criterion_group in root_group.group_list:
          for resource_group in criterion_group.group_list:
            for base_variant_group in resource_group.group_list:
              # Get a list of categories.
              category_dict = {}
              for variant_group in base_variant_group.group_list:
                for category in variant_group.category_list:
                  category_dict[category] = 1
              category_list = category_dict.keys()

              # Try to find a delivery line.
              delivery_line = None
              for movement in base_variant_group.movement_list:
                if movement in main_movement_list:
                  if movement.aq_parent.getPortalType() in self.getPortalSimulatedMovementTypeList() \
                    or movement.aq_parent.getPortalType() in self.getPortalInvoiceMovementTypeList():
                    delivery_line = movement.aq_parent
                  else:
                    delivery_line = movement
                  LOG('mergeDeliveryList', 0, 'delivery_line %s is found: criterion = %s, resource = %s, base_category_list = %s' % (repr(delivery_line), repr(criterion_group.criterion), repr(resource_group.resource), repr(base_variant_group.base_category_list)))
                  break

              if delivery_line is None:
                # Not found. So create a new delivery line.
                movement = base_variant_group.movement_list[0]
                if movement.aq_parent.getPortalType() in self.getPortalSimulatedMovementTypeList() \
                  or movement.aq_parent.getPortalType() in self.getPortalInvoiceMovementTypeList():
                  delivery_line_type = movement.aq_parent.getPortalType()
                else:
                  delivery_line_type = movement.getPortalType()
                delivery_line = main_delivery.newContent(portal_type = delivery_line_type,
                                                         resource = resource_group.resource)
                LOG('mergeDeliveryList', 0, 'New delivery_line %s is created: criterion = %s, resource = %s, base_category_list = %s' % (repr(delivery_line), repr(criterion_group.criterion), repr(resource_group.resource), repr(base_variant_group.base_category_list)))

              # Update the base categories and categories.
              #LOG('mergeDeliveryList', 0, 'base_category_list = %s, category_list = %s' % (repr(base_category_list), repr(category_list)))
              delivery_line.setVariationBaseCategoryList(base_variant_group.base_category_list)
              delivery_line.setVariationCategoryList(category_list)

              object_to_update = None
              for variant_group in base_variant_group.group_list:
                if len(variant_group.category_list) == 0:
                  object_to_update = delivery_line
                else:
                  for delivery_cell in delivery_line.contentValues():
                    predicate_value_list = delivery_cell.getPredicateValueList()
                    LOG('mergeDeliveryList', 0, 'delivery_cell = %s, predicate_value_list = %s, variant_group.category_list = %s' % (repr(delivery_cell), repr(predicate_value_list), repr(variant_group.category_list)))
                    if len(predicate_value_list) == len(variant_group.category_list):
                      for category in variant_group.category_list:
                        if category not in predicate_value_list:
                          break
                      else:
                        object_to_update = delivery_cell
                        break

                #LOG('mergeDeliveryList', 0, 'object_to_update = %s' % repr(object_to_update))
                if object_to_update is not None:
                  cell_price = object_to_update.getPrice() or 0.0
                  cell_quantity = object_to_update.getQuantity() or 0.0
                  cell_target_quantity = object_to_update.getNetConvertedTargetQuantity() or 0.0
                  cell_total_price = cell_target_quantity * cell_price
                  cell_category_list = list(object_to_update.getCategoryList())

                  for movement in variant_group.movement_list:
                    if movement in main_movement_list:
                      continue
                    LOG('mergeDeliveryList', 0, 'movement = %s' % repr(movement))
                    cell_quantity += movement.getQuantity()
                    cell_target_quantity += movement.getNetConvertedTargetQuantity()
                    try:
                      # XXX WARNING - ADD PRICED QUANTITY
                      cell_price = movement.getPrice()
                      cell_total_price += movement.getNetConvertedTargetQuantity() * cell_price
                    except:
                      cell_total_price = None
                    for category in movement.getCategoryList():
                      if category not in cell_category_list:
                        cell_category_list.append(category)
                    # Make sure that simulation movements point to an appropriate delivery line or
                    # delivery cell.
                    if hasattr(movement, 'getDeliveryRelatedValueList'):
                      for simulation_movement in \
                        movement.getDeliveryRelatedValueList(portal_type = 'Simulation Movement'):
                        simulation_movement.setDeliveryValue(object_to_update)
                        #simulation_movement.reindexObject()
                    if hasattr(movement, 'getOrderRelatedValueList'):
                      for simulation_movement in \
                        movement.getOrderRelatedValueList(portal_type = 'Simulation Movement'):
                        simulation_movement.setOrderValue(object_to_update)
                        #simulation_movement.reindexObject()

                  if cell_target_quantity != 0 and cell_total_price is not None:
                    average_price = cell_total_price / cell_target_quantity
                  else:
                    average_price = 0

                  LOG('mergeDeliveryList', 0, 'object_to_update = %s, cell_category_list = %s, cell_target_quantity = %s, cell_quantity = %s, average_price = %s' % (repr(object_to_update), repr(cell_category_list), repr(cell_target_quantity), repr(cell_quantity), repr(average_price)))
                  object_to_update.setCategoryList(cell_category_list)
                  if object_to_update.getPortalType() in self.getPortalSimulatedMovementTypeList():
                    object_to_update.edit(target_quantity = cell_target_quantity,
                                          quantity = cell_quantity,
                                          price = average_price,
                                          )
                  elif object_to_update.getPortalType() in self.getPortalInvoiceMovementTypeList():
                    # Invoices do not have target quantities, and the price never change.
                    object_to_update.edit(quantity = cell_quantity,
                                          price = cell_price,
                                          )
                  else:
                    raise self.MergeDeliveryListError, "Unknown portal type %s" % str(object_to_update.getPortalType())
                  #object_to_update.immediateReindexObject()
                else:
                  raise self.MergeDeliveryListError, "No object to update"

      # Merge containers. Just copy them from other deliveries into the main.
      for delivery in delivery_list:
        container_id_list = delivery.contentIds(filter = {'portal_type': self.getPortalContainerTypeList()})
        if len(container_id_list) > 0:
          copy_data = delivery.manage_copyObjects(ids = container_id_list)
          new_id_list = main_delivery.manage_pasteObjects(copy_data)

      # Unify the list of causality.
      causality_list = main_delivery.getCausalityValueList()
      for delivery in delivery_list:
        for causality in delivery.getCausalityValueList():
          if causality not in causality_list:
            causality_list.append(causality)
      LOG("mergeDeliveryList", 0, "causality_list = %s" % str(causality_list))
      main_delivery.setCausalityValueList(causality_list)

      # Cancel deliveries.
      for delivery in delivery_list:
        LOG("mergeDeliveryList", 0, "cancelling %s" % repr(delivery))
        delivery.cancel()

      # Reindex the main delivery.
      main_delivery.reindexObject()

      return main_delivery


InitializeClass(SimulationTool)
