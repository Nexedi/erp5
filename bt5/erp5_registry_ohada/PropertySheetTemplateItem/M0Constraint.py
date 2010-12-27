#############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
#                         Fabien Morin <fabien@nexedi.com>
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

class M0Constraint:
  """
    M0 Constrants
  """
  _constraints = (
    { 'id'            : 'title_existence',
      'description'   : 'Property title must be definied',
      'type'          : 'PropertyExistence',
      'title'         : None, 
      'message_no_such_property': 'The naming must be defined',
    },
    { 'id'            : 'name_existence',
      'description'   : 'Property name must be definied',
      'type'          : 'PropertyExistence',
      'name'          : None, 
      'message_no_such_property': 'The commercial name must be defined',
    },
    { 'id'            : 'head_office_address_existence',
      'description'   : 'Property address must be definied',
      'type'          : 'PropertyExistence',
      'head_office_address'       : None, 
    },
    { 'id'            : 'work_address_existence',
      'description'   : 'Property work_address must be definied',
      'type'          : 'PropertyExistence',
      'work_address'  : None, 
    },
    { 'id'            : 'legal_form_existence',
      'description'   : 'Property legal_form must be definied',
      'type'          : 'PropertyExistence',
      'legal_form'    : None, 
    },
    { 'id'            : 'duration',
      'description'   : 'Property duration must be definied',
      'type'          : 'PropertyExistence',
      'duration'      : None, 
    },
    { 'id'            : 'activity_free_text_existence',
      'description'   : 'Property activity_free_text must be definied',
      'type'          : 'PropertyExistence',
      'activity_free_text': None, 
    },
    { 'id'            : 'first_administrator_lastname_existence',
      'description'   : 'Property first_administrator_lastname must be definied',
      'type'          : 'PropertyExistence',
      'first_administrator_lastname': None, 
    },
    { 'id'            : 'first_administrator_firstname_existence',
      'description'   : 'Property first_administrator_firstname must be definied',
      'type'          : 'PropertyExistence',
      'first_administrator_firstname' : None, 
    },
    { 'id'            : 'first_administrator_birthday_existence',
      'description'   : 'Property first_administrator_birthday must be definied',
      'type'          : 'PropertyExistence',
      'first_administrator_birthday' : None, 
    },
    { 'id'            : 'first_administrator_birthplace_existence',
      'description'   : 'Property first_administrator_birthplace must be definied',
      'type'          : 'PropertyExistence',
      'first_administrator_birthplace' : None, 
    },
    { 'id'            : 'first_administrator_address_existence',
      'description'   : 'Property first_administrator_address must be definied',
      'type'          : 'PropertyExistence',
      'first_administrator_address': None, 
    }, 
    { 'id'            : 'date_existence',
      'description'   : 'Property date must be definied',
      'type'          : 'PropertyExistence',
      'date'     : None,
    },
    { 'id'            : 'rccm_check_existence',
      'description'   : 'Property rccm check must be definied',
      'type'          : 'PropertyExistence',
      'rccm_check'     : None,
      'condition'     : 'python: object.getInscriptionCheck() == None',
    },
    { 'id'            : 'inscription_check_existence',
      'description'   : 'Property inscription check must be definied',
      'type'          : 'PropertyExistence',
      'inscription_check'     : None,
      'condition'     : 'python: object.getRccmCheck() == None',
    },
  )
