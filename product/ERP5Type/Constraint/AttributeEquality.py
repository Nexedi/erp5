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

from PropertyExistence import PropertyExistence

class AttributeEquality(PropertyExistence):
  """
    This constraint class allows to check / fix
    attribute values.
    Configuration example:
    { 'id'            : 'title',
      'description'   : 'Title must be "ObjectTitle"',
      'type'          : 'AttributeEquality',
      'title'         : 'ObjectTitle',
    },
  """

  def checkConsistency(self, object, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
      We will make sure that each non None constraint_definition is 
      satisfied (equality)
    """
    errors = PropertyExistence.checkConsistency(self, object, fixit=fixit)
    for attribute_name, attribute_value in self.constraint_definition.items():
      error_message = None
      # If property does not exist, error will be raise by 
      # PropertyExistence Constraint.
      if object.hasProperty(attribute_name):
        identical = 1
        if type(attribute_value) in (type(()), type([])):
          # List type
          if len(object.getProperty(attribute_name)) != len(attribute_value):
            identical = 0
          else:
            for item in object.getProperty(attribute_name):
              if item not in attribute_value:
                identical = 0
                break
        else:
          # Other type
          identical = (attribute_value == object.getProperty(attribute_name))
        if not identical:
          # Generate error_message
          error_message =  "Attribute %s is '%s' but should be '%s'" % \
              (attribute_name, object.getProperty(attribute_name), 
               attribute_value)
      # Generate error
      if error_message is not None:
        if fixit:
          object._setProperty(attribute_name, attribute_value)
          error_message += " (Fixed)"
        errors.append(self._generateError(object, error_message))
    return errors
