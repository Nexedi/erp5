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

class CategoryMembershipArity(Constraint):
    """
    This method check and fix if an object respects the arity.

    For example we can check if every Organisation has at
    least one address.

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

        We are looking the definition of the constraing where
        are defined the minimum and the maximum arity, and the
        list of objects we wants to check the arity.
      """

      errors = []

      # Retrieve values inside de PropertySheet (_constraints)
      base_category = self.constraint_definition['base_category']
      min_arity = int(self.constraint_definition['min_arity'])
      max_arity = int(self.constraint_definition['max_arity'])
      portal_type = self.constraint_definition['portal_type']

      # Check arity and compare it with the min and max
      arity = len(object.getCategoryMembershipList(base_category,portal_type=portal_type))
      if arity < min_arity or arity > max_arity:
        if portal_type is ():
          error_message = "Arrity error for relation '%s'" % base_category  \
                + ", arity is equal to " \
                + str(arity) \
                + " but should be between " \
                + str(min_arity) + " and " + str(max_arity)
        else:
          error_message = "Arrity error for relation '%s' and  portal_type : " % base_category  \
                + str(portal_type) \
                + ", arity is equal to " \
                + str(arity) \
                + " but should be between " \
                + str(min_arity) + " and " + str(max_arity)
        errors += [(object.getRelativeUrl(), 'CategoryMembershipArity inconsistency',104, error_message)]

      return errors
