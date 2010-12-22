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

class Variation:
    """
        Properties which allow to define a discrete Variation instance
    """

    _properties = (
        # Pricing properties
        {   'id'          : 'source_additional_price',
            'description' : 'A typical per unit price at which this resource can be sourced (bought)',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'source_additional_price_validity',
            'description' : 'Validity of the typical per unit price at which this resource can be sourced',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'destination_additional_price',
            'description' : 'A typical per unit price at which this resource can be supplied (sold)',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'destination_additional_price_validity',
            'description' : 'Validity of the typical per unit price at which this resource can be supplied',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'additional_price',
            'description' : 'A default per unit price used for internal price calculations',
            'type'        : 'float',
            'mode'        : 'w' },
        # Physical properties
        {   'id'          : 'additional_weight',
            'description' : 'A typical per unit weight of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'additional_volume',
            'description' : 'A typical per unit volume of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
    )

