##############################################################################
#
# Copyright (c) 2002-2010 Nexedi SARL and Contributors. All Rights Reserved.
#                         Sebastien Robin <seb@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet

class PropertyExistenceConstraint(ConstraintMixin):
  """
  This constraint checks whether a property has been defined on this
  object.

  This is only relevant for ZODB Property Sheets (filesystem Property
  Sheets rely on Products.ERP5Type.Constraint.PropertyExistence
  instead).

  For example, if we would like to check whether an invoice line has a
  'price' property defined on it, we would create a 'Property
  Existence Constraint' within that property sheet and add 'price' to
  the 'Properties' field, then set the 'Predicate' if necessary (known
  as 'condition' for filesystem Property Sheets).
  """
  meta_type = 'ERP5 Property Existence Constraint'
  portal_type = 'Property Existence Constraint'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ConstraintMixin.property_sheets + \
                    (PropertySheet.PropertyExistenceConstraint,)

  def _checkPropertyConsistency(self, obj, property_id):
    """
    Check the consistency of the object only for the given Property ID
    and is meaningful for child constraints which only need to check
    one property
    """
    # Check whether the property exists and has been set
    if not obj.hasProperty(property_id):
      return "message_no_such_property"

    return None

  def _checkConsistency(self, obj, fixit=False):
    """
    Check the object's consistency
    """
    error_list = []
    # For each attribute name, we check if defined
    for property_id in self.getConstraintPropertyList():
      error_message_id = self._checkPropertyConsistency(obj, property_id)
      if error_message_id is not None:
        error_list.append(self._generateError(
          obj, self._getMessage(error_message_id),
          dict(property_id=property_id)))

    return error_list

  _message_id_tuple = ('message_no_such_property',)

  @staticmethod
  def _preConvertBaseFromFilesystemDefinition(filesystem_definition_dict):
    """
    Remove 'message_property_not_set' which used to be defined in
    filesystem Property Existence constraint but were useless, so
    remove it before converting the constraint for backward
    compatibility
    """
    filesystem_definition_dict.pop('message_property_not_set', None)
    return {}

  @staticmethod
  def _convertFromFilesystemDefinition(**property_dict):
    """
    @see ERP5Type.mixin.constraint.ConstraintMixin._convertFromFilesystemDefinition

    Filesystem definition example:
    { 'id'            : 'property_existence',
      'description'   : 'Property price must be defined',
      'type'          : 'PropertyExistence',
      'price'         : None,
      'condition'     : 'python: object.getPortalType() == 'Foo',
    }
    """
    yield dict(constraint_property_list=list(property_dict.keys()))
