##############################################################################
#
# Copyright (c) 2005-2008 Nexedi SA and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.OrderBuilder import OrderBuilder
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class SelectMethodError(Exception): pass
class SelectMovementError(Exception): pass

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

  def callBeforeBuildingScript(self):
    """
      Redefine this method, because it seems nothing interesting can be
      done before building Delivery.
    """
    pass

  def searchMovementList(self, *args, **kw):
    """
      defines how to query all Simulation Movements which meet certain criteria
      (including the above path path definition).

      First, select movement matching to criteria define on DeliveryBuilder
      Then, call script simulation_select_method to restrict movement_list
    """
    searchMovementList = UnrestrictedMethod(self._searchMovementList)
    return searchMovementList(*args, **kw)

  def _searchMovementList(self, applied_rule_uid=None,**kw):
    """This method is wrapped by UnrestrictedMethod."""
    movement_list = []
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
      movement_list = [x.getObject() for x in self.portal_catalog(**kw)]
    else:
      select_method = getattr(self.getPortalObject(), self.simulation_select_method_id)
      movement_list = select_method(**kw)
    # XXX Use buildSQLQuery will be better
    movement_list = [x for x in movement_list if \
                     x.getDeliveryValueList()==[]]
    # XXX  Add predicate test
    # XXX FIXME Check that there is no double in the list
    # Because we can't trust simulation_select_method
    # Example: simulation_select_method is not tested enough
    mvt_dict = {}
    for movement in movement_list:
      if mvt_dict.has_key(movement):
        raise SelectMethodError, \
              "%s return %s twice (or more)" % \
              (str(self.simulation_select_method_id),
               str(movement.getRelativeUrl()))
      else:
        mvt_dict[movement] = 1
    # Return result
    return movement_list

  def _setDeliveryMovementProperties(self, delivery_movement,
                                     simulation_movement, property_dict,
                                     update_existing_movement=0,
                                     force_update=0, activate_kw=None):
    """
      Initialize or update delivery movement properties.
      Set delivery ratio on simulation movement.
      Create the relation between simulation movement
      and delivery movement.
    """
    OrderBuilder._setDeliveryMovementProperties(
                            self, delivery_movement,
                            simulation_movement, property_dict,
                            update_existing_movement=update_existing_movement,
                            force_update=force_update, 
                            activate_kw=activate_kw)
    simulation_movement.edit(delivery_value=delivery_movement,
                             activate_kw=activate_kw)

  # Simulation consistency propagation
  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateFromSimulation')
  def updateFromSimulation(self, delivery_relative_url, **kw):
    """
      Update all lines of this transaction based on movements in the
      simulation related to this transaction.
    """
    # We have to get a delivery, else, raise a Error
    delivery = self.getPortalObject().restrictedTraverse(delivery_relative_url)

    divergence_to_adopt_list = delivery.getDivergenceList()
    return self.solveDivergence(
      delivery_relative_url,
      divergence_to_adopt_list=divergence_to_adopt_list)

  def solveDeliveryGroupDivergence(self, *args, **kw):
    """
      solve each divergence according to users decision (accept, adopt
      or do nothing).
    """
    solveDeliveryGroupDivergence = UnrestrictedMethod(self._solveDeliveryGroupDivergence)
    return solveDeliveryGroupDivergence(*args, **kw)

  def _solveDeliveryGroupDivergence(self, delivery_relative_url,
                                    property_dict=None):
    if property_dict in (None, {}):
      return
    delivery = self.getPortalObject().restrictedTraverse(delivery_relative_url)
    for (property, value) in property_dict.iteritems():
      delivery.setPropertyList(property, value)

    # Try to remove existing properties/categories from Movements that
    # should exist on Deliveries.
    for movement in delivery.getMovementList():
      for prop in property_dict.keys():
        # XXX The following should be implemented in better way.
        if movement.hasProperty(prop):
          try:
            # for Property
            movement._delProperty(prop)
          except AttributeError:
            # for Category
            movement.setProperty(prop, None)

    divergence_to_accept_list = []
    for divergence in delivery.getDivergenceList():
      if divergence.getProperty('tested_property') not in property_dict.keys():
        continue
      divergence_to_accept_list.append(divergence)
    self._solveDivergence(delivery_relative_url,
                          divergence_to_accept_list=divergence_to_accept_list)

  def solveDivergence(self, *args, **kw):
    """
      solve each divergence according to users decision (accept, adopt
      or do nothing).
    """
    solveDivergence = UnrestrictedMethod(self._solveDivergence)
    return solveDivergence(*args, **kw)

  def _solveDivergence(self, delivery_relative_url,
                       divergence_to_accept_list=None,
                       divergence_to_adopt_list=None,
                       **kw):
    # We have to get a delivery, else, raise a Error
    delivery = self.getPortalObject().restrictedTraverse(delivery_relative_url)

    if divergence_to_accept_list is None:
      divergence_to_accept_list = []
    if divergence_to_adopt_list is None:
      divergence_to_adopt_list = []

    if not len(divergence_to_accept_list) and \
           not len(divergence_to_adopt_list):
      return
    divergence_list = delivery.getDivergenceList()

    # First, we update simulation movements according to
    # divergence_to_accept_list.
    if len(divergence_to_accept_list):
      solver_script = delivery._getTypeBasedMethod('acceptDecision',
                                                   'Delivery_acceptDecision')
      solver_script(divergence_to_accept_list)

    # Then, we update delivery/line/cell from simulation movements
    # according to divergence_to_adopt_list.
    if not len(divergence_to_adopt_list):
      return

    # Select
    movement_type_list = (self.getDeliveryLinePortalType(),
            self.getDeliveryCellPortalType())
    movement_list = delivery.getMovementList(portal_type=movement_type_list)
    simulation_movement_list = []
    for movement in movement_list:
      movement.edit(quantity=0)
      for simulation_movement in movement.getDeliveryRelatedValueList(
                                            portal_type="Simulation Movement"):
        simulation_movement_list.append(simulation_movement)

    # Collect
    root_group_node = self.collectMovement(simulation_movement_list)

    # Build
    portal = self.getPortalObject()
    delivery_module = getattr(portal, self.getDeliveryModule())
    delivery_to_update_list = [delivery]
    self._resetUpdated()
    delivery_list = self._processDeliveryGroup(
      delivery_module,
      root_group_node,
      self.getDeliveryMovementGroupList(),
      delivery_to_update_list=delivery_to_update_list,
      divergence_list=divergence_to_adopt_list,
      force_update=1)

    # Then, we should re-apply quantity divergence according to 'Do
    # nothing' quanity divergence list because all quantity are already
    # calculated in adopt prevision phase.
    quantity_dict = {}
    for divergence in divergence_list:
      if divergence.getProperty('divergence_scope') != 'quantity' or \
             divergence in divergence_to_accept_list or \
             divergence in divergence_to_adopt_list:
        continue
      s_m = divergence.getProperty('simulation_movement')
      delivery_movement = s_m.getDeliveryValue()
      quantity_gap = divergence.getProperty('decision_value') - \
                     divergence.getProperty('prevision_value')
      delivery_movement.setQuantity(delivery_movement.getQuantity() + \
                                    quantity_gap)
      quantity_dict[s_m] = \
          divergence.getProperty('decision_value')

    # Finally, recalculate delivery_ratio
    #
    # Here, created/updated movements are not indexed yet. So we try to
    # gather delivery relations from simulation movements.
    delivery_dict = {}
    for s_m in simulation_movement_list:
      delivery_path = s_m.getDelivery()
      delivery_dict[delivery_path] = \
                                   delivery_dict.get(delivery_path, []) + \
                                   [s_m]

    for s_m_list_per_movement in delivery_dict.values():
      total_quantity = sum([quantity_dict.get(s_m, s_m.getQuantity()) \
                            for s_m in s_m_list_per_movement])
      if total_quantity != 0.0:
        for s_m in s_m_list_per_movement:
          delivery_ratio = quantity_dict.get(s_m, s_m.getQuantity()) \
                                             / total_quantity
          s_m.edit(delivery_ratio=delivery_ratio)
      else:
        for s_m in s_m_list_per_movement:
          delivery_ratio = 1.0 / len(s_m_list_per_movement)
          s_m.edit(delivery_ratio=delivery_ratio)

    # Call afterscript if new deliveries are created
    new_delivery_list = [x for x in delivery_list if x != delivery]
    self.callAfterBuildingScript(new_delivery_list, simulation_movement_list)

    return delivery_list
