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
from Products.ERP5.Document.Predicate import Predicate

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

  def getInventoryListQueryDict(self, budget_line):
    """Returns the query dict to pass to simulation query for a budget line
    """
    return {}

  def _getCellKeyFromInventoryListBrain(self, brain, budget_line):
    """Compute the cell key from an inventory brain.
    The cell key can be used to retrieve the budget cell in the corresponding
    budget line using budget_line.getCell
    """
    if not self.isMemberOf('budget_variation/budget_cell'):
      return None

    axis = self.getInventoryAxis()
    if not axis:
      return None
    base_category = self.getProperty('variation_base_category')
    if not base_category:
      return None

    movement = brain.getObject()
    # axis 'movement' is simply a category membership on movements
    if axis == 'movement':
      return movement.getDefaultAcquiredCategoryMembership(base_category,
                                                           base=True)

    # is it a source brain or destination brain ?
    is_source_brain = True
    if (brain.node_uid != brain.mirror_node_uid):
      is_source_brain = (brain.node_uid == movement.getSourceUid())
    elif (brain.section_uid != brain.mirror_section_uid):
      is_source_brain = (brain.section_uid == movement.getSourceSectionUid())
    elif brain.total_quantity:
      is_source_brain = (brain.total_quantity == movement.getQuantity())
    else:
      raise NotImplementedError('Could not guess brain side')

    if axis.endswith('_category') or\
            axis.endswith('_category_strict_membership'):
      # if the axis is category, we get the node and then returns the category
      # from that node
      if axis.endswith('_category'):
        axis = axis[:-len('_category')]
      if axis.endswith('_category_strict_membership'):
        axis = axis[:-len('_category_strict_membership')]
      if is_source_brain:
        if axis == 'node':
          node = movement.getSourceValue()
        else:
          node = movement.getProperty('source_%s_value' % axis)
      else:
        if axis == 'node':
          node = movement.getDestinationValue()
        else:
          node = movement.getProperty('destination_%s_value' % axis)
      if node is not None:
        return node.getDefaultAcquiredCategoryMembership(base_category,
                                                         base=True)
      return None

    # otherwise we just return the node
    if is_source_brain:
      if axis == 'node':
        return '%s/%s' % (base_category, movement.getSource())
      return '%s/%s' % (base_category,
                        movement.getProperty('source_%s' % axis))
    if axis == 'node':
      return '%s/%s' % (base_category, movement.getDestination())
    return '%s/%s' % (base_category,
                      movement.getProperty('destination_%s' % axis))

