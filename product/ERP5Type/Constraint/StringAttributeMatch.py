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

import re
from Products.ERP5Type.Constraint.PropertyExistence import PropertyExistence

class StringAttributeMatch(PropertyExistence):
  """
    This constraint class allows to check
    that a string property match a regular 
    expression. Configuration example:
    { 'id'            : 'title_not_empty',
      'description'   : 'Title must be defined',
      'type'          : 'StringAttributeMatch',
      'title'         : '^[^ ]'
    },
  """

  def checkConsistency(self, object, fixit=0):
    """
    This is the check method, we return a list of string,
    each string corresponds to an error.
    Check that each attribute does not match the RE
    """
    errors = PropertyExistence.checkConsistency(self, object, fixit=fixit)
    if not errors:
      for attribute_name, attribute_value in self.constraint_definition.items():
        error_message = None
        # If property does not exist, error will be raise by 
        # PropertyExistence Constraint.
        current_value = object.getProperty(attribute_name)
        regexp = re.compile(attribute_value)
        if (current_value is not None) and \
            (regexp.match(current_value) is None):
          # Generate error_message
          error_message =  "Attribute %s is '%s' and not match '%s'" % \
              (attribute_name, current_value,
               attribute_value)
          # Generate error
          errors.append(self._generateError(object, error_message))
    return errors
