##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Jean-Paul Smets-Solanes <jp@nexedi.com>
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

class Account:
  """
    Account properties and categories
  """

  _properties = (
      { 'id'        : 'credit_account',
      'storage_id'  : 'is_credit_account',
      'description' : 'Set to true if this account have a normal balance of'\
                      ' debit.',
      'type'        : 'boolean',
      'mode'        : 'w' ,
      'default'     : 0 },
 )

  _categories = ( 'account_type', 'gap', 'financial_section', )

  _constraints = (
    { 'id': 'account_type_category_existence',
      'description': 'Account Type must be set',
      'message_category_not_set': 'Account Type must be set',
      'type': 'CategoryExistence',
      'account_type' : 1,
      'condition' : 'python: object.getValidationState() not'
                     ' in ("invalidated", "deleted")'
    },
    { 'id': 'gap_category_existence',
      'description': 'GAP must be set',
      'type': 'CategoryExistence',
      'message_category_not_set': 'GAP must be set',
      'gap' : 1,
      'condition' : 'python: object.getValidationState() not'
                     ' in ("invalidated", "deleted")'
    },
 )
