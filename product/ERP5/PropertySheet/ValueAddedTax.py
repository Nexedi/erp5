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

from Products.ERP5.ERP5Globals import invoice_or_invoice_movement_type_list

class ValueAddedTax:
    """
        Properties for objects such as invoices which require specification of
        a VAT or sales tax. Based on these properties, accounting transaction lines
        can be generated.
    """

    _properties = (
        {   'id'          : 'value_added_tax_ratio',
            'description' : 'Ratio which should be applied to income to calculate VAT',
            'type'        : 'float',
            'acquisition_base_category' : ('parent',),
            'acquisition_portal_type'   : invoice_or_invoice_movement_type_list,
            'acquisition_copy_value'    : 0,
            'acquisition_mask_value'    : 1,
            'acquisition_sync_value'    : 0,
            'acquisition_accessor_id'   : 'getValueAddedTaxRatio',
            'acquisition_depends'       : None,
            'mode'        : 'w' },
        {   'id'          : 'value_added_tax_recoverable',
            'description' : 'Defines recoverability of the VAT',
            'type'        : 'boolean',
            'acquisition_base_category' : ('parent',),
            'acquisition_portal_type'   : invoice_or_invoice_movement_type_list,
            'acquisition_copy_value'    : 0,
            'acquisition_mask_value'    : 1,
            'acquisition_sync_value'    : 0,
            'acquisition_accessor_id'   : 'isValueAddedTaxRecoverable',
            'acquisition_depends'       : None,
            'mode'        : 'w' },
    )

