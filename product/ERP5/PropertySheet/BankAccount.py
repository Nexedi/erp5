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

class BankAccount:
    """
        Properties for BankAccount Objects
    """

    _properties = (
        {   'id'          : 'iban',
            'description' : """The IBAN of this bank account. IBAN
            is and international standard for identifying bank
            accounts worldwide. It is compulsory in the European Union.""",
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'bank_name',
            'description' : 'The name and country of the Bank holding this bank account',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'bank_branch_name',
            'description' : 'The branch holding this bank account',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'bank_account_number',
            'description' : 'The bank account number in the branch',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'bank_account_id_type',
            'description' : 'A type (ex. RIB, SWIFT, etc.) for the optional id',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'bank_account_id',
            'description' : 'An optional id for this bank account',
            'type'        : 'string',
            'mode'        : 'w' },
    )

    _categories = ( 'region', 'source')
