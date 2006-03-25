##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

from Products.CMFCore.Expression import Expression

class DeliveryBuilder:
  """
    Properties which allow to define a generic Delivery Builder.
  """
  _properties = (
    { 'id'          : 'delivery_module',
      'description' : 'Define the module name where to create the delivery.',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'delivery_portal_type',
      'description' : 'Define the portal type of the delivery.',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'delivery_line_portal_type',
      'description' : 'Define the portal type of the delivery line.',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'delivery_cell_portal_type',
      'description' : 'Define the portal type of the delivery cell.',
      'type'        : 'string',
      'mode'        : 'w' },

    { 'id'          : 'resource_portal_type',
      'description' : 'Define the portal type of the resource.',
      'type'        : 'string',
      'mode'        : 'w' },

    { 'id'          : 'simulation_select_method_id',
      'description' : 'defines how to query all Simulation Movements which\
                       meet certain criteria',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'delivery_collect_order',
      'description' : 'defines how to group selected movements according\
                       to gathering rules',
      'type'        : 'string',
      'multivalued' : 1,
      'mode'        : 'w' },
    { 'id'          : 'delivery_line_collect_order',
      'description' : 'defines how to group selected movements according\
                       to gathering rules',
      'type'        : 'string',
      'multivalued' : 1,
      'mode'        : 'w' },
    { 'id'          : 'delivery_cell_collect_order',
      'description' : 'defines how to group selected movements according\
                       to gathering rules',
      'type'        : 'string',
      'multivalued' : 1,
      'mode'        : 'w' },
    { 'id'          : 'delivery_select_method_id',
      'description' : 'defines how to select existing Delivery which may\
                       eventually be updated with selected simulation\
                       movements',
      'type'        : 'string',
      'mode'        : 'w' },

    { 'id'          : 'delivery_cell_separate_order',
      'description' : 'defines what to do with cell which share the same\
                       properties after being collecting.',
      'type'        : 'string',
      'multivalued' : 1,
      'mode'        : 'w' },

    { 'id'          : 'delivery_module_before_building_script_id',
      'description' : 'defines a script which is called before building.',
      'type'        : 'string',
      'mode'        : 'w' },
    { 'id'          : 'delivery_after_generation_script_id',
      'description' : 'defines a script which is called on each delivery\
                       created',
      'type'        : 'string',
      'mode'        : 'w' },
  )
