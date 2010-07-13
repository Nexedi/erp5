##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien MORIN <fabien@nexedi.com>
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

class SoftwareProduct:
    """
    """
    _properties = (
        {   'id'          : 'description',
            'description' : '',
            'type'        : 'text',
            'default'     : '',
            'mode'        : 'w',
            # we want description to be translatable
            'translatable': 1,},
        {   'id'          : 'sale_supply_line',
            'storage_id'  : 'default_ssl',
            'description' : '',
            'type'        : 'content',
            'portal_type' : ('Sale Supply Line',),
            'acquired_property_id' : ('base_price', 'id', 'priced_quantity',
                                  'price_currency', 'price_currency_title',
                                  'source', 'destination',
                                  'source_title', 'destination_title',
                                  'source_value', 'destination_value',
                                  'quantity_step', 'priced_quantity',
                                  'start_date', 'stop_date',
                                  'start_date_range_max',
                                  'start_date_range_min',
                                  'comment', 'source_reference',
                                  'destination_reference',
                                  'p_variation_base_category_list',
                                  'source_account',
                                  'min_delay', 'max_delay', 'min_flow', 'max_flow',
                                  'min_stock', 'max_stock',
                                  'aggregate', 'aggregate_value', 'aggregate_title'),
            'mode'        : 'w' },

    )
    _categories = ('activity', 'region', 'aggregate',)
