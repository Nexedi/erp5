from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from .Constraint import Constraint

class PropertyExistence(Constraint):
  """
    This method checks if an object respects the existence of a property.

    For example we can check if every invoice line has a price defined
    on it.
    Configuration example:
    { 'id'            : 'property_existence',
      'description'   : 'Property price must be defined',
      'type'          : 'PropertyExistence',
      'price'         : None,
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },
  """

  _message_id_list = ['message_no_such_property',
                      # Only keeping this message for backward-compatibility
                      # as it was meaningless to call a getProperty() after
                      # hasProperty() failed
                      'message_property_not_set']
  message_no_such_property =  "Property existence error for property "\
            "${property_id}, this document has no such property or the "\
            "property has never been set"

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    error_list = []
    # For each attribute name, we check if defined
    for property_id in list(self.constraint_definition.keys()):
      # Check existence of property
      mapping = dict(property_id=property_id)
      if not obj.hasProperty(property_id):
        error_message_id = "message_no_such_property"
      else:
        error_message_id = None

      if error_message_id:
        error_list.append(self._generateError(obj,
                     self._getMessage(error_message_id), mapping))
    return error_list
