##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.BudgetVariation import BudgetVariation

class CategoryBudgetVariation(BudgetVariation):
  """ A budget variation based on a category
  """
  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.SortIndex
                    , PropertySheet.Path
                    , PropertySheet.Predicate
                    , PropertySheet.BudgetVariation
                    )

  # CMF Type Definition
  meta_type = 'ERP5 Category Budget Variation'
  portal_type = 'Category Budget Variation'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # zope.interface.implements(BudgetVariation, )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asBudgetPredicate')
  def asBudgetPredicate(self):
    """This budget variation in a predicate
    """

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCellRangeForBudgetLine')
  def getCellRangeForBudgetLine(self, budget_line, matrixbox=0):
    """The cell range added by this variation
    """
    item_list = self.getBudgetLineVariationRangeCategoryList(budget_line)
    variation_category_list = budget_line.getVariationCategoryList()
    if matrixbox:
      return [[(i[1], i[0]) for i in item_list if i[1] in variation_category_list]]
    return [[i[1] for i in item_list if i[1] in variation_category_list]]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConsumptionCellRangeForBudgetLine')
  def getConsumptionCellRangeForBudgetLine(self, budget_line, matrixbox=0, engaged_budget=False):
    """The cell range added by this variation for consumption
    """
    cell_range = self.getCellRangeForBudgetLine(budget_line, matrixbox)
    if not self.getProperty('full_consumption_detail'):
      return cell_range

    base_category = self.getProperty('variation_base_category')
    prefix = ''
    if base_category:
      prefix = '%s/' % base_category

    item_list = self.getBudgetLineVariationRangeCategoryList(budget_line)

    if matrixbox:
      used_node_item_set = {item[0] for item in cell_range[0]}
    else:
      used_node_item_set = {item for item in cell_range[0]}

    if engaged_budget:
      consumption_dict = budget_line.getConsumedBudgetDict()
    else:
      consumption_dict = budget_line.getEngagedBudgetDict()
    for consumed_budget_key in consumption_dict.keys():
      for item in consumed_budget_key:
        if item.startswith(prefix):
          used_node_item_set.add(item)

    if matrixbox:
      return [[(i[1], i[0]) for i in item_list if i[0] in used_node_item_set]]
    return [[i[1] for i in item_list if i[1] in used_node_item_set]]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoryQueryDict')
  def getInventoryQueryDict(self, budget_cell):
    """ Query dict to pass to simulation query
    """
    query_dict = {}
    axis = self.getInventoryAxis()
    if not axis:
      return query_dict
    base_category = self.getProperty('variation_base_category')
    if not base_category:
      return query_dict

    context = budget_cell
    if self.isMemberOf('budget_variation/budget'):
      context = budget_cell.getParentValue().getParentValue()
    elif self.isMemberOf('budget_variation/budget_line'):
      context = budget_cell.getParentValue()

    uid_based_axis = False
    if axis == 'movement':
      axis = 'default_%s_uid' % base_category
      uid_based_axis = True
    elif axis == 'movement_strict_membership':
      axis = 'default_strict_%s_uid' % base_category
      uid_based_axis = True
    elif axis in ('node', 'section', 'payment', 'function', 'project',
                  'mirror_section', 'mirror_node', 'funding' ):
      axis = '%s_uid' % axis
      uid_based_axis = True

    for criterion_category in context.getMembershipCriterionCategoryList():
      if '/' not in criterion_category: # safe ...
        continue
      criterion_base_category, _ = criterion_category.split('/', 1)
      if criterion_base_category == base_category:
        if uid_based_axis:
          category_uid = self.getPortalObject().portal_categories\
                                .getCategoryUid(criterion_category)
          query_dict.setdefault(axis, []).append(category_uid)
        else:
          query_dict.setdefault(axis, []).append(criterion_category)

    return query_dict

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoryListQueryDict')
  def getInventoryListQueryDict(self, budget_line):
    """Returns the query dict to pass to simulation query for a budget line
    """
    axis = self.getInventoryAxis()
    if not axis:
      return {}
    base_category = self.getProperty('variation_base_category')
    if not base_category:
      return {}

    context = budget_line
    if self.isMemberOf('budget_variation/budget'):
      context = budget_line.getParentValue()

    query_dict = {}
    if axis == 'movement':
      axis = 'default_%s_uid' % base_category
      query_dict['group_by'] = [axis]
      query_dict['select_list'] = [axis]
    elif axis == 'movement_strict_membership':
      axis = 'default_strict_%s_uid' % base_category
      query_dict['group_by'] = [axis]
      query_dict['select_list'] = [axis]
    else:
      query_dict['group_by_%s' % axis] = True
      if axis in ('node', 'section', 'payment', 'function', 'project',
                  'mirror_section', 'mirror_node' ):
        axis = '%s_uid' % axis

    if self.getProperty('full_consumption_detail'):
      for _, category in self.getBudgetLineVariationRangeCategoryList(context):
        if not category:
          continue
        if axis.endswith('_uid'):
          # XXX move out getattrs
          category = self.getPortalObject().portal_categories\
                                  .getCategoryUid(category)
        query_dict.setdefault(axis, []).append(category)
      return query_dict

    found = False
    for category in context.getVariationCategoryList(
                  base_category_list=(base_category,)):
      if axis.endswith('_uid'):
        category = self.getPortalObject().portal_categories\
                                .getCategoryUid(category)
      query_dict.setdefault(axis, []).append(category)
      found = True
    if found:
      return query_dict
    return {}

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBudgetVariationRangeCategoryList')
  def getBudgetVariationRangeCategoryList(self, budget):
    """Returns the Variation Range Category List that can be applied to this
    budget.
    """
    base_category = self.getProperty('variation_base_category')
    if not base_category:
      return []

    portal = self.getPortalObject()
    item_list_method = portal.portal_preferences.getPreference(
                          'preferred_category_child_item_list_method_id',
                          'getCategoryChildCompactLogicalPathItemList')

    return getattr(portal.portal_categories._getOb(base_category),
                        item_list_method)(
                                base=1,
                                local_sort_id=('int_index',
                                               'translated_title'),
                                checked_permission='View')


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBudgetLineVariationRangeCategoryList')
  def getBudgetLineVariationRangeCategoryList(self, budget_line):
    """Returns the Variation Range Category List that can be applied to this
    budget line.
    """
    base_category = self.getProperty('variation_base_category')
    if not base_category:
      return []

    portal = self.getPortalObject()
    item_list_method = portal.portal_preferences.getPreference(
                          'preferred_category_child_item_list_method_id',
                          'getCategoryChildCompactLogicalPathItemList')

    item_list_method_parameter_dict = dict(
          base=1,
          local_sort_id=('int_index', 'translated_title'),
          checked_permission='View')

    # If this category is defined on budget level, starts at this level
    budget = budget_line.getParentValue()
    if base_category in budget.getVariationBaseCategoryList():
      for budget_variation_category in budget.getVariationCategoryList():
        if budget_variation_category.split('/')[0] == base_category:
          base_category = budget_variation_category
          item_list_method_parameter_dict['is_self_excluded'] = False
          break

    return getattr(portal.portal_categories.unrestrictedTraverse(base_category),
                        item_list_method)(**item_list_method_parameter_dict)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'initializeBudgetLine')
  def initializeBudgetLine(self, budget_line):
    """Initialize a budget line
    """
    budget_line_variation_category_list =\
       list(budget_line.getVariationBaseCategoryList() or [])
    budget_line_membership_criterion_base_category_list =\
       list(budget_line.getMembershipCriterionBaseCategoryList() or [])
    base_category = self.getProperty('variation_base_category')
    if base_category:
      budget_line_variation_category_list.append(base_category)
      budget_line.setVariationBaseCategoryList(
              budget_line_variation_category_list)
    if self.isMemberOf('budget_variation/budget_line'):
      budget_line_membership_criterion_base_category_list.append(base_category)
      budget_line.setMembershipCriterionBaseCategoryList(
          budget_line_membership_criterion_base_category_list)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'initializeBudget')
  def initializeBudget(self, budget):
    """Initialize a budget.
    """
    budget_variation_base_category_list =\
       list(budget.getVariationBaseCategoryList() or [])
    budget_membership_criterion_base_category_list =\
       list(budget.getMembershipCriterionBaseCategoryList() or [])
    base_category = self.getProperty('variation_base_category')
    if base_category:
      if base_category not in budget_variation_base_category_list:
        budget_variation_base_category_list.append(base_category)
      if base_category not in budget_membership_criterion_base_category_list:
        budget_membership_criterion_base_category_list.append(base_category)
      budget.setVariationBaseCategoryList(
              budget_variation_base_category_list)
      budget.setMembershipCriterionBaseCategoryList(
              budget_membership_criterion_base_category_list)


