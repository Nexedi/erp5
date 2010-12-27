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

class M2Constraint:
  """
    M2 Constraints
  """
  _constraints = (
     { 'id'            : 'date_existence',
       'description'   : 'Property date must be definied',
       'type'          : 'PropertyExistence',
       'date'     : None,
     },
#    { 'id'            : 'corporate_registration_code_existence',
#      'description'   : 'Property corporate registration code must be definied',
#      'type'          : 'PropertyExistence',
#      'corporate_registration_code'          : None, 
#      'message_no_such_property': 'The corporate registration must be defined',
#    },
#    { 'id'            : 'old_headquarters_existence',
#      'description'   : 'Property old_headquarters must be definied',
#      'type'          : 'PropertyExistence',
#      'old_headquarters'       : None, 
#    },
#    { 'id'            : 'old_legal_form_existence',
#      'description'   : 'Property old_legal_form must be definied',
#      'type'          : 'PropertyExistence',
#      'old_legal_form'  : None, 
#    },
#    { 'id'            : 'old_corporate_registration_code_existence',
#      'description'   : 'Property old corporate registration code must be definied',
#      'type'          : 'PropertyExistence',
#      'old_corporate_registration_code'    : None, 
#    },
#    { 'id'            : 'new_corporate_registration_code_existence',
#      'description'   : 'Property new corporate registration code must be definied',
#      'type'          : 'PropertyExistence',
#      'new_corporate_registration_code'    : None, 
#    },
#    { 'id'            : 'old_title_existence',
#      'description'   : 'Property old_title must be definied',
#      'type'          : 'PropertyExistence',
#      'old_title'      : None, 
#    },
#    { 'id'            : 'new_address_existence',
#      'description'   : 'Property new address must be definied',
#      'type'          : 'PropertyExistence',
#      'new_address'      : None, 
#    },
#    { 'id'            : 'first_rccm_check_existence',
#      'description'   : 'Property first rccm check must be definied',
#      'type'          : 'PropertyExistence',
#      'first_rccm_check'     : None,
#      'condition'     : 'python: object.getSecondRccmCheck() == None',
#    },
#    { 'id'            : 'second_rccm_check_existence',
#      'description'   : 'Property radiation check must be definied',
#      'type'          : 'PropertyExistence',
#      'second_rccm_check'     : None,
#      'condition'     : 'python: object.getFirstRccmCheck() == None',
#
#    },
  )
