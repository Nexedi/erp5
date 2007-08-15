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

from Constraint import Constraint
from DateTime import DateTime

try:
  boolean_types = (int, bool)
except NameError:
  boolean_types = (int, )

class PropertyTypeValidity(Constraint):
  """
    This constraint class allows to check / fix type of each
    attributes defined in the PropertySheets.
    This Constraint is always created in ERP5Type/Utils.py
  """

  # Initialize type dict
  _type_dict = {
    'string':             (str, ),
    'text':               (str, ),
    'int':                (int, ),
    'boolean':            boolean_types,
    'float':              (float, ),
    'long':               (long, ),
    'tales':              (str, ),
    'lines':              (list, tuple),
    'tokens':             (list, tuple),
    'selection':          (list, tuple),
    'multiple selection': (list, tuple),
    'date':               (DateTime, ),
  }

  # Properties of type eg. "object" can hold anything
  _permissive_type_list = ('object')

  def checkConsistency(self, obj, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
    """
    errors = []
    # For each attribute name, we check type
    for prop in obj.propertyMap():
      property_id = prop['id']
      if prop.get('multivalued', 0):
        property_type = 'lines'
      else:
        property_type = prop['type']
      if property_type in self._permissive_type_list:
        continue
      wrong_type = 0
      if property_type == 'tales':
        value = obj.getProperty(property_id, evaluate=0)
      else:
        value = obj.getProperty(property_id)
      if value is not None:
        # Check known type
        try:
          wrong_type = not isinstance(value, self._type_dict[property_type])
        except KeyError:
          wrong_type = 0
          error_message = "Attribute %s is defined with unknown type %s" % \
                          (property_id, property_type)
          errors.append(self._generateError(obj, error_message))
      if wrong_type:
        # Type is wrong, so, raise constraint error
        error_message = \
            "Attribute %s should be of type %s but is of type %s" % \
            (property_id, property_type, str(type(value)))
        if fixit:
          # try to cast to correct type
          if wrong_type:
            try:
              value = self._type_dict[property_type][0](value)
            except (KeyError, ValueError), error:
              error_message += " (Type cast failed : %s)" % error
            else:
              obj.setProperty(property_id, value)
              error_message += " (Fixed)"
        errors.append(self._generateError(obj, error_message))
      elif fixit:
        oldvalue = getattr(obj, property_id, value)
        if oldvalue != value:
          obj.setProperty(property_id, oldvalue)
    return errors
