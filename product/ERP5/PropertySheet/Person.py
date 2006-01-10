#############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke <kevin_AT_nexedi_DOT_com>
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


class Person:
  """
    Person properties and categories
  """

  _properties = (
    # Personnal properties
    { 'id'         : 'password'
    , 'description': ''
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'first_name'
    , 'description': ''
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'last_name'
    , 'description': ''
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'middle_name'
    , 'description': ''
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'birth_name'
    , 'description': 'Also called maiden name.'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'prefix'
    , 'description': ''
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'suffix'
    , 'description': ''
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'birthday'
    , 'description': ''
    , 'type'       : 'date'
    , 'mode'       : 'w'
    },
    { 'id'         : 'social_code'
    , 'description': 'The social code of this person.'
    , 'type'       : 'string'
    , 'mode'       : 'w'
    },
    { 'id'         : 'partner_count'
    , 'description': ''
    , 'type'       : 'int'
    , 'mode'       : 'w'
    },
    { 'id'         : 'child_count'
    , 'description': ''
    , 'type'       : 'int'
    , 'mode'       : 'w'
    },
    # Contact fields
    { 'id'                       : 'address'
    , 'storage_id'               : 'default_address'
    , 'description'              : 'The current address of the person'
    , 'type'                     : 'content'
    , 'portal_type'              : ( 'Address', )
    , 'acquisition_base_category': ( 'subordination', )
    , 'acquisition_portal_type'  : ( 'Organisation', )
    , 'acquisition_copy_value'   : 0
    , 'acquisition_mask_value'   : 1
    , 'acquisition_sync_value'   : 0
    , 'acquisition_accessor_id'  : 'getDefaultAddressValue'
    , 'acquisition_depends'      : None
    , 'alt_accessor_id'          : ( 'getCareerDefaultAddressValue', )
    , 'mode'                     : 'w'
    },
    { 'id'                       : 'telephone'
    , 'storage_id'               : 'default_telephone'
    , 'description'              : 'The current telephone of the person'
    , 'type'                     : 'content'
    , 'portal_type'              : ( 'Telephone', )
    , 'acquisition_base_category': ( 'subordination', )
    , 'acquisition_portal_type'  : ( 'Organisation', )
    , 'acquisition_copy_value'   : 0
    , 'acquisition_mask_value'   : 1
    , 'acquisition_sync_value'   : 0
    , 'acquisition_accessor_id'  : 'getDefaultTelephoneValue'
    , 'acquisition_depends'      : None
    , 'mode'                     : 'w'
    },
    { 'id'                       : 'fax'
    , 'storage_id'               : 'default_fax'
    , 'description'              : 'The current fax of the person'
    , 'type'                     : 'content'
    , 'portal_type'              : ( 'Fax', )
    , 'acquisition_base_category': ( 'subordination', )
    , 'acquisition_portal_type'  : ( 'Organisation', )
    , 'acquisition_copy_value'   : 0
    , 'acquisition_mask_value'   : 1
    , 'acquisition_sync_value'   : 0
    , 'acquisition_accessor_id'  : 'getDefaultFaxValue'
    , 'acquisition_depends'      : None
    , 'mode'                     : 'w'
    },
    { 'id'                       : 'email'
    , 'storage_id'               : 'default_email'
    , 'description'              : 'The current email of the person'
    , 'type'                     : 'content'
    , 'portal_type'              : ( 'Email', )
    , 'acquisition_base_category': ( 'subordination', )
    , 'acquisition_portal_type'  : ( 'Organisation', )
    , 'acquisition_copy_value'   : 0
    , 'acquisition_mask_value'   : 1
    , 'acquisition_sync_value'   : 0
    , 'acquisition_accessor_id'  : 'getDefaultEmailValue'
    , 'acquisition_depends'      : None
    , 'mode'                     : 'w'
    },
    # Using an empty id generate automaticality getSubordination() and setSubordination()
    #   methods on Person. These methods allow us to save subordination on the default career.
    { 'id'                  : 'career'
    , 'storage_id'          : 'default_career'
    , 'description'         : 'The default career hold some important properties of a Person.'
    , 'type'                : 'content'
    , 'portal_type'         : ( 'Career', )
    , 'acquired_property_id': ( 'start_date', 'stop_date', 'title', 'description'
                              , 'subordination', 'subordination_title', 'subordination_value'
                              , 'subordination_uid_list', 'subordination_uid'
                              , 'collective_agreement_title', 'salary_coefficient'
                              , 'skill_list', 'skill_id_list', 'skill_title_list', 'skill_value_list'
                              , 'salary_level', 'salary_level_id', 'salary_level_title', 'salary_level_value'
                              , 'grade', 'grade_id', 'grade_title', 'grade_value'
                              , 'role', 'role_id', 'role_title', 'role_value'
                              , 'function', 'function_id', 'function_title', 'function_value'
                              )
    , 'mode'                : 'w'
    },
  )

  _categories = ( 'region', 'gender', 'product_line', 'nationality', 'marital_status',
                  'subordination', 'destination_region' )

