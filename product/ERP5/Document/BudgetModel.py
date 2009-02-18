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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Predicate import Predicate

class BudgetModel(Predicate):
  """A model of budget, with all budget variation
  """

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
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
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  
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

  def getInventoryQueryDict(self, budget_cell):
    """Returns the query dict to pass to simulation query
    """
    query_dict = dict()
    for budget_variation in sorted(self.contentValues(
              portal_type=self.getPortalBudgetVariationTypeList()),
              key=lambda x:x.getIntIndex()):
      query_dict.update(
          budget_variation.getInventoryQueryDict(budget_cell))
    return query_dict
    
  def asBudgetPredicate(self):
    " "
    # XXX predicate for line / cell ?


  def getBudgetConsumptionMethod(self, budget_cell):
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

