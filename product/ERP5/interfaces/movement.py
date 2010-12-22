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
"""
Products.ERP5.interfaces.movement
"""
from Products.ERP5.interfaces.amount import IAmount
from Products.ERP5.interfaces.arrow_base import IArrowBase

class IAssetMovement(IAmount):
  """Asset Movement private interface specification

  Asset movements are use to represent the asset 
  value of a movement of resources leaving a 
  source and reach a destination. 
  """
  # We must a find a way to use property sheets in or as interfaces
  # property_sheets = (PropertySheet.Price, )

  def getSourceAssetPrice():
    """
    Return the asset price for the source section,
    usually the price of the movement converted to
    the currency of the source section using the currency
    rate of the day. If no price is defined, an internal
    price may be looked up. It is also possible for
    a movement to have 'None' source asset price,
    for example for a movement with positive quantity
    going from one warehouse to another warehouse of
    the same company.
    """

  def getDestinationAssetPrice():
    """
    Return the asset price for the destination section,
    usually the price of the movement converted to
    the currency of the destination section using the currency
    rate of the day. If no price is defined, an internal
    price may be looked up first. It is also possible for
    a movement to have 'None' destination asset price,
    for example for a movement with negative quantity
    going from one warehouse to another warehouse of
    the same company.
    """

  def getSourceInventoriatedTotalAssetPrice():
    """
    Returns the total asset price for the source section, either
    defined explicitely by the source_asset_price property
    (as in accounting) or by calling getSourceAssetPrice and
    multiplying it by the quantity. If no asset price
    is defined, return None. Asset calculation methods
    (SimulationTool.getInventoryAssetPrice) interprete
    None using FIFO, FILO or Average algorithm.
    """

  def getDestinationInventoriatedTotalAssetPrice():
    """
    Returns the total asset price for the destination section, either
    defined explicitely by the destination_asset_price property
    (as in accounting) or by calling getDestinationAssetPrice and
    multiplying it by the quantity. If no asset price
    is defined, return None. Asset calculation methods
    (SimulationTool.getInventoryAssetPrice) interprete
    None using FIFO, FILO or Average algorithm.
    """

class IProductionMovement(IAmount):
  """Production Movement private interface specification

  Production movements have a source or a destination equal
  to None. They are used to represent productions or
  consumptions or resources according to the following
  specification:

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
  """
  def getConsumptionQuantity():
    """
    Returns the consumed quantity during production
    """

  def getProductionQuantity():
    """
    Returns the produced quantity during production
    """

class IAccountingMovement(IAssetMovement):
  """
  Accounting Movement private interface specification

  The notion of debit and credit is used in accounting instead of signed
  quantity. The following calculation rules apply:

    Credit/Debit

    if quantity > 0
      source_credit = quantity
      source_debit = 0
      destination_credit = 0
      destination_debit = quantity

    if quantity < 0
      source_credit = 0
      source_debit = - quantity
      destination_credit = - quantity
      destination_debit = 0

  The cancellation amount concept from IAmount interface also applies for debit
  and credit. For a cancellation amount, the calculation rule are different:

    if quantity > 0
      source_credit = 0
      source_debit = - quantity
      destination_credit = - quantity
      destination_debit = 0

    if quantity < 0
      source_credit = quantity
      source_debit = 0
      destination_credit = 0
      destination_debit = quantity

  """
  # We must a find a way to use property sheets in or as interfaces
  # property_sheets = (PropertySheet.Price, )

  # Helper methods for single currency Accounting (debit / credit)
  def getSourceDebit():
    """
    Returns the source debit in the transaction currency
    """

  def getSourceCredit():
    """
    Returns the source credit in the transaction currency
    """

  def getDestinationDebit():
    """
    Returns the destination debit in the transaction currency
    """

  def getDestinationCredit():
    """
    Returns the destination credit in the transaction currency
    """

  # Helper methods for multi currency Accounting (debit / credit)
  def getSourceAssetDebit():
    """
    Returns the source debit in the source section management currency
    based on the source_total_asset price property
    """

  def getSourceAssetCredit():
    """
    Returns the source credit in the source section management currency
    based on the source_total_asset price property
    """

  def getDestinationAssetDebit():
    """
    Returns the destination debit in the destination section management currency
    based on the destination_total_asset price property
    """

  def getDestinationAssetCredit():
    """
    Returns the destination credit in the destination section management currency
    based on the destination_total_asset price property
    """

  # The following is really unclear - 
  #   It uses getSourceInventoriatedTotalAssetPrice instead of
  #   of getSourceInventoriatedTotalAssetPrice instead of getSourceTotalAssetPrice
  #   I can only see one purpose: presentation of reports in predictive accounting
  #   ie. in transactions generated by simulation which do not yet have
  #   well defined source_total_asset/destination_total_asset
  def getSourceInventoriatedTotalAssetDebit():
    """
    Unclear - XXX
    """

  def getSourceInventoriatedTotalAssetCredit():
    """
    Unclear - XXX
    """

  def getDestinationInventoriatedTotalAssetDebit():
    """
    Unclear - XXX
    """

  def getDestinationInventoriatedTotalAssetCredit():
    """
    Unclear - XXX
    """

class IMovement(IProductionMovement, IArrowBase):
  """Movement interface specification

  A movement represents an amount of resources which 
  is moved along an Arrow (source and destination)
  from a source A to a destination B. 
  """
  def isMovement():
    """
    Returns True if this movement should be indexed in the
    stock table of the catalog, False else.
    """
