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

class ActionInformation:
    """
      EXPERIMENTAL - DO NOT USE THIS PROPERTYSHEET BESIDES R&D
      Properties of an ERP5 Type action.
    """

    _properties = (
        { 'id':         'action_category',
          'storage_id': 'category', # CMF Compatibility
          'type':       'selection',
          'description':'The category of the action',
          'select_variable': 'getActionCategorySelectionList',
          'mode':       'w',
         },
        { 'id':         'condition',
          'type':       'tales',
          'description':'TALES Expression to define the applicability of the role definition',
          'mode':       'w',
         },
        { 'id':         'action_permission',
          'storage_id': 'permissions', # CMF Compatibility
          'type':       'lines',
          'description':'The permissions required to use the current view the current action',
          'mode':       'w',
         },
        { 'id':         'priority',
          'type':       'float',
          'description':'Priority of the current action',
          'mode':       'w',
         },
        { 'id':         'visible',
          'type':       'boolean',
          'description':'Visibility of the current action',
          'mode':       'w',
         },
        { 'id':         'action',
          'type':       'tales',
          'description':'TALES Expression to define the URL of the action',
          'mode':       'w',
         },
        { 'id':         'icon',
          'type':       'tales',
          'description':'TALES Expression to define the URL of the icon of the current action',
          'mode':       'w',
         },
        # This is the current way to define closed lists of values which are not categories
        { 'id'              : 'action_category_selection',
          'description'     : 'List of possible values for action_category',
          'type'            : 'tokens',
          'default'         : ['object_view', 'object_list', 'object_action',
                               'object_web_view', 'object_print', 'object_exchange',
                               'object_report', 'object_dialog', 'object_icon', ],
          'mode'            : 'w'},
    )

