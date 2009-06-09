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

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Predicate import Predicate

from Products.ERP5.Document.Delivery import Delivery
from Products.ERP5.Document.Inventory import Inventory

from zLOG import LOG

class BudgetVariation(Predicate):
  """Base class for budget variations.

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
  meta_type='ERP5 Budget Variation'
  portal_type='Budget Variation'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def asBudgetPredicate(self):
    """This budget variation in a predicate
    """

  def initializeBudgetLine(self, budget_line):
    """Initialize a budget line.
  
    Called when a new budget line is created.
    """

  def initializeBudget(self, budget):
    """Initialize a budget.

    Called when a budget is associated to a budget model.
    """

  def getBudgetLineVariationRangeCategoryList(self, budget_line):
    """Returns the variation range categories for this budget line
    """
    return []

  def getBudgetVariationRangeCategoryList(self, budget):
    """Returns the variation range categories for this budget
    """
    return []

  def getCellRangeForBudgetLine(self, budget_line, matrixbox=0):
    """Return the cell range to use for the budget line
    """
    return []

  def getInventoryQueryDict(self, budget_cell):
    """Returns the query dict to pass to simulation query
    """
    return {}

