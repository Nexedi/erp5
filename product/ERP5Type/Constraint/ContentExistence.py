##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type.Constraint import Constraint

class ContentExistence(Constraint):
  """
    This constraint class allows to check / fix
    that object contains one subobject.
    Configuration example:
    { 'id'            : 'line',
      'description'   : 'Object have to contain a Line',
      'type'          : 'ContentExistence',
      'portal_type'   : ('Line', ),
    },
  """

  def checkConsistency(self, object, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
      We are checking that object contains a subobject.
    """
    obj = object
    errors = []
    if self._checkConstraintCondition(object):
      # Retrieve values inside de PropertySheet (_constraints)
      portal_type = self.constraint_definition['portal_type']
      # Check arity and compare it with the min and max
      arity = len(obj.contentValues(portal_type=portal_type))
      if (arity == 0):
        # Generate error message
        error_message = "Does not contain any subobject"
        if portal_type is not ():
          error_message += " of portal type: '%s'" % str(portal_type)
        # Add error
        errors.append(self._generateError(obj, error_message))
    return errors
