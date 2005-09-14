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

class PropertyTypeValidity(Constraint):
  """
    This constraint class allows to check / fix type of each 
    attributes define in the PropertySheets.
    This Constraint is always created in ERP5Type/Utils.py
  """

  # Initialize type dict
  _type_dict = {
    'string':             (type('a'), ),
    'text':               (type('a'), ),
    'int':                (type(1), ),
    'boolean':            (type(1), ),
    'float':              (type(1.0), ),
    'long':               (type(1L), ),
    'lines':              (type([]), type(())),
    'tokens':             (type([]), type(())),
    'selection':          (type([]), type(())),
    'multiple selection': (type([]), type(())),
  }

  def _checkPropertiesAttributes(self):
    """
      Make sure instance has no _properties
    """
    # XXX FIXME what is _properties ?
    errors = []
    if '_properties' in object.__dict__:
      # Remove _properties
      error_message = "Instance has local _properties property"
      if fixit:
        # XXX FIXME we have to set exception name !
#           try:
        local_properties = object._properties
        del object._properties
        object._local_properties = []
        class_property_ids = object.propertyIds()
        for p in local_properties:
          if p['id'] not in class_property_ids:
            object._local_properties.append(p)
        error_message += " (Fixed)"
#           except:
#             error_message += " (ERROR)"
      errors.append(self._generateError(object, error_message))
    return errors

  def checkConsistency(self, object, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
    """
    errors = []
    # XXX FIXME Is this still useful ?
    errors.extend(self._checkPropertiesAttributes())
    # For each attribute name, we check type
    for property in object.propertyMap():
      property_id = property['id']
      property_type = property['type']
      wrong_type = 0
      value = object.getProperty(property_id)
      if value is not None:
        # Check known type
        try:
          wrong_type = (type(value) not in self._type_dict[property_type])
        except KeyError:
          wrong_type = 0
          error_message = "Attribute %s is defined with unknown type %s" % \
                          (property_id, property_type)
          errors += [(object.getRelativeUrl(), 
                     'PropertyTypeValidity inconsistency', 
                     100, error_message)]
      if wrong_type:
        # Type is wrong, so, raise constraint error
        error_message = \
            "Attribute %s should be of type %s but is of type %s" % \
            (property_id, property_type, str(type(value)))
        if fixit:
          # XXX FIXME do not use except without exception name !
#             try:
          object.setProperty(property_id, value)
          error_message += " (Fixed)"
#             except:
#               error_message += " (ERROR)"
        errors.append(self._generateError(object, error_message))
    return errors
