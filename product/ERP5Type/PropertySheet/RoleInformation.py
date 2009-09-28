##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

class RoleInformation:
  """
    EXPERIMENTAL - DO NOT USE THIS PROPERTYSHEET BESIDES R&D
    Properties of an ERP5 Type Role Information
  """

  _properties = (
    { 'id':          'role_name',
      'type':        'lines',
      'description': 'A list of role names defined by this Role Information',
      'default':     [],
      'mode':        'w',
      },
    { 'id':          'condition',
      'type':        'object',
      'description': 'TALES Expression to define the applicability of the' \
                     ' role',
      'mode':        'w',
      },
    { 'id':          'role_category',
      'type':        'lines',
      'description': 'Static definition of the security categories',
      'default':     [],
      'mode':        'w',
      },
    { 'id':          'role_base_category',
      'type':        'tokens',
      'description': 'Base categories to use in order to retrieve dynamic' \
                     ' security categories',
      'default':     [],
      'mode':        'w',
      },
    { 'id':          'role_base_category_script_id',
      'type':        'string',
      'description': 'Script ID to use in order retrieve dynamic' \
                     ' security categories',
      'mode':        'w',
      },
  )