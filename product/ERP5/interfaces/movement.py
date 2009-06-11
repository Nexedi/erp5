# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from zope.interface import Interface

class IMovement(Interface):
  """Movement interface specification

  A movement represents an amount of resources which 
  is moved along an Arrow (source and destination).

  Equations:
    Production/Consumption

    (A -> B)
      production_quantity means nothing
      consumption_quantity means nothing

    (A -> Nothing)
    if quantity > 0
      consumption_quantity = quantity
      production_quantity = 0

    if quantity < 0
      consumption_quantity = 0
      production_quantity = - quantity

    (Nothing -> B)
    if quantity > 0
      consumption_quantity = 0
      production_quantity = quantity

    if quantity < 0
      consumption_quantity = - quantity 
      production_quantity = 0

    Credit/Debit

    if quantity > 0
      source_credit = - quantity
      source_debit = quantity
      destination_credit = quantity
      destination_debit = - quantity

    if quantity < 0
      source_credit = quantity
      source_debit = - quantity
      destination_credit = - quantity
      destination_debit = quantity

    TODO:
      1. finish equations (for asset price)
      2. clarify asset value application for multi
         currency accunting
      3. clarify the use of asset price in ERP5
         (accounting and outside) since we no 
         longer store asset price on non accounting
         movements
  """
  # Helper API for Production
  def getConsumptionQuantity():
    """Returns the consumed quantity during
    production
    """

  def getProductionQuantity():
    """Returns the produced quantity during
    production
    """

  # Helper methods for asset value calculation
  def getSourceAssetPrice():
    """Returns the asset price on the source, if defined
    XXX - it is unclear if we still use this
    """

  def getDestinationAssetPrice():
    """Returns the asset price on the destination, if defined
    XXX - it is unclear if we still use this
    """

  def getSourceInventoriatedTotalAssetPrice():
    """Returns the total asset price for the source, if defined
    """

  def getDestinationInventoriatedTotalAssetPrice():
    """Returns the total asset price for the destination, if defined
    """

  # Helper methods for single currency Accounting (debit / credit)
  def getSourceDebit():
    """Returns the source debit in the transaction currency
    """

  def getSourceCredit():
    """Returns the source credit in the transaction currency
    """

  def getDestinationDebit():
    """Returns the destination debit in the transaction currency
    """

  def getDestinationCredit():
    """Returns the destination credit in the transaction currency
    """

  # Helper methods for multi currency Accounting (debit / credit)
  def getSourceAssetDebit():
    """Returns the source debit in the source management currency
    """

  def getSourceAssetCredit():
    """Returns the source credit in the source management currency
    """

  def getDestinationAssetDebit():
    """Returns the destination debit in the destination management currency
    """

  def getDestinationAssetCredit():
    """Returns the destination credit in the destination management currency
    """

  def getSourceInventoriatedTotalAssetDebit():
    """Unclear - XXX
    """

  def getSourceInventoriatedTotalAssetCredit():
    """Unclear - XXX
    """

  def getDestinationInventoriatedTotalAssetDebit():
    """Unclear - XXX
    """

  def getDestinationInventoriatedTotalAssetCredit():
    """Unclear - XXX
    """