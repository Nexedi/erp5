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

from Products.ERP5Type.Constraint import Constraint

class BudgetConsumptionFeasability(Constraint):
    """
    Check if there is enough budget to consumed.
    """

    def _checkConsistency(self, object, fixit=0):
      """
      Check if there is enough budget to consumed.
      """
      errors = []

      new_category_list = []
      new_category_list.append(object.getSourceSection())
      new_category_list.append(object.getResource())

      object_context = self.asContext(
          context=object,
          categories=new_category_list,
      )
      portal_domain = self.portal_domains
      result = portal_domain.searchPredicateList(
                     object_context, portal_type=["Budget Cell"])
      if len(result) != 1:
        error_message = 'One budget must be found for %s' % \
            object
        # Add error
        errors.append(self._generateError(object, error_message))
      else:
        budget_cell = result[0]
        budget = budget_cell.getAvailableBudget()
        quantity = object.getQuantity()
        if quantity > budget:
          error_message = 'Quantity is bigger than the budget %s' % \
              budget_cell
          # Add error
          errors.append(self._generateError(object, error_message))

      return errors
