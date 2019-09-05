# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
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
"""
Products.ERP5.interfaces.amount_arithmetic
"""

from zope.interface import Interface

class IAmountArithmetic(Interface):
  """Amount Arithmetic private interface specification

  IAmountArithmetic defines methods to add, substract,
  multiply or device amounts of resources. No rounding
  should happen. All amounts should be converted to
  the default management unit using getNetConvertedQuantity.
  """
  def __add__(value):
    """Add an amount to another amount

      'value' is an IAmount document
    """

  def __sub__(value):
    """Substract an amount from another amount

      'value' is an IAmount document
    """

  def __mul__(value):
    """Multiply an Amount by a float

      'value' is a float
    """

  def __div__(value):
    """Divide an Amount by a float

      'value' is a float
    """
