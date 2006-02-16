##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

class BudgetTransactionConstraint:
  """
  Budget transaction constraint.
  Commented constraint are kept as example.
  """

  _constraints = (
#     { 'id'            : 'source',
#       'type'          : 'CategoryMembershipArity',
#       'min_arity'     : '1',
#       'max_arity'     : '1',
#       'portal_type'   : ('Budget Cell', ),
#       'base_category' : ('source',),
#       'description'   : 'Source is not defined.'
#     },
#     { 'id'            : 'destination',
#       'type'          : 'CategoryMembershipArity',
#       'min_arity'     : '1',
#       'max_arity'     : '1',
#       'portal_type'   : ('Budget Cell', ),
#       'base_category' : ('destination',),
#       'description'   : 'Destination is not defined.'
#     },
    { 'id'            : 'property_existence',
      'type'          : 'PropertyExistence',
      'start_date'    : None,
      'description'   : 'Date is not defined.'
    },
#     { 'id'            : 'quantity_validity',
#       'type'          : 'TransactionQuantityValueValidity',
#       'description'   : 'The quantity of the transaction is greater than ' \
#                         'the transferable maximum quantity.'
#     },
    { 'id'            : 'quantity_feasability',
      'type'          : 'TransactionQuantityValueFeasability',
      'description'   : 'The quantity of the transaction is not possible.'
    },
  )
