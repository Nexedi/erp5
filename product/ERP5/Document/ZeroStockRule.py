##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
from DateTime import DateTime
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.ERP5Globals import movement_type_list
from Products.CMFCore.utils import getToolByName

from zLOG import LOG

class ZeroStockRule(Rule):
    """
      Zero Stock Rule object allows to generate
      orders and make sure we will not have
      a negative stock in the future

    """

    # CMF Type Definition
    meta_type = 'ERP5 Zero Stock Rule'
    portal_type = 'Zero Stock Rule'
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
         , 'factory'        : 'addZeroStockRule'
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
      # An order rule never applies since it is always explicitely instanciated
      return 0

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule):
      """
        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      now_date = DateTime()
      #LOG('ZeroStockRule.expand',0,'starting....')
      zero_stock_line_type = 'Simulation Movement'
      portal_simulation = getToolByName(self,'portal_simulation')
      portal_types = getToolByName(self,'portal_types')

      # First, find out which resources are missing
      # and build a dictionnary of quantity, variation
      quantity_dict = {}
      variation_dict = {}
      for inventory_item in self.SimulationTool_getGroupFutureInventoryList():
        if inventory_item.inventory < 0:
          # Only source negative stock
          key = (inventory_item.resource_relative_url, inventory_item.variation_text)
          movement = inventory_item.getObject()
          if movement is not None:
            quantity_dict[key] = - inventory_item.inventory
            variation_dict[key] = movement.getVariationCategoryList()
            if movement.getVariationText() != inventory_item.variation_text:
              LOG('ZeroStockRule WARNING',0,'getVariationText: %s' % str(movement.getRelativeUrl()))
          else:
              LOG('ZeroStockRule WARNING',0,'None movement found')
        else:
          break
      #LOG('ZeroStockRule.expand',0,'quantity_dict: %s' % str(quantity_dict))

      # Then parse folder to find out which movements
      # need to be deleted, created
      to_delete_id = []
      to_edit = []
      to_create = []
      for movement in applied_rule.objectValues():
        LOG('On y passe',0,'starting....')
        key = (movement.getResource(), movement.getVariationText())
        if not quantity_dict.has_key(key):
          to_delete_id +=[movement.id]
        else:
          to_edit += [key]
          resource = movement.getResourceValue()
          if resource is not None:
            stop_date = resource.getNextNegativeInventoryDate(variation_text = movement.getVariationText())
            if stop_date is None: # This happens if we have a negative stock already
              stop_date = now_date
            movement._setQuantityUnit(resource.getDefaultQuantityUnit())
            if resource.getPortalType() in ('Modele',):
              source = 'site/Piquage'
              source_section = 'group/Coramy'
              destination_section = 'group/Coramy'
              destination = 'site/Stock_PF/Gravelines'
            else:
              source = source_section = resource.getSource()
              destination_section = 'group/Coramy'
              destination = 'site/Stock_MP/Gravelines'
          else:
            stop_date = now_date
            source = source_section = 'role/Fournisseur'
            destination_section = 'group/Coramy'
            destination = 'site/Stock_MP/Gravelines'
          movement.edit(target_quantity = movement.getTargetQuantity() + quantity_dict[key])
          movement._edit( target_start_date = stop_date,
                          target_stop_date = stop_date,
                          source = source,
                          source_section = source_section,
                          destination_section = destination_section,
                          destination = destination,)
      for key in quantity_dict.keys():
        if key not in to_edit:
          to_create += [key]

      # Delete movements which are no longer needed
      # WE SHOULD NOT DELETE IN REALITY.... BECAUSE OF CYCLE
      #for id in to_delete_id:
      #  applied_rule._delObject(id)

      # Create movements which are needed
      for relative_url, variation_text in to_create:
        # CHECK IF EXISTING ID
        key = (relative_url, variation_text)
        new_id = "%s_%s" % (relative_url, '_'.join(variation_text.split('\n')))
        new_id = new_id.replace('/', '-')
        portal_types.constructContent(
          type_name=zero_stock_line_type,
          container=applied_rule,
          id=new_id)
        movement = applied_rule[new_id]
        movement._edit( resource=relative_url )
        movement._setVariationCategoryList( variation_dict[(relative_url, variation_text)] )
        resource = movement.getResourceValue()

        if resource is not None:
          stop_date = resource.getNextNegativeInventoryDate(variation_text = movement.getVariationText())
          if stop_date is None: # This happens if we have a negative stock already
            stop_date = now_date
          movement._setQuantityUnit(resource.getDefaultQuantityUnit())
          if resource.getPortalType() in ('Modele',):
            source = 'site/Piquage'
            source_section = 'group/Coramy'
            destination_section = 'group/Coramy'
            destination = 'site/Stock_PF/Gravelines'
          else:
            source = source_section = resource.getSource()
            destination_section = 'group/Coramy'
            destination = 'site/Stock_MP/Gravelines'
        else:
          stop_date = now_date
          source = source_section = 'role/Fournisseur'
          destination_section = 'group/Coramy'
          destination = 'site/Stock_MP/Gravelines'
        movement.edit(target_quantity = quantity_dict[key])
        movement._edit( target_start_date = stop_date,
                        target_stop_date = stop_date,
                        source = source,
                        source_section = source_section,
                        destination_section = destination_section,
                        destination = destination,)

      # Pass to base class
      # Rule.expand(self, applied_rule) # Not for now, later will expand

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
