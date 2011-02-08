# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Courteaud Romain <romain@nexedi.com>
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type import PropertySheet
from Products.CMFCore.Expression import Expression
from Products.ERP5Type.Core.CategoryMembershipArityConstraint \
          import CategoryMembershipArityConstraint

class CategoryRelatedMembershipArityConstraint(CategoryMembershipArityConstraint):
  """
  This constraint checks if an object respects the arity from a
  category reverse membership point of view. 'filter_parameter' is an
  additional parameters passed to catalog.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.CategoryRelatedMembershipArity
  instead).

  For example, if we would like to check whether the object respects a
  minimum arity of '1', a maximum arity of '1', and with a filter
  parameter 'simulation_state': ('planned',)' for the Portal Type
  'Organisation' and the Base Category 'source', then we would create
  a 'Category Related Membership Arity Constraint' within that
  Property Sheet and set 'Minimum arity' to '1', 'Maximum Arity' to
  '1', 'Filter parameters' to 'python: {'simulation_state':
  ('planned',)}' 'Portal Types' to 'Organisation', 'Base Categories'
  to 'source', then set the 'Predicate' if necessary (known as
  'condition' for filesystem Property Sheets).
  """
  meta_type = 'ERP5 Category Related Membership Arity Constraint'
  portal_type = 'Category Related Membership Arity Constraint'

  __compatibility_class_name__ = 'CategoryRelatedMembershipArity'

  property_sheets = CategoryMembershipArityConstraint.property_sheets + \
      (PropertySheet.CategoryRelatedMembershipArityConstraint,)

  def _calculateArity(self, obj, base_category_list, portal_type_list):
    # XXX: Only supports one category, the code with filesystem
    # Property Sheets assumes that 'base_category' is not a tuple but
    # a string
    assert len(base_category_list) != 0

    sql_kw = {'portal_type': portal_type_list,
              '%s_uid' % base_category_list[0]: obj.getUid()}

    sql_kw.update(self._getExpressionValue(obj, self.getFilterParameter()))

    portal = obj.getPortalObject()
    return len(portal.portal_catalog.unrestrictedSearchResults(**sql_kw))

  @staticmethod
  def _convertFromFilesystemDefinition(min_arity,
                                       portal_type=(),
                                       max_arity=None,
                                       base_category=(),
                                       filter_parameter=None):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition

    Filesystem definition example:
    { 'id'            : 'source',
      'description'   : '',
      'type'          : 'CategoryMembershipArity',
      'min_arity'     : '1',
      'max_arity'     : '1',
      'portal_type'   : ('Organisation', ),
      'base_category' : ('source',)
      'condition'     : 'python: object.getPortalType() == 'Foo',
    }
    """
    constraint_portal_type_str = isinstance(portal_type, Expression) and \
        portal_type.text or 'python: ' + repr(portal_type)

    zodb_property_dict = dict(
      min_arity=int(min_arity),
      constraint_portal_type=constraint_portal_type_str,
      constraint_base_category_list=base_category)

    if max_arity is not None:
      zodb_property_dict['max_arity'] = int(max_arity)

    if filter_parameter is not None:
      zodb_property_dict['filter_parameter'] = filter_parameter

    yield zodb_property_dict
