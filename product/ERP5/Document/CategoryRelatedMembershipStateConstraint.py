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

from Products.ERP5.Document.CategoryMembershipStateConstraint \
          import CategoryMembershipStateConstraint

class CategoryRelatedMembershipStateConstraint(CategoryMembershipStateConstraint):
  """
  This method checks if an object respects the arity from a category reverse
  membership point of view and is in a valid workflow state.
  """
  meta_type = 'ERP5 Category Related Membership State Constraint'
  portal_type = 'Category Related Membership State Constraint'

  def _getObjectCategoryMembershipList(self, obj, base_category, 
                                       portal_type_list):
    """
    Calculate the object category membership list.
    This method was created to allow CategoryAcquiredMembershipStateConstraint
    class to simply surcharge it.
    """
    return obj._getRelatedValueList(base_category, 
                                    portal_type=portal_type_list)
