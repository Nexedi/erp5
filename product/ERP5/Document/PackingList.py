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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.ERP5Globals import movement_type_list, draft_order_state
from Products.CMFCore.utils import getToolByName

from Products.ERP5.Document.Delivery import Delivery

class PackingList(Delivery):
    """
      Delivery/PackingList is the main document
      which allows to control causality in the simulation

      PackingList have 2 different states:

      - solved: this happens when quantities and target
        quantities are the same

      - diverged: this happens when quantities and target
        quantities are different

      Resolution of diverged PackingList is achieved by workflow
      methods. Such workflow methods eventually change
      movements in the simulation. Typical solution include:

      - reduce quantity

      - split delivery

      - postpone delivery

      solutions are implemented as solvers
    """
    # CMF Type Definition
    meta_type = 'ERP5 Packing List'
    portal_type = 'Packing List'
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
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An order..."""
         , 'icon'           : 'packing_list_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addPackingList'
         , 'immediate_view' : 'packing_list_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Movement', 'Container', 'Item'
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'packing_list_view'
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
          , 'action'        : 'packing_list_print'
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

    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self):
      """
        Returns 1 if not simulated or inconsistent target and values
      """
      if self.getSimulationState() not in draft_order_state:
        if not self.isSimulated():
          return 1
      return Delivery.isDivergent(self)

    security.declareProtected(Permissions.ModifyPortalContent, 'updateAppliedRule')
    def updateAppliedRule(self):
      if self.getSimulationState() not in draft_order_state:
        # Nothing to do if we are already simulated
        self._createDeliveryRule()

    security.declareProtected(Permissions.ModifyPortalContent, '_createDeliveryRule')
    def _createDeliveryRule(self):
      # Return if draft or cancelled simulation_state
      if self.getSimulationState() in ('cancelled',):
        # The applied rule should be cleaned up ie. empty all movements which have
        # no confirmed children
        return
      # Otherwise, expand
      # Look up if existing applied rule
      my_applied_rule_list = self.getCausalityRelatedValueList(portal_type='Applied Rule')
      if len(my_applied_rule_list) == 0:
        if self.isSimulated(): return # No need to create a DeliveryRule if we are already in the simulation process
        # Create a new applied order rule (portal_rules.order_rule)
        portal_rules = getToolByName(self, 'portal_rules')
        portal_simulation = getToolByName(self, 'portal_simulation')
        my_applied_rule = portal_rules.default_delivery_rule.constructNewAppliedRule(portal_simulation)
        # Set causality
        my_applied_rule.setCausalityValue(self)
        my_applied_rule.flushActivity(invoke = 1) # We must make sure this rule is indexed
                                                  # now in order not to create another one later
      elif len(my_applied_rule_list) == 1:
        # Re expand the rule if possible
        my_applied_rule = my_applied_rule_list[0]
      else:
        # Delete first rules and re expand if possible
        for my_applied_rule in my_applied_rule_list[0:-1]:
          my_applied_rule.flushActivity(invoke=0)
          my_applied_rule.aq_parent._delObject(my_applied_rule.getId())
        my_applied_rule = my_applied_rule_list[-1]

      # We are now certain we have a single applied rule
      # It is time to expand it
      self.activate().expand(my_applied_rule.getId())

    def updateTargetQuantityFromContainerQuantity(self):
      """
        Update quantities in all lines from the container quantities
      """
      movement_list = self.getMovementList()
      for movement in movement_list :
        # this is script dependent
        movement.setTargetQuantity(movement.DeliveryCell_getContainedTargetQuantity())
