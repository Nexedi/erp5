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

from Products.ERP5.ERP5Globals import *

class Amortisation:
    """
        Properties which allow to immobilise an item

        These properties are applied to an Immobilisation Movement or to an Item
        
        TODO:
          
          - rename categories for more genericity (input_acount -> input)
          
          - rename vat property            
    """

    _properties = (
        {   'id'          : 'amortisation_value', # XXX Naming - value has other meaning in ERP5
            'description' : 'The deprecated value of the item',
            'description' : 'The value to use to calculate the accounting amortisation movements (net of tax)',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : item_type_list,
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getAmortisationValue',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'amortisation_duration',
            'description' : 'The remaining amortisation duration in months',
            'type'        : 'int',
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : item_type_list,
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getAmortisationDuration',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'immobilisation',
            'description' : 'The item is immobilised after the movement',
            'type'        : 'boolean',
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : item_type_list,
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getImmobilisation',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'fiscal_coefficient',
            'description' : 'The fiscal coefficient to use in degressive amortisation',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : item_type_list,
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getFiscalCoefficient',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        {   'id'          : 'vat', # XXX Naming problem according to JPS
            'description' : 'The VAT at the beginning of the immobilisation period',
            'type'        : 'float',
            'acquisition_base_category'     : ('parent',),
            'acquisition_portal_type'       : item_type_list,
            'acquisition_copy_value'        : 1,
            'acquisition_mask_value'        : 1,
            'acquisition_accessor_id'       : 'getVat',
            'acquisition_depends'           : None,
            'mode'        : 'w' },
        
            )
    
    _categories = ('input_account', 'output_account', 'immobilisation_account', 
                   'amortisation_account', 'depreciation_account',
                   'vat_account', 'amortisation_type') # XXX Some rename required
