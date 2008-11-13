##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

class Preference:
  """
    User Preference PropertySheet

    XXX: why is this here and not in ERP5Form ?
  """
  
  _properties = (
    { 'id'          : 'priority',
      'description' : 'Priority of the preference.',
      'type'        : 'int',
      'default'     : 3, # ( Priority.USER )
      'mode'        : 'w',
      'write_permission': 'View management screens', },
    { 'id'          : 'preferred_section_category',
      'description' : 'The section category for documents; '\
                         'usually something like group/nexedi.',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_section',
      'description' : 'The section Organisation for documents.',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_date_order',
      'description' : 'The order of year, month and day.',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_money_quantity_style',
      'description' : 'The style of money quantities.',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_text_editor',
      'description' : 'Preferred Text Editor',
      'type'        : 'selection',
      'select_variable' : 'getPreferredTextEditorSelectionList',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'          : 'preferred_text_format',
      'description' : 'Preferred Text Format',
      'type'        : 'selection',
      'select_variable' : 'getPreferredTextFormatSelectionList',
      'preference'  : 1,
      'mode'        : '' },
    { 'id'              : 'preferred_text_editor_selection',
      'description'     : 'List of possible values for preferred_document_text_editor',
      'type'            : 'tokens',
      'default'         : ['text_area','fck_editor',],
      'mode'            : 'w'},
    { 'id'              : 'preferred_text_format_selection',
      'description'     : 'List of possible values for preferred_document_text_format',
      'type'            : 'tokens',
      'default'         : ['plain','html',],
      'mode'            : 'w'},
    { 'id'              : 'preferred_time_zone',
      'description'     : 'Preferred timezone',
      'type'            : 'string',
      'default'         : '',
      'mode'            : 'w'},
      { 'id'            : 'preferred_max_user_inactivity_duration',
      'description'     : 'Maximum user\'s inactivity duration in seconds before user is automatically logged out',
      'type'            : 'float',
      'default'         : '',
      'mode'            : 'w'},
  )

