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
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class TransformationRule(Rule):
    """
      Order Rule object make sure an Order in the similation
      is consistent with the real order
    """

    # CMF Type Definition
    meta_type = 'ERP5 Transformation Rule'
    portal_type = 'Transformation Rule'
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
         , 'factory'        : 'addTransformationRule'
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

    security.declareProtected(Permissions.ModifyPortalContent, 'constructNewAppliedRule')
    def constructNewAppliedRule(self, context, id=None):
      """
        Creates a new applied rule which points to self
      """
      my_applied_rule = Rule.constructNewAppliedRule(self, context, id=id)
      resource = context.getDefaultResourceValue()
      # Find my related transformation
      transformation = resource.getDefaultResourceRelatedValue(portal_type = ('Transformation',))
      if transformation is not None:
        #LOG('Transformation Causality', 0, str(transformation.getId()))
        my_applied_rule.setCausalityValue(transformation )
      return my_applied_rule

    security.declareProtected(Permissions.AccessContentsInformation, 'test')
    def test(self, movement):
      """
        Tests if the rule (still) applies
      """
      # Test if we must transform
      # The test should actually be based on nodes, paths
      # and capacities, which is not possible now
      # so we just test if it is a "model" !
      # and if it is being source from the workshop

      #LOG('Test Transformation Rule', 0, '')

      resource = movement.getResourceValue()
      if resource is None:
        return 0
      module = resource.aq_parent

      if module.id == 'modele':
        # This is the modele !
        # We must also test the nodes
        # if the source is a production node
        source = movement.getSource()
        if type(source) is type('a'):
          if source.find('site/Piquage') >= 0 :
            return 1
          return 0
      elif module.id == 'assortiment':
        destination = movement.getDestination()
        if type(destination) is type('a'):
          if destination.find('site/Stock_PF/Gravelines') >= 0 :
            source = movement.getSource()
            if type(source) is type('a'):
              if source.find('site/Stock_PF/Gravelines') >= 0 :
                return 1

      return 0

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, **kw):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      delivery_line_type = 'Simulation Movement'

      # Get the order where we come from
      my_transformation = applied_rule.getCausalityValue()

      # No transformation defined
      if my_transformation is None:
        # Things stop here
        applied_rule.diverge()
        return

      # Find production node
      my_context_movement = applied_rule.getParent()
      production_node = my_context_movement.getSource()
      production_section = my_context_movement.getSourceSection()
      # Generate production and consumption lines
      my_quantity = my_context_movement.getTargetQuantity()
      #LOG('Transformation', 0, str(my_transformation))
      # We used to call this with context = my_context_movement
      # but it still has some issue which need to be fixed XXX As
      # a temp solution, we use the dict based API, but it is not general enough
      # and will causse errors on countinuous variations
      # suspected bug cause is probably related to the use of REQUEST where it should not
      # ie. we acquire some unwanted context
      amount_list , grand_total_base_price, grand_total_source_base_price,\
      grand_total_duration, grand_total_duration_france, grand_total_variated_base_price,\
      grand_total_variated_source_base_price = my_transformation.getAggregatedAmountList(
                      REQUEST = {'categories':  my_context_movement.getVariationCategoryList()} )
                                                # Coramy Specific

      # Create a line for the resource produced by the transformation
      new_id = 'produced_resource'
      produced_resource = applied_rule.get(new_id)
      if produced_resource is None:
        my_context_movement.portal_types.constructContent(
              type_name = delivery_line_type,
              container = applied_rule,
              id = new_id,
          ) # quantity
        lost_quantity = 0.0
      else:
        lost_quantity = produced_resource.getLostQuantity()

      produced_resource = applied_rule[new_id]
      produced_resource._edit(
        target_start_date = my_context_movement.getTargetStartDate(),
        target_stop_date = my_context_movement.getTargetStartDate(),
        resource = my_context_movement.getResource(),
        target_quantity = my_context_movement.getTargetQuantity() + lost_quantity,
        source_list = (),
        source_section_list = (),
        quantity_unit = my_context_movement.getQuantityUnit(),
        destination_section = production_section,
        destination = production_node,
        deliverable = 0
      )
      # Mising quantity unit conversion for my_quantity !!!! XXXX
      produced_resource.setVariationCategoryList(my_context_movement.getVariationCategoryList())

      # Add lines
      line_number = 0
      acceptable_id_list = ['produced_resource']
      production_order = self.getRootAppliedRule().getCausalityValue() # get the production order
      filter_list = production_order.contentValues(filter={'portal_type': 'Amount Filter'})
      for amount_line in amount_list:
        # Apply each amount filter
        for f in filter_list:
          f.update(amount_line)
        new_id = 'transformed_resource_%s' % line_number
        transformed_resource = applied_rule.get(new_id)
        if transformed_resource is None:
          my_context_movement.portal_types.constructContent(
              type_name = delivery_line_type,
              container = applied_rule,
              id = new_id,
          ) # quantity
        transformed_resource = applied_rule[new_id]
        #LOG("amount_line", 0, str(amount_line))
        if amount_line['quantity'] != 0.0:
          # Only create line if it is not 0.0
          transformed_resource._edit(
            target_start_date = my_context_movement.getTargetStartDate(),
            target_stop_date = my_context_movement.getTargetStartDate(),
            target_quantity = amount_line['quantity'] * my_quantity,
            target_efficiency = amount_line['efficiency'],
            resource_value = amount_line['resource'],
            quantity_unit = amount_line['quantity_unit'],
            source = production_node,
            source_section = production_section,
            destination_list = (),
            deliverable = 0
          )
          #LOG('RESOURCE', 0, str(amount_line['resource'].getRelativeUrl()))
          #LOG('VC List', 0, str(amount_line['variation_category_list']))
          #LOG('Quantity', 0, str(amount_line['quantity']))
          #LOG('Co Quantity', 0, str(amount_line['converted_quantity']))
          variation_category_list = amount_line['variation_category_list']
          # Verify each category
          category_list = []
          for category in variation_category_list:
            value = self.portal_simulation.resolveCategory(category)
            if value is not None:
              category_list += [category]
          transformed_resource.setVariationCategoryList(category_list)
          acceptable_id_list += [new_id]
        line_number += 1

      # Remove each movement not in the transformation
      for movement in applied_rule.objectValues():
        if movement.getId() not in acceptable_id_list:
          movement.flushActivity(invoke=0)
          applied_rule._delObject(movement.getId()) # XXXX Make sur this is not deleted if already in delivery

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
