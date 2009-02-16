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

class DefaultSupply:
    """
        Properties which allow to define a Default Supply for a resource.

    """

    _properties = (
        # XXX Kept for compatibility.
        {   'id'          : 'supply_line',
            'storage_id'  : 'default_supply_line',
            'description' : '',
            'type'        : 'content',
            'portal_type' : ('Supply Line',),
            'acquired_property_id' : ('base_price', 'id', 'priced_quantity',
                                  'price_currency', 'source', 'destination',
                                  'quantity_step', 'priced_quantity',
                                  'start_date', 'stop_date',
                                  'start_date_range_max',
                                  'start_date_range_min',
                                  'comment', 'source_reference',
                                  'destination_reference',
                                  'p_variation_base_category_list'),
            'mode'        : 'w' },
        # Define default purchase supply line
        {   'id'          : 'purchase_supply_line',
            'storage_id'  : 'default_psl',
            'description' : '',
            'type'        : 'content',
            'portal_type' : ('Purchase Supply Line',),
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
                                  'p_variation_base_category_list',
                                  'destination_account'),
            'mode'        : 'w' },
        # Define default sale supply line
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
                                  'comment', 'destination_reference',
                                  'p_variation_base_category_list',
                                  'source_account'),
            'mode'        : 'w' },
       )

    _categories = ()

