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
    This constraint class allows to check that a string property matches a
    regular expression.
    Configuration example:
    { 'id'            : 'title_not_empty',
      'description'   : 'Title must be defined',
      'type'          : 'StringAttributeMatch',
      'title'         : '^[^ ]'
    },
  """

  _message_id_list = PropertyExistence._message_id_list +\
                      ['message_attribute_does_not_match']

  message_attribute_does_not_match = "Attribute ${attribute_name} is "\
     "${attribute_value} and does not match ${regular_expression}."

  def _checkConsistency(self, object, fixit=0):
    """Check the object's consistency.
    Check that each attribute matches the regular expression.
    """
    error_list = PropertyExistence._checkConsistency(
                                  self, object, fixit=fixit)
    if not error_list:
      for attribute_name, regular_expression in\
                      list(self.constraint_definition.items()):
        error_message = None
        # If property does not exist, error will be raised by
        # PropertyExistence Constraint.
        current_value = object.getProperty(attribute_name)
        regexp = re.compile(regular_expression)
        if (current_value is not None) and \
            (regexp.match(current_value) is None):

          # Generate error
          error_list.append(self._generateError(object,
            self._getMessage('message_attribute_does_not_match'),
            mapping=dict(attribute_name=attribute_name,
                         attribute_value=repr(current_value),
                         regular_expression=repr(regular_expression))))
    return error_list
