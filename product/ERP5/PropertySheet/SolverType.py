##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

class SolverType:
    """
      Properties of an ERP5 Solver portal type
    """

    _properties = (
        { 'id':         'tested_property',
          'type':       'lines',
          'default'     : (),
          'mode':       'w',
          'label':      'Property to be solved'
         },
        { 'id':         'solver_action_title',
          'type':       'string',
          'mode':       'w',
          'label':      'Solver Action Title'
         },
        { 'id':         'line_groupable',
          'type':       'boolean',
          'mode':       'w',
          'label':      'Line Groupable'
         },
        { 'id':         'line_exclusive',
          'type':       'boolean',
          'mode':       'w',
          'label':      'Line Exclusive'
         },
        { 'id':         'configuration_groupable',
          'type':       'boolean',
          'mode':       'w',
          'label':      'Configuration Groupable'
         },
        { 'id':         'process_exclusive',
          'type':       'boolean',
          'mode':       'w',
          'label':      'Process Exclusive'
         },
        { 'id':         'automatic_solver',
          'type':       'boolean',
          'mode':       'w',
          'label':      'Solve automatically if True'
         },
        { 'id':         'default_configuration_property_dict_method_id',
          'type':       'string',
          'mode':       'w',
          'description':'the method used to get a dict of default properties.',
         },
        { 'id':         'configuration_property_list_dict_method_id',
          'type':       'string',
          'mode':       'w',
          'description':'the method used to get a dict of possible values.',
         },
    )

    _categories = ('conflicting_solver', 'delivery_solver',)
