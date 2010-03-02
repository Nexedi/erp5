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

from Products.ERP5.Document.Rule import Rule

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

  def _generatePrevisionList(self, applied_rule, **kw):
    """Generates list of movements (as dicts), and let parent class to decide
    which is to add, modify or delete"""
    movement_list = []
    trade_condition = applied_rule.getTradeConditionValue()
    business_process = applied_rule.getBusinessProcessValue()

    if trade_condition is None or business_process is None:
      return movement_list

    context_movement = applied_rule.getParentValue()
    for amount in trade_condition.getAggregatedAmountList(context_movement):
      # business path specific
      business_path_list = business_process.getPathValueList(
          trade_phase=amount.getTradePhaseList())
      if len(business_path_list) == 0:
        raise ValueError('Cannot find Business Path')

      if len(business_path_list) != 1:
        raise NotImplementedError('Only one Business Path is supported')

      business_path = business_path_list[0]

      movement_kw = self._getExpandablePropertyDict(applied_rule,
        context_movement, business_path)

      # rule specific
      movement_kw['price'] = amount.getProperty('price')
      movement_kw['resource_list'] = amount.getProperty('resource_list')
      movement_kw['reference'] = amount.getProperty('reference')
      movement_kw['quantity'] = amount.getProperty('quantity')
      movement_kw['base_application_list'] = amount.getProperty(
          'base_application_list')
      movement_kw['base_contribution_list'] = amount.getProperty(
          'base_contribution_list')

      movement_list.append(movement_kw)

    return movement_list
