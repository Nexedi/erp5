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

import warnings
import zope.interface

from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.mixin.CompositionMixin import _getEffectiveModel
from erp5.component.document.MappedValue import MappedValue
from erp5.component.mixin.AmountGeneratorMixin import AmountGeneratorMixin
from Products.ERP5.mixin.variated import VariatedMixin
from erp5.component.interface.IMovementCollectionUpdater import IMovementCollectionUpdater
from erp5.component.interface.IAmountGenerator import IAmountGenerator
from erp5.component.interface.IMovementGenerator import IMovementGenerator

@zope.interface.implementer(IAmountGenerator,
                            IMovementGenerator,
                            IMovementCollectionUpdater,)
class TradeCondition(MappedValue, AmountGeneratorMixin, VariatedMixin):
  """
  Trade Conditions are used to store the conditions (payment, logistic,...)
  which should be applied (and used in the orders) when two companies make
  business together
  """
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
                    , PropertySheet.Reference
                    , PropertySheet.Version
                    , PropertySheet.Arrow
                    , PropertySheet.TradeCondition
                    , PropertySheet.Order
                    , PropertySheet.Task # XXX It is probably wrong to have
                           # Task propertysheet, however many tests fails
                           # if not present. Cleaning required.
                    )


  # Mapped Value implementation
  #  Transformation itself provides no properties or categories
  def getMappedValuePropertyList(self):
    return ()

  def getMappedValueBaseCategoryList(self): # pylint: disable=arguments-differ
    return ()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'findEffectiveSpecialiseValueList')
  #deprecated # XXX
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
                            'getAggregatedAmountList')
  def getAggregatedAmountList(self, *args, **kw):
    """
    """
    # Detect old use of getAggregatedAmountList
    if 'context' in kw:
      context = kw.pop('context')
    else:
      if 'force_create_line' in kw:
        del kw['force_create_line']
      elif not args or isinstance(args[0], (list, tuple)):
        return AmountGeneratorMixin.getAggregatedAmountList(self, *args, **kw)
      context, args = args[0], args[1:]
    warnings.warn("The API of getAggregatedAmountList has changed:"
                  " it must be called on the context instead of passing"
                  " the context as first parameter", DeprecationWarning)
    # XXX add a 'trade_amount_generator' group type
    kw['amount_generator_type_list'] = ('Purchase Trade Condition',
                                        'Sale Trade Condition',
                                        'Trade Model Line')
    return context.getAggregatedAmountList(*args, **kw)

  #deprecated # XXX
  security.declareProtected(Permissions.AccessContentsInformation,
      'getEffectiveModel')
  def getEffectiveModel(self, start_date=None, stop_date=None):
    return _getEffectiveModel(self, start_date, stop_date)