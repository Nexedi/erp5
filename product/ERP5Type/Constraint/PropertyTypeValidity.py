##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
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
from string import split

class PropertyTypeValidity(Constraint):
    """
      This constraint class allows to check / fix
      SetMappedValue object definitions:

      - modified attributes

      - modified base categories

      - domain base categories

      It is used for example in Transformations to check that elements
      of an XMLMatrix include appropriate attributes which participate
      in the price calculation.

      We consider that a list can be equal to a tuple.
    """

    def checkConsistency(self, object, fixit = 0):
      """
        This is the check method, we return a list of string,
        each string corresponds to an error.

        We will make sure that each non None constraint_definition is satisfied
        (equality)
      """

      errors = []

      # Make sure instance has no _properties
      if '_properties' in object.__dict__:
        # Remove _properties
        error_message =  "Instance has local _properties property"
        if fixit:
          try:
            local_properties = object._properties
            del object._properties
            object._local_properties = []
            class_property_ids = object.propertyIds()
            for p in local_properties:
              if p['id'] not in class_property_ids:
                object._local_properties.append(p)
            error_message += " (Fixed)"
          except:
            error_message += " (ERROR)"
        errors += [(object.getRelativeUrl(), 'PropertyTypeValidity inconsistency',
                                                                100, error_message)]

      # For each attribute name, we check equality
      for property in object.propertyMap():
        property_id = property['id']
        property_type = property['type']
        wrong_type = 0
        value = object.getProperty(property_id)
        if value is not None:
          if property_type == 'string' or property_type == 'text':
            wrong_type = type(value) is not type('a')
          elif property_type == 'int' or property_type == 'boolean':
            wrong_type = type(value) is not type(1)
          elif property_type == 'float':
            wrong_type = type(value) is not type(1.0)
          elif property_type == 'lines' or property_type == 'tokens'\
            or property_type == 'selection' or property_type == 'multiple selection':
            wrong_type = type(value) is not type([]) and type(value) is not type(())

        if wrong_type:
          error_message =  "Attribute %s should be of type %s but is of type %s" % (property_id,
                        property_type, str(type(value)))
          if fixit:
            try:
              object.setProperty(property_id, value)
              error_message += " (Fixed)"
            except:
              error_message += " (ERROR)"

          errors += [(object.getRelativeUrl(), 'PropertyTypeValidity inconsistency',
                                                                   100, error_message)]

      return errors

