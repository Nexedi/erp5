##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Julien Muchembled <jm@nexedi.com>
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
    Properties of an ERP5 Action Information
  """

  _properties = (
    { 'id':          'reference',
      'type':        'string',
      'mode':        'w',
      },
    { 'id':          'condition',
      'type':        'object',
      'description': 'TALES Expression to define the applicability of the' \
                     ' action',
      'mode':        'w',
      },
    { 'id':          'action_permission',
      'type':        'lines',
      'description': 'The permissions required to use the action',
      'mode':        'w',
      'default':     ['View'],
      },
    { 'id':          'float_index',
      'type':        'float',
      'description': 'Priority of the current action',
      'mode':        'w',
      'default':     1.0,
      },
    { 'id':          'visible',
      'type':        'boolean',
      'description': 'Visibility of the current action',
      'mode':        'w',
      'default':     True,
      },
    { 'id':          'action',
      'type':        'object',
      'description': 'TALES Expression to define the URL of the action',
      'mode':        'w',
      },
    { 'id':          'icon', # XXX not used
      'type':        'object',
      'description': 'TALES Expression to define the URL of the icon of the' \
                     ' action',
      'mode':        'w',
      },
  )

  _categories = ('action_type', )
