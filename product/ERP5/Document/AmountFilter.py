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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.MappedValue import MappedValue

from zLOG import LOG

class AmountFilter(MappedValue, Amount):
    """
      An AmountFilter allows to define last minute
      changes in a transformation. For example: different
      quantity, different efficiency, different resource.
      They are used mainly to customize production orders
      and are parsed by TransformationRule.

      It follows the mapped value API and is defined
      as an amount (resource, variation, quantity, efficiency)

      Definition is based on target values and values. For example,

        - quantity: 20

        - target_quantity: 25

      Means that we will actualy use 25 instead of theoretical 20.
    """

    meta_type = 'ERP5 Amount Filter'
    portal_type = 'Amount Filter'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative interfaces
    __implements__ = ( interfaces.IVariated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Predicate
                      , PropertySheet.MappedValue
                      )

    security.declareProtected(Permissions.AccessContentsInformation, 'update')
    def update(self, amount_line):
      context = self.getParentValue().asContext(**amount_line)
      # Test predicate
      if self.test(context):
        # Update amount_line
        if self.getQuantity():
          amount_line['quantity'] = self.getQuantity()
        if self.getEfficiency():
          amount_line['efficiency'] = self.getEfficiency()
        if self.getResource():
          amount_line['resource'] = self.getResource()
        if self.getVariationCategoryList():
          amount_line['variation_category_list'] = \
                      self.getVariationCategoryList()
