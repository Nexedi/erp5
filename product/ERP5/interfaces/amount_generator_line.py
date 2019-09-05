# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Lukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
Products.ERP5.interfaces.amount_generator_line
"""

from zope.interface import Interface

class IAmountGeneratorLine(Interface):
  """Amount Generator Line interface specification
  """

  def getCellAggregateKey():
    """Define a key in order to aggregate amounts at cell level

      Transformed Resource (Transformation)
        key must be None because:
          - quantity and variation are defined in different cells so that the
            user does not need to enter values depending on all axes
          - amount_generator_cell.test should filter only 1 variant
        current key = (acquired resource, acquired variation)

      Assorted Resource (Transformation)
        key = (assorted resource, assorted resource variation)
        usually resource and quantity provided together

      Payroll
        key = (payroll resource, payroll resource variation)

      Tax
        key = (tax resource, tax resource variation)
    """

  def getBaseAmountQuantity(delivery_amount, base_application, rounding):
    """Default method to compute quantity for the given base_application
    """
