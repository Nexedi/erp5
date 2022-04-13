##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Sebastien Robin <seb@nexedi.com>
#                         Jean-Paul Smets <jp@nexedi.com>
#                         Romain Courteaud <romain@nexedi.com>
#                         Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.Core.PropertyExistenceConstraint import \
     PropertyExistenceConstraint

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.CMFCore.Expression import Expression
import six

class AttributeEqualityConstraint(PropertyExistenceConstraint):
  """
  This constraint checks the values of a given attribute name on this
  object.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.AttributeEquality
  instead).

  Note that the attribute expected value is now a TALES Expression to
  be able to use any Python type and not only strings.

  For example, if we would like to check whether the attribute 'title'
  has 'ObjectTitle' as its value, we would create an 'Attribute
  Equality Constraint' within that Property Sheet and set 'title' as
  the 'Attribute Name' and 'python: "ObjectTitle"' as the 'Attribute
  Value', then set the 'Predicate' if necessary (known as 'condition'
  for filesystem Property Sheets).
  """
  meta_type = 'ERP5 Attribute Equality Constraint'
  portal_type = 'Attribute Equality Constraint'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.AttributeEqualityConstraint,)

  def _checkConsistency(self, obj, fixit=False):
    """
    Check the object's consistency
    """
    attribute_name = self.getConstraintAttributeName()

    error = self._checkPropertyConsistency(obj, attribute_name)
    if error:
      return [self._generateError(obj, self._getMessage(error),
        dict(property_id=attribute_name))]

    identical = True

    # The expected value of the attribute is a TALES Expression
    attribute_expected_value = self._getExpressionValue(
      obj, self.getConstraintAttributeValue())

    attribute_value = obj.getProperty(attribute_name)

    if isinstance(attribute_expected_value, (list, tuple)):
      # List type
      if len(attribute_value) != len(attribute_expected_value):
        identical = False
      else:
        for item in attribute_value:
          if item not in attribute_expected_value:
            identical = False
            break
    else:
      # Other primitive type
      identical = (attribute_expected_value == attribute_value)

    if not identical:
      # Generate error and fix it if required
      if fixit:
        obj._setProperty(attribute_name, attribute_expected_value)
        message_id = 'message_invalid_attribute_value_fixed'
      else:
        message_id = 'message_invalid_attribute_value'

      error = self._generateError(
        obj, self._getMessage(message_id),
        dict(attribute_name=attribute_name,
             current_value=attribute_value,
             expected_value=attribute_expected_value))

      return [error]

    return []

  _message_id_tuple = ('message_property_not_set',
                       'message_invalid_attribute_value',
                       'message_invalid_attribute_value_fixed')

  @staticmethod
  def _convertFromFilesystemDefinition(**property_dict):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition

    One constraint per property is created. Filesystem definition example:
    { 'id'            : 'title',
      'description'   : 'Title must be "ObjectTitle"',
      'type'          : 'AttributeEquality',
      'title'         : 'ObjectTitle',
      'condition'     : 'python: object.getPortalType() == 'Foo',
    }
    """
    for name, value in six.iteritems(property_dict):
      yield dict(name=value)
