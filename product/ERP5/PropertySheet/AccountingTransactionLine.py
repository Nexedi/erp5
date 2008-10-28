##############################################################################
#
# Copyright (c) 2006 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.CMFCore.Expression import Expression

class AccountingTransactionLine:
  """Constraints for Accounting Transaction Lines
  """

  _constraints = (
      # We need an account if we have a quantity for this side
    { 'id': 'source_existence',
      'description': 'Accounting Transaction Lines must use an account',
      'condition' : 'python: object.getSourceInventoriatedTotalAssetPrice()'\
                    ' and object.hasSourceSectionAccounting()'\
                    ' and not object.getDestination(portal_type="Account")',
      'type': 'CategoryExistence',
      'source' : 1,
      'portal_type': 'Account',
      'message_category_not_set': 'Account must be defined on lines',
    },
    { 'id': 'destination_existence',
      'description': 'Accounting Transaction Lines must use an account',
      'condition' :
        'python: object.getDestinationInventoriatedTotalAssetPrice()'\
        ' and object.hasDestinationSectionAccounting()'\
        ' and not object.getSource(portal_type="Account")',
      'type': 'CategoryExistence',
      'destination' : 1,
      'portal_type': 'Account',
      'message_category_not_set': 'Account must be defined on lines',
    },

      # We need a mirror section for recievable / payable accounts
    { 'id': 'destination_section_existence',
      'condition' :
        'python: object.getSourceValue(portal_type="Account") is not None'\
        ' and object.getSourceValue(portal_type="Account").getAccountTypeId()'\
        ' in ("receivable", "payable")',
      'type': 'CategoryAcquiredExistence',
      'destination_section' : 1,
      'portal_type': ('Person', 'Organisation'),
      'message_category_not_set': 'Third party must be defined for '\
          'payable or receivable accounts'
    },
    { 'id': 'source_section_existence',
      'condition' :
  'python: object.getDestinationValue(portal_type="Account") is not None'\
  ' and object.getDestinationValue(portal_type="Account").getAccountTypeId()'\
  ' in ("receivable", "payable")',
      'type': 'CategoryAcquiredExistence',
      'source_section' : 1,
      'portal_type': ('Person', 'Organisation'),
      'message_category_not_set': 'Third party must be defined for '\
          'payable or receivable accounts'
    },

       # We need a payment for bank accounts
    { 'id': 'source_payment_existence',
      'condition' : 'python: object.hasSourceSectionAccounting() and'\
      ' object.getSourceValue(portal_type="Account") is not None'\
      ' and object.getSourceValue(portal_type="Account").getAccountType()'\
      ' == "asset/cash/bank"',
      'type': 'CategoryAcquiredExistence',
      'source_payment' : 1,
      'portal_type': Expression('portal/getPortalPaymentNodeTypeList'),
      'message_category_not_set': 'Bank account must be defined for '\
          'bank type accounts'
    },
    { 'id': 'destination_payment_existence',
      'condition' : 'python: object.hasDestinationSectionAccounting()'\
    ' and object.getDestinationValue(portal_type="Account") is not None'\
    ' and object.getDestinationValue(portal_type="Account").getAccountType()'\
    ' == "asset/cash/bank"',
      'type': 'CategoryAcquiredExistence',
      'destination_payment' : 1,
      'portal_type': Expression('portal/getPortalPaymentNodeTypeList'),
      'message_category_not_set': 'Bank account must be defined for '\
          'bank type accounts'
    },
 )

