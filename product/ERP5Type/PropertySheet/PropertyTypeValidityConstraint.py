##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

class PropertyTypeValidityConstraint:
  """
  Define an Attribute Equality Constraint for ZODB Property Sheets
  """
  _properties = (
    {'id': 'message_unknown_type',
     'type': 'string',
     'description' : "Error message when the attribute's type is unknown",
     'default': "Attribute ${attribute_name} is defined with an unknown "\
                "type ${type_name}" },
    {'id': 'message_incorrect_type',
     'type': 'string',
     'description' : "Error message when the type of attribute's value is "\
                     "incorrect",
     'default': "Attribute ${attribute_name} should be of type "\
                "${expected_type} but is of type ${actual_type}" },
    {'id': 'message_incorrect_type_fix_failed',
     'type': 'string',
     'description' : "Error message when the type of attribute's value is "\
                     "incorrect and it could not be fixed",
     'default': "Attribute ${attribute_name} should be of type "\
                "${expected_type} but is of type ${actual_type} (Type cast "\
                "failed with error ${type_cast_error})" },
    {'id': 'message_incorrect_type_fixed',
     'type': 'string',
     'description' : "Error message when the type of attribute's value is "\
                     "incorrect but could be fixed",
     'default': "Attribute ${attribute_name} should be of type "\
                "${expected_type} but is of type ${actual_type} (Fixed)" },
    )
