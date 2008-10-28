##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#                            Jerome Perrin <jerome@nexedi.com>
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

class AccountingTransaction:
  """Constraints for Accounting Transactions
  """

  _constraints = (
    { 'id': 'section_existence',
      'description': 'Both sections must be defined for invoices',
      'message_category_not_set':
              'Both sections must be defined for invoices',
      'type': 'CategoryExistence',
      'destination_section' : 1,
      'source_section' : 1,
      'portal_type': ('Person', 'Organisation'),
      'condition' : 'python: object.getPortalType() in'
                    ' portal.getPortalInvoiceTypeList()',
    },

    { 'id': 'date_existence',
      'description': 'Date must be defined',
      'message_property_not_set': 'Date must be defined',
      'message_no_such_property': 'Date must be defined',
      'condition' : 'python: object.getSimulationState() not'
                     ' in ("cancelled", "deleted")',
      'type': 'PropertyExistence',
      'start_date' : 1,
    },

    { 'id': 'currency_existence',
      'description': 'Currency must be defined',
      'message_category_not_set':
           'Currency must be defined',
      'portal_type': ('Currency',),
      'condition' : 'python: object.getSimulationState() not'
                     ' in ("cancelled", "deleted")',
      'type': 'CategoryExistence',
      'resource' : 1,
    },

    { 'id': 'debit_credit_balance',
      'description': 'Total Debit must equal Total Credit',
      'condition' : 'python: object.getSimulationState() not'
                     ' in ("cancelled", "deleted")',
      'type': 'AccountingTransactionBalance',
    },

 )
