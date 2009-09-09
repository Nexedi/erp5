# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
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

from Products.ERP5.Document.Rule import Rule

class TradeModelRule(Rule):
  """
    Rule for Trade Model
  """
  # TODO:
  #  * override overrideable helpers
  #  * more usage of Business Process (remove 'if 0' conditions)

  # CMF Type Definition
  meta_type = 'ERP5 Trade Model Rule'
  portal_type = 'Trade Model Rule'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _isBPM(self):
    return True

  def _getMovementDictByBusinessPath(self, movement, business_path_list):
    """Sets Business Path's provided values"""
    if len(business_path_list) > 1:
      raise NotImplementedError('Only one path supported')

    business_path = business_path_list[0]
    movement_dict = {}

    if 0: # XXX use arrow from path (not working currently)
      for base_category in \
          business_path.getSourceArrowBaseCategoryList() +\
          business_path.getDestinationArrowBaseCategoryList():
        movement_dict[base_category] = business_path\
                  .getDefaultAcquiredCategoryMembership(base_category,
                      context=movement)
        print base_category, movement_dict[base_category]
    else:
      movement_dict['source'] = movement.getSource()
      movement_dict['source_section'] = movement.getSourceSection()
      movement_dict['source_administration'] = \
              movement.getSourceAdministration()
      movement_dict['destination'] = movement.getDestination()
      movement_dict['destination_section'] = movement.getDestinationSection()
      movement_dict['destination_administration'] = \
              movement.getDestinationAdministration()

    if business_path.getQuantity():
      movement_dict['quantity'] = business_path.getQuantity()
    elif business_path.getEfficiency():
      movement_dict['quantity'] = movement.getQuantity() * \
          business_path.getEfficiency()
    else:
      movement_dict['quantity'] = movement.getQuantity()

    if 0: # XXX use path date calculation system
      movement_dict['start_date'] = business_path \
       .getExpectedStartDate(movement)
      movement_dict['stop_date'] = business_path.getExpectedStopDate(movement)
    else:
      movement_dict['start_date'] = movement.getStartDate()
      movement_dict['stop_date'] = movement.getStopDate()

    movement_dict['causality_value'] = business_path

    return movement_dict

  def _getStaticPropertyDict(self, context_movement):
    movement_kw = {}
    for prop in self.getExpandablePropertyList():
      movement_kw[prop] = context_movement.getProperty(prop)
    return movement_kw

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
      # everything static
      movement_kw = self._getStaticPropertyDict(context_movement)

      # business path specific
      business_path_list = business_process.getPathValueList(
          trade_phase=amount.getTradePhaseList())
      movement_kw.update(**self._getMovementDictByBusinessPath(
        context_movement, business_path_list))

      # rule specific
      movement_kw['price'] = amount.getProperty('price')
      movement_kw['resource'] = amount.getProperty('resource')
      movement_kw['reference'] = amount.getProperty('reference')
      movement_kw['quantity'] = amount.getProperty('quantity')
      movement_kw['base_application_list'] = amount.getProperty(
          'base_application_list')
      movement_kw['base_contribution_list'] = amount.getProperty(
          'base_contribution_list')

      movement_list.append(movement_kw)

    return movement_list
