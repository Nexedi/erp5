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

from zLOG import LOG

class AttributeEquality(Constraint):
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

      # For each attribute name, we check equality
      for attribute_name in self.constraint_definition.keys():
        attribute_value = self.constraint_definition[attribute_name]
        if attribute_name is "mapped_value_base_category_list":
          LOG("checkConsistency", 0, str((object.id, attribute_name,attribute_value)))
        error_message = None
        if not object.hasProperty(attribute_name):
          error_message =  "Attribute %s is not defined" % attribute_name
        elif type(attribute_value) is type([]) or type(attribute_value) is type(()):
          if list(object.getProperty(attribute_name)) != list(attribute_value):
            error_message =  "Attribute %s is %s but sould be %s" % (attribute_name,
                        object.getProperty(attribute_name), attribute_value)
        elif object.getProperty(attribute_name) != attribute_value:
          error_message =  "Attribute %s is %s but sould be %s" % (attribute_name,
                        object.getProperty(attribute_name), attribute_value)
        if error_message is not None:
          if fixit:
            object._setProperty(attribute_name, attribute_value)
            error_message += " (Fixed)"
          errors += [(object.getRelativeUrl(), 'AttributeEquality inconsistency', 100, error_message)]

      return errors

