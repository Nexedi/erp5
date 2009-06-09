# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
#                    Fabien Morin <fabien@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Transformation import Transformation
from Products.ERP5.Document.Path import Path
from Products.ERP5.AggregatedAmountList import AggregatedAmountList

import zope.interface

# XXX TODO : getTradeModelLineComposedList and findSpecialiseValueList should
# probably move to Transformation (better names sould be used)

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
    model_line_portal_type_list = ('Trade Model Line',)
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

    zope.interface.implements(interfaces.ITransformation)

    security.declareProtected(Permissions.ModifyPortalContent,
                              'updateAggregatedAmountList')
    def updateAggregatedAmountList(self, context, **kw):
      existing_movement_list = context.getMovementList()
      aggregated_amount_list = self.getAggregatedAmountList(context=context,
          **kw)
      modified_resource_list = []
      normal_use_list = self.getPortalObject().portal_preferences\
              .getPreferredNormalResourceUseCategoryList()
      # check if the existing movements are in aggregated movments
      movement_to_delete_list = []
      movement_to_add_list = []
      if len(aggregated_amount_list):
        for movement in existing_movement_list:
          keep_movement = False
          for amount in aggregated_amount_list:
            # here we have to check if the movement is a generated one or
            # entered by the user. If it has been entered by user, we have to
            # keep it.
            # if movement is generated and if not exist, append to delete list
            # else, break
            resource = movement.getResourceValue()
            if resource is not None and \
                len(set(normal_use_list).intersection(set(resource\
                .getUseList()))):
              keep_movement = True
              break
            update_kw = {}
            for p in self.edited_property_list:
              update_kw[p] = amount.getProperty(p)
            if movement.getProperty('resource') == update_kw['resource'] and\
                movement.getVariationCategoryList() == \
                amount.getVariationCategoryList():
              movement.edit(**update_kw)
              modified_resource_list.append(update_kw['resource'])
              keep_movement = True
          if not keep_movement:
            movement_to_delete_list.append(movement)
        movement_to_add_list = [amount for amount in aggregated_amount_list if
            amount.getResource() not in modified_resource_list]
      return {'movement_to_delete_list' : movement_to_delete_list,
              'movement_to_add_list': movement_to_add_list}

    security.declareProtected(Permissions.AccessContentsInformation,
        'findSpecialiseValueList')
    def findSpecialiseValueList(self, context, portal_type_list=None,
        visited_trade_condition_list=None):
      """Returns a list of specialised objects representing inheritance tree.

         Uses Breadth First Search.
      """
      if visited_trade_condition_list is None:
        visited_trade_condition_list = []
      specialise_value_list = []
      if portal_type_list is None:
        portal_type_list = [self.getPortalType()]
      if context.getPortalType() in portal_type_list:
        specialise_value_list.append(context)
      for specialise in context.getSpecialiseValueList(portal_type=\
          portal_type_list):
        if specialise in visited_trade_condition_list:
          raise CircularException
        visited_trade_condition_list.append(specialise)
        specialise_value_list.extend(self.findSpecialiseValueList(context=specialise,
          portal_type_list=portal_type_list,
          visited_trade_condition_list=visited_trade_condition_list))
      return specialise_value_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTradeModelLineComposedList')
    def getTradeModelLineComposedList(self, context=None, portal_type_list=None):
      """Returns list of Trade Model Lines using composition.

      Reference of Trade Model Line is used to hide other Trade Model Line
      In chain first found Trade Model Line has precedence
      Context's, if not None, Trade Model Lines have precedence
      Result is sorted in safe order to do one time pass - movements which
      applies are before its possible contributions.
      """
      if portal_type_list is None:
        portal_type_list = self.model_line_portal_type_list

      reference_list = []
      trade_model_line_composed_list = []
      containting_object_list = []
      if context is not None:
        document = context
        if getattr(context, 'getExplanationValue', None) is not None:
          # if context is movement it is needed to ask its explanation
          # for contained Trade Model Lines
          document = context.getExplanationValue()
        containting_object_list.append(document)
      containting_object_list.extend(self.findSpecialiseValueList(self))

      for specialise in containting_object_list:
        for trade_model_line in specialise.contentValues(
            portal_type=portal_type_list):
          reference = trade_model_line.getReference()
          if reference not in reference_list or reference is None:
            reference_list.append(reference)
            base_contribution_list = trade_model_line \
              .getBaseContributionList()
            if len(base_contribution_list) == 0:
              # when movement will not generate anything which contributes
              # it is safe to be last on list
              trade_model_line_composed_list.append(trade_model_line)
            else:
              # if movements contributes to anything it have to be placed
              # just before to what it contributes
              index = 0
              inserted = False
              for old_trade_model_line in trade_model_line_composed_list:
                for base_application in old_trade_model_line \
                  .getBaseApplicationList():
                  if base_application in base_contribution_list:
                    trade_model_line_composed_list.insert(index,
                        trade_model_line)
                    inserted = True
                    break
                if inserted:
                  break
                index += 1
              if not inserted:
                # last resort - nothing was found, it is safe to put movement
                # in beginning of list
                trade_model_line_composed_list.insert(0, trade_model_line)

      return trade_model_line_composed_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAggregatedAmountList')
    def getAggregatedAmountList(self, context, movement_list=None, **kw):
      result = AggregatedAmountList()

      trade_model_line_composed_list = \
          self.getTradeModelLineComposedList(context)

      need_to_run = 1
      if movement_list is None:
        movement_list = []
      while need_to_run:
        need_to_run = 0
        for model_line in trade_model_line_composed_list:
          model_line_result = model_line.getAggregatedAmountList(context,
            movement_list=movement_list,
            current_aggregated_amount_list=result,
            **kw)
          result.extend(model_line_result)
        if len(result) != len(movement_list):
          # something was added
          need_to_run = 1
          movement_list = result

      # remove movement that should not be created
      final_list = []
      for movement in result:
        if movement.getCausalityValue().getCreateLine():
          final_list.append(movement)
      return final_list
