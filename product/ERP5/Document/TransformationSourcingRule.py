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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class TransformationSourcingRule(Rule):
    """
      Transformation Sourcing Rule object make sure
      items required in a Transformation are sourced
    """

    # CMF Type Definition
    meta_type = 'ERP5 Transformation Sourcing Rule'
    portal_type = 'Transformation Sourcing Rule'
    add_permission = Permissions.AddERP5Content
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
         , 'factory'        : 'addTransformationSourcingRule'
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

    security.declareProtected(Permissions.AccessContentsInformation, 'test')
    def test(self, movement):
      """
        Tests if the rule (still) applies
      """
      # Test if some movements are "spendings" movements
      # ie. with  destination equal to None
      destination = movement.getDestination()
      if destination is not None:
        return 0

      # Is the resource sourceable (ie. tissue, composant in Coramy Case)
      # This must become generic in the future through path XXXX
      resource = movement.getDefaultResourceValue()
      if resource is None:
        return 0
      module = resource.aq_parent

      # Source components and workforce at this point
      # This must become generic in the future through path XXXX
      if module.id in ('tissu', 'composant'):
        return 1
      # We accept operations at this point
      resource = movement.getDefaultResource()
      if resource.find('operation/') >= 0:
        return 1
      return 0

    # Simulation workflow
    def reset(self, applied_rule):
      """
        DO WE NEED IT ?

        -> this does either a diverge or a reset depending
        on the position in the tree

        if it is in root position, it is a solve
        if it is in non root position, it is a diverse
      """

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule):
      """
        Expands the current movement downward.

        -> new status -> expanded

        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      delivery_line_type = 'Simulation Movement'

      # Source that movement from the next node / stock
      my_context_movement = applied_rule.getParent()
      if my_context_movement.getSource() is not None:
        # We should only expand movements if they have a source
        # otherwise, it creates infinite recursion
        # This happens for example whenever the source of a movement is acquired
        # from an order which is deleted afterwards
        # LOG('Sourcing', 0, str(my_context_movement.getDefaultResource()))
        new_id = 'transformation_source'
        transformation_source = getattr(aq_base(applied_rule), new_id, None)
        if transformation_source is None:
          my_context_movement.portal_types.constructContent(
                type_name = delivery_line_type,
                container = applied_rule,
                id = new_id
              )
        transformation_source = applied_rule[new_id]

        resource = my_context_movement.getResource()
        if resource.find('operation/') >= 0:
          # This is an operation - produce it
          transformation_source._edit(
                  target_quantity = my_context_movement.getTargetQuantity(),
                  target_efficiency = my_context_movement.getTargetEfficiency(),
                  resource = resource,
                  target_start_date = my_context_movement.getTargetStartDate(),
                  target_stop_date = my_context_movement.getTargetStartDate(),
                  source_list = (),
                  source_section_list = (),
                  quantity_unit = my_context_movement.getQuantityUnit(),
                  destination = my_context_movement.getSource(),
                  destination_section = my_context_movement.getSourceSection()
              )
          transformation_source.setVariationCategoryList(
                    my_context_movement.getVariationCategoryList())
        else:
          # This is a component - source from Stock
          transformation_source._edit(
                  target_quantity = my_context_movement.getTargetQuantity(),
                  target_efficiency = my_context_movement.getTargetEfficiency(),
                  resource = resource,
                  target_start_date = my_context_movement.getTargetStartDate(),
                  target_stop_date = my_context_movement.getTargetStartDate(),
                  source = 'site/Stock_MP/Gravelines',
                  source_section = 'group/Coramy',
                  quantity_unit = my_context_movement.getQuantityUnit(),
                  destination = my_context_movement.getSource(),
                  destination_section = my_context_movement.getSourceSection()
              )
          transformation_source.setVariationCategoryList(
                    my_context_movement.getVariationCategoryList())

      # Create one submovement which sources the transformation
      Rule.expand(self, applied_rule)

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
