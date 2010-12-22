##############################################################################
#
# Copyright (c) 2005-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.co.jp>
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

class LocalizationPreference:
  """
    Localization-related preferences.
  """

  _properties = (
    { 'id'          : 'preferred_date_order',
      'description' : 'The order of year, month and day.',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_float_number_style',
      'description' : 'The style of float number (with comma, point, '\
                      'space, ...).',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_money_quantity_style',
      'description' : 'The style of money quantities.',
      'type'        : 'string',
      'preference'  : 1,
      'mode'        : 'w'},
    { 'id'          : 'preferred_user_interface_language',
      'description' : 'A list of languages displayed in the user interface.',
      'type'        : 'tokens',
      'default'     : (),
      'preference'  : 1,
      'mode'        : 'w'},
  )

