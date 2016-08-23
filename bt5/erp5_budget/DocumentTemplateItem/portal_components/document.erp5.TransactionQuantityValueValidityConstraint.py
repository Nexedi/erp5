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

class TransactionQuantityValueValidityConstraint(ConstraintMixin):
    """
    This is only relevant for ZODB Property Sheets (filesystem Property
    Sheets rely on Products.ERP5.Constraint.TransactionQuantityValueValidity
    instead).
    """
    meta_type = 'ERP5 Transaction Quantity Value Validity Constraint'
    portal_type = 'Transaction Quantity Value Validity Constraint'

    def _checkConsistency(self, object, fixit=0):
      """
      Check if the quantity of the transaction is greater than the
      balance of the source.
      """
      errors = []

      source_cell = object.getSourceValue()
      destination_cell = object.getDestinationValue()

      if (source_cell is not None) and \
         (destination_cell is not None):
        # XXX Dirty code !
        quantity = object.getQuantity()
        budget_list = object.getPortalObject().budget_module.objectValues()
        max_quantity = 0
        for obj in budget_list:
          for item in obj.objectValues():
             if (item.getPortalType() == 'Budget Transfer Line') and \
                (item.getSourceValue() == source_cell) and \
                (item.getDestinationValue() == destination_cell):
               max_quantity = item.getQuantity()
        if quantity > max_quantity:
          if fixit != 0:
            self.setQuantity(max_quantity)
          else:
            error_message = 'The quantity of the transaction is greater than ' \
                            'the transferable maximum quantity (TMQ): ' \
                            'TMQ = %.2f' % max_quantity
            # Add error
            errors.append(self._generateError(object, error_message))
      return errors
