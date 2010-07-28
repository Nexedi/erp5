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

from collections import deque
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.composition import _getEffectiveModel
from Products.ERP5.Document.Transformation import Transformation
from Products.ERP5.Document.Path import Path
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery

import zope.interface

# XXX TODO : getTradeModelLineComposedList and findSpecialiseValueList should
# probably move to Transformation (better names should be used)
# XXX TODO: review naming of new methods
# XXX WARNING: current API naming may change although model should be stable.

class TradeCondition(Path, Transformation):
    """
      Trade Conditions are used to store the conditions (payment, logistic,...)
      which should be applied (and used in the orders) when two companies make
      business together
    """
    edited_property_list = ['price', 'resource', 'quantity',
        'reference', 'base_application_list', 'base_contribution_list']

    meta_type = 'ERP5 Trade Condition'
    portal_type = 'Trade Condition'
    model_line_portal_type_list = ('Trade Model Line',)

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

    zope.interface.implements(interfaces.IAmountGenerator,
                              interfaces.IMovementGenerator,
                              interfaces.IMovementCollectionUpdater,)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'updateAggregatedAmountList')
    def updateAggregatedAmountList(self, context, movement_list=None, rounding=None, **kw):
      existing_movement_list = context.getMovementList()
      aggregated_amount_list = self.getAggregatedAmountList(context=context,
          movement_list=movement_list, **kw)

      modified_reference_list = []
      # check if the existing movements are in aggregated movements
      movement_to_delete_list = []
      for movement in existing_movement_list:
        keep_movement = False
        # check if the movement is a generated one or entered by the user.
        # If it has been entered by user, keep it.
        if not movement.getBaseApplicationList():
          continue

        for amount in aggregated_amount_list:
          # if movement is generated and if not exist, append to delete list
          update_kw = {}
          for p in self.edited_property_list:
            update_kw[p] = amount.getProperty(p)

          if movement.getProperty('reference') == update_kw['reference'] and\
              movement.getVariationCategoryList() == \
              amount.getVariationCategoryList():
            movement.edit(**update_kw)
            modified_reference_list.append(update_kw['reference'])
            keep_movement = True

        if not keep_movement:
          movement_to_delete_list.append(movement)

      movement_to_add_list = AggregatedAmountList(
                  [amount for amount in aggregated_amount_list if
                    amount.getReference() not in modified_reference_list])

      return {'movement_to_delete_list' : movement_to_delete_list,
              'movement_to_add_list': movement_to_add_list}

    security.declareProtected(Permissions.AccessContentsInformation,
                              'findEffectiveSpecialiseValueList')
    def findEffectiveSpecialiseValueList(self, context, portal_type_list=None):
      """Return a list of effective specialised objects that is the
      inheritance tree.
      An effective object is an object which have start_date and stop_date
      included to the range of the given parameters start_date and stop_date.

      This algorithm uses Breadth First Search.
      """
      portal_type_set = set(portal_type_list or
                            self.getPortalAmountGeneratorTypeList())
      return [x for x in context._findEffectiveSpecialiseValueList()
                if x.getPortalType() in portal_type_set]

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTradeModelLineComposedList')
    def getTradeModelLineComposedList(self, context=None,
                                      portal_type_list=None):
      """Returns list of Trade Model Lines using composition.

      Reference of Trade Model Line is used to hide other Trade Model Line
      In chain first found Trade Model Line has precedence
      Context's, if not None, Trade Model Lines have precedence
      Result is sorted in safe order to do one time pass - movements which
      applies are before its possible contributions.
      """
      if portal_type_list is None:
        portal_type_list = self.model_line_portal_type_list
      trade_model_line_composed_list = \
        context.asComposedDocument().contentValues(portal_type=portal_type_list)

      # build a graph of precedences
      # B---\
      #      \
      # C-----> A
      # A is parent of B and C, and returned order should be
      #   (BC) A
      # where (BC) cannot be sorted
      parent_dict = {}
      # B and C are leaves
      leaf_line_list = []
      for line in trade_model_line_composed_list:
        has_child = False
        for other_line in trade_model_line_composed_list:
          if line == other_line:
            continue
          parent_dict.setdefault(other_line, [])
          for base_application in line.getBaseApplicationList():
            if base_application in other_line.getBaseContributionList():
              parent_dict[other_line].append(line)
              has_child = True
        if not has_child:
          leaf_line_list.append(line)

      final_list = []
      if len(parent_dict):
        # longest distance to a root (A)
        depth = {}
        tovisit = leaf_line_list
        while tovisit:
          node = tovisit[-1]
          if node in depth:
            tovisit.pop()
            continue

          parent_list = parent_dict.get(node, [])
          if len(parent_list) == 0:
            depth[node] = 0
            tovisit.pop()
          else:
            for parent in parent_list:
              if parent not in depth:
                tovisit.append(parent)
            if tovisit[-1] == node:
              depth[node] = max(depth[p] for p in parent_list) + 1
              tovisit.pop()

        # the farther a line is from a root, the earlier it should be returned
        final_list = sorted(depth.iterkeys(), key=depth.get, reverse=True)

      if len(final_list) == 0:
        # at least return original lines retrieved
        final_list = trade_model_line_composed_list

      ### If all items in final_list has int_index value, then sort it by
      ### int_index to solve undetermined order problem.
      if len([item for item in final_list if not item.getIntIndex()])==0:
        final_list.sort(key=lambda a:a.getIntIndex())

      return final_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAggregatedAmountList')
    def getAggregatedAmountList(self, context, movement_list=None,
                                force_create_line=False, **kw):
      if movement_list is None:
        movement_list = []
      result = AggregatedAmountList()

      trade_model_line_composed_list = \
          self.getTradeModelLineComposedList(context)

      # trade_model_line_composed_list is sorted in good way to have
      # simple algorithm
      for model_line in trade_model_line_composed_list:
        result.extend(model_line.getAggregatedAmountList(context,
          movement_list=movement_list,
          current_aggregated_amount_list=result,
          **kw))
      movement_list = result

      # remove amounts that should not be created, or with "incorrect" references.
      # XXX what are incorrect references ???
      # getTradeModelLineComposedList should have removed duplicate reference
      # in the model graph
      # TODO: review this part
      aggregated_amount_list = AggregatedAmountList()
      for movement in movement_list:
        movement_reference = movement.getReference()
        if movement_reference is None:
            raise ValueError('Reference on Trade Model Line %s is None. '
                'Reference must be set.' % (movement.getPath(),))
        for model_line in trade_model_line_composed_list:
          if model_line.getReference() == movement_reference and\
              (force_create_line or model_line.isCreateLine()):
            aggregated_amount_list.append(movement)

      return aggregated_amount_list

    security.declareProtected(Permissions.AccessContentsInformation,
        'getEffectiveModel')
    def getEffectiveModel(self, start_date=None, stop_date=None):
      return _getEffectiveModel(self, start_date, stop_date)

