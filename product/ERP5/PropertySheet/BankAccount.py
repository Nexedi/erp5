##############################################################################
#
# Copyright (c) 2002-2005 Nexedi SARL and Contributors. All Rights Reserved.
#               Jean-Paul Smets-Solanes <jp@nexedi.com>
#               Kevin Deldycke <kevin@nexedi.com>
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
    {'id'          : 'bank_country_code',
     'description' : 'The ISO 3166 2-letters country code of the bank to include in the IBAN.',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'bank_code',
     'description' : 'The code that identify the Bank holding this bank account. It it the first part of the BBAN.',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'branch',
     'description' : 'The branch code holding this bank account. This is the middle part of the BBAN.',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'bank_account_number',
     'description' : 'The bank account number. This is the last part of the BBAN',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'bank_account_key',
     'description' : 'The bank account key. This is an additionnal part of the BBAN',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'bank_account_holder_name',
     'description' : 'The bank account holder\'s name',
     'type'        : 'string',
     'mode'        : 'w'
    },
    {'id'          : 'overdraft_facility',
     'description' : 'The bank account overdraft facility indicator',
     'type'        : 'boolean',
     'mode'        : 'w'
    },
    {'id'          : 'internal_bank_account_number',
     'description' : 'An internal bank account number',
     'type'        : 'string',
     'mode'        : 'w'
    },

  )

  _categories = ( 'source', )
