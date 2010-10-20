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
  object. This is only relevant for ZODB Property Sheets (filesystem
  Property Sheets rely on Products.ERP5Type.Constraint.PropertyExistence
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

  property_sheets = (PropertySheet.SimpleItem,
                     PropertySheet.Predicate,
                     PropertySheet.Reference,
                     PropertySheet.PropertyExistenceConstraint)

  # Define by default error messages
  _message_id_list = ['message_no_such_property',
                      'message_property_not_set']
  message_no_such_property =  "Property existence error for property "\
            "${property_id}, this document has no such property"
  message_property_not_set = "Property existence error for property "\
            "${property_id}, this property is not defined"

  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkConsistency')
  def checkConsistency(self, obj, fixit=0):
    """
    Check the object's consistency.
    """
    error_list = []
    if not self.test(obj):
      return []

    # For each attribute name, we check if defined
    for property_id in self.getConstraintPropertyList() or ():
      # Check existence of property
      mapping = dict(property_id=property_id)
      if not obj.hasProperty(property_id):
        error_message_id = "message_no_such_property"
      elif obj.getProperty(property_id) is None:
        # If value is '', attribute is considered a defined
        # XXX is this the default API ?
        error_message_id = "message_property_not_set"
      else:
        error_message_id = None

      if error_message_id:
        error_list.append(self._generateError(obj,
                     self._getMessage(error_message_id), mapping))
    return error_list
