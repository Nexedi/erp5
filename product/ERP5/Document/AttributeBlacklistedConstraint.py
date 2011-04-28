##############################################################################
#
# Copyright (c) 2002, 2009 Nexedi SA and Contributors. All Rights Reserved.
#                   Nicolas Delaby <nicolas@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.Utils import evaluateExpressionFromString
from Products.ERP5Type.Core.PropertyExistenceConstraint import \
    PropertyExistenceConstraint

class AttributeBlacklistedConstraint(PropertyExistenceConstraint):
  """
  This constraint class allows to check attribute non equality to a 
  list of blacklisted value
  """

  property_sheets = PropertyExistenceConstraint.property_sheets + \
                               (PropertySheet.AttributeBlacklistedConstraint,) 

  _message_id_tuple = ('message_invalid_attribute_blacklisted',)

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
      We will make sure that each non None constraint_definition is 
      satisfied
    """
    error_list = PropertyExistenceConstraint._checkConsistency(
                                                   self, obj, fixit=fixit)
    blacklisted_list_expression = self.getBlacklistedList()
    expression_context = createExpressionContext(obj)
    blacklisted_list = evaluateExpressionFromString(expression_context,
                                                    blacklisted_list_expression)
    message_id = 'message_invalid_attribute_blacklisted'
    for property_id in self.getConstraintPropertyList():

      value = obj.getProperty(property_id)
      if value in blacklisted_list:
        mapping = dict(attribute_name=property_id)
        # Generate error
        error_list.append(self._generateError(obj, 
                                              self._getMessage(message_id),
                                              mapping=mapping)
                         )
    return error_list

