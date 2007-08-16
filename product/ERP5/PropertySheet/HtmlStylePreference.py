##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

class HtmlStylePreference:
  """
    User Preferences for HtmlStyle
  """
  
  _properties = (
    { 'id'          : 'preferred_html_style_developper_mode',
      'description' : 'When true, usefull links for developpers are shown in '\
                      'the interface.',
      'type'        : 'boolean',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_html_style_translator_mode',
      'description' : 'When true, links to translation system will be '\
                      'displayed.',
      'type'        : 'boolean',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_html_style_contextual_help',
      'description' : 'When true, links to contextual help will be displayed.',
      'type'        : 'boolean',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_html_style_documentation_base_url',
      'description' : 'Defines the base URL where portal type action '\
                      'documentation will be searched for.',
      'type'        : 'string',
      'preference'  : 1,
      'default'     : 'http://www.erp5.com/erp5_help/',
      'mode'        : 'w' },
    { 'id'          : 'preferred_string_field_width',
      'description' : 'The default width of string fields',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_textarea_width',
      'description' : 'The default width of text area fields',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_textarea_height',
      'description' : 'The default height of text area fields',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_listbox_view_mode_line_count',
      'description' : 'Number of lines in a listbox in view mode',
      'type'        : 'int',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_listbox_list_mode_line_count',
      'description' : 'Number of lines in a listbox in list mode',
      'type'        : 'int',
      'preference'  : 1,
      'mode'        : 'w' },
    { 'id'          : 'preferred_category_child_item_list_method_id',
      'description' : 'The method used to list categories in ListFields',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w' },
  )
