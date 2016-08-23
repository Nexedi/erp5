##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#             Romain Courteaud <romain@nexedi.com>
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin
from Products.ERP5Type import PropertySheet

class TransactionQuantityValueFeasabilityConstraint(ConstraintMixin):
    """
    Check if the quantity of the transaction is possible
    for the source and the destination

    This is only relevant for ZODB Property Sheets (filesystem Property
    Sheets rely on Products.ERP5.Constraint.TransactionQuantityValueFeasability
    instead).
    """
    meta_type = 'ERP5 Transaction Quantity Value Feasability Constraint'
    portal_type = 'Transaction Quantity Value Feasability Constraint'

    def _checkConsistency(self, object, fixit=0):
      """
      Check if the quantity of the transaction is possible
      for the source and the destination
      """
      errors = []
      source_cell = object.getSourceValue()
      destination_cell = object.getDestinationValue()
      # Check for source and destination
      for node, sign, node_title in ((source_cell, 1, 'source'),
                                     (destination_cell, -1, 'destination')):
        # As the quantity can change a few lines letter,
        # we need to get it each time.
        object_quantity = object.getQuantity()
        quantity = object_quantity * sign
        if node is not None:
          balance = node.getCurrentBalance()
          is_transaction_ok = 1
          # Check if balance and quantity have the same sign
          if ((balance < 0) and (quantity < 0)):
            if balance > quantity:
              is_transaction_ok = 0
          elif ((balance >= 0) and (quantity >= 0)):
            if balance < quantity:
              is_transaction_ok = 0
          # Raise error
          if not is_transaction_ok:
            if fixit != 0:
              object.setQuantity(balance)
            else:
              error_message = 'The quantity "%s" of the transaction is not ' \
                              'compatible with budget "%s" defined on the ' \
                              '%s "%s".' % \
                              (object_quantity, balance, node_title, node)
              # Add error
              errors.append(self._generateError(object, error_message))
      return errors
