from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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

from .Constraint import Constraint

class CategoryExistence(Constraint):
  """This constraint checks if an object respects the existence of
    a category, without acquisition.

    Configuration example:
    { 'id'            : 'category_existence',
      'description'   : 'Category causality must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Person', 'Organisation'),
      'causality'     : None,
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },
  """

  _message_id_list = [ 'message_category_not_set',
                       'message_category_not_associated_with_portal_type' ]
  message_category_not_set = "Category existence error for base"\
      " category ${base_category}, this category is not defined"
  message_category_not_associated_with_portal_type = "Category existence"\
      " error for base category ${base_category}, this"\
      " document has no such category"

  def _calculateArity(self, obj, base_category, portal_type):
    return len(obj.getCategoryMembershipList(base_category,
                                             portal_type=portal_type))

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    error_list = []
    portal_type = self.constraint_definition.get('portal_type', ())
    # For each attribute name, we check if defined
    for base_category in self.constraint_definition.keys():
      if base_category in ('portal_type', ):
        continue
      mapping = dict(base_category=base_category)
      # Check existence of base category
      if base_category not in obj.getBaseCategoryList():
        error_message = 'message_category_not_associated_with_portal_type'
      elif self._calculateArity(obj, base_category, portal_type) == 0:
        error_message = 'message_category_not_set'
      else:
        error_message = None

      # Raise error
      if error_message:
        error_list.append(self._generateError(obj,
                  self._getMessage(error_message), mapping))
    return error_list


class CategoryAcquiredExistence(CategoryExistence):
  """This constraint checks if an object respects the existence of a category,
  with acquisition.

    Configuration example:
    { 'id'            : 'category_existence',
      'description'   : 'Category causality must be defined',
      'type'          : 'CategoryExistence',
      'portal_type'   : ('Person', 'Organisation'),
      'causality'     : None,
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },
  """

  def _calculateArity(self, obj, base_category, portal_type):
    return len(obj.getAcquiredCategoryMembershipList(base_category,
                                             portal_type=portal_type))

