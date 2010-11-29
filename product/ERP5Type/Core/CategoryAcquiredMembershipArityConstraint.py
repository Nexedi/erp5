##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Sebastien Robin <seb@nexedi.com>
#                         Romain Courteaud <romain@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.Core.CategoryMembershipArityConstraint \
          import CategoryMembershipArityConstraint

class CategoryAcquiredMembershipArityConstraint(CategoryMembershipArityConstraint):
  """
  This constraint checks if an object respects the arity with
  Acquisition.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.CategoryAcquiredMembershipArity
  instead).

  For example, if we would like to check whether the object respects a
  minimum arity of '1' and a maximum arity of '1 for the Portal Type
  'Organisation' and the Base Category 'source', then we would create
  a 'Category Acquired Membership Arity Constraint' within that
  Property Sheet and set 'Minimum arity' to '1', 'Maximum Arity' to
  '1', 'Portal Types' to 'Organisation', 'Base Categories' to
  'source', then set the 'Predicate' if necessary (known as
  'condition' for filesystem Property Sheets).
  """
  meta_type = 'ERP5 Category Acquired Membership Arity Constraint'
  portal_type = 'Category Acquired Membership Arity Constraint'

  def _calculateArity(self, obj, base_category_list, portal_type_list):
    return len(obj.getAcquiredCategoryMembershipList(
      base_category, portal_type=portal_type))
