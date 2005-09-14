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

from Constraint import Constraint

class PropertyExistence(Constraint):
  """
    This method check and fix if an object respects the existence of a
    property.
    For example we can check if every invoice line has a price defined
    on it.
    Configuration example:
    { 'id'            : 'property_existence',
      'description'   : 'Property price must be defined',
      'type'          : 'PropertyExistence',
      'price'         : None,
    },
  """

  def checkConsistency(self, object, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
    """
    errors = []
    # For each attribute name, we check if defined
    for property_id in self.constraint_definition.keys():
      # Check existence of property
      error_message = \
          "Property existence error for property '%s': " % property_id
      if not object.hasProperty(property_id):
        error_message += " this document has no such property"
      elif object.getProperty(property_id) is None:
        error_message += " this property was not defined"
      else:
        error_message = None
      # Return error
      error = self._generateError(object, error_message)
      if error is not None:
        errors.append(error)
    return errors
