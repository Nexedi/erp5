# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from Products.ERP5Type import Permissions

from Products.ERP5Legacy.Document.Rule import Rule, \
  AppliedRule_getExplanationSpecialiseValue

class TradeModelRule(Rule):
  """
    Rule for Trade Model
  """
  # CMF Type Definition
  meta_type = 'ERP5 Trade Model Rule'
  portal_type = 'Trade Model Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _isBPM(self):
    return True

  def _getExpandableAmountPropertyDict(self, amount):
    """Return a dict of properties extracted from an amount."""
    d = {}
    for property in ('price', 'resource_list', 'reference', 'quantity',
                     'base_application_list', 'base_contribution_list', 'use'):
      d[property] = amount.getProperty(property)
    return d

  def _generatePrevisionList(self, applied_rule, **kw):
    """Generates list of movements (as dicts), and let parent class to decide
    which is to add, modify or delete"""
    movement_list = []
    trade_condition = AppliedRule_getExplanationSpecialiseValue(applied_rule,
        ('Purchase Trade Condition', 'Sale Trade Condition'))
    business_process = AppliedRule_getExplanationSpecialiseValue(applied_rule,
        ('Business Process',))

    if trade_condition is None or business_process is None:
      return movement_list

    context_movement = applied_rule.getParentValue()
    for amount in trade_condition.getAggregatedAmountList(context_movement):
      if not amount.getQuantity():
        continue
      # business path specific
      business_path_list = business_process.getPathValueList(
          trade_phase=amount.getTradePhaseList(), context=context_movement)
      if len(business_path_list) > 1:
        raise NotImplementedError('Only one Business Path is supported')

      if business_path_list:
        business_path = business_path_list[0]
      else:
        business_path = None

      movement_kw = self._getExpandablePropertyDict(applied_rule,
        context_movement, business_path)
      movement_kw.update(self._getExpandableAmountPropertyDict(amount))
      movement_list.append(movement_kw)

    return movement_list
