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
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An ERP5 Rule..."""
         , 'icon'           : 'rule_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addDeliveryRule'
         , 'immediate_view' : 'rule_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ()
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'rule_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'rule_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    def test(self, movement):
      """
        Tests if the rule (still) applies
      """
      # A deliveyr rule never applies since it is always explicitely instanciated
      return 0

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, **kw):
      """
        Expands the current movement downwards.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      delivery_line_type = 'Simulation Movement'

      # Get the delivery when we come from
      my_delivery = applied_rule.getDefaultCausalityValue() # Causality is a kind of Delivery (ex. Packing List)

      # Only expand if my_delivery is not None and state is not 'confirmed'
      if my_delivery is not None:
        #if my_delivery.getSimulationState() not in ('delivered', ):
        # Even if delivered, we should always calculate consequences
        if 1:
          # First, check each contained movement and make
          # a list of delivery ids which do not need to be copied
          # eventually delete movement which do not exist anylonger
          existing_uid_list = []
          for movement in applied_rule.contentValues(filter={'portal_type':applied_rule.getPortalMovementTypeList()}):
            delivery_value = movement.getDeliveryValue(portal_type=applied_rule.getPortalOrderMovementTypeList())
            if delivery_value is None:
              movement.flushActivity(invoke=0)
              applied_rule._delObject(movement.getId())  # XXXX Make sure this is not deleted if already in delivery
            else:
              if getattr(delivery_value, 'isCell', 0):
                if len(delivery_value.getDeliveryRelatedValueList()) > 1:
                  # Our delivery_value is already related to another simulation movement
                  # Delete ourselve
                  movement.flushActivity(invoke=0)
                  applied_rule._delObject(movement.getId())  # XXXX Make sure this is not deleted if already in delivery
                else:
                  existing_uid_list += [delivery_value.getUid()]
              elif delivery_value.hasCellContent():
                # Do not keep head of cells
                delivery_value.flushActivity(invoke=0)
                applied_rule._delObject(movement.getId())  # XXXX Make sure this is not deleted if already in delivery
              else:
                if len(delivery_value.getDeliveryRelatedValueList()) > 1:
                  # Our delivery_value is already related to another simulation movement
                  # Delete ourselve
                  movement.flushActivity(invoke=0)
                  applied_rule._delObject(movement.getId())  # XXXX Make sure this is not deleted if already in delivery
                else:
                  existing_uid_list += [delivery_value.getUid()]

          # Copy each movement (line or cell) from the delivery is that
          for delivery_line_object in my_delivery.contentValues(filter={'portal_type':applied_rule.getPortalMovementTypeList()}):
            try:
              if delivery_line_object.hasCellContent():
                for c in delivery_line_object.getCellValueList():
                  if len(c.getDeliveryRelatedValueList()) == 0: # Only create if orphaned movement
                    if c.getUid() not in existing_uid_list:
                      new_id = delivery_line_object.getId() + '_' + c.getId()
                      my_delivery.portal_types.constructContent(type_name=delivery_line_type,
                          container=applied_rule,
                          id=new_id,
                          delivery_value = c,
                          order_value = c,
                          quantity = c.getQuantity(),
                          target_quantity = c.getTargetQuantity(),
                          start_date = c.getStartDate(),
                          stop_date = c.getStopDate(),
                          target_start_date = c.getTargetStartDate(),
                          target_stop_date = c.getTargetStopDate(),
                          deliverable = 1
                      )
                      # We must create both order and delivery link in this case
                      # since our simulation model is based on order and delivery
                      my_delivery.flushActivity(invoke=1) # Flush since we may need immediately getDeliveryRelatedValueList
              else:
                if len(delivery_line_object.getDeliveryRelatedValueList()) == 0: # Only create if orphaned movement
                  if delivery_line_object.getUid() not in existing_uid_list:
                    new_id = delivery_line_object.getId()
                    my_delivery.portal_types.constructContent(type_name=delivery_line_type,
                        container=applied_rule,
                        id=new_id,
                        delivery_value = delivery_line_object,
                        order_value = delivery_line_object,
                        quantity = delivery_line_object.getQuantity(),
                        target_quantity = delivery_line_object.getTargetQuantity(),
                        start_date = delivery_line_object.getStartDate(),
                        stop_date = delivery_line_object.getStopDate(),
                        target_start_date = delivery_line_object.getTargetStartDate(),
                        target_stop_date = delivery_line_object.getTargetStopDate(),
                        deliverable = 1
                    )
                    # Source, Destination, Quantity, Date, etc. are
                    # acquired from the delivery line and need not to be copied.
            except AttributeError:
              LOG('ERP5: WARNING', 0, 'AttributeError during expand on delivery line %s'
                                                      % delivery_line_object.absolute_url())

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
      if m.getSimulationState() in m.getPortalDraftOrderState():
        return 0
      return 1
