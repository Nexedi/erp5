##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon <guillaume@nexedi.com>
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

class Amortisation:
    """
        Properties which allow to immobilise an item

        These properties are applied to an Immobilisation Movement or to an Item

        TODO:
          - rename categories for more genericity (input_acount -> input)
    """

    _properties = (
        {   'id'          : 'amortisation_start_price',
            'description' : 'The value to use to calculate the accounting amortisation movements (net of tax)',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getAmortisationStartPrice',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'extra_cost_price',
            'description' : 'The extra costs to immobilise with the main price (net of tax)',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getExtraCostPrice',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'disposal_price',
            'description' : 'The estimated price at the end of the lifetime (net of tax)',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getDisposalPrice',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'durability',
            'description' : 'The remaining durability of the item',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getDurability',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'amortisation_duration',
            'description' : 'The remaining amortisation duration in months',
            'type'        : 'int',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getAmortisationDuration',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'immobilisation_vat',
            'description' : 'The VAT at the beginning of the immobilisation period',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getImmobilisationVat',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'amortisation_method',
            'description' : 'The amortisation method used for this particular immobilisation period',
            'type'        : 'string',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getAmortisationMethod',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        # Properties specific to each amortisation method
        {   'id'          : 'degressive_coefficient',
            'description' : 'The fiscal coefficient to use in degressive amortisation',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getDegressiveCoefficient',
            'acquisition_portal_type'       : Expression('python:[]'),
            'acquisition_depends'           : None,
            'mode'        : 'w' },
            )

    _categories = ('input_account', 'output_account', 'immobilisation_account', 'amortisation_account',
                   'depreciation_account', 'extra_cost_account', 'monthly_amortisation_account',
                   'immobilisation_vat_account') # XXX Some rename required
