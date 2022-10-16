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
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5.mixin.variated import VariatedMixin
from Products.ERP5Type.Cache import transactional_cached
from ZTUtils import make_query
import six

class TempBudgetCell(object):
  __allow_access_to_unprotected_subobjects__ = 1
  __slots__ = ('amount', 'cell_index', 'url', 'engaged_budget')
  def __init__(self, amount, cell_index, url, engaged_budget):
    self.amount = amount
    self.cell_index = cell_index
    self.url = url
    self.engaged_budget = engaged_budget

  def getConsumedBudget(self):
    return self.amount

  def getAvailableBudget(self):
    return self.amount

  def getEngagedBudget(self):
    return self.amount

  def getExplanationUrl(self, *args, **w):
    return '%s/BudgetLine_viewConsumedBudgetMovementList?%s' % (
      self.url,
      make_query(dict(cell_index=list(self.cell_index), engaged_budget=self.engaged_budget)))


class BudgetLine(Predicate, XMLMatrix, VariatedMixin):
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
    kw.setdefault('stock_explanation_simulation_state',
                  self.getPortalReservedInventoryStateList() +
                  self.getPortalCurrentInventoryStateList() +
                  self.getPortalTransitInventoryStateList())
    kw['simulation_period'] = ''
    return self._getBudgetDict(**kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAvailableBudgetDict')
  @transactional_cached(key_method=lambda self, *args, **kw:
    (self.getRelativeUrl(), tuple(kw.items())))
  def getAvailableBudgetDict(self, **kw):
    """Returns all the engagements in a dict where the keys are the cells, and
    the value is the engaged budget.
    """
    budget_dict = {k: v * -1
      for k, v in six.iteritems(self.getEngagedBudgetDict(**kw))}

    cell_key_list = self.getCellKeyList()
    for cell_key in cell_key_list:
      cell_key = tuple(cell_key)
      cell = self.getCell(*cell_key)
      if cell is not None:
        engaged = budget_dict.get(cell_key, 0)
        budget_dict[cell_key] = cell.getCurrentBalance() + engaged

    return budget_dict

  @transactional_cached(key_method=lambda self, **kw:
    (self.getRelativeUrl(), tuple(kw.items())))
  def _getBudgetDict(self, simulation_period='Current', **kw):
    """Use getCurrentInventoryList to compute all budget cell consumptions at
    once, and returns them in a dict.
    """
    budget = self.getParentValue()
    budget_model = budget.getSpecialiseValue(portal_type='Budget Model')
    if budget_model is None:
      return {}

    query_dict = budget_model.getInventoryListQueryDict(self)
    query_dict.update(kw)
    query_dict.setdefault('ignore_group_by', True)

    sign = self.BudgetLine_getConsumptionSign()
    cell_key_cache = {}
    budget_dict = {}

    portal = self.getPortalObject()
    getInventoryList = portal.portal_simulation.getInventoryList
    if simulation_period == 'Current':
      getInventoryList = portal.portal_simulation.getCurrentInventoryList

    for brain in getInventoryList(**query_dict):
      cell_key = budget_model._getCellKeyFromInventoryListBrain(brain, self,
                                       cell_key_cache=cell_key_cache)
      # XXX total_quantity or total_price ??
      previous_value = budget_dict.get(cell_key, 0)
      budget_dict[cell_key] = previous_value + brain.total_price * sign

    return budget_dict

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConsumedBudgetCell')
  def getConsumedBudgetCell(self, *cell_index, **kw):
    consumed_budget_dict = self.getConsumedBudgetDict()
    return TempBudgetCell(consumed_budget_dict.get(cell_index),
      cell_index, self.absolute_url(), False)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAvailableBudgetCell')
  def getAvailableBudgetCell(self, *cell_index, **kw):
    available_budget_dict = self.getAvailableBudgetDict()
    return TempBudgetCell(available_budget_dict.get(cell_index),
      cell_index, self.absolute_url(), True)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getEngagedBudgetCell')
  def getEngagedBudgetCell(self, *cell_index, **kw):
    engaged_budget_dict = self.getEngagedBudgetDict()
    return TempBudgetCell(engaged_budget_dict.get(cell_index),
      cell_index, self.absolute_url(), True)
