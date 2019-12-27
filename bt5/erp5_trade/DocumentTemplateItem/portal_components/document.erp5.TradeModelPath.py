# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Yusuke Muraoka <yusuke@nexedi.com>
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

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.Path import Path
from Products.ERP5.ExplanationCache import _getExplanationCache

import zope.interface

class TradeModelPath(Path):
  """
    The TradeModelPath class embeds all information related to
    lead times and parties involved at a given phase of a business
    process. TradeModelPath are also the most common way to trigger
    the build deliveries from buildable movements.

    The idea is to invoke isBuildable() on the collected simulation
    movements (which are orphan) during build "after select" process

    Here is the typical code of an alarm in charge of the building process::

      builder = portal_deliveries.a_delivery_builder
      for trade_model_path in builder.getDeliveryBuilderRelatedValueList():
        builder.build(causality_uid=trade_model_path.getUid(),) # Select movements

    WRONG - too slow

      Pros: global select is possible by not providing a causality_uid
      Cons: global select retrieves long lists of orphan movements which
            are not yet buildable the build process could be rather
            slow or require activities

    TODO:
    - IArrowBase implementation has too many comments which need to be
      fixed
    - _getExplanationRelatedMovementValueList may be superfluous. Make
      sure it is really needed
  """
  meta_type = 'ERP5 Trade Model Path'
  portal_type = 'Trade Model Path'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Reference
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.Amount
                    , PropertySheet.Chain # XXX-JPS Why N
                    , PropertySheet.SortIndex
                    , PropertySheet.TradeModelPath
                    , PropertySheet.FlowCapacity
                    , PropertySheet.Reference
                    , PropertySheet.PaymentCondition # XXX-JPS must be renames some day
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.ICategoryAccessProvider,
                            interfaces.IArrowBase,
                            interfaces.ITradeModelPath,
                            interfaces.IPredicate,
                            )

  # Helper Methods
  def _getExplanationRelatedSimulationMovementValueList(self, explanation):
    explanation_cache = _getExplanationCache(explanation)
    return explanation_cache.getTradeModelPathRelatedSimulationMovementValueList(self)

  def _getExplanationRelatedMovementValueList(self, explanation):
    explanation_cache = _getExplanationCache(explanation)
    return explanation_cache.getTradeModelPathRelatedMovementValueList(self)

  # IArrowBase implementation
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSourceArrowBaseCategoryList')
  def getSourceArrowBaseCategoryList(self):
    """
      Returns all categories which are used to define the source
      of this Arrow
    """
    # Naive implementation - we must use category groups instead - XXX
    return ('source',
            'source_account',
            'source_administration',
            #'source_advice',
            'source_carrier',
            'source_decision',
            'source_function',
            'source_funding',
            'source_payment',
            'source_project',
            'source_referral',
            'source_section',
            'source_trade',
            #'source_transport'
            )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDestinationArrowBaseCategoryList')
  def getDestinationArrowBaseCategoryList(self):
    """
      Returns all categories which are used to define the destination
      of this Arrow
    """
    # Naive implementation - we must use category groups instead - XXX-JPS review this later
    return ('destination',
            'destination_account',
            'destination_administration',
            #'destination_advice',
            #'destination_carrier',
            'destination_decision',
            'destination_function',
            'destination_funding',
            'destination_payment',
            'destination_project',
            'destination_referral',
            'destination_section',
            'destination_trade',
            #'destination_transport'
            )

  # XXX-JPS UNkonwn ?
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getArrowCategoryDict')
  def getArrowCategoryDict(self, context=None, **kw): # XXX-JPS do we need it in API ?
    # This method returns the dict like
    # {base_category_id:[category value url list], ...}
    # for all Arrow base categories.
    # Each category values are self's category values (if exist) or
    # dynamically computed values (if not exist).
    result = {}
    dynamic_category_list = self._getDynamicCategoryList(context)
    for base_category in self.getSourceArrowBaseCategoryList() +\
            self.getDestinationArrowBaseCategoryList():
      category_url_list = self._getAcquiredCategoryMembershipList(
        base_category, **kw)
      if len(category_url_list) == 0 and len(dynamic_category_list) > 0:
        category_url_list = self._filterCategoryList(dynamic_category_list,
                                                     base_category, **kw)
      if len(category_url_list) > 0:
        result[base_category] = category_url_list
    return result

  def _filterCategoryList(self, category_list, category, spec=(),
                          filter=None, portal_type=(), base=0,
                          keep_default=1, checked_permission=None):
    """
      XXX - implementation missing
      TBD - look at CategoryTool._buildFilter for inspiration
    """
    # basic filtering:
    #  * remove categories which base name is not category
    #  * respect base parameter
    prefix = category + '/'
    start_index = 0 if base else len(prefix)
    return [category[start_index:]
            for category in category_list
            if category.startswith(prefix)]

  # Dynamic context based categories
  def _getDynamicCategoryList(self, context):
    return self._getDynamicSourceCategoryList(context) \
         + self._getDynamicDestinationCategoryList(context)

  def _getDynamicSourceCategoryList(self, context):
    method_id = self.getSourceMethodId()
    if method_id:
      method = getattr(self, method_id)
      return method(context)
    return []

  def _getDynamicDestinationCategoryList(self, context):
    method_id = self.getDestinationMethodId()
    if method_id:
      method = getattr(self, method_id)
      return method(context)
    return []

  security.declareProtected(Permissions.AccessContentsInformation,
                                            'getExpectedQuantity')
  def getExpectedQuantity(self, amount):
    """Returns the new quantity for the provided amount taking
    into account the efficiency or the quantity defined on the business path.
    This is used to implement payment conditions or splitting production
    over multiple path. The total of getExpectedQuantity for all business
    path which are applicable should never exceed the original quantity.
    The implementation of this validation is left to rules.
    """
    if self.getQuantity():
      return self.getQuantity()
    elif self.getEfficiency():
      return amount.getQuantity() * self.getEfficiency()
    else:
      return amount.getQuantity()
