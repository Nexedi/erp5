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

from Constraint import Constraint

class CategoryExistence(Constraint):
  """
    This method check and fix if an object respects the existence of 
    a category.
    Configuration example:
    { 'id'            : 'category_existence',
      'description'   : 'Category causality must be defined',
      'type'          : 'CategoryExistence',
      'causality'     : None,
    },
  """

  def checkConsistency(self, object, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
    """
    errors = []
    # For each attribute name, we check if defined
    for base_category in self.constraint_definition.keys():
      # Check existence of base category
      error_message = "Category existence error for base category '%s': " % \
                      base_category
      if not object.hasCategory(base_category):
        error_message += " this document has no such category"
      elif object.getProperty(base_category) is None:
        error_message += " this property was not defined"
      else:
        error_message = None
      # Raise error
      if error_message:
        errors.append(self._generateError(object, error_message))
    return errors
