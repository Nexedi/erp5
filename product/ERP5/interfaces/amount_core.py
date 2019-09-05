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
Products.ERP5.interfaces.amount_core
"""

from zope.interface import Interface

class IAmountCore(Interface):
  """Amount Core private interface specification

  IAmountCore defines the minimal set of getters required
  to implement an amount.
  """
  def getQuantity():
    """
    Returns the quantity of the resource
    in the unit specified by the Amount

    NOTE: declaration is redundant with IAmountGetter
    """

  def getResource():
    """
    Returns the resource category relative URL
    of the Amount

    NOTE: declaration is redundant with IAmountGetter
    """

  def getQuantityUnit():
    """
    Returns the quantity unit category relative URL
    of the Amount

    NOTE: declaration is redundant with IAmountGetter
    """

  def isCancellationAmount():
    """
    A cancellation amount must be interpreted
    reversely wrt. to the sign of quantity.

    For example, a negative credit for a cancellation
    amount is a negative credit, not a positive
    debit.

    A negative production quantity for a cancellation
    amount is a cancelled production, not
    a consumption

    NOTE: declaration is redundant with IAmountGetter
    """

  def getEfficiency():
    """
    Returns the ratio of loss for the given amount. This
    is only used in Path such as Transformation. In other
    words, efficiency of movements is always 100%.

    NOTE: declaration is redundant with IAmountGetter
    """

  def getBaseContributionList():
    """
    The list of bases this amount contributes to.

    XXX: explain better
    """

  def getBaseApplicationList():
    """
    The list of bases this amount has been applied on. Only set if the
    amount comes from a transformation.

    XXX: explain better
    """
