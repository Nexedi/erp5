##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
        # Personal properties
        {   'id'          : 'first_name',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'last_name',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'middle_name',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'prefix',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'suffix',
            'description' : '',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'birthday',
            'description' : '',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'social_code',
            'description' : 'The social code of this person',
            'type'        : 'string',
            'mode'        : 'w' },                                                     
        # Contact fields
        { 'id'          : 'address',
          'storage_id'  : 'default_address',
          'description' : 'The organisations this persons works for',
          'type'        : 'content',
          'portal_type' : ('Address'),
          'acquisition_base_category' : ('subordination', ),
          'acquisition_portal_type'   : ('Organisation',),
          'acquisition_copy_value'    : 0,
          'acquisition_mask_value'    : 1,
          'acquisition_sync_value'    : 0,
          'acquisition_accessor_id'   : 'getDefaultAddressValue',
          'acquisition_depends'       : None,
          'mode'        : 'w' },
        { 'id'          : 'telephone',
          'storage_id'  : 'default_telephone',
          'description' : 'The organisations this persons works for',
          'type'        : 'content',
          'portal_type' : ('Telephone'),
          'acquisition_base_category' : ('subordination', ),
          'acquisition_portal_type'   : ('Organisation',),
          'acquisition_copy_value'    : 0,
          'acquisition_mask_value'    : 1,
          'acquisition_sync_value'    : 0,
          'acquisition_accessor_id'   : 'getDefaultTelephoneValue',
          'acquisition_depends'       : None,
          'mode'        : 'w' },
        { 'id'          : 'fax',
          'storage_id'  : 'default_fax',
          'description' : 'The organisations this persons works for',
          'type'        : 'content',
          'portal_type' : ('Fax'),
          'acquisition_base_category' : ('subordination', ),
          'acquisition_portal_type'   : ('Organisation',),
          'acquisition_copy_value'    : 0,
          'acquisition_mask_value'    : 1,
          'acquisition_sync_value'    : 0,
          'acquisition_accessor_id'   : 'getDefaultFaxValue',
          'acquisition_depends'       : None,
          'mode'        : 'w' },
        { 'id'          : 'email',
          'storage_id'  : 'default_email',
          'description' : 'The organisations this persons works for',
          'type'        : 'content',
          'portal_type' : ('Email'),
          'acquisition_base_category' : ('subordination', ),
          'acquisition_portal_type'   : ('Organisation',),
          'acquisition_copy_value'    : 0,
          'acquisition_mask_value'    : 1,
          'acquisition_sync_value'    : 0,
          'acquisition_accessor_id'   : 'getDefaultEmailValue',
          'acquisition_depends'       : None,
          'mode'        : 'w' },
        # Subordination properties
        { 'id'          : 'career',
          'storage_id'  : 'default_career',
          'description' : 'The current career status of a person.',
          'type'        : 'content',
          'portal_type' : ('Career'),

#           'acquisition_base_category' : ('subordination', ),  # Useless
#           'acquisition_portal_type'   : ('Organisation',),  # Useless
#           'acquisition_copy_value'    : 0,  # Useless
#           'acquisition_mask_value'    : 1,  # Useless
#           'acquisition_sync_value'    : 0,  # Useless
#           'acquisition_accessor_id'   : 'getDefaultEmailValue',  # Useless
#           'acquisition_depends'        : None,
                    
          
          'acquired_property_id'       : ('title', 'subordination_title', 'subordination'), # User address_region_uid_list to forward accessors
          'mode'        : 'w' }, 
        )

    _categories = ( 'group', 'market_segment', 'region',
                    'gender', 'product_line', 'subordination', 'nationality',)

