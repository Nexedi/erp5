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

class P0Constraint:
  """
    P0 Constraints
  """
  _constraints = (
    { 'id'            : 'last_name_existence',
      'description'   : 'Property last name must be definied',
      'type'          : 'PropertyExistence',
      'last_name'         : None, 
      'message_no_such_property': 'The last name must be defined',
      'message_property_not_set': 'The last name must be defined',
    },
    { 'id'            : 'first_name_existence',
      'description'   : 'Property first name  code must be definied',
      'type'    : 'PropertyExistence',
      'first_name'          : None, 
      'message_no_such_property': 'The first name address must be defined',
      'message_property_not_set': 'The first name address must be defined',
    },
    { 'id'            : 'date_exitence',
      'description'   : 'Property date must be definied',
      'type'    : 'PropertyExistence',
      'date'          : None,
    },
    { 'id'            : 'miss_check_existence',
      'description'   : 'Property miss check must be definied',
      'type'          : 'PropertyExistence',
      'miss_check'    : None, 
      'condition'     : 'python: object.getMrsCheck() == None \
                              and object.getMrCheck() == None',
    },
    { 'id'            : 'mrs_check_existence',
      'description'   : 'Property mrs check must be definied',
      'type'          : 'PropertyExistence',
      'mrs_check'     : None, 
      'condition'     : 'python: object.getMissCheck() == None \
                               and object.getMrCheck() == None',
    },
    { 'id'            : 'mr_check_existence',
      'description'   : 'Property mr check must be definied',
      'type'          : 'PropertyExistence',
      'mr_check'      : None, 
      'condition'     : 'python: object.getMrsCheck() == None \
                            and object.getMissCheck() == None',
    },
    { 'id'            : 'divorced_check_existence',
      'description'   : 'Property divorced check must be definied',
      'type'          : 'PropertyExistence',
      'divorced_check'     : None, 
      'condition'     : 'python: object.getMarriedCheck() == None and \
                                  object.getSingleCheck() == None and \
                                  object.getWidowerCheck() == None',
    },
    { 'id'            : 'married_check_existence',
      'description'   : 'Property married check must be definied',
      'type'          : 'PropertyExistence',
      'married_check'     : None, 
      'condition'     : 'python: object.getDivorcedCheck() == None and \
                                 object.getSingleCheck() == None and \
                                 object.getWidowerCheck() == None',
    },
    { 'id'            : 'single_check_existence',
      'description'   : 'Property single check must be definied',
      'type'          : 'PropertyExistence',
      'single_check'     : None, 
      'condition'     : 'python: object.getMarriedCheck() == None and \
                                 object.getDivorcedCheck() == None and \
                                 object.getWidowerCheck() == None',
    },
    { 'id'            : 'widower_check_existence',
      'description'   : 'Property Widower check must be definied',
      'type'          : 'PropertyExistence',
      'widower_check'     : None, 
      'condition'     : 'python: object.getMarriedCheck() == None and \
                                 object.getSingleCheck() == None and \
                                 object.getDivorcedCheck() == None',
    },
    { 'id'            : 'creation_check_existence',
      'description'   : 'Property creation check must be definied',
      'type'          : 'PropertyExistence',
      'creation_check'          : None,
      'condition'     : 'python: object.getOtherCheck() == None \
                             and object.getPurchaseCheck() == None \
                             and object.getContributionCheck() == None \
                             and object.getRentCheck() == None ',
    },
    { 'id'            : 'purchase_check_existence',
      'description'   : 'Property purchase check must be definied',
      'type'          : 'PropertyExistence',
      'purchase_check'          : None,
      'condition'     : 'python: object.getCreationCheck() == None \
                             and object.getOtherCheck() == None \
                             and object.getContributionCheck() == None \
                             and object.getRentCheck() == None ',
    },
    { 'id'            : 'contribution_check_existence',
      'description'   : 'Property contribution check must be definied',
      'type'          : 'PropertyExistence',
      'contribution_check'          : None,
      'condition'     : 'python: object.getCreationCheck() == None \
                             and object.getPurchaseCheck() == None \
                             and object.getOtherCheck() == None \
                             and object.getRentCheck() == None ',
    },
    { 'id'            : 'rent_check_existence',
      'description'   : 'Property rent check must be definied',
      'type'          : 'PropertyExistence',
      'rent_check'          : None,
      'condition'     : 'python: object.getCreationCheck() == None \
                             and object.getPurchaseCheck() == None \
                             and object.getContributionCheck() == None \
                             and object.getOtherCheck() == None ',
    },
    { 'id'            : 'other_check_existence',
      'description'   : 'Property other check must be definied',
      'type'          : 'PropertyExistence',
      'other_check'          : None,
      'condition'     : 'python: object.getCreationCheck() == None \
                             and object.getPurchaseCheck() == None \
                             and object.getContributionCheck() == None \
                             and object.getRentCheck() == None ',
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
    { 'id'            : 'previous_activity_corporate_registration_code_existence',
      'description'   : 'Property must be definied',
      'type'          : 'PropertyExistence',
      'previous_activity_corporate_registration_code'     : None,
      'condition'     : 'python: object.getActivityRestartCheck() ==1',
      'message_no_such_property': 'for a restart activity you must define the previous registration code',
      'message_property_not_set': 'for a restart activity you must define the previous registration code',
    },
  )
