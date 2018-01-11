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

from AccessControl.ZopeGuards import guarded_getattr
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.BudgetVariation import BudgetVariation

from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery, ComplexQuery

class NodeBudgetVariation(BudgetVariation):
  """ A budget variation for node

  A script will return the list of possible nodes, or they will be configured
  explicitly on the budget variation. It is also possible to include a virtual
  node for all others not selected nodes.
  """
  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.SortIndex
                    , PropertySheet.Path
                    , PropertySheet.Predicate
                    , PropertySheet.BudgetVariation
                    )

  # CMF Type Definition
  meta_type = 'ERP5 Node Budget Variation'
  portal_type = 'Node Budget Variation'
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

  def _getNodeList(self, context):
    """Returns the list of possible nodes
    """
    node_select_method_id = self.getProperty('node_select_method_id')
    if node_select_method_id:
      return guarded_getattr(context, node_select_method_id)()

    # no script defined, used the explicitly selected values
    node_list = self.getAggregateValueList()
    portal_categories = self.getPortalObject().portal_categories
    if self.getProperty('include_virtual_none_node'):
      node_list.append(portal_categories.budget_special_node.none)
    if self.getProperty('include_virtual_other_node'):
      node_list.append(portal_categories.budget_special_node.all_other)
    return node_list

  def _getNodeTitle(self, node):
    """Returns the title of a node
    """
    node_title_method_id = self.getProperty('node_title_method_id', 'getTitle')
    return guarded_getattr(node, node_title_method_id)()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCellRangeForBudgetLine')
  def getCellRangeForBudgetLine(self, budget_line, matrixbox=0):
    """The cell range added by this variation
    """
    base_category = self.getProperty('variation_base_category')
    prefix = ''
    if base_category:
      prefix = '%s/' % base_category

    node_item_list = [('%s%s' % (prefix, node.getRelativeUrl()),
                       self._getNodeTitle(node))
                           for node in self._getNodeList(budget_line)]
    variation_category_list = budget_line.getVariationCategoryList()
    if matrixbox:
      return [[i for i in node_item_list if i[0] in variation_category_list]]
    return [[i[0] for i in node_item_list if i[0] in variation_category_list]]

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

    node_item_list = [('%s%s' % (prefix, node.getRelativeUrl()),
                       self._getNodeTitle(node))
                           for node in self._getNodeList(budget_line)]
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
      return [[i for i in node_item_list if i[0] in used_node_item_set]]
    return [[i[0] for i in node_item_list if i[0] in used_node_item_set]]

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
    budget_line = budget_cell.getParentValue()

    context = budget_cell
    if self.isMemberOf('budget_variation/budget'):
      context = budget_line.getParentValue()
    elif self.isMemberOf('budget_variation/budget_line'):
      context = budget_line

    if axis == 'movement':
      axis = 'default_%s' % base_category
    if axis == 'movement_strict_membership':
      axis = 'default_strict_%s' % base_category

    uid_based_axis = False
    if axis in ('node', 'section', 'payment', 'function', 'project',
                'mirror_section', 'mirror_node', 'funding' ):
      axis = '%s_uid' % axis
      uid_based_axis = True

    query = None
    portal_categories = self.getPortalObject().portal_categories
    for criterion_category in context.getMembershipCriterionCategoryList():
      if '/' not in criterion_category: # safe ...
        continue
      criterion_base_category, node_url = criterion_category.split('/', 1)
      if criterion_base_category == base_category:
        if node_url == 'budget_special_node/none':
          # This is the "Nothing" virtual node
          query = Query(**{axis: None})
        elif node_url == 'budget_special_node/all_other':
          # This is the "All Other" virtual node
          other_uid_list = []
          none_node_selected = False
          for node in self._getNodeList(budget_line):
            if '%s/%s' % (base_category, node.getRelativeUrl()) in\
                                    budget_line.getVariationCategoryList():
              if node.getRelativeUrl() == 'budget_special_node/none':
                none_node_selected = True
              else:
                if uid_based_axis:
                  other_uid_list.append(node.getUid())
                else:
                  other_uid_list.append(node.getRelativeUrl())
          if none_node_selected:
            # in this case we don't want to include NULL in All others
            query = NegatedQuery(Query(**{axis: other_uid_list}))
          else:
            query = ComplexQuery(
                            NegatedQuery(Query(**{axis: other_uid_list})),
                            Query(**{axis: None}),
                            logical_operator="OR")

        else:
          value = portal_categories.getCategoryValue(node_url,
                  base_category=criterion_base_category)
          if uid_based_axis:
            query_dict.setdefault(axis, []).append(value.getUid())
          else:
            query_dict.setdefault(axis, []).append(value.getRelativeUrl())

    if query:
      if axis in query_dict:
        query_dict[axis] = ComplexQuery(
              query,
              Query(**{axis: query_dict[axis]}),
              logical_operator='OR')
      else:
        query_dict[axis] = query


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

    portal_categories = self.getPortalObject().portal_categories
    query_dict = {}
    uid_based_axis = False
    if axis == 'movement':
      axis = 'default_%s_uid' % base_category
      query_dict['select_list'] = [axis]
      query_dict['group_by'] = [axis]
      uid_based_axis = True
    elif axis == 'movement_strict_membership':
      axis = 'default_strict_%s_uid' % base_category
      query_dict['select_list'] = [axis]
      query_dict['group_by'] = [axis]
      uid_based_axis = True
    else:
      query_dict['group_by_%s' % axis] = True

    if axis in ('node', 'section', 'payment', 'function', 'project',
                'mirror_section', 'mirror_node', 'funding' ):
      axis = '%s_uid' % axis
      uid_based_axis = True

    # if we have a virtual "all others" node, we don't set a criterion here.
    if self.getProperty('include_virtual_other_node'):
      return query_dict

    if self.getProperty('full_consumption_detail'):
      if self.isMemberOf('budget_variation/budget'):
        category_list = [item[1] for item in
          self.getBudgetVariationRangeCategoryList(context)]
      else:
        category_list = [item[1] for item in
          self.getBudgetLineVariationRangeCategoryList(context)]
    else:
      category_list = context.getVariationCategoryList(
        base_category_list=(base_category,))

    found = False
    for node_url in category_list:
      if node_url != '%s/budget_special_node/none' % base_category:
        __traceback_info__ = (node_url, ) # pylint: disable=unused-variable
        if uid_based_axis:
          query_dict.setdefault(axis, []).append(
                portal_categories.getCategoryValue(node_url,
                      base_category=base_category).getUid())
        else:
          query_dict.setdefault(axis, []).append(
                portal_categories.getCategoryValue(node_url,
                      base_category=base_category).getRelativeUrl())
      found = True
    if found:
      if self.getProperty('include_virtual_none_node'):
        if axis in query_dict:
          query_dict[axis] = ComplexQuery(
                Query(**{axis: None}),
                Query(**{axis: query_dict[axis]}),
                logical_operator="OR")
        else:
          query_dict[axis] = Query(**{axis: None})
      return query_dict
    return {}

  def _getCellKeyFromInventoryListBrain(self, brain, budget_line,
                                         cell_key_cache=None):
    """Compute key from inventory brain, with support for virtual nodes.
    """
    cell_key_cache[None] = '%s/budget_special_node/none'\
                                 % self.getProperty('variation_base_category')

    key = BudgetVariation._getCellKeyFromInventoryListBrain(
                   self, brain, budget_line, cell_key_cache=cell_key_cache)
    if self.getProperty('include_virtual_other_node'):
      if key not in budget_line.getVariationCategoryList(
          base_category_list=(self.getProperty('variation_base_category'),)):
        key = '%s/budget_special_node/all_other' % (
            self.getProperty('variation_base_category'),)
    return key

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBudgetLineVariationRangeCategoryList')
  def getBudgetLineVariationRangeCategoryList(self, budget_line):
    """Returns the Variation Range Category List that can be applied to this
    budget line.
    """
    base_category = self.getProperty('variation_base_category')
    prefix = ''
    if base_category:
      prefix = '%s/' % base_category
    return [(self._getNodeTitle(node), '%s%s' % (prefix, node.getRelativeUrl()))
                for node in self._getNodeList(budget_line)]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getBudgetVariationRangeCategoryList')
  def getBudgetVariationRangeCategoryList(self, budget):
    """Returns the Variation Range Category List that can be applied to this
    budget.
    """
    base_category = self.getProperty('variation_base_category')
    prefix = ''
    if base_category:
      prefix = '%s/' % base_category
    return [(self._getNodeTitle(node), '%s%s' % (prefix, node.getRelativeUrl()))
                for node in self._getNodeList(budget)]

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

