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

class Resource:
    """
        Properties which allow to define a generic Resource.

        The underlying idea is that we only define 'base' properties
        which correspond to a generic variations of the resource.

        Variations can change the base properties by introduction
        new attributions such as 'option' properties.
    """

    _properties = (
        # Pricing properties
        {   'id'          : 'source_base_price',
            'description' : 'A typical per unit price at which this resource can be sourced (bought)',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'source_base_price_validity',
            'description' : 'Validity of the typical per unit price at which this resource can be sourced',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'destination_base_price',
            'description' : 'A typical per unit price at which this resource can be supplied (sold)',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'destination_base_price_validity',
            'description' : 'Validity of the typical per unit price at which this resource can be supplied',
            'type'        : 'date',
            'mode'        : 'w' },
        {   'id'          : 'base_price',
            'description' : 'A default per unit price used for internal price calculations',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'priced_quantity',
            'description' : 'Number of units involved in base prices',
            'type'        : 'float',
            'default'     : 1.0,
            'mode'        : 'w' },
        {   'id'          : 'consumer_unit_quantity',
            'description' : 'Number of consumer_unit involved in the resoure (sku)',
            'type'        : 'float',
            'default'     : 1.0,
            'mode'        : 'w' },
        {   'id'          : 'base_unit_quantity',
            'description' : 'The smallest transferrable amount expressed in the default unit',
            'type'        : 'float',
            'default'     : 1.0,
            'mode'        : 'w' },
        # Physical properties
        {   'id'          : 'base_weight',
            'description' : 'A typical per unit weight of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'base_volume',
            'description' : 'A typical per unit volume of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'base_length',
            'description' : 'A typical per unit length of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'base_width',
            'description' : 'A typical per unit width of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'base_height',
            'description' : 'A typical per unit height of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'base_surface',
            'description' : 'A typical per unit surface of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        # Basic conversion properties
        # A property is set on categories to define if it is length, weight etc.
        # another property defines the conversion to the default lenght
        #                                         (ie. nomber of meters in 1 inch)
        # This allows to implement universal conversions
        {   'id'          : 'length_quantity',
            'description' : 'length of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'weight_quantity',
            'description' : 'weight of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'height_quantity',
            'description' : 'height of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'width_quantity',
            'description' : 'width of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'surface_quantity',
            'description' : 'surface area of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'volume_quantity',
            'description' : 'volume of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'unit_quantity',
            'description' : 'units of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'time_quantity',
            'description' : 'time of the resource',
            'type'        : 'float',
            'mode'        : 'w' },
        # Sourcing / planning properties
        {   'id'          : 'source_title',
            'storage_id'  : 'default_source_title', # Compatibility
            'description' : 'The titles of the sources of this resource',
            'type'        : 'string',
            'acquisition_base_category'     : ('source',),
            'acquisition_portal_type'       : ('Organisation','MetaNode'),
            'acquisition_copy_value'        : 0,
            'acquisition_accessor_id'       : 'getTitle',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'destination_title',
            'storage_id'  : 'default_destination_title', # Compatibility
            'description' : 'The titles of the destinations of this resource',
            'type'        : 'string',
            'acquisition_base_category'     : ('destination',),
            'acquisition_portal_type'       : ('Organisation','MetaNode'),
            'acquisition_copy_value'        : 0,
            'acquisition_accessor_id'       : 'getTitle',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        # Default attributes overriden in supply lines (should be in supply line)
        {   'id'          : 'trade_description',
            'description' : 'A description of the document intended for client',
            'type'        : 'text',
            'default'     : '',
            'mode'        : 'w' },
        {   'id'          : 'instructions',
            'description' : 'instructions in order to explain how to use the resource',
            'type'        : 'text',
            'default'     : '',
            'mode'        : 'w' },
        # Pricing
        {  'id'          : 'p_variation_base_category',
           # XXX Compatibility
           'description' : 'Base category range of matrix',
           'type'        : 'lines',
           'default'     : [],
           'multivalued' : 1,
           'mode'        : 'w' },

    )

    _categories = ( 'source', 'destination', 'quantity_unit', 'price_unit',
                    'weight_unit', 'length_unit', 'height_unit', 'width_unit',
                    'volume_unit',
                    'base_contribution',
                    'use',
                    'price_currency',  'source_price_currency',
                    'destination_price_currency', 'product_line',
                    'industrial_phase')

