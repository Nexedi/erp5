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
from Products.ERP5.Document.BudgetVariation import BudgetVariation


class SectionCategoryBudgetVariation(BudgetVariation):
  """A budget variation for section category.
  """
  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.SimpleItem
                    , PropertySheet.SortIndex
                    , PropertySheet.Path
                    , PropertySheet.Predicate
                    )

  # CMF Type Definition
  meta_type = 'ERP5 Section Category Budget Variation'
  portal_type = 'Section Category Budget Variation'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # __implements__ = (BudgetVariation, )

  def asBudgetPredicate(self):
    """This budget variation in a predicate
    """

  def getCellRangeForBudgetLine(self, budget_line, matrixbox=0):
    """The cell range added by this variation
    """
    portal = self.getPortalObject()
    resolveCategory = portal.portal_categories.resolveCategory

    cell_range_dict = dict()
    for variation_base_category in \
          self.getProperty('variation_base_category_list'):
      for category in budget_line.getVariationCategoryList():
        if category.startswith(variation_base_category):
          if matrixbox:
            cell_range_dict.setdefault(
                variation_base_category, []).append(
                    (category,
                      resolveCategory(category).getTranslatedLogicalPath(),))
          else:
            cell_range_dict.setdefault(
                variation_base_category, []).append(category)

    return cell_range_dict.values()

  def getInventoryQueryDict(self, budget_cell):
    """ Query dict to pass to simulation query
    """
    section_category_list = []
    for variation_base_category in \
          self.getProperty('variation_base_category_list'):
      for category in budget_cell.getMembershipCriterionCategoryList():
        if category.startswith(variation_base_category):
          section_category_list.append(category)

    # FIXME: this should be a AND, but passing this to inventory API:
    # section_category=dict(query=section_category_list,
    #                      operator='AND')
    # just generates an impossible query
    return dict(section_category=section_category_list)

  def getBudgetLineVariationRangeCategoryList(self, budget_line):
    portal = self.getPortalObject()
    variation_range_category_list = []
    category_tool = portal.portal_categories
    item_list_method_id = portal.portal_preferences\
            .getPreferredCategoryChildItemListMethodId()
    for variation_base_category in \
          self.getProperty('variation_base_category_list'):
      if variation_base_category in category_tool.objectIds():
        base_category = category_tool._getOb(variation_base_category)
        variation_range_category_list.extend(
            getattr(base_category, item_list_method_id)(base=1))
    return variation_range_category_list

  def initializeBudgetLine(self, budget_line):
    """Initialize a budget line
    """
    budget_line_variation_category_list =\
       list(budget_line.getVariationBaseCategoryList() or [])
    for variation_base_category in \
          self.getProperty('variation_base_category_list'):
      if variation_base_category not in budget_line_variation_category_list:
        budget_line_variation_category_list.append(variation_base_category)
    budget_line.setVariationBaseCategoryList(
              budget_line_variation_category_list)


