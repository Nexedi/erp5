##############################################################################
#
# Copyright (c) 2005, 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5.Variated import Variated


class BudgetLine(Predicate, XMLMatrix, Variated):
  """ A Line of budget, variated in budget cells.
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
                    , PropertySheet.Amount
                    , PropertySheet.VariationRange
  )

  # CMF Type Definition
  meta_type='ERP5 Budget Line'
  portal_type='Budget Line'    
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConsumedBudgetDict')
  def getConsumedBudgetDict(self, **kw):
    """Returns all the consumptions in a dict where the keys are the cells, and
    the value is the consumed budget.
    """
    return self._getBudgetDict(**kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getEngagedBudgetDict')
  def getEngagedBudgetDict(self, **kw):
    """Returns all the engagements in a dict where the keys are the cells, and
    the value is the engaged budget.
    """
    kw.setdefault('explanation_simulation_state',
                  self.getPortalReservedInventoryStateList() +
                  self.getPortalCurrentInventoryStateList() +
                  self.getPortalTransitInventoryStateList())
    return self._getBudgetDict(**kw)

  def _getBudgetDict(self, **kw):
    """Use getCurrentInventoryList to compute all budget cell consumptions at
    once, and returns them in a dict.
    """
    budget = self.getParentValue()
    budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
    if budget_model is None:
      return dict()

    query_dict = budget_model.getInventoryListQueryDict(self)
    query_dict.update(kw)
    query_dict.setdefault('ignore_group_by', True)

    sign = self.BudgetLine_getConsumptionSign()
    budget_dict = dict()
    for brain in self.getPortalObject().portal_simulation\
                             .getCurrentInventoryList(**query_dict):
      # XXX total_quantity or total_price ??
      previous_value = budget_dict.get(
          budget_model._getCellKeyFromInventoryListBrain(brain, self), 0)
      budget_dict[budget_model._getCellKeyFromInventoryListBrain(brain, self)] = \
                  previous_value + brain.total_price * sign

    return budget_dict

