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
from Products.ERP5Type.Core.Predicate import Predicate

class BudgetModel(Predicate):
  """A model of budget, with all budget variation
  """

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Folder
                    , PropertySheet.Predicate
                    , PropertySheet.SortIndex
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Budget
                    , PropertySheet.Path
                    )

  # CMF Type Definition
  meta_type = 'ERP5 Budget Model'
  portal_type = 'Budget Model'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCellRangeForBudgetLine')
  def getCellRangeForBudgetLine(self, budget_line, matrixbox=0):
    """Return the cell range to use for the budget.
    """
    cell_range = []
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList(),),
              key=lambda x:x.getIntIndex()):
      if not budget_variation.isMemberOf('budget_variation/budget_cell'):
        continue
      variation_cell_range = budget_variation.getCellRangeForBudgetLine(
                               budget_line, matrixbox=matrixbox)
      if variation_cell_range \
          and variation_cell_range != [[]] \
          and variation_cell_range not in cell_range:
        cell_range.extend(variation_cell_range)
    return cell_range

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConsumptionCellRangeForBudgetLine')
  def getConsumptionCellRangeForBudgetLine(self, budget_line, matrixbox=0, engaged_budget=False):
    """Return the cell range to use for the budget consumption.

    It can be different from the cell range for definition when using full
    consumption detail on budget variations.
    """
    cell_range = []
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList(),),
              key=lambda x:x.getIntIndex()):
      if not budget_variation.isMemberOf('budget_variation/budget_cell'):
        continue
      variation_cell_range = budget_variation.getConsumptionCellRangeForBudgetLine(
               budget_line, matrixbox=matrixbox, engaged_budget=engaged_budget)
      if variation_cell_range \
          and variation_cell_range != [[]] \
          and variation_cell_range not in cell_range:
        cell_range.extend(variation_cell_range)
    return cell_range

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoryQueryDict')
  def getInventoryQueryDict(self, budget_cell):
    """Returns the query dict to pass to simulation query for a budget cell
    """
    query_dict = {}
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      query_dict.update(
          budget_variation.getInventoryQueryDict(budget_cell))

    # include dates from the budget
    budget = budget_cell.getParentValue().getParentValue()
    query_dict.setdefault('from_date', budget.getStartDateRangeMin())
    start_date_range_max = budget.getStartDateRangeMax()
    if start_date_range_max:
      query_dict.setdefault('at_date', start_date_range_max.latestTime())
    return query_dict

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoryListQueryDict')
  def getInventoryListQueryDict(self, budget_line):
    """Returns the query dict to pass to simulation query for a budget line
    """
    query_dict = {}
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      variation_query_dict = budget_variation.getInventoryListQueryDict(
                                                      budget_line)
      # Merge group_by and select_list arguments.
      # Other arguments should not conflict
      if 'group_by' in query_dict and 'group_by' in variation_query_dict:
        variation_query_dict['group_by'].extend(query_dict['group_by'])
      if 'select_list' in query_dict \
          and 'select_list' in variation_query_dict:
        variation_query_dict['select_list'].extend(
            query_dict['select_list'])

      query_dict.update(variation_query_dict)

    # include dates from the budget
    budget = budget_line.getParentValue()
    query_dict.setdefault('from_date', budget.getStartDateRangeMin())
    start_date_range_max = budget.getStartDateRangeMax()
    if start_date_range_max:
      query_dict.setdefault('at_date', start_date_range_max.latestTime())
    return query_dict

  def _getCellKeyFromInventoryListBrain(self, brain, budget_line,
                                        cell_key_cache=None):
    """Compute the cell key from an inventory brain, the cell key can be used
    to retrieve the budget cell in the corresponding budget line.
    """
    cell_key = ()
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      key = budget_variation._getCellKeyFromInventoryListBrain(
                  brain, budget_line, cell_key_cache=cell_key_cache)
      if key:
        cell_key += (key,)
    return cell_key

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asBudgetPredicate')
  def asBudgetPredicate(self):
    " "
    # XXX predicate for line / cell ?

  def getBudgetConsumptionMethod(self, budget_cell):
    # XXX this API might disapear
    # XXX return the method, or compute directly ?
    budget_consumption_method = None
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      if budget_variation.getBudgetConsumptionMethod(budget_cell):
        budget_consumption_method = \
          budget_variation.getBudgetConsumptionMethod(budget_cell)
    return budget_consumption_method

  def getBudgetLineVariationRangeCategoryList(self, budget_line):
    variation_range_category_list = []
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      if budget_variation.isMemberOf('budget_variation/budget'):
        continue
      variation_range = \
        budget_variation.getBudgetLineVariationRangeCategoryList(budget_line)
      if variation_range and variation_range not in\
                  variation_range_category_list:
        variation_range_category_list.extend(variation_range)
    return variation_range_category_list

  def getBudgetVariationRangeCategoryList(self, budget):
    variation_range_category_list = []
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      if not budget_variation.isMemberOf('budget_variation/budget'):
        continue
      variation_range = \
        budget_variation.getBudgetVariationRangeCategoryList(budget)
      if variation_range and variation_range not in\
                  variation_range_category_list:
        variation_range_category_list.extend(variation_range)
    return variation_range_category_list

  def initializeBudgetLine(self, budget_line):
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      if not budget_variation.isMemberOf('budget_variation/budget'):
        budget_variation.initializeBudgetLine(budget_line)

  def initializeBudget(self, budget):
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      if budget_variation.isMemberOf('budget_variation/budget'):
        budget_variation.initializeBudget(budget)

