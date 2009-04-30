# -*- coding: utf8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Transformation import Transformation
from Products.ERP5.Document.Path import Path
from Products.ERP5.AggregatedAmountList import AggregatedAmountList

class CircularException(Exception): pass

class TradeCondition(Path, Transformation):
    """
      Trade Conditions are used to store the conditions (payment, logistic,...)
      which should be applied (and used in the orders) when two companies make
      business together
    """
    edited_property_list = ['price', 'causality','resource','quantity',
        'base_application_list', 'base_contribution_list']

    meta_type = 'ERP5 Trade Condition'
    portal_type = 'Trade Condition'
    isPredicate = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Folder
                      , PropertySheet.Comment
                      , PropertySheet.Arrow
                      , PropertySheet.TradeCondition
                      , PropertySheet.Order
                      )

    def updateAggregatedAmountList(self, context, **kw):
      existing_movement_list = context.contentValues()
      aggregated_amount_list = self.getAggregatedAmountList(context = context,
          **kw)
      modified_resource_list = []
      for amount in aggregated_amount_list:
        update_kw = {}
        for p in self.edited_property_list:
          update_kw[p] = amount.getProperty(p)
        for movement in existing_movement_list:
          if movement.getProperty('resource') == update_kw['resource']:
            movement.edit(**update_kw)
            modified_resource_list.append(update_kw['resource'])
      return [amount for amount in aggregated_amount_list if
          amount.getResource() not in modified_resource_list]

    def getTradeModelLineComposedList(self, context=None):
      """Returns list of Trade Model Lines using composition
      Resource of Trade Model Line is used to hide other Trade Model Line
      In chain first found Trade Model Line has precedence
      Context's, if not None, Trade Model Lines have precedence"""
      visited_trade_condition_list = []
      def findSpecialiseValueList(context):
        specialise_value_list = []
        if context.getPortalType() in self.getPortalType():
          specialise_value_list.append(context)
        for specialise in context.getSpecialiseValueList():
          if specialise in visited_trade_condition_list:
            raise CircularException
          visited_trade_condition_list.append(specialise)
          specialise_value_list.extend(findSpecialiseValueList(specialise))
        return specialise_value_list

      resource_list = []
      trade_model_line_composed_list = []
      containting_object_list = []
      if context is not None:
        document = context
        if getattr(context, 'getExplanationValue', None) is not None:
          # if context is movement it is needed to ask its explanation
          # for contained Trade Model Lines
          document = context.getExplanationValue()
        containting_object_list.append(document)
      containting_object_list.extend(findSpecialiseValueList(self))

      for specialise in containting_object_list:
        for trade_model_line in specialise.contentValues(
            portal_type='Trade Model Line'):
          resource = trade_model_line.getResource()
          if resource not in resource_list:
            trade_model_line_composed_list.append(trade_model_line)
            resource_list.append(resource)
      return trade_model_line_composed_list

    def getAggregatedAmountList(self, context, **kw):
      result = AggregatedAmountList()

      trade_model_line_composed_list = \
          self.getTradeModelLineComposedList(context)

      need_to_run = 1
      movement_list = []
      while need_to_run:
        need_to_run = 0
        for model in trade_model_line_composed_list:
          model_result = model.getAggregatedAmountList(context,
            movement_list=movement_list, current_aggregated_amount_list = result,
            **kw)
          result.extend(model_result)
        if len(result) != len(movement_list):
          # something was added
          need_to_run = 1
        movement_list = result

      return result
