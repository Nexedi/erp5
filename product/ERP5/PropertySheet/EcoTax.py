##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

class EcoTax:
    """
        Properties for objects such as invoices which require specification of
        an environmental tax (ex.recupel in Belgium).
        Based on these properties, accounting transaction lines can be generated.
    """

    _properties = (
        {   'id'          : 'eco_tax_base_price',
            'description' : 'A minimum value for the ecologic tax',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'eco_tax_ratio',
            'description' : 'Ratio which should be applied to income to calculate ecologic tax',
            'type'        : 'float',
            'mode'        : 'w' },
        {   'id'          : 'eco_tax_recoverable',
            'description' : 'Defines recoverability of the ecologic tax',
            'type'        : 'boolean',
            'mode'        : 'w' },
    )

