##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class DeliveryRule(Rule):
    """
      Delivery Rule object make sure orphaned movements in a Delivery
      (ie. movements which have no explanation in terms of order)
      are part of the simulation process
    """

    # CMF Type Definition
    meta_type = 'ERP5 Delivery Rule'
    portal_type = 'Delivery Rule'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )

    def test(self, movement):
      """
        Tests if the rule (still) applies
      """
      # A delivery rule never applies 
      # since it is always explicitely instanciated
      return 0

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule,
               movement_type_method='getPortalOrderMovementTypeList', **kw):
      """
        Expands the current movement downwards.
        -> new status -> expanded
        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      delivery_line_type = 'Simulation Movement'
      # Get the delivery when we come from
      # Causality is a kind of Delivery (ex. Packing List)
      my_delivery = applied_rule.getDefaultCausalityValue() 
      # Only expand if my_delivery is not None 
      # and state is not 'confirmed'
      if my_delivery is not None:
        #if my_delivery.getSimulationState() not in ('delivered', ):
        # Even if delivered, we should always calculate consequences

        # First, check each contained movement and make
        # a list of delivery ids which do not need to be copied
        # eventually delete movement which do not exist anylonger
        existing_uid_list = []
        existing_uid_list_append = existing_uid_list.append
        movement_type_list = applied_rule.getPortalMovementTypeList()
        order_movement_type_list = getattr(applied_rule, 
                                           movement_type_method)()

        for movement in applied_rule.contentValues(
                                filter={'portal_type':movement_type_list}):
          delivery_value = movement.getDeliveryValue(
                                        portal_type=order_movement_type_list)

          if (delivery_value is None) or\
             (delivery_value.hasCellContent()) or\
             (len(delivery_value.getDeliveryRelatedValueList()) > 1):
            # Our delivery_value is already related 
            # to another simulation movement
            # Delete ourselve
            # XXX Make sure this is not deleted if already in delivery
            applied_rule._delObject(movement.getId())
          else:
            existing_uid_list_append(delivery_value.getUid())

        # Copy each movement (line or cell) from the delivery is that
        for delivery_movement in my_delivery.getMovementList():
          try:
            if len(delivery_movement.getDeliveryRelatedValueList()) == 0: 
              # Only create if orphaned movement
              if delivery_movement.getUid() not in existing_uid_list:
                # Generate a nicer ID
                if delivery_movement.getParentUid() ==\
                                      delivery_movement.getExplanationUid():
                  # We are on a line
                  new_id = delivery_movement.getId()
                else:
                  # On a cell
                  new_id = "%s_%s" % (delivery_movement.getParentId(),
                                      delivery_movement.getId())
                # Generate the simulation movement
                new_sim_mvt = applied_rule.newContent(
                                portal_type=delivery_line_type,
                                id=new_id,
                                order_value=delivery_movement,
                                delivery_value=delivery_movement,
                                # XXX Do we need to copy the quantity
                                # Why not the resource, the variation,...
                                quantity=delivery_movement.getQuantity(),
                                variation_category_list=\
                                  delivery_movement.getVariationCategoryList(),
                                delivery_ratio=1,
                                deliverable=1)
          except AttributeError:
            LOG('ERP5: WARNING', 0, 
                'AttributeError during expand on delivery line %s'\
                % delivery_movement.absolute_url())
      # Pass to base class
      Rule.expand(self, applied_rule, **kw)

    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self, applied_rule, solution_list):
      """
        Solve inconsitency according to a certain number of solutions
        templates. This updates the

        -> new status -> solved

        This applies a solution to an applied rule. Once
        the solution is applied, the parent movement is checked.
        If it does not diverge, the rule is reexpanded. If not,
        diverge is called on the parent movement.
      """

    security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
    def diverge(self, applied_rule):
      """
        -> new status -> diverged

        This basically sets the rule to "diverged"
        and blocks expansion process
      """

    # Solvers
    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self, applied_rule):
      """
        Returns 1 if divergent rule
      """

    security.declareProtected(Permissions.View, 'getDivergenceList')
    def getDivergenceList(self, applied_rule):
      """
        Returns a list Divergence descriptors
      """

    security.declareProtected(Permissions.View, 'getSolverList')
    def getSolverList(self, applied_rule):
      """
        Returns a list Divergence solvers
      """

    # Deliverability / orderability
    def isOrderable(self, m):
      return 1

    def isDeliverable(self, m):
      if m.getSimulationState() in m.getPortalDraftOrderStateList():
        return 0
      return 1
