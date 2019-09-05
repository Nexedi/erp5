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
Products.ERP5.interfaces.amount_price
"""

from zope.interface import Interface

class IAmountPrice(Interface):
  """Amount Price private interface specification

  IAmountPrice defines methods to compute total price
  and unit price of a resource, taking into account
  contributions and roundings.
  """
  def getPrice():
    """
    Returns the input unit price of the resource

    NOTE: redundant with IPriceGetter
    """

  def getUnitPrice(base_contribution=None, rounding=False):
    """
    Returns the unit price of the resource, taking into
    account rounding and contributions (ex. taxes).

    base_contribution -- optional base_contribution.
                If defined, a complex process is launched
                to add or remove to the price various amounts
                calculated from applicable trade models if
                any.

    rounding -- optional rounding parameter. If set to True,
                find and applies appropriate rounding model.
    """

  def getTotalPrice(base_contribution=None, rounding=False):
    """
    Returns total price ie. the unit price of the resource
    multiplied by the quantity, taking into
    account rounding and contributions (ex. taxes).

    base_contribution -- optional base_contribution.
                If defined, a complex process is launched
                to add or remove to the price various amounts
                calculated from applicable trade models if
                any.

    rounding -- optional rounding parameter. If set to True,
                find and applies appropriate rounding model.
    """
