##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved
#                    Lukasz Nowak <luke@nexedi.com>
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

class SoftwareInstanceConstraint:
  """Constraints for Software Instance"""
  _constraints = (
    { 'id'            : 'text_content_existence',
      'description'   : 'Property text content must be defined',
      'type'          : 'PropertyExistence',
      'text_content'  : None,
      "message_property_not_set" : 'XML must be set',
      "message_no_such_property" : 'XML must be set'
    },
    { 'id'            : 'reference_property_existence',
      'description'   : 'Property reference must be defined',
      'type'          : 'PropertyExistence',
      'reference'     : None,
      "message_property_not_set" : 'Reference must be set',
      "message_no_such_property" : 'Reference must be set'
    },
    { 'id'            : 'property_existence',
      'description'   : 'Property source reference must be defined',
      'type'          : 'PropertyExistence',
      'source_reference'     : None,
      "message_property_not_set" : 'Source Reference must be set',
      "message_no_such_property" : 'Source Reference must be set'
    },
    { 'id'            : 'destination_reference_property_existence',
      'description'   : 'Property destination reference must be defined',
      'type'          : 'PropertyExistence',
      'destination_reference'     : None,
      "message_property_not_set" : 'Destination Reference must be set',
      "message_no_such_property" : 'Destination Reference must be set'
    },
    { 'id'            : 'ssl_key',
      'description'   : 'Property SSL Key must be defined',
      'type'          : 'PropertyExistence',
      'ssl_key'     : None,
      "message_property_not_set" : 'SSL Key must be set',
      "message_no_such_property" : 'SSL Key must be set'
    },
    { 'id'            : 'ssl_certificate',
      'description'   : 'Property SSL Certificate must be defined',
      'type'          : 'PropertyExistence',
      'ssl_certificate'     : None,
      "message_property_not_set" : 'SSL Certificate must be set',
      "message_no_such_property" : 'SSL Certificate must be set'
    },
    { 'id'            : 'text_content_validation',
      'description'   : 'Property text content must be valid against Softwa'\
                        're Instance XSD',
      'type'          : 'SoftwareInstanceXmlValidationConstraint',
    },
  )
