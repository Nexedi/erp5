from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
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

from .PropertyExistence import PropertyExistence

class AttributeEquality(PropertyExistence):
  """
    This constraint class allows to check / fix
    attribute values.
    Configuration example:
    { 'id'            : 'title',
      'description'   : 'Title must be "ObjectTitle"',
      'type'          : 'AttributeEquality',
      'title'         : 'ObjectTitle',
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },
  """

  _message_id_list = ['message_invalid_attribute_value',
                      'message_invalid_attribute_value_fixed']
  message_invalid_attribute_value = "Attribute ${attribute_name} "\
       "value is ${current_value} but should be ${expected_value}"
  message_invalid_attribute_value_fixed = "Attribute ${attribute_name} "\
       "value is ${current_value} but should be ${expected_value} (Fixed)"

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
      We will make sure that each non None constraint_definition is
      satisfied (equality)
    """
    errors = PropertyExistence._checkConsistency(self, obj, fixit=fixit)
    for attribute_name, expected_value in list(self.constraint_definition.items()):
      message_id = None
      mapping = {}
      # If property does not exist, error will be raised by
      # PropertyExistence Constraint.
      if obj.hasProperty(attribute_name):
        identical = 1
        if isinstance(expected_value, (list, tuple)):
          # List type
          if len(obj.getProperty(attribute_name)) != len(expected_value):
            identical = 0
          else:
            for item in obj.getProperty(attribute_name):
              if item not in expected_value:
                identical = 0
                break
        else:
          # Other type
          identical = (expected_value == obj.getProperty(attribute_name))
        if not identical:
          message_id = 'message_invalid_attribute_value'
          mapping(attribute_name=attribute_name,
                  attribute_value=obj.getProperty(attribute_name),
                  expected_value=expected_value)
      # Generate error
      if message_id is not None:
        if fixit:
          obj._setProperty(attribute_name, expected_value)
          message_id = 'message_invalid_attribute_value_fixed'
        errors.append(self._generateError(obj,
                        self._getMessage(message_id), mapping))
    return errors

