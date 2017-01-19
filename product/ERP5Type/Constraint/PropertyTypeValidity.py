##############################################################################
#
# Copyright (c) 2002-2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

boolean_type_list = (int, bool)

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
    'boolean':            boolean_type_list,
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
  _permissive_type_list = ('object', 'data')

  # Properties which shall be never set on object.
  _wrong_property_id_list = ('creation_date', 'modification_date')

  _message_id_list = [ 'message_unknown_type',
                       'message_incorrect_type',
                       'message_incorrect_type_fix_failed',
                       'message_incorrect_type_fixed',
                       'message_local_property_migrated',
                       'message_wrong_property_dropped']

  message_unknown_type = "Attribute ${attribute_name} is defined with"\
                         " an unknown type ${type_name}"
  message_incorrect_type = "Attribute ${attribute_name}"\
    " should be of type ${expected_type} but is of type ${actual_type}"
  message_incorrect_type_fix_failed = "Attribute ${attribute_name}"\
    " should be of type ${expected_type} but is of type ${actual_type}"\
    " (Type cast failed with error ${type_cast_error})"
  message_incorrect_type_fixed = "Attribute ${attribute_name}"\
    " should be of type ${expected_type} but is of type ${actual_type} (Fixed)"
  message_local_property_migrated = "Property ${property_id} was migrated from local properties."
  message_wrong_property_dropped = "Wrong property ${property_id} dropped from object dict."

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    error_list = []
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
      elif any(t in (list, tuple) for t in self._type_dict[property_type]):
        value = obj.getPropertyList(property_id)
      else:
        value = obj.getProperty(property_id)
      if value is not None:
        # Check known type
        try:
          wrong_type = not isinstance(value, self._type_dict[property_type])
        except KeyError:
          wrong_type = 0
          error_list.append(self._generateError(obj,
            self._getMessage('message_unknown_type'),
             mapping=dict(attribute_name=property_id,
                          type_name=property_type)))

      if wrong_type:
        # Type is wrong, so, raise constraint error
        error_message = 'message_incorrect_type'
        mapping = dict(attribute_name=property_id,
                       expected_type=property_type,
                       actual_type=str(type(value)))
        if fixit:
          # try to cast to correct type
          if wrong_type:
            try:
              value = self._type_dict[property_type][0](value)
            except (KeyError, ValueError), error:
              error_message = 'message_incorrect_type_fix_failed'
              mapping['type_cast_error'] = str(error)

            else:
              obj.setProperty(property_id, value)
              error_message = 'message_incorrect_type_fixed'

        error_list.append(self._generateError(obj,
            self._getMessage(error_message), mapping))
      elif fixit:
        if property_id in \
          [x['id'] for x in getattr(obj, '_local_properties', ())]:
          # if this property was a local property and has been later added in a
          # property sheet, we want to remove it from _local_properties
          # but as property key in local_properties does not have to match
          # property sheet key name, just all properties will be tried to be migrated
          obj._local_properties = tuple([x for x in obj._local_properties
                                         if x['id'] != property_id])
          oldvalue = getattr(obj, property_id, value)
          if oldvalue != value and \
            property_id not in self._wrong_property_id_list:
            # drop totally low level properties
            obj.setProperty(property_id, oldvalue)
          if property_id not in \
              [x['id'] for x in getattr(obj, '_local_properties', ())]:
            error_list.append(self._generateError(obj,
              self._getMessage('message_local_property_migrated'), dict(
                property_id=property_id)))
        if property_id in self._wrong_property_id_list:
          # drop totally low level properties
          if obj.__dict__.pop(property_id, None) is not None:
            error_list.append(self._generateError(obj,
              self._getMessage('message_wrong_property_dropped'), dict(
                property_id=property_id)))

    return error_list
