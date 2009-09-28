##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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

class BaseType:
    """
      Properties of an ERP5 portal type
    """

    _properties = (
        { 'id':         'type_icon',
          'storage_id': 'content_icon', # CMF Compatibility
          'type':       'string',
          'mode':       'w',
         },
        { 'id':         'type_factory_method_id',
          'storage_id': 'factory', # CMF Compatibility
          'type':       'string',
          'mode':       'w',
          'label':      'Product factory method'
         },
        { 'id':         'type_add_permission',
          'storage_id': 'permission', # CMF Compatibility
          'type':       'string',
          'mode':       'w',
          'label':      'Add permission'
         },
        { 'id':         'type_init_script_id',
          'storage_id': 'init_script', # CMF Compatibility
          'type':       'string',
          'mode':       'w',
          'label':      'Init Script'
         },
        { 'id':         'type_acquire_local_role'
        , 'storage_id': 'acquire_local_roles' # CMF Compatibility
        , 'type':       'boolean'
        , 'mode':       'w'
        , 'label':      'Acquire Local Roles'
         },
        { 'id':         'type_filter_content_type',
          'storage_id': 'filter_content_types', # CMF Compatibility
          'type':       'boolean',
          'mode':       'w',
          'label':      'Filter content types?'
         },
        { 'id':         'type_allowed_content_type'
        , 'storage_id': 'allowed_content_types' # CMF Compatibility
        , 'type':       'lines'
        , 'mode':       'w'
        , 'label':      'Allowed content types'
         },
        { 'id':         'type_hidden_content_type'
        , 'storage_id': 'hidden_content_type_list' # CMF Compatibility
        , 'type':       'lines'
        , 'mode':       'w'
        , 'label':      'Hidden content types'
         },
        { 'id':         'type_property_sheet'
        , 'storage_id': 'property_sheet_list' # CMF Compatibility
        , 'type':       'multiple selection'
        , 'mode':       'w'
        , 'label':      'Property Sheets'
        , 'select_variable':'getAvailablePropertySheetList'
         },
        { 'id':         'type_base_category'
        , 'storage_id': 'base_category_list' # CMF Compatibility
        , 'type':       'multiple selection'
        , 'mode':       'w'
        , 'label':      'Base Categories'
        , 'select_variable':'getAvailableBaseCategoryList'
         },
        { 'id':         'type_group'
        , 'storage_id': 'group_list' # CMF Compatibility
        , 'type':       'multiple selection'
        , 'mode':       'w'
        , 'label':      'Groups'
        , 'select_variable':'getAvailableGroupList'
         },
    )

