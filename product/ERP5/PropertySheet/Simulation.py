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

class Simulation:
  """
      Attributes used in the optimisation of the simulation
  """

  _properties = (
        # Change of dates and quantities
        {   'id'          : 'quantity_frozen',
            'description' : 'If set to 1, the quantity can not be changed',
            'type'        : 'boolean',
            'mode'        : 'w' },
        {   'id'          : 'start_date_frozen',
            'description' : 'If set to 1, the start date can not be changed',
            'type'        : 'boolean',
            'mode'        : 'w' },
        {   'id'          : 'stop_date_frozen',
            'description' : 'If set to 1, the stop date can not be changed',
            'type'        : 'boolean',
            'mode'        : 'w' },
        # Change of dates and quantities
        {   'id'          : 'orderable',
            'description' : 'If set to 1, self must be associated to an order',
            'type'        : 'boolean',
            'mode'        : 'w' },
        {   'id'          : 'deliverable',
            'description' : 'If set to 1, self must be associated to a delivery',
            'type'        : 'boolean',
            'mode'        : 'w' },


        {   'id'          : 'delivery_ratio',
            'description' : 'ratio to apply on the quantity property of the' \
                            'corresponding delivery to obtain the current quantity',
            'default'     : 1.,
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'order_ratio',
            'description' : 'ratio to apply on the quantity property of the' \
                            'corresponding order to obtain the current quantity',
            'default'     : 1.,
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'delivery_error',
            'description' : 'correction to make the match between delivery quantity and simulation quantity consistent',
            'type'        : 'float',
            'mode'        : 'w' },
  )

  _categories = ('order', 'delivery','delivery_mode','incoterm')

