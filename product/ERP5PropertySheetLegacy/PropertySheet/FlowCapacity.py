##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

class FlowCapacity:
  """
        Properties for Path.
  """

  _properties = (
    # Accounting
    # XXX efficiency is already defined on Amount
    # Need to be removed
    { 'id'          : 'efficiency',
      'description' : """The efficiency.""",
      'type'        : 'float',
      'default'     : 1.0,
      'mode'        : 'w' },
    { 'id'          : 'min_flow',
      'description' : """Minimal quantity to use on a movement.""",
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
    { 'id'          : 'max_flow',
      'description' : """Maximal quantity to use on a movement.""",
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
    { 'id'          : 'min_delay',
      'description' : """The minimal delay time of a movement process.""",
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
    { 'id'          : 'max_delay',
      'description' : """The maximal delay time of a movement process.""",
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
    { 'id'          : 'min_stock',
      'description' : """The minimal stock quantity of a resource.""",
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
    { 'id'          : 'max_stock',
      'description' : """The maximal stock quantity of a resource.""",
      'type'        : 'float',
      'default'     : 0.0,
      'mode'        : 'w' },
  )

  _categories = ('quantity_unit',)
