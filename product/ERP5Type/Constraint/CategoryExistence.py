##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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
    This method check and fix if an object respects the existence of a property.

    For example we can check if every invoice line has a price defined on it.
    """

    def __init__(self, **constraint_definition):
      """
        We need the definition list of the constraint
      """
      self.constraint_definition = constraint_definition

    def checkConsistency(self, object, fixit = 0):
      """
        this is the check method, we return a list of string,
        each string corresponds to an error.
      """

      errors = []

      # Retrieve values inside de PropertySheet (_constraints)
      property_id = self.constraint_definition['base_category']

      # Check arity and compare it with the min and max
      error_message = None
      if not object.hasCategory(base_category):
          error_message = "Category existence error for base category '%s': " % property_id  \
                + " this document has no such category"
      elif object.getProperty(property_id) is None:
          error_message = "Category existence error for base category '%s': " % property_id  \
                + " this property was not defined"
      if error_message:
        errors = [(object.getRelativeUrl(), 'CategoryMembershipArity inconsistency',104, error_message)]
      else:
        errors = []
        
      return errors
