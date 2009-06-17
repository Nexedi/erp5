##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule
from Products.ERP5Type.Errors import TransformationRuleError
from Products.ERP5.Document.TransformationSourcingRule import\
                                            TransformationSourcingRuleMixin

from zLOG import LOG

class TransformationRule(TransformationSourcingRuleMixin, Rule):
    """
      Order Rule object make sure an Order in the similation
      is consistent with the real order
    """
    # CMF Type Definition
    meta_type = 'ERP5 Transformation Rule'
    portal_type = 'Transformation Rule'
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)
    zope.interface.implements(interfaces.IPredicate,
                              interfaces.IRule )
    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      )
    # Class variable 
    simulation_movement_portal_type = "Simulation Movement"

    # Simulation workflow
    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, **kw):
      """
        Expands the current movement downward.
        -> new status -> expanded
        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      parent_movement = applied_rule.getParentValue()
      # Get production node and production section
      production = parent_movement.getSource()
      production_section = parent_movement.getSourceSection()
      # Get the current supply link used to calculate consumed resource
      # The current supply link is calculated from the parent AppliedRule.
      supply_chain = self.getSupplyChain(parent_movement.getParentValue())
      parent_supply_link = self.getCurrentSupplyLink(parent_movement)
      current_supply_link_list = supply_chain.\
                     getPreviousProductionSupplyLinkList(parent_supply_link)
      if len(current_supply_link_list) != 1:
        # We shall no pass here.
        # The test method returned a wrong value !
        raise TransformationRuleError,\
              "Expand must not be called on %r" %\
                  applied_rule.getRelativeUrl()
      else:
        current_supply_link = current_supply_link_list[0]
        # Generate produced movement
        movement_dict = self._expandProducedResource(applied_rule,
                                                     production,
                                                     production_section,
                                                     current_supply_link)
        # Generate consumed movement
        consumed_mvt_dict = self._expandConsumedResource(applied_rule,
                                                         production,
                                                         production_section,
                                                         current_supply_link)
        movement_dict.update(consumed_mvt_dict)
        # Finally, build movement
        self._buildMovementList(applied_rule, movement_dict, **kw)
      # Expand each movement created
      Rule.expand(self, applied_rule, **kw)

    def _expandProducedResource(self, applied_rule, production,
                                production_section, current_supply_link):
      """
        Produced resource.
        Create a movement for the resource produced by the transformation.
        Only one produced movement can be created.
      """
      parent_movement = applied_rule.getParentValue()
      stop_date = parent_movement.getStartDate()
      produced_movement_dict = {
        'pr': {
          "resource": parent_movement.getResource(),
          # XXX what is lost quantity ?
          "quantity": parent_movement.getQuantity(),# + lost_quantity,
          "quantity_unit": parent_movement.getQuantityUnit(),
          "variation_category_list":\
                        parent_movement.getVariationCategoryList(),
          "variation_property_dict": \
                        parent_movement.getVariationPropertyDict(),
          "source_list": (),
          "source_section_list": (),
          "destination": production,
          "destination_section": production_section,
          "deliverable": 1,
          'start_date': current_supply_link.calculateStartDate(stop_date),
          'stop_date': stop_date,
          'causality_value': current_supply_link,
        }
      }
      return produced_movement_dict

    def _expandConsumedResource(self, applied_rule, production,
                                production_section, current_supply_link):
      """
        Consumed resource.
        Create a movement for each resource consumed by the transformation,
        and for the previous variation of the produced resource.
      """
      # Calculate all consumed resource
      # Store each value in a dictionnary before created them.
      # { movement_id: {property_name: property_value,} ,}
      consumed_movement_dict = {}
      parent_movement = applied_rule.getParentValue()
      supply_chain = self.getSupplyChain(parent_movement.getParentValue())
      # Consumed previous variation
      previous_variation_dict = self._expandConsumedPreviousVariation(
                                                        applied_rule, 
                                                        production, 
                                                        production_section,
                                                        supply_chain,
                                                        current_supply_link)
      consumed_movement_dict.update(previous_variation_dict)
      # Consumed raw materials
      raw_material_dict = self._expandConsumedRawMaterials(
                                                        applied_rule, 
                                                        production, 
                                                        production_section,
                                                        supply_chain,
                                                        current_supply_link)
      consumed_movement_dict.update(raw_material_dict)
      return consumed_movement_dict

    def _expandConsumedPreviousVariation(self, applied_rule, production,
                                         production_section, supply_chain,
                                         current_supply_link):
      """
        Create a movement for the previous variation of the produced resource.
      """
      id_count = 1
      consumed_movement_dict = {}
      parent_movement = applied_rule.getParentValue()
      # Calculate the variation category list of parent movement
      base_category_list = parent_movement.getVariationBaseCategoryList()
      if "industrial_phase" in base_category_list:
        # We do not want to get the industrial phase variation
        base_category_list.remove("industrial_phase")
      category_list = parent_movement.getVariationCategoryList(
                                  base_category_list=base_category_list)
      # Calculate the previous variation
      for previous_supply_link in supply_chain.\
            getPreviousSupplyLinkList(current_supply_link):
        previous_ind_phase_list = supply_chain.\
            getPreviousProductionIndustrialPhaseList(previous_supply_link,
                                                     all=1)
        if previous_ind_phase_list != []:
          # Industrial phase is a category
          ind_phase_list = [x.getRelativeUrl() for x in \
                            previous_ind_phase_list]
          consumed_mvt_id = "%s_%s" % ("mr", id_count)
          id_count += 1
          stop_date = parent_movement.getStartDate()
          consumed_movement_dict[consumed_mvt_id] = {
            'start_date': current_supply_link.calculateStartDate(stop_date),
            'stop_date': stop_date,
            "resource": parent_movement.getResource(),
            # XXX Is the quantity value correct ?
            "quantity": parent_movement.getNetQuantity(), # getNetQuantity to support efficency from transformation
            "quantity_unit": parent_movement.getQuantityUnit(),
            "destination_list": (),
            "destination_section_list": (),
            "source": production,
            "source_section": production_section,
            "deliverable": 1,
            "variation_category_list": category_list+ind_phase_list,
            "variation_property_dict": \
                        parent_movement.getVariationPropertyDict(),
            'causality_value': current_supply_link,
            }
      return consumed_movement_dict

    def _expandConsumedRawMaterials(self, applied_rule, production,
                                    production_section, supply_chain,
                                    current_supply_link):
      """
        Create a movement for each resource consumed by the transformation,
      """
      parent_movement = applied_rule.getParentValue()
      # Calculate the context for getAggregatedAmountList
      base_category_list = parent_movement.getVariationBaseCategoryList()
      if "industrial_phase" in base_category_list:
        # We do not want to get the industrial phase variation
        base_category_list.remove("industrial_phase")
      category_list = parent_movement.getVariationCategoryList(
                                  base_category_list=base_category_list)
      # Get the transformation to use
      transformation = self.getTransformation(applied_rule)
      # Generate the fake context 
      tmp_context = parent_movement.asContext(
                   context=parent_movement, 
                   REQUEST={'categories':category_list})
      # Calculate the industrial phase list
      previous_ind_phase_list = supply_chain.\
          getPreviousPackingListIndustrialPhaseList(current_supply_link)
      ind_phase_id_list = [x.getRelativeUrl() for x in previous_ind_phase_list]
      # Call getAggregatedAmountList
      # XXX expand failed if transformation is not defined.
      # Do we need to catch the exception ?
      amount_list = transformation.getAggregatedAmountList(
                   tmp_context,
                   ind_phase_url_list=ind_phase_id_list)
      # Add entries in the consumed_movement_dict
      consumed_movement_dict = {}
      for amount in amount_list:
        consumed_mvt_id = "%s_%s" % ("cr", amount.getId())
        stop_date = parent_movement.getStartDate()
        resource_price = amount.getResourcePrice()
        price = None
        if resource_price is not None:
          price = amount.getNetQuantity() * resource_price # getNetQuantity to support efficency from transformation
        consumed_movement_dict[consumed_mvt_id] = {
          'start_date': current_supply_link.calculateStartDate(stop_date),
          'stop_date': stop_date,
          "resource": amount.getResource(),
          "variation_category_list":\
                        amount.getVariationCategoryList(),
          "variation_property_dict": \
                        amount.getVariationPropertyDict(),
          "quantity": amount.getNetQuantity() * parent_movement.getQuantity(), # getNetQuantity to support efficency from transformation
          "price": price,
          "quantity_unit": amount.getQuantityUnit(),
          "destination_list": (),
          "destination_section_list": (),
          "source": production,
          "source_section": production_section,
          "deliverable": 1,
          'causality_value': current_supply_link,
        }
      return consumed_movement_dict

    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self, applied_rule, solution_list):
      """
        Solve inconsistency according to a certain number of solutions
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

#    # Solvers
#    security.declareProtected(Permissions.View, 'isDivergent')
#    def isDivergent(self, applied_rule):
#      """
#        Returns 1 if divergent rule
#      """
#
#    security.declareProtected(Permissions.View, 'getDivergenceList')
#    def getDivergenceList(self, applied_rule):
#      """
#        Returns a list Divergence descriptors
#      """
#
#    security.declareProtected(Permissions.View, 'getSolverList')
#    def getSolverList(self, applied_rule):
#      """
#        Returns a list Divergence solvers
#      """

    # Deliverability / orderability
    def isDeliverable(self, m):
      return 1
    def isOrderable(self, m):
      return 0

