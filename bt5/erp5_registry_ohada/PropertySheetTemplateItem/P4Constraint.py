#############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
#                         Thibaut Deheunynck <thibaut@nexedi.com>
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

class P4Constraint:
  """
    P4 Constraints
  """
  _constraints = (
    { 'id'            : 'owner_last_name_existence',
      'description'   : 'Property owner last name must be definied',
      'type'          : 'PropertyExistence',
      'owner_last_name'         : None, 
      'message_no_such_property': 'The owner last name must be defined',
    },
    { 'id'            : 'owner_first_name_existence',
      'description'   : 'Property owner first name  code must be definied',
      'type'    : 'PropertyExistence',
      'owner_first_name'          : None, 
      'message_no_such_property': 'The owner first name address must be defined',
    },
    { 'id'            : 'corporate_registration_code_existence',
      'description'   : 'Property corporate registration code must be definied',
      'type'          : 'PropertyExistence',
      'corporate_registration_code'  : None,
    },
    { 'id'            : 'date_existence',
      'description'   : 'Property date must be definied',
      'type'          : 'PropertyExistence',
      'date'  : None,
    },
    { 'id'            : 'ask_to_change_check_existence',
      'description'   : 'Property ask_to_change_check must be definied',
      'type'          : 'PropertyExistence',
      'ask_to_change_check'     : None,
      'condition'     : 'python: object.getAskToChangeCheck() == None',
    },
    { 'id'            : 'ask_to_delete_check_existence',
      'description'   : 'Property ask_to_delete_check check must be definied',
      'type'          : 'PropertyExistence',
      'ask_to_delete_check'     : None, 
      'condition'     : 'python: object.getAskToChangeCheck() == None',
    },
  )
