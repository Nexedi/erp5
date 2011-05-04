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

  _message_id_tuple = ('message_attribute_match',)

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
                       self._getMessage("message_attribute_match"),
            mapping=dict(attribute_name=property_id,
                         attribute_value=repr(current_value),
                         regular_expression=repr(regular_expression))))
    return error_list
