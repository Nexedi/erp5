#############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5.Document.Predicate import Predicate
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Cache import getReadOnlyTransactionCache, enableReadOnlyTransactionCache, disableReadOnlyTransactionCache


class ContributionPredicate(Predicate, XMLObject):
  """
  """

  meta_type = 'ERP5 Contribution Predicate'
  portal_type = 'Contribution Predicate'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isPredicate = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Predicate
                    , PropertySheet.SortIndex
                    , PropertySheet.ContributionPredicate
                    )

  security.declareProtected( Permissions.AccessContentsInformation, 'test')
  def test(self, context, tested_base_category_list=None, **kw):
    """
      A Predicate can be tested on a given context.
      Parameters can passed in order to ignore some conditions.

      - tested_base_category_list:  this is the list of category that we do
        want to test. For example, we might want to test only the
        destination or the source of a predicate.

      This method returns portal type name if test success, else returns False.
    """
    self = self.asPredicate()
    result = 1
    if getattr(aq_base(self), '_identity_criterion', None) is None:
      self._identity_criterion = {}
      self._range_criterion = {}
    for property, value in self._identity_criterion.iteritems():
      result = result and (context.getProperty(property) in value)
    for property, (min, max) in self._range_criterion.iteritems():
      value = context.getProperty(property)
      if min is not None:
        result = result and (value >= min)
      if max is not None:
        result = result and (value < max)
    multimembership_criterion_base_category_list = \
        self.getMultimembershipCriterionBaseCategoryList()
    membership_criterion_base_category_list = \
        self.getMembershipCriterionBaseCategoryList()
    tested_base_category = {}
    membership_criterion_category_list = \
                            self.getMembershipCriterionCategoryList()
    if tested_base_category_list is not None:
      membership_criterion_category_list = [x for x in \
          membership_criterion_category_list if x.split('/', 1)[0] in \
          tested_base_category_list]

    # Test category memberships. Enable the read-only transaction cache
    # temporarily, if not enabled, because this part is strictly read-only,
    # and context.isMemberOf is very expensive, when the category list has
    # many items.
    enabled = (getReadOnlyTransactionCache(self) is not None)
    try:
      if not enabled:
        enableReadOnlyTransactionCache(self)
      for c in membership_criterion_category_list:
        bc = c.split('/', 1)[0]
        if (bc not in tested_base_category) and \
           (bc in multimembership_criterion_base_category_list):
          tested_base_category[bc] = 1
        elif (bc not in tested_base_category) and \
             (bc in membership_criterion_base_category_list):
          tested_base_category[bc] = 0
        if (bc in multimembership_criterion_base_category_list):
          tested_base_category[bc] = tested_base_category[bc] and \
                                     context.isMemberOf(c)
        elif (bc in membership_criterion_base_category_list):
          tested_base_category[bc] = tested_base_category[bc] or \
                                     context.isMemberOf(c)
    finally:
      if not enabled:
        disableReadOnlyTransactionCache(self)

    result = result and (0 not in tested_base_category.values())
    # Test method calls
    test_method_id_list = self.getTestMethodIdList()
    if test_method_id_list:
      for test_method_id in test_method_id_list:
        if (test_method_id is not None) and result:
          method = getattr(context, test_method_id)
          result = result and method(self)
    else:
      result = result and self.getDestinationPortalType()
    return result

  def asSQLExpression(self):
    raise NotImplementedError, 'ContributionPredicate does not support asSQLExpression.'
