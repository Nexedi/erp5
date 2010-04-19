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
import zope.interface

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.mixin.composition import _getEffectiveModel
from Products.ERP5.Document.Transformation import Transformation
from Products.ERP5.AggregatedAmountList import AggregatedAmountList
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
from Products.ERP5.Document.MappedValue import MappedValue

from Products.ERP5.mixin.amount_generator import AmountGeneratorMixin
from Products.ERP5.mixin.variated import VariatedMixin

class TradeCondition(MappedValue, AmountGeneratorMixin, VariatedMixin):
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


    # Mapped Value implementation
    #  Transformation itself provides no properties or categories
    def getMappedValuePropertyList(self):
      return ()

    def getMappedValueBaseCategoryList(self):
      return ()

    # Amount Generator Mixin
    def _getGlobalPropertyDict(self, context, amount_list=None, rounding=False):
      """
      No global properties needed
      """
      return {
        'delivery_count' : 1, # Use a better category here if possible - XXX - System preference
      }

    def _getAmountPropertyDict(self, amount, amount_list=None, rounding=False):
      """
      Produced amount quantity is needed to initialize transformation
      """
      result = {
        'quantity' : amount.getQuantity(), # Use a better category here if possible - XXX - System preference      
                                           # and possibly make it extensible
      }
      for category in amount.getBaseContributionList():
        result[category] = amount.getTotalPrice()
      return result

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
      try:
        context = context.getExplanationValue()
      except AttributeError:
        pass
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

      return final_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getAggregatedAmountList')
    def getAggregatedAmountList(self, context, amount_list=None,
                                force_create_line=False, **kw):
      """
      XXX-JPS - TODO
      """
      return self.getGeneratedAmountList(context, amount_list=amount_list, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
        'getEffectiveModel')
    def getEffectiveModel(self, start_date=None, stop_date=None):
      return _getEffectiveModel(self, start_date, stop_date)

