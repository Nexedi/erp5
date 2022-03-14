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
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.Utils import evaluateExpressionFromString
from Products.ERP5Type.Core.PropertyExistenceConstraint import \
    PropertyExistenceConstraint

class StringAttributeMatchConstraint(PropertyExistenceConstraint):
  """
    This constraint class allows to check that a string property matches a
    regular expression.
  """
  property_sheets = PropertyExistenceConstraint.property_sheets + \
      (PropertySheet.StringAttributeMatchConstraint,)

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    Check that each attribute matches the regular expression.
    """
    error_list = PropertyExistenceConstraint._checkConsistency(
                                                self, obj, fixit=fixit)
    if not error_list:
      regular_expression = self.getRegularExpression()
      regexp = re.compile(regular_expression)
      for property_id in self.getConstraintPropertyList():
        # If property does not exist, error will be raised by
        # PropertyExistence Constraint.
        current_value = obj.getProperty(property_id)
        if (current_value is not None) and \
            (regexp.match(current_value) is None):

          # Generate error
          error_list.append(self._generateError(
                       obj,
                       self._getMessage("message_attribute_not_match"),
            mapping=dict(attribute_name=property_id,
                         attribute_value=repr(current_value),
                         regular_expression=repr(regular_expression))))
    return error_list

  _message_id_tuple = PropertyExistenceConstraint._message_id_tuple + \
      ('message_attribute_not_match',)

  @staticmethod
  def _preConvertBaseFromFilesystemDefinition(filesystem_definition_dict):
    """
    'message_property_does_not_match' has been renamed to
    'message_property_not_match' to follow ERP5 naming conventions
    """
    filesystem_definition_dict['message_property_not_match'] = \
        filesystem_definition_dict.pop('message_property_does_not_match',
                                       None)

    return PropertyExistenceConstraint._preConvertBaseFromFilesystemDefinition(
      filesystem_definition_dict)

  @staticmethod
  def _convertFromFilesystemDefinition(**property_dict):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition

    One constraint per regular expression and containing one or several
    properties is created. Filesystem definition example:
    { 'id'            : 'title_not_empty',
      'description'   : 'Title must be defined',
      'type'          : 'StringAttributeMatch',
      'title'         : '^[^ ]'
    }
    """
    property_list = list(property_dict.keys())
    regex_list = list(property_dict.values())
    regex_list_len = len(regex_list)
    seen_property_set = set()
    for property_index, property_id in enumerate(property_list):
      if property_id in seen_property_set:
        continue

      constraint_property_list = [property_id]
      constraint_regex = regex_list[property_index]
      property_index += 1
      for regex_index, regex in enumerate(regex_list[property_index:], property_index):
        if constraint_regex == regex:
          regex_property_id = property_list[regex_index]
          constraint_property_list.append(regex_property_id)
          seen_property_set.add(regex_property_id)

      yield dict(constraint_property_list=constraint_property_list,
                 regular_expression=constraint_regex)
