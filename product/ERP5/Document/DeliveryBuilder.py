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
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.ERP5 import MovementGroup
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5.Document.OrderBuilder import OrderBuilder

from zLOG import LOG

class DeliveryBuilder(OrderBuilder):
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

  def callBeforeBuildingScript(self):
    """
      Redefine this method, because it seems nothing interesting can be
      done before building Delivery.
    """
    pass
  
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
    if self.getResourcePortalType() not in ('', None):
      kw['resourceType'] = self.getResourcePortalType()
    if self.simulation_select_method_id in ['', None]:
      kw.update(self.portal_catalog.buildSQLQuery(**kw))
      movement_list = [x.getObject() for x in self.portal_catalog(**kw)]
    else:
      select_method = getattr(self, self.simulation_select_method_id)
      movement_list = select_method(**kw)
    # XXX Use buildSQLQuery will be better
    movement_list = filter(lambda x: x.getDeliveryRelatedValueList()==[],
                           movement_list)
    # XXX  Add predicate test
    return movement_list

  def _setDeliveryMovementProperties(self, delivery_movement,
                                     simulation_movement, property_dict,
                                     update_existing_movement=0):
    """
      Initialize or update delivery movement properties.
      Set delivery ratio on simulation movement.
      Create the relation between simulation movement
      and delivery movement.
    """
    OrderBuilder._setDeliveryMovementProperties(
                            self, delivery_movement, 
                            simulation_movement, property_dict,
                            update_existing_movement=update_existing_movement)
    # Check if simulation movement is not already linked to a existing
    # movement
    if simulation_movement.getDeliveryValue() is not None:
      raise "SelectMovementError",\
            "simulation_movement '%s' must not be selected !" %\
            simulation_movement.getRelativeUrl()
    # Update simulation movement
    simulation_movement.edit(delivery_value=delivery_movement)

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
      sim_mvt_list = movement.getDeliveryRelatedValueList(
                                             portal_type="Simulation Movement")

      for simulation_movement in sim_mvt_list:
        total_quantity += simulation_movement.getQuantity()

      if total_quantity != 0:
        for simulation_movement in sim_mvt_list:
          quantity = simulation_movement.getQuantity()
          #simulation_movement.setDeliveryRatio(quantity/total_quantity)
          simulation_movement.edit(delivery_ratio=quantity/total_quantity)
      else:
        if len(sim_mvt_list) != 0:
          # Distribute equally ratio to all movement
          mvt_ratio = 1 / len(sim_mvt_list)
          for simulation_movement in sim_mvt_list:
            #simulation_movement.setDeliveryRatio(mvt_ratio)
            simulation_movement.edit(delivery_ratio=mvt_ratio)

      movement.edit(quantity=total_quantity)
      # To update the divergence status, the simulation movements
      # must be reindexed, and then the delivery must be touched
      path_list = []
    # Launch delivery creation
    if (create_new_delivery == 1) and\
       (rejected_movement_list != []):
      movement_relative_url_list = []
      for movement in rejected_movement_list:
        # XXX FIXME Not very generic...
        if movement.__class__.__name__ == "FakeMovement":
          movement_relative_url_list.extend(
                    [x.getRelativeUrl() for x in movement.getMovementList()])
        else:
          movement_relative_url_list.append(movement.getRelativeUrl())
      self.activate(activity="SQLQueue").build(
                        movement_relative_url_list=movement_relative_url_list)

  def _deliveryUpdateGroupProcessing(self, delivery, movement_group):
    """
      Update delivery movement
    """
    rejected_movement_list = []
    property_dict = {}

    for collect_order in self.getDeliveryCollectOrderList():
      for group in movement_group.getGroupList()[1:]:
        rejected_movement_list.extend(group.getMovementList())
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
